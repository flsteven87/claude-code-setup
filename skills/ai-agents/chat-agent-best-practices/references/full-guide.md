---
name: chat-agent-best-practices
description: Use when building AI chat agents with LangGraph, implementing SSE streaming, integrating AG-UI protocol events, adding Mem0 memory, creating MCP tools, or managing conversation state in React. Covers human-in-the-loop interrupts, checkpointing, JSON Patch state sync, and token streaming patterns.
updated: 2026-01-22
---

# Chat Agent Best Practices

## Overview

Reference guide for building production-ready AI chat agents combining:

- **LangGraph v1.0**: Agent workflow orchestration with tool calling and HITL
- **AG-UI Protocol**: Standardized agent-to-frontend event streaming (CopilotKit)
- **A2UI Protocol**: Agent-driven UI intent description (Google, complementary to AG-UI)
- **Mem0**: Persistent AI memory across sessions (+26% accuracy over OpenAI Memory)
- **MCP**: Model Context Protocol for tool/resource exposure
- **SSE**: Server-Sent Events for real-time streaming
- **React State**: Frontend conversation management

## Quick Reference

| Technology | Key Pattern                         | Critical Pitfall                |
| ---------- | ----------------------------------- | ------------------------------- |
| LangGraph  | `Annotated[T, reducer]` for state   | State resets without reducer    |
| LangGraph  | PostgreSQL checkpointer             | No cross-session resume without it |
| AG-UI      | 16 event types + JSON Patch         | Missing lifecycle events        |
| Mem0       | `search_memories()` before LLM call | Storing every turn (too noisy)  |
| Mem0       | Graph Memory for relationships      | Flat memory loses context       |
| MCP        | Tools (model) vs Resources (app)    | Bare exceptions in tools        |
| SSE        | `X-Accel-Buffering: no` header      | Nginx buffering kills stream    |
| React      | `useReducer` + Context for chat     | Stale closure in event handlers |

---

## 1. LangGraph v1.0 Patterns

### State with Reducers (Critical)

```python
from typing import Annotated
from langgraph.graph import StateGraph

# Custom reducer to preserve data across turns
def merge_collected_info(existing: CollectedInfo, new: CollectedInfo) -> CollectedInfo:
    if existing.completeness_score() > 0 and new.completeness_score() == 0:
        return existing  # Don't overwrite with empty
    return existing.merge_with(new)

class AgentState(TypedDict):
    # Without Annotated + reducer, state resets each turn!
    collected_info: Annotated[CollectedInfo, merge_collected_info]
    messages: Annotated[list, add_messages]
    counter: Annotated[int, lambda old, new: max(old, new)]
```

### Bypassing Reducers with Overwrite (2026)

In some cases, you need to reset state rather than merge:

```python
from langgraph.types import Overwrite

def reset_context_node(state: AgentState):
    # Bypass reducer, directly overwrite the value
    return {"collected_info": Overwrite(CollectedInfo())}
```

### Resilient Application Pattern (2026)

A production-ready LangGraph application follows:

| Aspect    | Guideline                                                    |
| --------- | ------------------------------------------------------------ |
| **State** | Small, typed, validated; reducers used sparingly             |
| **Flow**  | Simple edges where possible; conditional only at real decisions |
| **Memory**| PostgreSQL checkpointer with thread-scoped checkpoints       |
| **Stream**| Choose messages/updates/values/custom per UX and bandwidth   |
| **Errors**| Node + graph + app-level handling with graceful degradation  |

### Node Separation Pattern (2026 Best Practice)

Split monolithic nodes into single-responsibility nodes for better observability and testability:

```python
# BAD: Monolithic node doing everything
async def respond(state):
    # Routing logic
    # LLM invocation
    # Tool calling
    # Response formatting
    # AG-UI event emission
    pass  # 200+ lines

# GOOD: ReAct-style separated nodes
graph.add_node("classify_intent", classify_intent)  # Routing decision
graph.add_node("extract_info", extract_info)        # LLM with tools
graph.add_node("execute_tools", execute_tools)      # Tool execution
graph.add_node("generate_response", generate_response)  # Response formatting
```

**Node Responsibilities:**

