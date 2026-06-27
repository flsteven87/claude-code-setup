# Design-narration visual — rendered architecture diagram

The Mode C visual is what makes a design legible in one glance: the system's structure as boxes-and-arrows, each box colored by its **role** (canonical / transitional / module), with one callout banner naming the end-state invariant. Render it with `mcp__visualize__show_widget`. **Always call `mcp__visualize__read_me({modules:["diagram"]})` once before your first `show_widget`** (silently — don't narrate the setup call) — but everything you need to get it right on the first try is distilled below.

## When to render

- **Mode C (design narration)** — default deliverable, lead artifact. Render the architecture; the prose names the decisions.
- Skip only if the design is a single box (no structure to show) — then a sentence already says it.
- ASCII (Pattern A in SKILL.md) is the fallback when the visualization tool is unavailable.

## Role → color legend (the whole semantic system)

Color encodes **architectural role**, not dispatch state (that's dispatch-strategy's job). Keep this fixed so design diagrams read the same every run:

| Role | Ramp | Meaning |
|---|---|---|
| Canonical / SSOT / end-state | `c-green` | the source of truth; where the design is converging |
| Module / read-contract / active component | `c-blue` | a live, decoupled part — the translation module, the read API, a consumer |
| Transitional / being-retired / deprecated | `c-gray` + `stroke-dasharray="5 4"` | a temporary store/path the design is removing |
| Plain pipeline node (no special role) | neutral (no `c-*` class) | seed/curate, a generic stage |
| Invariant / end-state banner | filled `c-amber` | the one load-bearing rule the whole picture drives toward |

Keep to **≤3 colored ramps + neutral**, and always include a one-row legend so the colors are self-documenting. The banner at the bottom is a filled `c-amber` box — it states the end-state invariant (the `❗` decision), the call the whole design makes.

## SVG conventions that matter (honor these or it renders wrong)

- **`viewBox="0 0 680 H"` — the 680 is load-bearing**, don't change it (maps 1:1 to the container; any other width rescales text). Set `H` = bottom edge of the last element + ~20.
- Root: `<svg width="100%" viewBox="0 0 680 H" role="img">` with `<title>` and `<desc>` as the first two children (screen-reader requirement).
- **Two font sizes only**, via pre-built classes: `th` = 14px medium (box titles / layer labels), `ts` = 12px (subtitles, legend, arrow labels). Never set `fill` or font-size yourself.
- **Color a node by wrapping its `rect` + `text` in one `<g class="c-{ramp}">`.** The ramp sets rect fill+stroke and auto-adjusts child `th`/`ts` text in light + dark mode. Put the class on the innermost group holding the shapes — `c-*` uses a direct-child selector, so a shape nested one `<g>` too deep renders black.
- **Transitional/deprecated = add `stroke-dasharray="5 4"` to the rect** (inside its `c-gray` g).
- Arrows: `<line class="arr" .../>` (1.5px with a chevron head). Draw them in the gaps between nodes, **never across a node** — if an arrow would cross a box, reorder the boxes.
- **Sentence case everywhere.** Keep subtitles to a few words — detail goes in the prose, not the box. CJK glyphs ≈ 13–14px wide; check `(text width + padding) < box width` before placing.
- One `<svg>` per `show_widget` call. No `<style>` blocks for color; no gradients/shadows; transparent background (the host provides the card).

## Layout recipe — layered data flow (top → bottom)

A design diagram is usually a **data flow**, not swim lanes. Stack tiers top-to-bottom in the direction data moves:

