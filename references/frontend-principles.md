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

## Layout Stability 🔴

> **Content position must never shift based on panel state.** Panels appear/disappear beside content, not around it.

| Principle | Rule |
| --------- | ---- |
| **Left-aligned always** | Form/settings content stays left-aligned with `max-w-*`. Never `mx-auto` as a reaction to panel collapse. |
| **Whitespace is intentional** | Empty right space when a panel is hidden = breathing room, not a bug. Form readability degrades beyond ~700px. |
| **Panel toggle = additive** | Toggling a side panel only affects the panel's column. Content column width/position stays identical. |
| **Width tiers** | `max-w-3xl` for forms/settings, `wide` (no cap) for dashboards/tables. Defined in layout component, not per-page. |

**Anti-Patterns:**

- ❌ `mx-auto` that toggles based on sidebar/panel open state (causes content jump)
- ❌ Content stretching wider when a panel closes (layout instability)
- ❌ Per-page `max-w-*` + centering overrides — use layout component props (`wide`)

## Bot Builder UI Patterns 🔴

> **Canonical patterns for all bot editor pages.** These ensure visual consistency
> across Profile, Knowledge, Behavior, Safety, Channels, Analytics, and Memory.
> Full spec: `docs/plans/2026-03-16-ui-ux-refinement-guide.md`

### Section Card Pattern

Every settings group on a bot editor page must be wrapped in a section card:

```tsx
<section className="rounded-xl border border-border bg-card p-6 space-y-6">
  <div>
    <h3 className="text-base font-semibold">{title}</h3>
    <p className="text-sm text-muted-foreground mt-0.5">{description}</p>
  </div>
  {/* content */}
</section>
```

**Rules:**
- Sections separated by `space-y-6` on the parent (NOT `<Separator>`)
- Each card has ONE clear responsibility
- `bg-card` provides contrast against `bg-background` in both themes

### Selection Card Pattern (visual radio)

For multi-choice settings (tone, response length, out-of-scope behavior):

| State | Classes |
|-------|---------|
| Default | `border-border hover:border-primary/30 hover:bg-muted/50 cursor-pointer` |
| Selected | `border-primary bg-primary/5 ring-1 ring-primary/20 shadow-sm` |

**Rules:**
- Always include `cursor-pointer` on clickable cards
- Icon container: selected = `bg-primary text-primary-foreground`, default = `bg-muted text-muted-foreground`
- Show example/preview text — users should see the impact of their choice
- Large cards (2 cols): `rounded-xl px-4 py-4`, icon `h-8 w-8 rounded-lg`
- Compact cards (3 cols): `rounded-lg px-3 py-3`, icon `h-6 w-6 rounded-md`

### Toggle Switch Row Pattern

For boolean settings:

```tsx
<div className="flex items-start gap-3">
  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted">
    <Icon className="h-4 w-4 text-muted-foreground" />
  </div>
  <div className="flex-1 min-w-0">
    <div className="flex items-center justify-between">
      <Label htmlFor="id" className="cursor-pointer">Label</Label>
      <Switch id="id" checked={value} onCheckedChange={onChange} />
    </div>
    <p className="text-xs text-muted-foreground mt-0.5">Description</p>
  </div>
</div>
```

### Save Bar Pattern

All bot editor pages with editable forms must use a sticky save bar:

```tsx
<div className={cn(
  "sticky bottom-0 z-10 transition-all duration-300",
  isDirty ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
)}>
  <div className="flex items-center justify-between rounded-xl border border-border bg-card px-5 py-3 shadow-lg">
    <div className="flex items-center gap-2">
      <span className="h-2 w-2 rounded-full bg-amber-500" />
      <span className="text-sm text-muted-foreground">Unsaved changes</span>
    </div>
    <div className="flex items-center gap-2">
      <Button variant="ghost" size="sm" onClick={handleDiscard}>Discard</Button>
      <Button size="sm" onClick={handleSave}>Save Changes</Button>
    </div>
  </div>
</div>
```

**Rules:**
- Track dirty state by comparing current form values to initial snapshot
- Save button shows `Loader2` spinner during save, `Check` icon on success
- Show `toast.success()` via Sonner after save completes
- Discard resets form to initial state

### Contrast Rules (NEVER violate)

| Anti-pattern | Fix |
|-------------|-----|
| `text-muted-foreground/60` | `text-muted-foreground` (no opacity modifier) |
| `text-muted-foreground/50` | `text-muted-foreground` |
| `text-[10px]` | `text-[11px]` minimum, prefer `text-xs` (12px) |
| Italic at small sizes | Remove italic (readability issue) |

### Live Preview Pattern

For content users can preview (welcome message, chat bubble):

- Box: `rounded-xl border border-dashed border-border/60 bg-muted/30 p-4`
- Label: `text-[11px] font-medium uppercase tracking-wider text-muted-foreground mb-3`
- Bot icon: `h-7 w-7 rounded-full bg-primary/10 text-primary`
- Bubble: `rounded-2xl rounded-tl-md bg-card border border-border px-3.5 py-2.5 shadow-sm`

---

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