| Node                | Responsibility                         | Output                                   |
| ------------------- | -------------------------------------- | ---------------------------------------- |
| `classify_intent`   | Determine next action                  | `classified_intent`, `intent_confidence` |
| `extract_info`      | LLM invocation with tool binding       | `pending_tool_calls`, `llm_analysis`     |
| `execute_tools`     | Execute tools, emit AG-UI events       | `extracted_updates`, `agui_events`       |
| `generate_response` | Format response with structured output | `response`, `suggested_replies`          |

### Conditional Routing with Intent Classification

```python
from pydantic import BaseModel, Field
from typing import Literal

class IntentClassification(BaseModel):
    """Structured output for intent classification."""
    intent: Literal[
        "continue_conversation",
        "ready_for_confirmation",
        "user_confirmed",
        "quick_post",
    ] = Field(description="Classified intent")
    confidence: float = Field(ge=0, le=1)
    reasoning: str

# Intent classifier with structured output
intent_classifier = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,  # Low for consistent classification
).with_structured_output(IntentClassification)

def _build_graph(self):
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify_intent", self._classify_intent)
    graph.add_node("extract_info", self._extract_info)
    graph.add_node("request_confirmation", self._request_confirmation)
    graph.add_node("generate_spec", self._generate_spec)

    # Conditional routing based on intent
    graph.add_conditional_edges(
        "classify_intent",
        self._route_by_intent,
        {
            "continue": "extract_info",
            "confirm": "request_confirmation",
            "generate": "generate_spec",
        }
    )

def _route_by_intent(self, state: AgentState) -> str:
    intent = state.get("classified_intent", "continue_conversation")
    if intent in ("user_confirmed", "quick_post"):
        return "generate"
    if intent == "ready_for_confirmation":
        return "confirm"
    return "continue"
```

### Human-in-the-Loop with Interrupt and Command

```python
from langgraph.types import interrupt, Command

def confirmation_node(state: AgentState):
    # Pause execution, surface data to frontend
    user_response = interrupt({
        "type": "confirmation_request",
        "message": state["confirmation_message"],
        "data": state["collected_info"],
        "completeness_score": state["completeness_score"],
    })
    # Execution resumes here after Command(resume=...)
    return {"user_confirmed": is_confirmation(user_response)}

# Resume from interrupt with Command
async def handle_message(graph, config, message):
    current_state = await graph.aget_state(config)
    if current_state and current_state.next:
        # Resuming from interrupt - use Command
        input_data = Command(resume=message)
    else:
        # Normal message
        input_data = {"messages": [{"role": "user", "content": message}]}

    async for event in graph.astream(input_data, config):
        yield event
```

### Structured Output for Agent Responses

Replace tag-based parsing (e.g., `<suggested_replies>`) with structured output:

```python
from pydantic import BaseModel, Field

class SuggestedReply(BaseModel):
    text: str = Field(description="Reply text to display")
    intent: str | None = Field(default=None, description="Intent hint")

class AgentResponse(BaseModel):
    """Structured response replacing tag parsing."""
    content: str = Field(description="Response text")
    suggested_replies: list[SuggestedReply] = Field(
        default_factory=list,
        description="2-4 quick reply options"
    )

# Response generator with structured output
response_generator = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
).with_structured_output(AgentResponse)

async def generate_response(state: AgentState):
    response: AgentResponse = await response_generator.ainvoke([...])
    return {
        "response": response.content,
        "suggested_replies": [r.model_dump() for r in response.suggested_replies],
    }
```

**Benefits over tag parsing:**

- No complex regex/streaming filters
- Type-safe suggested_replies
- Reliable extraction (no partial tag issues)
- Simpler streaming code (~100 lines less)

### Checkpointer Setup (PostgreSQL)

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def get_checkpointer():
    saver = AsyncPostgresSaver.from_conn_string(DATABASE_URL)
    await saver.setup()  # MUST call setup() on first use
    return saver

# Thread ID format: {user_id}:{conversation_id}
config = {"configurable": {"thread_id": f"{user_id}:{conv_id}"}}
```

### Streaming Modes

| Mode                           | Use Case           | Events                 |
| ------------------------------ | ------------------ | ---------------------- |
| `astream()`                    | Node-level updates | `{node_name: output}`  |
| `astream_events(version="v2")` | Token streaming    | `on_chat_model_stream` |

```python
# Token-level streaming
async for event in graph.astream_events(input_data, config, version="v2"):
    if event["event"] == "on_chat_model_stream":
        chunk = event["data"]["chunk"]
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content
```

**Interrupt Detection in astream_events**: Check state AFTER stream completes:

```python
async for event in graph.astream_events(...):
    # process events
    pass

