---
name: narrate-glance
description: "Compress one ticket, incident, system, or decision into 5 sentences + 1-2 ASCII diagrams in zh-tw — a 30-second glance, NOT a deep narration. Use when the user wants quick legibility: '5 句話跟我說明', '5 句話總結', '圖解 + 解釋', '簡單跟我說 X 解了什麼還要做什麼', '30 秒看懂', '一句話 + 一張圖', 'tldr X', 'lite narrate', '/narrate-glance', or any combination of 簡單講/快速/總結 + 一張票/這個 bug/這個 pipeline. Distinguishes from `narrate-topic` (full 6-section onboarding, 200+ lines) by being status-at-a-glance (≤50 lines), and from `catchup` (whole-project context rebuild) by being topic-focused (one ticket/system/decision)."
status: active
tags: [core, communication, narrative, zh-tw, glance]
---

# narrate-glance — One topic → 5 sentences + 1 diagram

A 30-second briefing on ONE thing — a ticket, a shipped bug-fix, a small system, or a specific decision. The output is small by design: a reader should be able to consume it without scrolling.

The defining property is **dual-axis honesty**: every output separates what is *resolved* from what *remains*. A ticket that's "Day-1 hotfix done, structural cleanup pending" should read that way, not "we shipped it 🎉". A pipeline that's stable should say so explicitly. Don't pad, don't pretend, don't gloss over the boundary.

## When this triggers vs adjacent skills

| User wants | Use |
|---|---|
| 5 句話 + 圖解 ONE ticket/bug/system/decision | **narrate-glance** (this) |
| 完整 business-first narration (multi-section, 2-min read) | `narrate-topic` |
| 重建 project-wide context after reset | `catchup` |
| Memory drift / multi-source consolidation | `latest` |
| 收尾 / handoff at session end | `handoff` |
| Strategy / "what next" | `strategic-next` |

If the input is a multi-ticket cluster or roadmap with 4+ items, suggest `narrate-topic` instead — this skill collapses below useful at that scale.

## Input shape detection (decides template)

| Shape | Looks like | Diagram pattern |
|---|---|---|
| **A. Bug-fix / hotfix** | "X was broken, we fixed it" | Before/After |
| **B. Multi-phase ticket** | One Linear ticket with R0/R1/R2 phases or A/B/C milestones | Phase progress bar |
| **C. System / pipeline** | Already-shipped subsystem, "explain how X works" | Component flow |
| **D. Decision** | "Why did we choose A over B for X?" | Side-by-side comparison |

When the shape is ambiguous, ask one clarifier — don't guess across shapes.

## Workflow

1. **Identify the focal subject.** Exactly one thing. If the input names ≥2 unrelated things, ask the user to pick one OR redirect to `narrate-topic`.
2. **Detect shape** (A/B/C/D table above).
3. **Verify ground truth — lite version**. Read at most these three:
   - Linear ticket status (1 API call if a ticket ID is in scope)
   - Latest 1-2 commits touching the subject (`git log --oneline -5 -- <path>` or grep for ticket ID in commits)
   - 0-2 file:line reads ONLY if a specific code claim needs grounding
   Do NOT run full codebase grep, multi-file read chains, or cross-repo verification — those belong to `narrate-topic` / `codebase-audit`.
4. **Pick the 5-sentence template** for the detected shape (see next section).
5. **Pick the diagram pattern** (1 primary, 1 secondary only if it adds distinct information).
6. **Output**: 5 sentences in zh-tw + diagram(s). No headers, no section labels, no "結論" prefix. Total ≤50 lines including diagrams.

## 5-sentence templates by shape

### Shape A — Bug-fix / hotfix
1. **使用者影響** — concrete data / symptom that changed (numbers, IDs, before→after)
2. **根本原因** — the mechanism that was broken (1 sentence, name the file/class)
3. **預防機制** — tests / alerts / contracts now in place
4. **邊界** — why the parent ticket may still be open / what's intentionally not fixed
5. **下一步** — single concrete next action (ticket ID + ~1 day estimate if known)

