---
name: chat-agent-best-practices
description: Use when building or reviewing production AI chat agents with LangGraph, AG-UI events, Mem0 memory, MCP tools, SSE streaming, and React conversation state.
status: active
tags: [chat-agent, langgraph, ag-ui, mem0, mcp, sse, react]
updated: 2026-02-07
---

# Chat Agent Best Practices

Production workflow for chat agents that combine:
- LangGraph agent orchestration
- AG-UI event streaming
- Mem0 long-term memory
- MCP tools/resources
- SSE transport
- React conversation state

## When To Use

Use this skill when the task involves one or more of:
- LangGraph state/reducer/checkpointer design
- AG-UI protocol events and JSON patch synchronization
- Mem0 memory retrieval and write strategy
- MCP tool wrapping, argument typing, and error handling
- SSE endpoint/event-stream implementation
- React chat state, reducer, and streaming event handling

## Workflow

1. Scope the stack pieces in this task.
2. Load only the required reference files (do not load all).
3. Implement with existing project conventions first.
4. Validate streaming, state consistency, and error paths.
5. Report tradeoffs and unresolved risks.

## Reference Map (Progressive Disclosure)

Load only the file you need:
- `references/langgraph.md`: reducers, routing, HITL, checkpointers, stream modes
- `references/ag-ui.md`: event model, event factory, JSON Patch patterns
- `references/mem0.md`: retrieval/write strategy, scopes, graph memory
- `references/sse.md`: FastAPI SSE endpoint and streaming patterns
- `references/mcp-tools.md`: FastMCP tool registration and REST wrappers
- `references/react-state.md`: reducer/context/hook patterns for chat UI
- `references/common-mistakes.md`: anti-pattern checklist
- `references/architecture-summary.md`: recommended target architecture
- `references/sources.md`: primary sources list

Full historical guide remains at:
- `references/full-guide.md`

## Output Expectations

For implementation or review tasks, include:
- Chosen architecture (short rationale)
- Key invariants (state consistency, ordering, idempotency)
- Failure handling strategy (timeouts, retries, partial events)
- Validation performed (tests/checks) and any gaps
