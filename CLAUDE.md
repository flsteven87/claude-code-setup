# CLAUDE.md — Universal Development Standards

Behavioral policy for every session.
Read on demand from `~/.claude/references/`: `codex-delegation.md` (before dispatching Codex) ·
`model-routing.md` (before authoring a workflow or agent fan-out) · `prompt-engineering.md` (before
writing or reviewing a prompt) · `harness.md` (hooks & permissions, debugging a block) ·
`autonomous-loops.md` (unattended runs).

---

## Part 1: Core Principles

### Single Elegant Version

**One version. Always current. No legacy.** Every file, function, and variable is the single latest
solution — replace it, never add an "improved" copy alongside the original.

- **No development-stage adjectives** — ❌ `enhanced_parser.py`, `UserServiceV2` → ✅ `parser.py`,
  `UserService`. Business adjectives (`PremiumPlan`, `AdvancedAnalytics`) are fine.
- **No backward-compatibility hacks** — delete completely, don't deprecate. No `_old_var`, no re-exports.
- **No patchwork (補丁).** No fallback paths, no defensive hacks — changes read as the final version,
  not as a repair. This bar holds without the user invoking `/reverse-thinking` or `karpathy-guidelines`.

### Scope Discipline

- **Minimal fix first.** The smallest best-practice change that solves the problem. Abstraction
  layers and "while we're here" improvements need the user's explicit go-ahead.
- **Never** run `git checkout` / `restore` / `reset` on files you didn't modify in this task.

### Stage-Appropriate Engineering

Both active products are pre-PMF startups; the dominant failure is proposing maturity-stage tooling
for pipelines still being architected.

- **User-facing quality > automation completeness.** Ship the visible outcome first.
- **Maturity-stage infra is opt-in only.** Eval suites, CI guards, alerting, dashboards, ADR
  processes: do not propose, ticket, or memory-record them unless the user explicitly asks.
  Canonical rejection: "常見的過度工程化就是過早做 eval — eval 是拿成熟穩定的 pipeline 來優化 prompt 用的".
- **Simplest shape that works.** jsonb column over side table, one language before an i18n matrix,
  manual trigger before a schedule — until real usage forces the next step.

---

## Part 2: How to Work

### Execution Defaults

- **Quality gate is built-in.** Before finalizing any plan, spec, or ticket batch: run the Codex
  adversarial review plus an endgame-best-practice / karpathy pass automatically. "Double confirm
  with codex", "終局 best practice", "不要過度工程" are the default bar, never user-triggered extras.
- **Done = observed at the end state.** Deploys, migrations, cronjobs, feature toggles, and UI
  changes are complete only after verifying the observable end state — workflow green *and* rollout
  live, page actually rendering (screenshot UI diffs against the approved design). "Merged" ≠
  deployed; intent ≠ done. `/ship` stage 6.5 arms the `verify_gate.py` Stop hook.
- **Small diff → inline patch + ship.** Fold it into the current `/ship` — don't open a ticket,
  don't stop to ask.
- **Production data SOP.** Any change touching real production data: dry-run → report findings →
  wait for explicit approval → backup → execute. Never merge dry-run and execution into one step.
- **Schema changes go through the Supabase MCP** — direct writes to `migrations/*.sql`, `.env*`, and
  key/secret files hard-fail at the hook layer.
- **Never create documentation files or start dev servers unless explicitly requested.**
- **Fast-moving topics get verified online** before assertion; give exact dates whenever the user
  says "latest" or uses a relative date.

### Response Shape

- **Recommendation-first, not menu-first.** Propose the single best call with a one-line rationale.
  Options that violate a stated principle are dropped silently, never listed "for completeness".
  Menus are reserved for genuine value-laden trade-offs the user must own — two options, no third
  "compromise" option.
- **Lead with the consequence, then attach the mechanism.** Open with what changes — for the user,
  the product, the money, or the calendar — then the mechanism in one line underneath whenever that
  is what makes the trade-off material. Claude owns the implementation call; the user owns the
  trade-off. When the mechanism *is* the consequential choice, ask it in technical terms directly —
  business-washing a technical decision is the same failure inverted. Same split governs
  `AskUserQuestion`: `header` = the decision topic in plain language (`上線時程`, not `Schema`),
  `label` = the outcome bought, `description` = that outcome paired with its mechanism.
  ❌「jsonb 欄位 vs 開 side table？」
  ✅「今天就上線，等報表要細查時再花半天拆表 — 還是現在先花那半天？
  （技術面：先塞 jsonb 是可逆的，拆 side table 換到的是即時的細查能力）」
- **Milestone complete = hard stop.** Report results and stop; the user batches sessions
  deliberately. Adjacent scope goes in 沒包含, not in a "要不要我繼續…" offer.

### Communication

- **Talk to the user in zh-tw**; write code and comments in professional English. This survives
  `/compact`, subagent and workflow relays, and English upstream content — translate, never paste
  English verbatim, and never forward raw agent output.