### Shape B — Multi-phase ticket
1. **為什麼有這張票** — felt pain (1 sentence, user-facing not technical)
2. **目前完成的部分** — phases shipped, what they unlocked
3. **還沒做的部分** — phases pending + the *ordering reason* (not just the list)
4. **Locked decisions** — 1-2 most load-bearing constraints
5. **下個 pickup** — next phase ticket ID + estimated effort

### Shape C — System / pipeline
1. **這系統做什麼** — user-facing function (1 sentence, no jargon)
2. **核心 mechanism** — the spine in one sentence (3-5 named components)
3. **關鍵 invariants** — 1-2 contracts the system MUST preserve
4. **已知限制** — what it explicitly does NOT do
5. **演進方向** — active work pointer, OR "stable, no current changes"

### Shape D — Decision
1. **問題** — what had to be decided
2. **選擇** — chosen path + 1-line rationale
3. **被否決的另一條路** — alternative + why rejected
4. **接受的 trade-off** — the cost we accepted
5. **重新評估 trigger** — what would make us reopen this

## Diagram patterns (pick ONE primary, optional secondary)

### Pattern P1 — Before / After (for Shape A)
```
Before <subject>:
  <component A> ──> <component B>  ❌
                   ↓
                   <user-visible bad state>

After <subject>:
  <component A> ──> <component B>  ✅
                   ↓
                   <user-visible good state>
```

### Pattern P2 — Phase progress bar (for Shape B)
```
<TICKET> 進度
═══════════════════════════════
✅ Phase 1 — <short title>   ◄── 完成
📋 Phase 2 — <short title>   ◄── 下一張
⏳ Phase 3 — <short title>
⏳ Phase 4 — <short title>
   ─────────────────────────
   全做完才 close <TICKET>
```

### Pattern P3 — Component flow (for Shape C)
```
<input> ──► <stage 1> ──► <stage 2> ──► <output>
                ▲
                └── <key invariant or contract>
```

### Pattern P4 — Side-by-side comparison (for Shape D)
```
Option A (chosen)          Option B (rejected)
  ├ <pro 1>                  ├ <pro 1>
  ├ <pro 2>                  ├ <con 1>
  └ <con accepted>           └ <blocker>
```

Diagram constraints: ≤30 lines, ≤80 chars wide, ASCII only. The diagram must illustrate something the 5 sentences can't say cleanly — if it's just decoration, drop it.

## Anti-patterns

| Mistake | Fix |
|---|---|
| Padding to 5 sentences when 3 say it cleanly | Output 3-4; the "5" is a ceiling not a floor |
| Stacking 3 diagrams because each is "kind of useful" | Pick the ONE that adds the most signal; second only if a distinct dimension |
| Diagram as code dump (showing actual function bodies) | Use conceptual labels (`<component A>`, `materializer`) not literal code |
| Citing 5+ `file:line` in the sentences | This is a glance, not an audit. At most 1-2 anchor citations |
| Skipping the honesty axis ("we shipped it 🎉" without remaining) | Shape A sentence 4 is mandatory unless truly done end-to-end |
| Translating EVERY English term to Chinese | Keep technical terms in English (function names, ticket IDs, `idempotency`, `cronjob`) |
| Writing section headers / "## 5-sentence summary" / "### Diagram" | No headers in the output — just the sentences then the diagram |
| Running full codebase audit before answering | If verification takes >3 reads, you're in `narrate-topic` territory — switch skills |

## Output rules

- zh-tw narrative + English technical terms (function names, file paths, ticket IDs, `idempotency`, `cronjob`, etc.)
- Mirror the user's language if they wrote in pure English or pure Chinese — default zh-tw otherwise
- Total output ≤50 lines including the diagram
- No file writes; the output is ephemeral chat content
- If ground truth verification surfaces a contradiction (Linear says Todo but code shows shipped), flag it neutrally in sentence 4 — verification is part of the glance, not a separate report

## When NOT to use this skill

- Multi-ticket cluster / roadmap with 4+ items → `narrate-topic`
- Cross-cutting architectural critique → `reverse-thinking`
- Restructuring tickets → `topic-to-tickets`
- Whole-project status rebuild → `catchup` or `latest`
- The user explicitly said "deep dive" / "完整解析" / "把每個環節都 cover 到" → `narrate-topic`
