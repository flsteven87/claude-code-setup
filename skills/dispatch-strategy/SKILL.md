---
name: dispatch-strategy
description: Plan the dispatch order for a series of topic tickets and render a visual convergence playbook, grounded in live git + Linear. Two modes. (1) Targeted — name an epic / cluster / ticket-list and get its dispatch waves. (2) Auto / board — run it with NO topic (the natural step right after /latest) and it auto-discovers the live workstreams from the freshly-synced MEMORY.md current-state + Linear epics with in-flight or newly-unblocked children, no topic needed. It maps each series' blockedBy/blocks DAG against current reality, classifies tickets into dispatch-now / blocked-next / in-flight / deferred, finds the real parallelism and the single next action, and draws a swim-lane SVG (state-colored nodes, fan-out markers, a convergence banner). Read-only — it PLANS dispatch order; it never edits tickets, writes code, or hands a ticket to an agent. Communicates in Traditional Chinese (zh-tw). Use whenever the user has a related ticket series OR just wants the next move, asking 'what do I dispatch next', '這個系列接下來怎麼派', 'dispatch 策略', '排一下這串票的執行順序', '哪些可以平行', '誰先誰後', '畫出收斂攻略圖', 'NEX-XXXX 系列下一步派什麼', or runs it after /latest with no topic for a board-level playbook, or returns to a multi-ticket workstream after the board has moved and needs a fresh execution frontier. Strongly trigger on '/dispatch-strategy' with OR without arguments. Absorbs the retired /triage-next — also trigger on '清板', '降噪選題', '下一步收什麼', '挑一題收尾', '接下來收哪個', '幫我選一題推進', 'what should I close next' (board mode ranks by open-loop reduction and tags each frontier item's closing move; the user then says 接手 to drive). This is NOT /topic-to-tickets (that CREATES/restructures tickets; this READS an existing set and orders it). NOT /strategic-next (big-bet direction choice; this is execution sequencing). NOT executing a dispatch or implementing a single ticket — it only plans. NOT explaining or visualizing what a ticket means (that's /narrate; the visual here is a dispatch map, not an explainer).
---

# dispatch-strategy — ticket series → grounded dispatch wave plan + visual

`/topic-to-tickets` decomposes a topic into PR-shaped, dependency-ordered tickets. But the moment those tickets exist, the board starts moving: a PR merges, a blocker clears, one ticket goes In Progress, another is silently already done. The original dependency order printed at decomposition time **goes stale within a session**. This skill answers the recurring question you actually face when you sit back down: *given where main and Linear are RIGHT NOW, what is the dispatch frontier — in what order, with what parallelism, routed to whom — and what is the single next thing I do?* And it answers it for the series you name, or — given nothing — for whatever is currently live.

It is a **planner, not a driver**. It reads git + Linear + (where load-bearing) the code, and emits a dispatch plan + a visual. It does not create tickets, edit tickets, write code, or dispatch agents. The human (or a follow-up skill) acts on the plan. Keeping it read-only is what makes it safe to run every session as the board moves.

## Where this sits (don't reach for the wrong tool)

| You want… | Skill |
|---|---|
| Turn a topic into a clean set of tickets | `/topic-to-tickets` |
| **Plan the dispatch order/waves (+ visual) against current reality** | **this skill** |
| 清板／挑一題收尾（pick what to close next off the whole board） | **this skill**, board mode — then say 「接手 <item>」 to drive it |
| Choose a big-bet *direction* among competing topics | `/strategic-next` |
| Sync memory to ground truth first | `/latest` |

Natural chain: `/latest` (sync) → `/dispatch-strategy` (no arg → auto board playbook, OR name a series) → dispatch the frontier (Codex / external agent / self) → review returned PRs → re-run next session (frontier has advanced).

## Two modes

- **Targeted** — the user names a series (epic ID, umbrella, cluster name, or ticket list). Plan that one series. Skip discovery; go straight to grounding.
- **Auto / board** — the user gives **no series** (most often right after `/latest`, or "畫個 dispatch 攻略", "現在該派什麼"). The skill **discovers the live series itself** (step 0), plans each, and synthesizes one cross-series convergence. This is the mode that makes the skill runnable as a standing "where do I point next" without the user re-supplying context every time.

When ambiguous (a bare `/dispatch-strategy` with prior conversation about a specific series), prefer targeting that series; only fall to board mode when there's genuinely no series in scope.

## The one rule that makes this skill worth running

**Memory and Linear lag merges; the dispatch frontier is defined by reality, not by ticket status.** A ticket marked `Backlog` whose PR already merged is *done* and unblocks its dependents. A ticket marked `blockedBy X` where X landed an hour ago is *newly dispatchable*. If you plan dispatch off Linear status alone you will either re-dispatch finished work or sit on an unblocked frontier. So the spine of this skill is: **establish ground truth first, classify second.**

This also means the documented Linear gotcha applies hard here: `list_issues(state:"started")` has missed real WIP children before. For every ticket in the series whose classification matters, confirm with a direct `get_issue` (with `includeRelations:true`) — never trust the list filter alone.

## Method

### 0 — Discover the live series (board mode only)

When no series is named, the skill must figure out *which* series are worth planning before it can plan them. The source of truth for "what is in play" is the state `/latest` just synced — so use it as a **discovery index**, then re-ground every candidate against live Linear + git (memory points you where to look; Linear/git decide what is true — the project's #1 rule, and memory lags merges even right after a sync).

1. **Read `MEMORY.md`** at `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`, specifically the "Now" / "WIP / open loops" / "Active chains" sections. These name the user's active workstreams and usually carry the epic/cluster/ticket IDs (e.g. `NEX-1106` race epic, `NEX-1327` i18n cluster). Extract every `[A-Z]+-\d+` that anchors a workstream.
2. **Resolve each to a series** — for each anchor ID, `get_issue`; if it's an epic/umbrella, pull its `parentId` children; if it's a cluster umbrella, pull the listed children.
3. **Keep only LIVE series** — a series is live (a dispatch decision is actually pending) if it has ≥1 child that is In-flight, a frontier (blocker just merged), or freshly unblocked. **Drop** series that are fully Done, or entirely deep-backlog with nothing newly actionable — they have no pending dispatch decision. Don't plan the whole board; plan where a decision is waiting.
4. **Cross-check git for "silently advanced" series** — grep `git log --oneline -30 origin/main` for ticket IDs / PR numbers; a series memory calls "dispatched, awaiting PR" whose PR already merged is live in a *different* way (its frontier just advanced).
5. **Cap at the top ~3-4 live series**, ranked by ordered criteria (inherited from the retired triage-next — reason through signals, no magic-number scores): **open-loop reduction first** (half-open things: stalled WIP, mergeable-but-unmerged PRs, a finished rung blocking its successors, few steps-to-fully-closed) > **momentum** (smallest thing that ships value; express/standard lane over heavy) > **delegatability** (readiest to become a clean contract). Immediacy (recently-moved > stale) breaks ties. Note any others as "other live series (not shown)" so the cap is visible, never silent.

If discovery finds nothing live (everything Done or deep-backlog), say so plainly and point at `/strategic-next` (choose a direction) — don't manufacture a plan.

### 1 — Resolve the series

(Targeted mode starts here; board mode arrives here with the discovered set.) Accept any of: an epic/umbrella ticket ID (pull all `parentId` children), an explicit list of ticket IDs, or a named cluster from memory. Produce the full member set. If the user names just the epic, fetch the epic body too — `/topic-to-tickets` umbrellas usually carry an authoritative "children (dependency order)" list and end-state invariants worth honoring.

### 2 — Ground against reality (read-only, this is the whole value)

Run these in parallel where independent:

- **git**: `git fetch --all --prune --tags`; capture HEAD; `git log --oneline -30 origin/main`. Grep the log for PR numbers / ticket IDs in the series to find what already merged.
- **Linear, per ticket**: `get_issue` with `includeRelations:true`. Capture `statusType`, `status`, `priority`, `assignee`/`delegate`, `attachments` (open/merged PR links), and the `blockedBy` / `blocks` relations. Do this as direct fetches, not a single `list_issues` filter (gotcha above).
- **Codebase spot-check (only where load-bearing)**: these series tickets carry `file:line` evidence and "blocked by" claims. Before you declare a ticket *unblocked* or *frontier*, verify the one or two facts its dispatchability hinges on — does the blocker's code actually exist in main now? did the merge land the contract the dependent needs? Codebase is ground truth; a green Linear status is not. Don't re-audit everything — just the load-bearing edge.

Record every place where reality differs from Linear/memory — these become the "真值校正" section so the user trusts the rest of the plan.

### 3 — Build the DAG and classify

From the `blockedBy`/`blocks` relations, build the dependency graph for the series. Then bucket every ticket into exactly one of:

- **🟢 Frontier** — all blockers are Done/merged-in-main AND the ticket itself is not Done/Canceled/already-in-flight. Dispatchable now.
- **🟡 Blocked** — at least one blocker still open. Note which blocker, so the unlock condition is explicit.
- **🔵 In-flight** — already In Progress / In Review, or has an open PR. Do NOT re-dispatch; the action here is *await + review the PR*, which is itself how the frontier advances.
- **⚫ Deferred / gated** — explicitly deferred (`DEFERRED` in title, "gate on <condition>", demand-gated). These do not enter the schedule until their gate trips. Surface the gate; do not put them on the frontier just because they're unblocked.

A ticket whose PR merged but Linear still says Backlog/In Progress is **Done** for DAG purposes — say so in 真值校正 and let it unblock dependents.

### 4 — Order the frontier (and find the real parallelism)

Within 🟢, order by, in priority:

1. **Topology** — a ticket that unblocks others goes before a leaf.
2. **Unblocking power** — among independent frontier items, the one that releases the most downstream work first (it widens the future frontier).
3. **Risk lane** — foundation / heavy data-correctness / contract-defining tickets earlier. They are load-bearing and want careful review with runway; thin-UI / leaf tickets can trail. (An early contract-defining ticket also prevents two later tickets from drifting against an unfrozen contract.)
4. **Priority** — Urgent/High before Med/Low as the final tiebreak.

**Parallelism only where the DAG genuinely forks.** Two frontier tickets can be dispatched concurrently only if they don't both write the same module/contract and neither blocks the other. A strict chain (P1→P2→P3) means **one in flight at a time** — dispatching P2 before P1's PR is reviewed risks building on a contract that review will change. The parallel window usually opens at a *fan-out* node (one upstream unblocks several independent branches). Call out the fork point explicitly; don't manufacture parallelism that creates merge conflicts or contract drift.

### 5 — Route each frontier unit

For every 🟢 item, name the executor and the gate, per the project's delegation model:

- **Finalized spec, implementation-shaped** → external implementing agent (e.g. the ticket's "Notes for Joi / TARS") or `Agent(subagent_type:"codex:codex-rescue")`. The brief must be self-contained (paths, line numbers, acceptance) because the executor starts cold.
- **Heavy lane / production-data correctness / cross-stack contract** → dispatch with the extra gates the ticket demands (dry-run-first, backup + rollback, adversarial review before merge). Flag these so they don't get a thin review.
- **Self (gatekeeper)** → the human reviews and merges each returned PR before advancing the frontier; In-flight items are *await + review*, not new dispatches.
- **Deferred/gated** → not routed; the only "action" is to watch for the gate condition.

Honor any human-decision flags on a ticket — if `human_decision_needed: yes` and undecided, it is NOT frontier no matter how unblocked; the action is to surface the decision.

**Tag each frontier item's closing move** (inherited from the retired triage-next), so 「接手」 has an unambiguous meaning per item:

- **開約** — no contract yet → first `/topic-to-tickets` builds one (it owns the mutation gate)
- **直接派** — already a contract passing the Definition of Ready in `docs/architecture/ticket-contract/README.md` → hand to the executor as-is
- **收半成品** — code/PR already exists → `/code-review` deep pass first, then finish; never re-dispatch from scratch

### 6 — Synthesize across series, then render the visual

In board mode you now hold 2-4 planned series. Don't just stack their per-series plans — **find the single convergence**: very often one action (review a contract-defining PR, merge the foundation ticket) unblocks the most across series, and one in-flight item is the true bottleneck. Collapse to **one cross-series next action**. Where two series share a code surface (e.g. two frontier tickets both touching the curator console), flag the conflict so they're serialized, not blind-parallelized — apparent cross-series parallelism is where merge conflicts hide.

Then render the **visual playbook** — a swim-lane SVG (one lane per series, state-colored nodes, fan-out markers, a single convergence banner). It is a **default deliverable in board mode** and a useful option in targeted mode (single-lane DAG). The full diagram spec — when to render, the state→color legend, the distilled SVG conventions so it comes out right on the first try, and a parametric skeleton — lives in `references/visual-playbook.md`. Read it before calling the visualization tool.

## Output template

Communicate in zh-tw (English only for tokens: ticket IDs, PR #, SHAs, file paths, commands, status names). Keep it scannable; the single next action is the deliverable.

```
## Dispatch 策略 — <series name / epic> @ <YYYY-MM-DD>

### 系列 DAG
<compact ASCII: nodes = tickets, edges = blockedBy; mark fan-out points>

### 真值校正（Linear / memory 落後處）
- <ticket>：Linear 標 <X>，實際 <Y> — 依據：<PR #N merged @ SHA | blocker cleared | code grep>
（若無落差：「無 — Linear 與 main 一致」）

### 🟢 Frontier（現在可 dispatch，依序）
1. <ticket> · <priority> · <lane> — why-now：<blocker 已清> · 路由：<Codex / Joi / self> · 收法：<開約 / 直接派 / 收半成品> · brief：<一行>
2. ...
（標出哪幾項可平行：<fork point>；其餘須序列化的原因：<contract/module 衝突>）

### 🟡 Blocked（下一波 + 解鎖條件）
- <ticket> — 等 <blocker ticket/PR> land 後解鎖

### 🔵 In-flight（已派、勿重派、等 PR）
- <ticket> — <status>，<PR #N | 無 PR 回來>；動作＝review/merge 以推進 frontier

### ⚫ Deferred / gated（不照排程派）
- <ticket> — gate：<condition>

### ▶ 下一個動作（單一）
<the ONE thing to do right now — usually: dispatch the top frontier item with <executor>, or review the in-flight PR that advances the frontier. One sentence.>
```

If the series is a strict chain with everything downstream blocked, the honest output is small: one frontier item (or one in-flight PR to review) and a clear "下一波要等它 land" — that *is* the right answer; don't pad it into fake parallelism.

**Board mode** runs the same template once per discovered series (drop the per-series `▶ 下一個動作`), then closes with a single cross-series block + the visual:

```
### 🎯 跨系列收斂（單一下一步）
<the ONE action that unblocks the most across all series — usually a contract-defining PR review or a foundation merge>
<if two series share a surface: 「<A> 與 <B> 同碰 <surface> → 序列化、勿盲目平行」>

### 🖼 視覺攻略
<rendered swim-lane SVG via the visualization tool — see references/visual-playbook.md>
```

## Worked example (i18n cluster, the richest DAG)

Series `NEX-1327` (catalog i18n) decomposed by `/topic-to-tickets` into P1→P5. After grounding: P1 `NEX-1338` is In-flight (dispatched, no PR yet), P2→P5 all Blocked, with a fan-out at P3.

```
NEX-1338 (P1 foundation) ──> NEX-1339 (P2 translate lib) ──> NEX-1108 (P3 apply)
                                                                 ├──> NEX-1340 (P4a curator) ──> NEX-1109 (P4b run race)
                                                                 └──> NEX-1341 (P5 promote training)
```

- 🟢 Frontier: *(empty — P1 is in-flight; nothing else is unblocked yet)*
- 🔵 In-flight: `NEX-1338` In Progress, no PR → action = await + review its PR.
- 🟡 Blocked: P2 (waits P1) → P3 (waits P2) → then fork: {P4a→P4b} ‖ P5 (all wait P3).
- ▶ 下一個動作：等 `NEX-1338` PR 回來，review/merge，**然後**才派 P2 `NEX-1339`。**不要**提前派 P2 — 它建在 P1 的 shared primitives 上，contract 未凍。

The lesson the skill encodes: a 6-ticket series can have a frontier of *zero* when it's a strict chain mid-flight. The value is saying so with evidence, plus marking the future fork (P3 → P4a‖P5) so the user knows the parallel window is coming and where.

## Discipline checklist

- Board mode: discover from `MEMORY.md`, but re-ground every candidate against live Linear + git before planning — memory points, Linear/git decide.
- Keep only live series (a dispatch decision is pending); cap at ~3-4 ranked open-loop-reduction > momentum > delegatability, and name what was dropped. If nothing is live, point at `/strategic-next` instead of inventing a plan.
- Ground truth before classification — `git fetch` + per-ticket `get_issue(includeRelations)`; never the `state:"started"` filter alone.
- Verify the load-bearing edge in code before declaring "unblocked"; codebase beats Linear status.
- One-in-flight for a strict chain; parallelize only at a genuine fan-out — including *across* series that share a code surface.
- Deferred/gated ≠ frontier even when unblocked — respect the gate.
- Collapse to exactly one next action (per series in targeted mode; one cross-series convergence in board mode).
- Render the visual playbook (default in board mode) per `references/visual-playbook.md`.
- Read-only: no ticket edits, no code, no dispatch. Plan and hand off.