# astream_events doesn't emit __interrupt__ directly
post_state = await graph.aget_state(config)
if post_state and post_state.next:
    # Agent is paused at interrupt
    yield interrupt_event(post_state.tasks[0].interrupts[0])
```

### StreamWriter for Custom Events (LangGraph v1.0)

Use `StreamWriter` to emit AG-UI events from within nodes:

```python
from langgraph.types import StreamWriter

async def execute_tools(state: AgentState, writer: StreamWriter):
    """Execute tools with real-time AG-UI event emission."""
    for tool_call in state["pending_tool_calls"]:
        # Emit TOOL_CALL_START immediately
        writer(tool_call_start(tool_call["name"], tool_call["id"]))

        # Execute tool
        result = await execute_tool(tool_call)

        # Emit TOOL_CALL_END
        writer(tool_call_end(tool_call["id"]))

    # Emit STATE_DELTA for collected_info changes
    if updates:
        writer(state_delta(compute_patch(old_info, new_info)))

    return {"extracted_updates": updates}
```

---

## 2. AG-UI Protocol Events

### AG-UI + A2UI Relationship (2026)

| Protocol | Purpose | Layer |
| -------- | ------- | ----- |
| **A2UI** (Google) | Describes UI intent (what to render) | Semantic |
| **AG-UI** (CopilotKit) | Transport protocol (how to stream) | Transport |

Use together: Agent uses A2UI to describe UI intent, AG-UI streams it to client.

### Event Categories

```
Lifecycle:     RUN_STARTED → RUN_FINISHED | RUN_ERROR
Text:          TEXT_MESSAGE_START → TEXT_MESSAGE_CONTENT* → TEXT_MESSAGE_END
Tool:          TOOL_CALL_START → TOOL_CALL_ARGS* → TOOL_CALL_END
State:         STATE_SNAPSHOT | STATE_DELTA (JSON Patch)
Custom:        CUSTOM (suggested_replies, interrupt, etc.)
```

### Event Factory Pattern

```python
from pydantic import BaseModel
from enum import Enum
from uuid import uuid4
from datetime import datetime

class AGUIEventType(str, Enum):
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    CUSTOM = "CUSTOM"

class AGUIEvent(BaseModel):
    type: AGUIEventType
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    # ... other fields per event type

def text_message_content(delta: str, message_id: str | None = None) -> dict:
    return AGUIEvent(
        type=AGUIEventType.TEXT_MESSAGE_CONTENT,
        message_id=message_id,
        delta=delta,
    ).model_dump(mode="json", exclude_none=True)
```

### JSON Patch for STATE_DELTA (RFC 6902)

```python
def compute_state_delta(old: dict | None, new: dict) -> list[dict]:
    """Generate minimal JSON Patch operations."""
    if old is None:
        return [{"op": "add", "path": f"/{k}", "value": v}
                for k, v in new.items() if v]

    patches = []
    for field, new_val in new.items():
        old_val = old.get(field)
        if old_val == new_val:
            continue

        old_empty = old_val is None or old_val == [] or old_val == ""
        new_empty = new_val is None or new_val == [] or new_val == ""

        if old_empty and not new_empty:
            patches.append({"op": "add", "path": f"/{field}", "value": new_val})
        elif not old_empty and new_empty:
            patches.append({"op": "remove", "path": f"/{field}"})
        elif not old_empty and not new_empty:
            patches.append({"op": "replace", "path": f"/{field}", "value": new_val})

    return patches
```

### Frontend State Reducer

```typescript
function applyJsonPatch(
  target: Record<string, unknown>,
  patches: JSONPatchOp[],
): Record<string, unknown> {
  const result = { ...target };
  for (const patch of patches) {
    const key = patch.path.slice(1); // Remove leading "/"
    switch (patch.op) {
      case "add":
      case "replace":
        result[key] = patch.value;
        break;
      case "remove":
        delete result[key];
        break;
    }
  }
  return result;
}

