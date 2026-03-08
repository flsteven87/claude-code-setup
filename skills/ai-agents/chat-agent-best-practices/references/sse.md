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