- **Legend row** at the top (`y≈12–22`): one small `c-{ramp}` swatch + `ts` label per role used.
- **Tiers** (write → canonical → read → consume, or input → process → store → serve), each a `th` tier label (x=40) + its row of nodes below, ~80px pitch.
- **The canonical/SSOT box** is usually full-width (`x=40 w=600`) and `c-green` — it's the spine the rest hangs off.
- **Arrows between tiers** go in the vertical gaps (downward); arrows within a tier in the horizontal gaps.
- A **transitional store** (e.g. a sidecar being retired) sits beside the read tier as a `c-gray` dashed box with a short arrow merging into the read node — visually "still feeding in, but dashed = leaving".
- **Invariant banner** at the bottom: full-width (`x=40 w=600`) filled `c-amber`, `rx="8"`, ~50px tall, a `th` `❗ <the end-state rule>` line + one `ts` elaboration.
- Keep tiers from overlapping: a node row ending at `y=Y+H` must clear the next tier's label at `Y+pitch` (≈26px gap).

## Parametric skeleton

Adapt — swap labels/roles/counts for the design. Four tiers shown; add/remove by shifting subsequent `y` by ~pitch and recomputing `H`.

```
<svg width="100%" viewBox="0 0 680 408" role="img" xmlns="http://www.w3.org/2000/svg">
<title>…一句話設計標題…</title><desc>…一句話描述資料流 + 終局 invariant…</desc>

<!-- legend: green canonical / blue module·contract / gray-dashed transitional -->
<g class="c-green"><rect x="40" y="12" width="12" height="12" rx="3"/></g><text class="ts" x="56" y="22">canonical（SSOT）</text>
<g class="c-blue"><rect x="220" y="12" width="12" height="12" rx="3"/></g><text class="ts" x="236" y="22">module / read contract</text>
<g class="c-gray"><rect x="430" y="12" width="12" height="12" rx="3" stroke-dasharray="5 4"/></g><text class="ts" x="446" y="22">transitional（退役中）</text>

<!-- tier 1: write / assembly (neutral + module) -->
<text class="th" x="40" y="46">① 寫側</text>
<g><rect x="40" y="54" width="170" height="46" rx="4" fill="none" stroke="var(--border-strong, #888)"/>
  <text class="th" x="125" y="73" text-anchor="middle">seed / curate</text></g>
<g class="c-blue"><rect x="240" y="54" width="230" height="46" rx="4">…translation module…</rect></g>
<line class="arr" x1="125" y1="100" x2="125" y2="122"/>

<!-- tier 2: canonical SSOT (full-width green) -->
<g class="c-green"><rect x="40" y="124" width="600" height="50" rx="4"/>
  <text class="th" x="340" y="146" text-anchor="middle">PG …— CANONICAL（SSOT）</text>
  <text class="ts" x="340" y="163" text-anchor="middle">…what lives here…</text></g>

<!-- tier 3: read contract + transitional sidecar -->
<text class="th" x="40" y="198">③ 讀側</text>
<g class="c-blue"><rect x="40" y="206" width="300" height="48" rx="4">…read API…</rect></g>
<g class="c-gray"><rect x="370" y="206" width="270" height="48" rx="4" stroke-dasharray="5 4">…sidecar ⏳…</rect></g>
<line class="arr" x1="190" y1="174" x2="190" y2="204"/>
<line class="arr" x1="368" y1="230" x2="342" y2="230"/>  <!-- sidecar merges in, dashed = leaving -->

<!-- tier 4: consumers -->
<g class="c-blue"><rect x="110" y="286" width="180" height="44" rx="4">…consumer A…</rect></g>
<g class="c-blue"><rect x="390" y="286" width="180" height="44" rx="4">…consumer B…</rect></g>
<line class="arr" x1="190" y1="254" x2="190" y2="284"/>

<!-- invariant banner -->
<g class="c-amber"><rect x="40" y="346" width="600" height="50" rx="8"/>
  <text class="th" x="56" y="368">❗ 終局 = …the one load-bearing rule…</text>
  <text class="ts" x="56" y="386">…one line elaboration / the trade-off accepted…</text></g>
</svg>
```

The lesson the skeleton encodes: data flows top-down through colored-by-role tiers, the full-width green box is the SSOT spine, a dashed gray sidecar visibly "leaves" the read path, and the bottom amber banner is the single invariant the whole design converges toward.
