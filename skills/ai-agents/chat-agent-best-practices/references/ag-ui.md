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

