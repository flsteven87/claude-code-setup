# Frontend Principles Reference

> Extracted from global CLAUDE.md for detailed reference. Core rules remain in CLAUDE.md.

## Hyper-Minimalist UI Principle 🔴

> **Less, but better.** Every element must earn its place.

| Aspect           | ❌ Avoid                             | ✅ Prefer                            |
| ---------------- | ------------------------------------ | ------------------------------------ |
| Color            | Multiple accent colors, gradients    | Single accent + neutrals             |
| Decoration       | Borders, shadows, rounded everything | Whitespace, typography hierarchy     |
| Visual hierarchy | Color/icon differentiation           | Font size/weight changes             |
| Feedback         | Flashy animations, bounces           | Subtle opacity/transform transitions |
| Loading          | Skeleton loaders everywhere          | Simple spinner, or optimistic UI     |
| Density          | Sparse "airy" layouts for aesthetics | Appropriate information density      |

**Before adding any visual element, ask:**

1. Does this help the user complete their task?
2. Can I achieve this with whitespace or typography instead?
3. Am I adding decoration or function?

**Anti-Patterns:**

- ❌ Decorative icons next to every label
- ❌ Color coding when text labels suffice
- ❌ Multiple visual treatments (border + shadow + background)
- ❌ Animated transitions longer than 150ms

## Use Project Systems First 🔴

> **Discover before creating.** The codebase already has what you need.

**Priority Order:**

1. **Existing project code** - Search `components/`, `hooks/`, `lib/`
2. **UI component library** - shadcn/ui, Radix primitives
3. **Create new** - Only when above don't exist

**Before Writing New Code, Search For:**

| Need             | Check First                                           |
| ---------------- | ----------------------------------------------------- |
| Layout/Container | `components/layout/`, existing page structures        |
| Status display   | Existing badge variants, status components            |
| Icons            | Project icon system or existing lucide usage patterns |
| Data fetching    | `hooks/queries/` for existing query hooks             |
| Forms            | Existing form components with zod validation          |
| Modals           | `dialog.tsx`, `sheet.tsx`, `drawer.tsx`               |
| Loading          | Existing spinner/skeleton patterns                    |
| Colors           | CSS variables in `globals.css`, `tailwind.config`     |

**Common AI Mistakes:**

| ❌ Wrong                                  | ✅ Correct                                 |
| ----------------------------------------- | ------------------------------------------ |
| `className="text-red-500 font-medium"`    | Use existing Badge/Status component        |
| Inline SVG or new icon imports            | Use project's icon system consistently     |
| `<div className="max-w-7xl mx-auto">`     | Use existing layout components             |
| New `useState` + `useEffect` for API data | Find/create query hook in `hooks/queries/` |
| Custom validation logic                   | Use existing zod schemas and form patterns |
| `bg-gray-100 rounded-lg p-4 border`       | Use existing Card component variant        |

## State Management Hierarchy 🔴

**Choose the right level (prefer top, avoid bottom):**

| Priority | Type         | When to Use                                | Tool                      |
| -------- | ------------ | ------------------------------------------ | ------------------------- |
| 1st      | URL State    | Filters, pagination, tabs, shareable state | `useSearchParams`, `nuqs` |
| 2nd      | Server State | API data, remote state                     | TanStack Query            |
| 3rd      | Local State  | UI-only, single component                  | `useState`                |
| 4th      | Global State | Cross-component UI, WebSocket              | Zustand (sparingly)       |

**Anti-Patterns:**

- ❌ `useState` for filter values (should be URL params)
- ❌ Zustand for data TanStack Query should manage
- ❌ Prop drilling when URL state would work
- ❌ Global state for single-component concerns
