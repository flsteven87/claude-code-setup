---
name: simplify
description: Use when the user says /simplify or wants to reduce code, architecture, or workflow complexity while preserving intended behavior.
---

# Simplify

Reduce complexity with the smallest safe change.

## Workflow

1. Identify the target code path, abstraction, or workflow.
2. Determine what complexity is accidental versus load-bearing.
3. Prefer deleting indirection, duplication, and dead branches over adding new abstraction.
4. Reuse existing project patterns instead of inventing a new one.
5. Verify that intended behavior still holds after simplification.

## Output

Explain briefly:
- What was unnecessarily complex
- What was simplified
- What behavior was preserved
- What still remains intentionally complex

## Rules

- If simplification would change public behavior, stop and surface the tradeoff.
- Prefer one clear path over multiple defensive branches.
- Keep scope tight; this is not a broad refactor license.