function reduceAgentState(state: AgentState, event: ChatEvent): AgentState {
  switch (event.type) {
    case "STATE_DELTA":
      return {
        ...state,
        collectedInfo: applyJsonPatch(state.collectedInfo, event.patch),
      };
    case "STATE_SNAPSHOT":
      return { ...state, collectedInfo: event.snapshot };
    default:
      return state;
  }
}
```

---

## 3. Mem0 Integration

### Memory Search Before LLM Call

```python
class Mem0Service:
    def __init__(self, api_key: str):
        self._client = MemoryClient(api_key=api_key)

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """Search relevant memories for context injection."""
        return await asyncio.to_thread(
            self._client.search,
            query,
            user_id=user_id,
            limit=limit,
        )

    def format_for_context(self, memories: list[dict]) -> str:
        if not memories:
            return ""
        lines = ["## Previous Context:"]
        for m in memories:
            lines.append(f"- {m.get('memory', '')}")
        return "\n".join(lines)
```

### Memory Storage Strategy

```python
# Store at meaningful checkpoints, not every turn
async def store_memory_node(state: AgentState):
    if not mem0_service:
        return {}

    # Only store when significant info collected
    info = state["collected_info"]
    if info.completeness_score() < 0.3:
        return {}  # Too early, nothing meaningful

    # Store with category for retrieval
    await mem0_service.add_memory(
        content=f"Project requirements: {info.model_dump_json()}",
        user_id=state["user_id"],
        metadata={
            "category": "project_requirement",
            "completeness": info.completeness_score(),
        }
    )
    return {}
```

### Memory Scopes

| Scope   | Persistence         | Use Case                 |
| ------- | ------------------- | ------------------------ |
| User    | Cross-session       | Preferences, history     |
| Session | Single conversation | Current context          |
| Agent   | Per agent instance  | Agent-specific knowledge |

### Graph Memory (2026 - Advanced)

Mem0 now supports relationship-based memory for complex contexts:

```python
# Store with relationships
await mem0.add_memory(
    content="User prefers morning runs",
    user_id=user_id,
    metadata={
        "category": "preference",
        "relates_to": ["training_schedule", "workout_timing"],
    }
)

# Query with graph traversal
memories = await mem0.search_memories(
    query="when should I schedule workouts",
    user_id=user_id,
    include_relations=True,  # Traverses related memories
)
```

### Mem0 MCP Integration (2026)

Integrate Mem0 via Model Context Protocol for automatic tool discovery:

```python
from mem0.mcp import Mem0MCPServer

# MCP server exposes memory tools automatically
mcp_server = Mem0MCPServer(api_key=MEM0_API_KEY)

# Tools available: search_memory, add_memory, get_all_memories
# LangChain Tool Router discovers these automatically
```

### Performance Benchmarks (2026)

| Metric        | Mem0 vs Full Context | Mem0 vs OpenAI Memory |
| ------------- | -------------------- | --------------------- |
| Accuracy      | Comparable           | **+26%**              |
| Response Time | **91% faster**       | Comparable            |
| Token Usage   | **90% less**         | Comparable            |

---

## 4. SSE Streaming Implementation

### FastAPI SSE Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.post("/chat/{conversation_id}")
async def chat_stream(conversation_id: str, request: ChatRequest):
    async def event_generator():
        async for event in service.stream_chat(conversation_id, request.message):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Critical for nginx
        }
    )
```

### Simplified Streaming with Structured Output

With structured output for suggested_replies, streaming becomes much simpler:

```python
async def stream_with_tokens(graph, input_data, config):
    """Simplified streaming - no tag filtering needed."""
    accumulated = []

    async for event in graph.astream_events(input_data, config, version="v2"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                accumulated.append(chunk.content)
                yield {"type": "token", "content": chunk.content}

        elif event["event"] == "on_chain_end":
            output = event.get("data", {}).get("output", {})

            # Emit AG-UI events from node output
            for agui_event in output.get("agui_events", []):
                yield agui_event

            # suggested_replies come from state, not parsed from text
            if suggested := output.get("suggested_replies"):
                yield suggested_replies_event(suggested)
```

---

## 5. MCP Tools Pattern