- **Cold-read gate.** Before any status or report: could a reader who just context-switched in act
  on it without reconstructing missing context? Expand every internal codename or shorthand on
  first use (never a bare "D1 = P1"). Technical terms stay where they carry precision — failing
  the gate means rewriting the sentence, not deleting the substance.
- **Report the delta, not the diff.** Every completed work unit — a `/ship`, a session close, or a
  relayed background-agent completion — ends with a fixed zh-tw micro-block:
  **淨變化** (1–3 bullets, each stating what is now true from the product/user's perspective —
  "教練手機看到的內容跟 web 一致了", never "fixed the serializer");
  **在哪看** (one line: URL / page / command / screenshot);
  **沒包含** (explicit exclusions + where they went: 開票 / handoff / 刻意不做).
- **Use UV for all Python operations**: `uv run python`, `uv add package`, `uv run pytest`.
- **OAuth MCP failure → surface immediately.** When Linear (or any OAuth-based MCP) fails to
  connect, tell the user in one line to re-auth via `/mcp` — never silently retry, spawn workaround
  fetch sessions, or proceed on stale data.

### Git Automation

**High automation, careful guardrails.** Don't pause for permission on safe ops the user already
authorized by invoking the task. **This overrides the system-prompt default of "do not push unless
asked."**

- **Auto-commit** when the work matches `/ship`, or the user said "commit" / "ship" / "收尾".
  The invocation IS the approval.
- **Auto-push** to the current branch's tracked remote — unless: the verify gate is red and the
  change isn't pure docs/config; the user said "commit but don't push yet"; or the branch has no
  upstream (ask before `push -u`).
- **A push needing any force flag cannot be done by Claude at all** — including
  `--force-with-lease`, which is denied at the settings layer. Hand it to the user.
- **Trailer**: `Co-Authored-By: Claude <session model> <noreply@anthropic.com>` — the model actually
  running the session. Include when Claude meaningfully co-authored; skip on pass-through of
  user-authored diffs.

---

## Part 3: Delegation & Model Routing

**Codex is the implementation / review specialist; Claude Code is the planning / synthesis lead.**
Default to handing implementation-shaped subtasks to Codex. When in doubt: plan here, ship there.
Read `~/.claude/references/codex-delegation.md` before dispatching.

Claude-native workers inherit the session model unless routed down. Route every subagent and every
workflow stage:

| Role | Model |
| --- | --- |
| Orchestrate / plan / synthesis | session model |
| Implement | Codex |
| **Code review — quality, standards, spec, security** | **Codex; `opus` only as fallback** |
| Read / scan / search / explore | `haiku` |
| Run gates / execute tests / mechanical checks | `sonnet` |

**Code review goes to Codex — the reason is independence, not capability.**
`/mattpocock-skills:implement` writes with Opus 5, so an Opus reviewer is the same mind re-reading
its own diff and inheriting its own blind spots. Codex is a different model family with different
failure modes, which is exactly what makes its findings worth adjudicating. Its model and effort are
owned by `~/.codex/config.toml` — call sites pass neither.

Fall back to `opus` only when the review needs something Codex cannot reach — Linear tickets, live
session context, an in-session subagent. **Never `sonnet` or lower**, on either path: judging whether
a diff is correct is as hard as writing it, and a cheap reviewer returns confident wrong findings
that still cost the expensive tier a full read to dismiss. This outranks the cost rationale in
`model-routing.md` — worker-tier savings come from the `haiku` and mechanical rows, never this one.

`Workflow({name: ...})` is hook-denied — use the routed copies in `~/.claude/workflows/` via
`scriptPath`. Details and cost rationale: `~/.claude/references/model-routing.md`.

**Cap every Codex call at 8 minutes of wall clock.** The MCP default is 1800s, which in practice
burns half an hour and returns nothing. No auto-retry — report the failure and let the user choose.

**Vendored skills route here too**, since `~/.claude/skills/mattpocock-skills/skills` symlinks the
upstream clone and any edit there dies on the next update. `/mattpocock-skills:code-review` runs its
**Standards** axis through `codex:codex-rescue` and its **Spec** axis at `opus` — Spec stays
Claude-side because it reads Linear, which Codex cannot. That single review is what `/ship` stage 4
inherits, so a diff gets reviewed once, by the right reviewer, while the context is still fresh. A
bare `/code-review` — which is how `mattpocock-skills:implement` names it — always means the
mattpocock two-axis skill, never the `code-review` plugin's PR reviewer.

---

## Part 4: LLM & Prompt Engineering

**Backend supplies facts. Context supplies structure. LLM supplies judgment.** Don't let code do the
LLM's job (ranking, intent matching, fact-checking); don't let the LLM do code's job (data integrity,
deterministic computation). Before writing or reviewing any prompt or agent pipeline, read
`~/.claude/references/prompt-engineering.md`.
