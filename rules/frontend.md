---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.jsx"
---

# Frontend Rules

Project patterns that differ from stock React conventions. The repository's own instructions add
specifics.

## Code

- Type critical paths explicitly (query hooks, error handling, API responses). Components are
  function declarations with a typed props interface, written in JSX with ES module imports.
- Import icons and components by deep path rather than from a library barrel.
- Run independent awaits together with `Promise.all`.
- TanStack Query: key factories (project `hooks/factories/` when present), granular invalidation
  such as `userKeys.detail(id)`, `onSettled` on every mutation, and `enabled: !!param` plus a
  `staleTime` so a query never fires with undefined params.
- React Compiler is on with `eslint-plugin-react-compiler` and owns memoization. Reach for
  `"use no memo"` only after finding the root cause, typically TanStack Table or Query interior
  mutability.
- SSE: backend `EventSourceResponse` with `X-Accel-Buffering: no`; frontend `EventSource` cleaned
  up in the effect return and closed on terminal events.
- State lives at the highest fitting level: URL, then server state (TanStack Query), then local,
  then global (Zustand).

## UI

- Less, but better: every element earns its place. Discover the project's `components/`, `hooks/`,
  and `lib/` before creating; a new page is visually indistinguishable from existing ones (same
  theme provider, tokens, spacing).
- UX copy is for non-technical users: the fewest words that work, with no pipeline or system
  vocabulary, parser state, coverage figures, or capability disclaimers.
- Show the value inline (dates, numbers, names) rather than a boolean indicator the user must click
  through.
- Calm, not flashy: normal states get no alarmist styling; a first record is "new", not a caution.
- Shipped UI matches the approved design; confirm with a screenshot at the real viewport before
  reporting done.