### Tool Registration with FastMCP

```python
from mcp.server.fastmcp import FastMCP, Context
from functools import lru_cache

mcp = FastMCP(name="my-agent")

@lru_cache
def get_service() -> MyService:
    """Singleton service - don't instantiate per call."""
    return MyService()

@mcp.tool()
async def my_tool(
    param: str,
    ctx: Context,
    user_id: str | None = None,
) -> dict:
    """Tool description for AI discovery.

    Args:
        param: Description of param
        ctx: MCP context (injected)
        user_id: User ID (for REST API transport)
    """
    effective_user_id = user_id or (ctx.client_id if ctx else None)
    if not effective_user_id:
        return {"error": "Authentication required", "success": False}

    service = get_service()
    try:
        result = await service.do_thing(param)
        ctx.info(f"Completed operation for {effective_user_id}")
        return {"success": True, "data": result}
    except ValidationError as e:
        return {"success": False, "error": str(e)}
```

### REST Wrapper with Typed Arguments

```python
from pydantic import BaseModel

# Avoid Any type - use explicit union
ToolArgumentValue = str | int | float | bool | list[str] | None

class ToolCallRequest(BaseModel):
    arguments: dict[str, ToolArgumentValue] = {}

@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolCallRequest):
    try:
        result = await mcp.call_tool(tool_name, request.arguments)
        return {"result": result}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (KeyError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid arguments: {e}") from e
```

---

## 6. React Conversation State

### useReducer for Complex Chat State

```typescript
interface ConversationState {
  readonly messages: Message[];
  readonly isStreaming: boolean;
  readonly agentState: AgentState;
  readonly suggestedReplies: SuggestedReply[];
  readonly error: string | null;
  // Side-effect flags (processed by useEffect)
  readonly shouldInvalidateQuery: boolean;
}

type ConversationAction =
  | { type: "START_STREAMING" }
  | { type: "PROCESS_SSE_EVENT"; payload: ChatEvent }
  | { type: "STREAMING_COMPLETE" }
  | { type: "CLEAR_SIDE_EFFECT_FLAGS" };

function conversationReducer(
  state: ConversationState,
  action: ConversationAction,
): ConversationState {
  switch (action.type) {
    case "PROCESS_SSE_EVENT": {
      const event = action.payload;
      let newState = state;

      // Update agent state via sub-reducer
      newState = {
        ...newState,
        agentState: reduceAgentState(state.agentState, event),
      };

      // Handle text streaming
      if (event.type === "TEXT_MESSAGE_CONTENT") {
        const lastMsg = newState.messages[newState.messages.length - 1];
        if (lastMsg?.role === "assistant") {
          newState = {
            ...newState,
            messages: [
              ...newState.messages.slice(0, -1),
              { ...lastMsg, content: lastMsg.content + event.delta },
            ],
          };
        }
      }

      // Handle structured suggested_replies (from CUSTOM event)
      if (
        event.type === "CUSTOM" &&
        event.custom_type === "suggested_replies"
      ) {
        newState = {
          ...newState,
          suggestedReplies: event.custom_data?.replies ?? [],
        };
      }

      return newState;
    }
    // ... other cases
  }
}
```

### Context Provider with Side Effects

```typescript
function ConversationProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(conversationReducer, INITIAL_STATE);
  const queryClient = useQueryClient();

  // Handle side effects via flags (not in reducer)
  useEffect(() => {
    if (state.shouldInvalidateQuery) {
      queryClient.invalidateQueries({ queryKey: ["conversation"] });
      dispatch({ type: "CLEAR_SIDE_EFFECT_FLAGS" });
    }
  }, [state.shouldInvalidateQuery, queryClient]);

  return (
    <ConversationContext.Provider value={{ state, dispatch }}>
      {children}
    </ConversationContext.Provider>
  );
}
```

### SSE Event Processing Hook

