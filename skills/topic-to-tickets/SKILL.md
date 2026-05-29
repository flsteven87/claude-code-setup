---
name: topic-to-tickets
description: Run a deep audit on a high-level topic — verify codebase ground truth, consult Codex independently for blunt push-back, then consolidate or restructure Linear tickets into PR-shaped, dependency-ordered work units. Communicates decisions in Traditional Chinese (zh-tw). Use this skill when the user wants to take a topic (incident class, architectural concern, backlog cluster) and turn it into a clean set of implementation-ready tickets, get independent expert push-back via Codex before handing implementation to others, or restructure existing backlog tickets after architectural rethinking. Strongly trigger on '/topic-to-tickets', or phrases like '深度審視', '深度檢視', '從 high-level 角度看', '把這個議題拆成 tickets', '一系列 ticket', '跟 codex 確認過嗎', '/reverse-thinking 然後改 ticket', '幫我整合這幾張票', '我要確認方向正確', or any combination of '/reverse-thinking' alongside ticket-management intent. Even if the user does not explicitly ask for an audit, trigger this when the request implies multi-ticket consolidation + expert second-opinion + scope rewriting.
---

# topic-to-tickets — High-level topic to PR-shaped tickets

Orchestrates a deep, evidence-based audit + Codex consultation + Linear ticket mutation. The user enters with a topic (incident class, architectural concern, backlog cluster) and exits with restructured, dependency-ordered tickets ready to hand to an implementing engineer.

The point of this skill is to **never hand over implementation work that hasn't been independently challenged**. Self-review by the same model is not independent. Codex consultation is the gate.

## When this skill triggers vs. adjacent skills

| If the user wants… | Use… |
|---|---|
| Audit only an existing plan / spec | `/reverse-thinking` (audit mode) |
| Build a new feature from rough idea | `/build` or `/brainstorm` |
| Strategic "what next" prioritization | `/strategic-next` |
| Review code changes already made | `/code-review` or `/review-change` |
| **Audit a topic + restructure tickets + Codex push-back** | **this skill** |

## Audit deliverables

This is what the skill returns to the user — the audit artifacts, distinct from the *ticket* contract (the SSOT cited in Phase 6). In this order:
1. **End-state vision** (1 sentence + 3-5 invariants) — anchor for everything downstream
2. **Codebase ground-truth report** — every load-bearing claim cited as `file:line`
3. **Reverse-thinking audit Part A-F** — including RISK verdict
4. **Codex push-back transcript** — direct quotes, severity-marked
5. **zh-tw decision checkpoint** — wait for user OK before mutation
6. **Linear ticket mutations** — final layout table with block chain
7. **Final report** — Codex critique → ticket landing map

## Workflow

### Phase 1 — Confirm topic scope (zh-tw)

The user's prompt may name a single ticket or a vague "X 議題". Before any work, confirm in zh-tw:

- **這個 audit 涵蓋哪些 ticket / 哪段 codebase？** Topic must span 2+ tickets or be architectural in nature; otherwise this is the wrong skill.
- **End goal 是什麼？** Pure review, restructure existing tickets, or open new ones?
- **Output 形態？** Updated tickets / new ticket cluster / ADR / handoff doc?

Do NOT begin the audit until scope is confirmed. Mis-scoped audits waste Codex tokens and produce misleading restructuring.

### Phase 2 — Codebase ground truth

This is the layer that everything else stands on. Memory files, ticket descriptions, and documentation **all lag merges** and produce false claims. Verify directly.

Spawn an `Explore` subagent (breadth: very thorough) tasked with:

```
For EACH claim in the relevant tickets / MEMORY / docs about codebase state:
- Return file:line cite + short snippet
- Mark anything that contradicts the ticket description in **bold**
For commits referenced (post-fix shipped):
- `git show --stat <sha>` to confirm scope
For IaC / config / workflow files:
- Read actual content not docs
```

**Invariant**: every "load-bearing" claim downstream MUST have a `file:line`. Audit credibility depends on this. If you cannot cite, you cannot claim.

In parallel, read the originating commit messages — they often describe the exact pre/post state more honestly than tickets.

### Phase 3 — Reverse-thinking audit (mode: audit)

Invoke the `reverse-thinking` skill, mode `audit`. This produces Part A–F:

```
A. End-state Ultrathink — 1 sentence + invariants
B. Reverse Thinking — preconditions table (Gap column = highest value)
C. Codebase Reality Check — cite file:line, severity-marked contradictions
D. Best-Practice Critique — dimension-scored
E. Restructuring Recommendation — Keep / Reorder / Insert / Reduce / Delete
F. RISK Verdict — LOW / MEDIUM / HIGH + rationale
```

Even if Part F returns `LOW`, **continue to Codex consultation**. Self-audit confidence is unreliable; the cost of a 500-word Codex check is small compared to the cost of shipping a wrong direction.

### Phase 4 — Codex deep consultation

This is where the pattern earns its name. Same-model self-review (codex-rescue subagent included — it is also Claude) does not catch the same class of gaps that an independent model architecture catches.

#### Tool selection (priority order)

1. **`codex` CLI via Bash** (preferred — bypasses MCP wrapper version issues):
   ```bash
   cd /tmp && codex exec --skip-git-repo-check --sandbox read-only '<prompt>' 2>&1 | tail -200
   ```
   The CLI uses the user's installed `@openai/codex` binary directly, avoiding stale MCP wrappers.

2. **`mcp__codex__codex` MCP** — try this if Bash CLI not available; may fail with model version errors.

3. **`codex:codex-rescue` subagent** — LAST RESORT. **It is Claude, not Codex.** If you fall back to this, label clearly in your report ("Codex unavailable; rescue subagent stood in"). Do not silently substitute.

If Codex returns "model requires newer version" errors, see `references/codex-troubleshooting.md` for CLI upgrade + model availability flow.

#### Prompt structure

The prompt to Codex should be ~400-600 words containing:

```
1. CONTEXT block (200-300 words)
   - Stack summary
   - Origin (incident, audit trigger, etc.)
   - Already-shipped fixes with commit SHAs
   - Current ticket scope

2. Your proposed plan (bullet list)
   - Each PR / mutation, blunt and concrete

3. Specific questions (3-5)
   - "Anything OBVIOUSLY WRONG before handoff?"
   - "Is X pattern the right shape, or code smell to refactor toward Y?"
   - "Is parameter Z appropriate for this context, or do I need a different shape?"
   - "Best-practice anchors I missed?"

4. Explicit framing
   - "Be blunt — push back, do not validate."
   - "I want gaps, not polite agreement."
   - "Cite SRE / domain refs."
```

The framing matters. Without "push back, do not validate", Codex (like any LLM) tends toward agreement. State the bias you want it to fight.

#### Multi-round consultation

If Codex's first response surfaces architectural disagreements (e.g., re-ordering, renaming concepts, dropping a sub-task entirely), **do a second consultation round** before mutation. Show Codex the user-confirmed updates and ask "anything else missed?". One round is usually enough; two rounds for high-stakes architectural decisions.

### Phase 5 — zh-tw decision checkpoint

Before any ticket mutation, report Codex's push-back to the user **in Traditional Chinese**:

- Quote each push-back item directly (in code or English where the technical content matters)
- Mark severity:
  - 🔴 Load-bearing — would cause silent failure or wrong direction
  - 🟡 Scope-shifting — significantly changes work or risk
  - 🟢 Cosmetic — naming or framing
- Show what each implies for tickets (which ticket, which section, what change)
- Ask: **「全套 patch 嗎？還是要 selective？」**

The user's confirmation is the gate. **Do NOT mutate Linear without explicit OK.** This is the most common failure mode of this workflow — Claude treats Codex's word as truth and patches without confirmation. Codex is a strong second opinion, not the user.

### Phase 6 — Linear ticket mutation

**Contract conformance — the ticket-contract SSOT governs every ticket here.** Produce each ticket body from the policy at `docs/architecture/ticket-contract/` (in the nr-platform repo): use `ticket-template.md` — the compact form for `express`/`standard` lanes, the full form for `heavy` — assign a **lane** with risk reasons, and confirm the ticket passes the README **Definition of Ready** *before* you mutate. Cite the policy path; never copy its schema into this skill — a second copy would drift from the SSOT. A ticket failing any Definition-of-Ready item is not ready for Joi/TARS; keep refining it (or hand back to the caller) rather than shipping a half-contract.

Use `mcp__linear__save_issue` and related tools. See `references/linear-quirks.md` for the full set of gotchas. Critical points:

- **Linear strips multi-row markdown tables AND multi-item bullet lists on re-save.** Wrap all structured content in ` ``` ` code fences.
- **`blockedBy` is append-only.** To rewire, use `removeBlockedBy` first, then `blockedBy` to add new.
- **Assignee field is `assignee` (not `assigneeId`).** Accepts user ID, name, email, or `"me"`.
- **Closing as duplicate**: set `state: "Duplicate"` + `duplicateOf: "<TARGET-ID>"`.

Standard mutation pattern:

```
For each ticket in the restructure plan:
1. Update title to reflect new scope
2. Rewrite description per `ticket-template.md` (with code fences for structured content)
3. Adjust priority if scope changed
4. Re-wire blockedBy chain (removeBlockedBy → blockedBy)
5. Set assignee
6. If consolidating: set state Duplicate + duplicateOf
```

Run mutations in parallel (Linear tool calls) where they don't depend on each other.

### Phase 7 — Final report (zh-tw)

Always end with this structure:

```
## 最終 ticket layout
| ID | New title | Priority | State | Block chain |
|---|---|---|---|---|
| ... |

## Codex push-back → ticket landing map
| # | Codex critique | Severity | Landed in |
|---|---|---|---|
| 1 | ... | 🔴 | NEX-XXX §Y |

## Out of scope (deferred + reasoning)

## 下一步建議
```

The landing map is the durable artifact. If implementation later goes sideways, you can trace each design decision back to its origin.

## Communication discipline

- **All decision checkpoints in zh-tw.** Code, file paths, identifiers, log lines stay in English.
- **Be honest about Codex availability.** If MCP failed and rescue-subagent stood in, say so explicitly. The user's trust in this workflow depends on it.
- When citing claims, prefer "I read X at `file:line`" over "I think X is the case."
- When Codex disagrees with codex-rescue or your prior take, **side with Codex** unless you can cite codebase evidence to the contrary. The whole point of Codex is independent push-back.

## Anti-patterns (do not do)

- ❌ Claim "Codex confirmed" if the rescue subagent answered without forwarding. Audit the rescue agent's first sentence; if it says "I'll handle this directly", that's NOT Codex.
- ❌ Mutate tickets before user confirms the push-back. Even if your confidence is high.
- ❌ Rely on MEMORY / ticket descriptions as ground truth. Both lag merges.
- ❌ Skip Phase 4 even if Phase 3 returns RISK: LOW. A 50-word Codex sanity check still catches things self-review can't.
- ❌ Inflate scope by "while we're at it" additions during Phase 6. The Codex round is over; no new scope unless user asks.
- ❌ Lose the file:line citations in the final report. They are the audit's load-bearing evidence.

## Worked example

The skill's origin session: a 4-ticket consolidation from a 2026-04-07 nr-chat connection-pool incident. Pattern executed:

```
Phase 1 — confirmed scope = 4 tickets, restructure-not-review
Phase 2 — Explore subagent verified 12 claims with file:line cites; found 3 outdated (NEX-567 §2 already done; §3 path doesn't exist; §4 numbers stale)
Phase 3 — reverse-thinking audit returned RISK: MEDIUM
Phase 4 — Codex unavailable initially (MCP wrapper version mismatch); fell back to codex-rescue subagent (clearly labeled); after CLI upgrade 0.118 → 0.125, real Codex (gpt-5.5) returned 7 substantive push-backs that codex-rescue had not surfaced (block-chain order inverted; "GitOps" misnomer; kubectl diff semantics; hardcoded thresholds = theater; log-text alerts rot; single-window burn-rate is wrong shape; /health/ready ≠ user path)
Phase 5 — reported all 7 in zh-tw; user said "全套 patch"
Phase 6 — rewrote 3 ticket descriptions, re-wired block chain (NEX-570 → NEX-567 → NEX-569), closed NEX-568 as duplicate of NEX-567
Phase 7 — final report linked each push-back to ticket section
```

Honest moment from origin session: when user asked "這些方向跟結論，都是跟 codex 確認過的對嗎？", the correct answer was "no — codex-rescue stood in for Codex; here is what we actually did." Hiding that would have shipped a half-validated plan. Be that honest.

## References

Read these when the relevant phase is active:

- `references/codex-troubleshooting.md` — CLI version, model availability, MCP fallback path, prompt-structure templates
- `references/linear-quirks.md` — `save_issue` gotchas, block-chain rewiring, duplicate closure, assignee resolution
- `references/anti-pattern-examples.md` — concrete examples of what Codex catches that self-review misses (SRE-flavored from origin session, but the *shape* generalizes)
