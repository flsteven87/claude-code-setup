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

