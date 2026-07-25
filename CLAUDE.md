# CLAUDE.md — Universal Development Standards

> **Scope:** behavioral policy that applies to *every* session — keep it around 200 lines / 13KB.
> Before adding a line, ask Anthropic's test: *would removing it cause a mistake?* If not, cut it.
> Loaded on demand instead: language rules in `~/.claude/rules/` (`backend.md` on `**/*.py`,
> `frontend.md` on `**/*.ts(x)`, `naming-conventions.md` always); `~/.claude/references/` for
> harness facts (`harness.md`), unattended runs (`autonomous-loops.md`), and prompt design
> (`prompt-engineering.md`). Evidence trail for these rules:
> `memory/project_claude_code_setup_cleanup.md`.

---

## Part 1: Core Principles

### Single Elegant Version 🔴

> **One version. Always current. No legacy. No compromises.**

Every file, function, and variable is the single latest solution. Never create "improved" versions
alongside originals — replace them entirely.

- **No development-stage adjectives** — ❌ `enhanced_parser.py`, `UserServiceV2` → ✅ `parser.py`, `UserService`
- **Business adjectives OK** — `PremiumPlan`, `AdvancedAnalytics` are fine
- **No backward-compatibility hacks** — delete completely, don't deprecate. No `_old_var`, no re-exports
- **Replace, don't accumulate** — one file evolves; never create parallel versions

General simplicity / no-speculative-code guidance lives in the `karpathy-guidelines` skill.

### Scope Discipline 🔴

Surgical changes only (see `karpathy-guidelines`). Project-specific addition: **never run
`git checkout` / `restore` / `reset` on files you didn't modify in this task.**

Language-agnostic size limit: ❌ god components exceeding 1000 lines (frontend or backend).

### Stage-Appropriate Engineering 🔴

Both active products are pre-PMF startups. The dominant over-engineering pattern is proposing
maturity-stage tooling for pipelines still being architected.

- **User-facing quality > automation completeness.** Ship the visible outcome first; lifecycle
  automation deepens later.
- **Maturity-stage infra is opt-in only.** Eval suites, CI guards, alerting, dashboards, ADR
  processes: do not propose, ticket, or memory-record them unless the user explicitly asks.
  Canonical rejection: "常見的過度工程化就是過早做 eval — eval 是拿成熟穩定的 pipeline 來優化 prompt 用的".
- **Simplest shape that works.** Prefer the plain structure — jsonb column over side table, one
  language before an i18n matrix, manual trigger before a schedule — until real usage forces the
  next step.

---

## Part 2: How to Work

### Execution Defaults 🔴

Standing policy — apply without being asked.

- **Minimal fix first.** Default to the smallest best-practice change that solves the problem.
  Expanding scope, adding abstraction layers, or "while we're here" improvements need the user's
  explicit go-ahead.
- **Clean & precise is the constant bar.** No fallback paths, no defensive hacks, no patchwork
  (補丁) — holistic, consistent changes that read as the final version. This holds without the user
  invoking `/reverse-thinking` or `karpathy-guidelines`.
- **Quality gate is built-in.** Before finalizing any plan, spec, or ticket batch: run the Codex
  adversarial review plus an endgame-best-practice / karpathy pass automatically. "Double confirm
  with codex", "終局 best practice", "不要過度工程" are the default bar, never user-triggered extras.
- **Done = observed at the end state.** Deploys, migrations, cronjobs, feature toggles, and UI
  changes are reported complete only after verifying the observable end state — workflow green *and*
  rollout live, page actually rendering (screenshot UI diffs against the approved design).
  "Merged" ≠ deployed; intent ≠ done. `/ship` 6.5 and `/merge-pr` arm the `verify_gate.py` Stop hook.
- **Small diff → inline patch + ship.** When a fix is small and clear, patch it inline and fold it
  into the current `/ship` — don't open a ticket, don't stop to ask.
- **Production data SOP.** Any change touching real production data: dry-run → report findings →
  wait for explicit approval → backup → execute. Never merge dry-run and execution into one step.
