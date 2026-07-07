---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.jsx"
---

# Frontend Development Rules

> Project-specific patterns that differ from standard React conventions.

## Core Principles 🔴

- **Hyper-Minimalist UI** — Less, but better. Every element must earn its place.
- **Use Project Systems First** — Discover before creating. Search `components/`, `hooks/`, `lib/` first. New pages must be visually indistinguishable from existing ones — same theme/layout provider, design tokens, spacing. Never introduce a parallel visual style.
- **State Hierarchy** — URL State > Server State (TanStack Query) > Local State > Global State (Zustand)

## UI Design Language 🔴

Mined from repeated user corrections (2026-06/07 session audit). Repo `AGENTS.md` adds project specifics.

- **UX copy is for non-technical users** — zero technical or pipeline vocabulary in user-facing strings (no "identity match tier"-style wording); the fewest words that work.
- **Show the value, not its existence** — render the actual data (dates, numbers, names) inline; never "有/沒有" boolean indicators the user must click through to inspect.
- **Calm, not flashy** — no 浮誇 styling or decoration; no alarmist warnings for normal states (a first-time record is "new", not a caution).
- **Mock fidelity** — shipped UI must match the approved design; verify with a screenshot before reporting done, not by code review alone.

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
