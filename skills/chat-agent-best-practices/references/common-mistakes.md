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