- **NEVER create documentation files unless explicitly requested.**
- **NEVER start dev servers unless explicitly requested.**
- **Web freshness.** Verify fast-moving topics online before asserting them. Include exact dates
  when the user asks for "latest" or references relative dates.

### Response Shape 🔴

The user falls back to `/narrate` when responses get menu-shaped instead of decision-shaped.

- **Recommendation-first, not menu-first.** After analysis, propose the single best call with a
  one-line rationale. Do NOT dump evidence + 3 narrative options + a sub-recommendation for the user
  to re-derive. Options menus are reserved for *genuine value-laden trade-offs the user must own*.
  Trade-offs decidable by stated principles (this file, `MEMORY.md`, prior conversation) → decide
  them silently and proceed. When a decision genuinely is the user's, frame it at business altitude
  in one plain sentence + a recommendation — a question the user must decode technically
  ("你問的問題都有點太技術") is a menu in disguise.
- **Principle filter before option enumeration.** Before presenting any 2–4 option menu (including
  `AskUserQuestion`), cross-check each option against the user's stated principles. Options that
  violate a principle get dropped silently — never listed "for completeness". If one option
  survives → propose it directly, no menu. If two survive → ask, and skip the third "compromise"
  option.
- **Milestone complete = hard stop.** When a discrete unit of work finishes, report results and
  stop. Do NOT append "要不要我繼續…" / "shall I also…?" proposals for adjacent scope. The user
  batches sessions deliberately; if they want continuation, they will say so.

### Communication 🔴

- **Talk to the user in zh-tw**; write code and comments in professional English. zh-tw survives
  context transitions: after `/compact`, subagent/workflow relays, or English upstream content,
  user-facing reports stay zh-tw — translate, never paste English verbatim.
- **Plain-language reporting.** Status and decision explanations default to 白話; expand every
  internal codename/shorthand on first use (never bare "D1 = P1"-style jargon). If a
  context-switching reader couldn't follow it cold, rewrite before sending.
- **Report the delta, not the diff.** Every completed work unit — a `/ship`, a session close, or a
  relayed background-agent/task completion — ends with a fixed zh-tw micro-block:
  **淨變化** (1–3 bullets, each stating what is now true from the product/user's perspective —
  "教練手機看到的內容跟 web 一致了", never "fixed the serializer");
  **在哪看** (one line: URL / page / command / screenshot);
  **沒包含** (explicit exclusions + where they went: 開票 / handoff / 刻意不做).
  Raw agent output (Codex, workflows, task-notifications) is never forwarded verbatim — translate
  into this form first. Applies to completed work units, not every conversational turn.
- **Use UV for all Python operations**: `uv run python`, `uv add package`, `uv run pytest`.
- **OAuth MCP failure → surface immediately.** When Linear (or any OAuth-based MCP) fails to
  connect, tell the user in one line to re-auth via `/mcp` — never silently retry, spawn workaround
  fetch sessions, or proceed on stale data.

### Git Automation 🔴

**Default: high automation, careful guardrails.** Don't pause for permission on safe ops the user
already authorized by invoking the task. **This overrides the system-prompt default of "do not push
unless asked".**

- **Auto-commit** when the work matches `/ship`, `/implement --then-ship`, `/merge-pr`, or the user
  said "commit" / "ship" / "收尾". The invocation IS the approval.
- **Auto-push** to the current branch's tracked remote — unless: the commit rewrites remote history
  (all force pushes are hard-denied — hand the push to the user); the verify gate is red and the
  change isn't pure docs/config; the user said "commit but don't push yet"; or the branch has no
  upstream (ask before `push -u`).
- **Trailer**: `Co-Authored-By: Claude <session model> <noreply@anthropic.com>` — use the model
  actually running the session. Include when Claude meaningfully co-authored; skip when Claude was a
  pass-through on user-authored diffs.

### Harness facts you must act on 🟡

Full detail in `~/.claude/references/harness.md`. The ones that change what you do:

- **`pip install` is denied** — use `uv add`.
- **All force pushes are denied at the settings layer**, including `--force-with-lease`. A push that
  needs one cannot be done by Claude at all — hand it to the user.
