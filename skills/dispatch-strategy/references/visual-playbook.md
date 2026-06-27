# Visual dispatch playbook — swim-lane convergence diagram

The visual is what makes a board-mode run legible at a glance: one lane per live series, every node colored by its dispatch state, the future parallel windows marked, and a single convergence banner naming the one next action. Render it with the `mcp__visualize__show_widget` tool. **Always call `mcp__visualize__read_me({modules:["diagram"]})` once before your first `show_widget`** — it's required — but everything you need to get the diagram right on the first try is distilled below, so you don't have to re-derive it from the full guidance.

## When to render

- **Board mode** — default deliverable. One lane per discovered series (cap ~4), plus the convergence banner.
- **Targeted mode** — optional but useful: a single-lane DAG of the one series. Offer it; render if the user wants the picture.
- Skip only if the series is a trivial 1-2 ticket chain where prose already says everything.

## State → color legend (this is the whole semantic system)

Color encodes **dispatch state**, nothing else. Keep this mapping fixed so the chart reads the same every run:

| State | Ramp | Meaning |
|---|---|---|
| Done / merged into main | `c-green` | settled; unblocks its dependents |
| In-flight | `c-blue` | dispatched / In Progress / In Review — action is *await + review the PR* |
| Frontier (dispatch now) | `c-amber` | unblocked + not yet dispatched — the actionable nodes |
| Blocked / deferred | `c-gray` | waiting; **deferred adds `stroke-dasharray="5 4"`** to distinguish from merely-blocked |
| Heavy-lane flag | `c-red` dot | a small marker on a node that carries production-data / cross-stack risk |

