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

