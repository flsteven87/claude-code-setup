# Frontend Development Rules

> Extracted from CLAUDE.md. These rules apply to all frontend (React/TypeScript) development.

## TanStack Query Patterns 🟡

- **Query Key Factory required**: use `hooks/factories/` — never hardcode query keys
- **Invalidation**: granular (`userKeys.detail(id)`) over nuclear (`userKeys.all`)
- **Mutations**: always include `onSettled` for cache consistency
- **Race Conditions**: `enabled: !!param`, set `staleTime`, never fire with undefined params

## Component Standards 🟡

| Rule                           | Rationale                                         |
| ------------------------------ | ------------------------------------------------- |
| Max 1000 lines per component   | Split into sub-components                         |
| Explicit prop interfaces       | No `React.ComponentProps<'div'>`                  |
| Composition over configuration | Prefer children/slots over many boolean props     |
| Collocate related code         | Keep hook + component + types together when small |

## SSE (Server-Sent Events) 🟡

- Backend: `EventSourceResponse` with `X-Accel-Buffering: no` header
- Frontend: `EventSource` + cleanup in `useEffect` return
- Close on terminal events (`completed`, `failed`, `cancelled`)

## React Compiler 🔴

- ✅ Required: `babel-plugin-react-compiler` + `eslint-plugin-react-compiler` in all projects
- ❌ No manual `useMemo`/`useCallback`/`memo()` — Compiler handles automatically
- Escape hatch: `"use no memo"` directive — use sparingly, investigate root cause
- ⚠️ TanStack Table/Query interior mutability may cause stale UI — add `"use no memo"` if needed

## useEffect & Race Condition Prevention 🔴

**Every useEffect with async/timers/listeners MUST return cleanup:**

| Resource | Cleanup Pattern |
| -------- | --------------- |
| fetch/async | `AbortController` → `return () => controller.abort()` |
| `setTimeout`/`setInterval` | Store IDs → `return () => ids.forEach(clearTimeout)` |
| `addEventListener` | Same ref → `return () => removeEventListener(type, handler)` |
| `EventSource` (SSE) | `return () => { es.close(); ref.current = null }` |

- ✅ Unstable callbacks in deps: use ref pattern (`cbRef.current = callback`) to avoid re-runs
- ❌ Never mutate state arrays/objects — Compiler assumes immutability (`toSorted()`, spread)
- ❌ Never read/write refs during render — move to `useEffect` or event handler
- ❌ Never use dual completion sources (SSE + polling) without `ref.current.handled` guard
- ❌ Never fire fetch/mutation without checking if component is still mounted or request is current