```typescript
function useSSEStream(conversationId: string) {
  const { dispatch } = useConversation();
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (message: string) => {
      abortRef.current = new AbortController();
      dispatch({ type: "START_STREAMING" });

      try {
        const response = await fetch(`/api/chat/${conversationId}`, {
          method: "POST",
          body: JSON.stringify({ message }),
          signal: abortRef.current.signal,
        });

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          for (const line of text.split("\n")) {
            if (line.startsWith("data: ")) {
              const event = JSON.parse(line.slice(6));
              dispatch({ type: "PROCESS_SSE_EVENT", payload: event });
            }
          }
        }
      } finally {
        dispatch({ type: "STREAMING_COMPLETE" });
      }
    },
    [conversationId, dispatch],
  );

  return { sendMessage };
}
```

---

## Common Mistakes

| Mistake                                | Fix                                             |
| -------------------------------------- | ----------------------------------------------- |
| State resets between turns             | Use `Annotated[T, reducer]`                     |
| No cross-session resume                | Add PostgreSQL checkpointer                     |
| Monolithic node doing everything       | Split into classify/extract/execute/respond     |
| Tag parsing for suggested_replies      | Use structured output with Pydantic             |
| Interrupt not detected in token stream | Check state after `astream_events` completes    |
| SSE buffered by nginx                  | Add `X-Accel-Buffering: no` header              |
| Stale closure captures old state       | Use `useReducer` + dispatch, not `useState`     |
| Memory stored every turn               | Only store at meaningful checkpoints            |
| Flat memory loses relationships        | Use Mem0 Graph Memory for complex contexts      |
| No parallel update handling            | Add reducers for concurrent state updates       |
| Service created per tool call          | Use `@lru_cache` singleton                      |
| `Any` type in tool arguments           | Define explicit `TypedDict` or union type       |
| Missing `from e` in exception          | Always chain: `raise HTTPException(...) from e` |
| Ignoring recursion limits              | Set bounded cycles to prevent runaway graphs    |

---

## Architecture Summary (2026 Best Practice)

```
┌─────────────────────────────────────────────────────────────────┐
│                        LangGraph Workflow                        │
│                                                                  │
│  START → retrieve_memory → classify_intent ─┬─→ extract_info    │
│                                             │      ↓            │
│                                             │   execute_tools   │
│                                             │      ↓            │
│                                             ├─→ generate_response│
│                                             │      ↓            │
│                                             │   store_memory    │
│                                             │      ↓            │
│                                             │     END           │
│                                             │                    │
│                                             ├─→ request_confirm │
│                                             │   (interrupt)      │
│                                             │                    │
│                                             └─→ generate_spec   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        AG-UI Events
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI SSE Endpoint                       │
│  - TOKEN events from astream_events                              │
│  - STATE_DELTA from execute_tools                                │
│  - CUSTOM (suggested_replies) from generate_response             │
│  - INTERRUPT event when paused                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      React Frontend                              │
│  - useReducer for conversation state                             │
│  - applyJsonPatch for STATE_DELTA                                │
│  - SuggestedReplies from CUSTOM event                            │
│  - Handle interrupt for confirmation UI                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sources (Updated 2026-01-22)

### LangGraph
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Best Practices](https://www.swarnendu.de/blog/langgraph-best-practices/)
- [LangGraph State Management 2025](https://sparkco.ai/blog/mastering-langgraph-state-management-in-2025)
- [Mastering State Reducers](https://medium.com/data-science-collective/mastering-state-reducers-in-langgraph-a-complete-guide-b049af272817)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

### AG-UI & A2UI
- [AG-UI Protocol Overview](https://docs.ag-ui.com/)
- [AG-UI GitHub](https://github.com/ag-ui-protocol/ag-ui)
- [A2UI Protocol Guide 2026](https://a2aprotocol.ai/blog/a2ui-guide)
- [AG-UI Microsoft Integration](https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/)

### Mem0 & Memory
- [Mem0 LangChain Integration](https://docs.mem0.ai/integrations/langchain)
- [Mem0 + LangGraph Integration](https://blog.futuresmart.ai/ai-agents-memory-mem0-langgraph-agent-integration)
- [AI Memory Systems Comparison 2026](https://www.index.dev/skill-vs-skill/ai-mem0-vs-zep-vs-langchain-memory)
- [Mem0 MCP Integration](https://composio.dev/toolkits/mem0/framework/langchain)

### Structured Output
- [LangChain Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Pydantic Output Parser](https://python.langchain.com/api_reference/core/output_parsers/langchain_core.output_parsers.pydantic.PydanticOutputParser.html)

### MCP
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
