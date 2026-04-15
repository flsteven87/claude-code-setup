# Frontend Development Rules

> Project-specific patterns that differ from standard React conventions.

## TanStack Query Patterns 🟡

- **Invalidation**: granular (`userKeys.detail(id)`) over nuclear (`userKeys.all`)
- **Mutations**: always include `onSettled` for cache consistency
- **Race Conditions**: `enabled: !!param`, set `staleTime`, never fire with undefined params

## SSE (Server-Sent Events) 🟡

- Backend: `EventSourceResponse` with `X-Accel-Buffering: no` header
- Frontend: `EventSource` + cleanup in `useEffect` return
- Close on terminal events (`completed`, `failed`, `cancelled`)

## React Compiler 🔴

- ❌ No manual `useMemo`/`useCallback`/`memo()` — Compiler handles automatically
- Escape hatch: `"use no memo"` directive — use sparingly, investigate root cause
- ⚠️ TanStack Table/Query interior mutability may cause stale UI — add `"use no memo"` if needed