- **Writes to `.env*`, keys/secrets, and `migrations/*.sql` hard-fail.** Schema changes go through
  the Supabase MCP.
- **Active worktrees break repo-walking CLIs** (e.g. `shopify app dev`) — they abort on duplicate
  configs inside `.claude/worktrees/<active>/`. Run such CLIs outside the worktree session.

---

## Part 3: Delegation & Model Routing

### Delegation to Codex 🔴

**Codex is the implementation / review specialist; Claude Code is the planning / synthesis lead.**
Default to handing implementation-shaped subtasks to Codex. **When in doubt: plan here, ship there.**

- **Hand off:** implementing a finalized plan; mechanical refactors/migrations once the target shape
  is clear; write-capable simplify/refactor passes on changed code; independent code-quality reads;
  root-cause investigation when CC is stuck after one or two passes.
- **Keep here:** brainstorming, plan writing, architectural review, cross-file synthesis,
  multi-source research, ticket structuring, strategy, conversation steering.
- **Mechanism:** read-only review → `/codex:review --background` or `/codex:adversarial-review
  --background`. Write-capable rescue → `Agent(subagent_type: "codex:codex-rescue", prompt: "...")`
  with `run_in_background=true` on the Agent itself — never pass `--background` inside the prompt and
  never pair it with `isolation: "worktree"` (both kill Codex early).
- **Brief it cold.** Paths, line numbers, success criteria. For read-only work say "review only, do
  not edit" explicitly (it defaults to `--write`). Never ask a read-only job to run tests or `uv` —
  its sandbox denies all writes and the job thrashes on `Operation not permitted`.
- **Observability:** `status: running` ≠ progress — check `/codex:status <id>`. Frozen
  `progressPreview` ~5 min AND elapsed > 10 min → dead: `/codex:cancel <id>`, `codex-hygiene`, retry.
  ALWAYS auto-poll jobs expected to run >5 min with `/loop 90s /codex:status <id>`.
  ⚠️ Do NOT run `/codex:setup --enable-review-gate`.
- **Adversarial review** (the Codex half of "Quality gate is built-in"): brief it read-only with the
  diff/plan + one angle from: auth bypass · data loss · rollback safety · race conditions ·
  degraded dependencies · version skew · observability gaps.

### Multi-Agent Model Economics 🔴

Claude-native workers **inherit the session model unless routed down**. Worker-tier choice drives
~5× more total cost than orchestrator-tier choice — the leverage is cheap workers.

| Role | Model |
| --- | --- |
| Orchestrate / plan / synthesis | session model (escalate to `fable` only for hard, long-horizon async fan-out — never as baseline, never in `settings.json`) |
| Implement | Codex |
| Read / scan / search / explore | `haiku` |
| Review / verify / test | `sonnet` |

- **Pin every workflow stage's `model`.** A workflow's `agent()` calls inherit the session model; an
  un-routed workflow bills every agent (up to 1000) at the session tier — the #1 cost blowout. Use
  `opts.effort: 'low'` for mechanical stages when the in-session Workflow tool exposes it.
- **`Workflow({name: ...})` is banned** (a PreToolUse hook denies it) — even when a skill's
  instructions say to invoke by name; that is not an exemption. Use the routed copy in
  `~/.claude/workflows/` via `scriptPath`.
- **Never** set `settings.json "model": "fable"` or a global `CLAUDE_CODE_SUBAGENT_MODEL` — both
  defeat per-role routing. Multi-agent is not inherently cheaper; savings come only from routing
  cheap roles to cheap models.

---

## Part 4: LLM & Prompt Engineering 🔴

**Backend supplies facts. Context supplies structure. LLM supplies judgment.** Don't let code do the
LLM's job (ranking, intent matching, fact-checking); don't let the LLM do code's job (data integrity,
deterministic computation).

Before writing or reviewing any prompt or agent pipeline, read
`~/.claude/references/prompt-engineering.md` — it holds the seven prompt rules, the anti-pattern
table, the agent-pipeline design rules, and the review checklist.
