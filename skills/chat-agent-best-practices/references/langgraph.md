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