Always include a one-row legend at the top so the colors are self-documenting. The convergence banner at the bottom is a **filled `c-amber`** box (it's the call to action).

## SVG conventions that matter (distilled — honor these or it renders wrong)

- **`viewBox="0 0 680 H"` — the 680 is load-bearing**, don't change it (it maps 1:1 to the container; any other width rescales all your text). Set `H` = bottom edge of the last element + ~20.
- Root must be `<svg width="100%" viewBox="0 0 680 H" role="img">` with `<title>` and `<desc>` as the first two children (screen-reader requirement).
- **Two font sizes only**, via pre-built classes: `th` = 14px medium (node titles / region labels), `t` = 14px (labels), `ts` = 12px (subtitles, legend, arrow labels). Never set `fill` or font-size yourself.
- **Color a node by wrapping its `rect` + `text` in one `<g class="c-{ramp}">`.** The ramp sets the rect fill+stroke and auto-adjusts the child `th`/`ts` text to the correct dark stops in both light and dark mode. Put the class on the innermost group holding the shapes — `c-*` uses a direct-child selector, so a shape nested one `<g>` too deep renders black.
- **Deferred = add `stroke-dasharray="5 4"` to the rect** (inside its `c-gray` g — it keeps the gray stroke and dashes it).
- **Heavy-lane red dot must be a SIBLING of the node group, never a child.** A `<circle class="c-red">` placed *inside* a `c-gray` g renders **gray**, not red — `.c-gray > circle` (specificity 0-1-1) beats `.c-red` (0-1-0). Put the dot as a separate element positioned over the node's corner. (Real gotcha; cost a debug last time.)
- Arrows: `<line class="arr" .../>` (1.5px with a chevron head). Draw them in the gaps between nodes, never across a node.
- **Sentence case everywhere** (incl. SVG labels). Keep subtitles to a few chars — detail goes in the prose around the widget, not in the box. CJK glyphs ≈ 13-14px wide each; check `(text width + padding) < box width` before placing.
- One `<svg>` per `show_widget` call. No `<style>` blocks for color; no gradients/shadows; transparent background (the host provides the card).

## Layout recipe

- **Legend row** at the top (`y≈12-22`): one small `c-{ramp}` swatch + `ts` label per state, spaced left-to-right within x=40..640.
- **One lane per series**, stacked vertically with ~80px pitch. Each lane = a `th` region label (x=40) + its DAG row of nodes just below.
- **Nodes** ≈ `w` 120-180, `h` 48, `rx="4"`, two text lines (`th` title centered, `ts` subtitle centered). Keep **≤4 nodes per lane**; when a series fans out wider, collapse the tail into one **fan-out pill** (a wider node labeled e.g. `fan-out（待 P3）` / `A→B ‖ C`) rather than drawing the whole sub-tree.
- **Arrows** between sequential nodes in a lane (in the inter-node gap).
- **Convergence banner** at the bottom: a full-width (`x=40 w=600`) filled `c-amber` rect, `rx="8"`, ~60px tall, with a `th` "▶ 單一收斂點" line and 1-2 `ts` lines stating the one cross-series next action.
- Keep lanes from overlapping: a node row ending at `y=Y+48` must clear the next lane's label at `Y+78` (≈30px gap).

## Parametric skeleton

Adapt this structure — swap labels/colors/counts for the discovered series. Lane Y origins shown for 3 series; add/remove lanes by shifting subsequent Y by ~80 and recomputing `H`.

```
<svg width="100%" viewBox="0 0 680 405" role="img" xmlns="http://www.w3.org/2000/svg">
<title>…一句話標題…</title><desc>…一句話描述 series 與收斂點…</desc>

<!-- legend: green 已併 / blue 進行中 / amber 可派 / gray 阻塞·延後 / red heavy -->
<g class="c-green"><rect x="40" y="12" width="12" height="12" rx="3"/></g><text class="ts" x="56" y="22">已併入 main</text>
<g class="c-blue"><rect x="150" y="12" width="12" height="12" rx="3"/></g><text class="ts" x="166" y="22">進行中</text>
<g class="c-amber"><rect x="232" y="12" width="12" height="12" rx="3"/></g><text class="ts" x="248" y="22">可派</text>
<g class="c-gray"><rect x="300" y="12" width="12" height="12" rx="3"/></g><text class="ts" x="316" y="22">阻塞 / 延後</text>
<g class="c-red"><circle cx="420" cy="18" r="6"/></g><text class="ts" x="432" y="22">heavy lane</text>

<!-- lane 1 (y≈70) -->
<text class="th" x="40" y="58">① …series name…</text>
<g class="c-blue"><rect x="40" y="70" width="150" height="48" rx="4"/>
  <text class="th" x="115" y="90" text-anchor="middle">NEX-####</text>
  <text class="ts" x="115" y="106" text-anchor="middle">…state tag…</text></g>
<line class="arr" x1="190" y1="94" x2="253" y2="94"/>
<g class="c-amber"><rect x="255" y="70" width="150" height="48" rx="4"/>… frontier node …</g>
<line class="arr" x1="405" y1="94" x2="468" y2="94"/>
<g class="c-gray"><rect x="470" y="70" width="150" height="48" rx="4" stroke-dasharray="5 4"/>… deferred node …</g>

<!-- lane 2 (y≈160): chain + fan-out pill; heavy-lane red dot is a SIBLING -->
<text class="th" x="40" y="148">② …series name…</text>
<g class="c-blue"><rect x="40" y="160" width="120" height="48" rx="4"/>…</g>
<line class="arr" x1="160" y1="184" x2="178" y2="184"/>
<g class="c-gray"><rect x="180" y="160" width="120" height="48" rx="4"/>…</g>
<line class="arr" x1="300" y1="184" x2="318" y2="184"/>
<g class="c-gray"><rect x="320" y="160" width="120" height="48" rx="4"/>… P3 apply …</g>
<g class="c-red"><circle cx="434" cy="166" r="5"/></g>   <!-- heavy dot: sibling, NOT inside the c-gray g -->
<line class="arr" x1="440" y1="184" x2="458" y2="184"/>
<g class="c-gray"><rect x="460" y="160" width="180" height="48" rx="4" stroke-dasharray="5 4"/>… fan-out（待 P3）/ A→B ‖ C …</g>

<!-- lane 3 (y≈250): independent frontier nodes + deferred bucket -->
<text class="th" x="40" y="238">③ …series name…</text>
<g class="c-amber"><rect x="40" y="250" width="180" height="48" rx="4"/>…</g>
<g class="c-amber"><rect x="240" y="250" width="170" height="48" rx="4"/>…</g>
<g class="c-gray"><rect x="430" y="250" width="210" height="48" rx="4" stroke-dasharray="5 4"/>… 延後 backlog bucket …</g>

<!-- convergence banner (y≈320) -->
<g class="c-amber"><rect x="40" y="320" width="600" height="62" rx="8"/>
  <text class="th" x="56" y="342">▶ 單一收斂點</text>
  <text class="ts" x="56" y="361">…the one cross-series next action…</text>
  <text class="ts" x="56" y="377">…second line / parallel option…</text></g>
</svg>
```

The lesson the skeleton encodes: lanes are independent rows, the fan-out pill keeps wide series from blowing the 680 budget, the red heavy-lane dot is a sibling, and the bottom amber banner is the single thing the whole chart drives toward.
