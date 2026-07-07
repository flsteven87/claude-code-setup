# narrate visual reference — rendering the one diagram

The diagram carries *structure and state*; the prose carries *why*. Render with `mcp__visualize__show_widget`; **always call `mcp__visualize__read_me({modules:["diagram"]})` once before the first `show_widget`** (silently). Skip rendering only when the topic is a single box — then a sentence already says it. ASCII (same grammar, ≤30 lines) is the fallback when the widget tool is unavailable.

## Two color grammars — pick by the question being answered

**Grammar A — 狀態（"where does it stand?"）** — sitemap, pipeline-status, feature briefs:

| State | Style |
|---|---|
| 已上線 / done | `c-gray` solid |
| 進行中 / 收尾中 | `c-amber` solid |
| 未開始 / planned | neutral `class="box"` + `stroke-dasharray="4 3"` |
| Surface containers（sitemap only） | `c-blue` = web／教練端, `c-teal` = app／學員端 |

**Grammar B — 角色（"what's the design?"）** — architecture / design-decision briefs:

| Role | Style |
|---|---|
| Canonical / SSOT / end-state | `c-green` |
| Live module / read contract / consumer | `c-blue` |
| Transitional / being retired | `c-gray` + `stroke-dasharray="5 4"` |
| 終局 invariant banner（bottom, full-width） | filled `c-amber`, `❗` line |

Both: ≤3 colored ramps + neutral, and always a one-row legend (small swatch rects + `ts` labels) so colors are self-documenting. Never mix the two grammars in one diagram.

## SVG conventions (honor these or it renders wrong)

- **`viewBox="0 0 680 H"` — the 680 is load-bearing**, never change it. `H` = bottom of last element + ~30.
- Root: `<svg width="100%" viewBox="0 0 680 H" role="img">` with `<title>` + `<desc>` as first children.
- Two font sizes only via pre-built classes: `th` = 14px titles, `ts` = 12px subtitles/legend. Never set fill or font-size yourself.
- Color a node by wrapping rect + text in one `<g class="c-{ramp}">` — the class uses direct-child selectors, so a shape nested one `<g>` deeper renders black.
- Every box text: `text-anchor="middle" dominant-baseline="central"`, y = center of its slot. Two-line boxes ≥56px tall, ~24px between lines.
- CJK glyphs ≈ 14–15px wide at 14px font (12px → ~13px/char): check `(chars × width + 24) ≤ box width` before placing. 白話 title ≤6 字 fits a 104px box.
- Arrows: `<line class="arr" marker-end="url(#arrow)"/>` with the standard `<defs>` marker; draw in gaps, never across a box.
- Clickable: `<g class="node c-{ramp}" onclick="sendPrompt('drill-down question')">`.
- Safe area x=40..640; 5+ boxes in a row → shrink to ≤110px each or wrap. Sentence case. No `<style>` blocks, no gradients/shadows; transparent background.

## Layout recipe A — Sitemap（UI/UX topics）

Left→right = user journey; containment = surface.

- External actor (教練/商家) as `ts` text + short arrow into the first container.
- One container per surface (`c-blue` web, `c-teal` app): rounded rect rx=16, `th` title「nr-platform web · 教練端」+ `ts` subtitle carrying the entry gate（「navbar 入口 · PostHog toggle 控制」）.
- Pages as boxes inside (Grammar A status colors), 2-line: 白話頁名 + 狀態. Routes/component names never appear here — they go to the 節點表.
- Arrow between containers = the publish/handoff moment.
- Legend row at the bottom.

Skeleton (the user-approved shape — adapt labels/counts):

```
<svg width="100%" viewBox="0 0 680 250" role="img"><title>…</title><desc>…</desc>
<defs>…standard arrow marker…</defs>
<g class="c-blue"><rect x="90" y="40" width="400" height="150" rx="16"/>
  <text class="th" x="290" y="62" text-anchor="middle" dominant-baseline="central">nr-platform web · 教練端</text>
  <text class="ts" x="290" y="82" text-anchor="middle" dominant-baseline="central">navbar 入口 · PostHog toggle 控制</text></g>
<g class="node c-gray" onclick="sendPrompt('…')"><rect x="110" y="100" width="104" height="64" rx="8"/>
  <text class="th" x="162" y="121" text-anchor="middle" dominant-baseline="central">工作室主頁</text>
  <text class="ts" x="162" y="145" text-anchor="middle" dominant-baseline="central">已上線</text></g>
<!-- …more pages at x=238, x=366… -->
<g class="c-teal"><rect x="520" y="40" width="120" height="150" rx="16"/>…</g>
<g class="node"><rect x="535" y="100" width="90" height="64" rx="8" class="box" stroke-dasharray="4 3"/>…未開始…</g>
<text class="ts" x="48" y="132" text-anchor="middle" dominant-baseline="central">教練</text>
<line x1="66" y1="132" x2="84" y2="132" class="arr" marker-end="url(#arrow)"/>
<line x1="493" y1="132" x2="514" y2="132" class="arr" marker-end="url(#arrow)"/>
<!-- legend row at y≈206: swatch rect 12×12 + ts label ×3 -->
</svg>
```

## Layout recipe B — 泳道 blueprint（pipeline / system topics）

- Two horizontal lanes as dashed neutral rects with `th` labels at left: 上泳道「使用者看到的」, 下泳道「系統」.
- Nodes left→right in data-flow order; user-visible artifacts (頁面、通知、報告) in the top lane, system stages (crawler、翻譯、儲存、API) in the bottom; vertical arrows where a system stage surfaces something to the user.
- Grammar A colors for status briefs; Grammar B if the brief is about the design itself.
- ≤5 nodes per lane; parallel engines collapse to one box + 「×N」.

## Layout recipe C — Role-colored 架構圖（design topics）

Top→bottom data flow in tiers (write → canonical → read → consume): legend row on top; the SSOT box full-width `c-green` (x=40 w=600) as the spine; transitional stores as dashed `c-gray` beside the read tier ("still feeding in, dashed = leaving"); bottom full-width `c-amber` banner, rx=8, with `th` `❗ 終局 = …the one load-bearing rule…` + one `ts` elaboration. ~80px tier pitch; arrows in vertical gaps.

## Before/After & 對照

Two panels side by side (each ≤3 boxes), `th` panel captions「以前」/「現在」or「選了」/「沒選」, one `c-red`/`c-green` accent maximum. If it needs more than 6 boxes total, it is a blueprint topic, not a before/after.
