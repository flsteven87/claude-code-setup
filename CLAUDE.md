# CLAUDE.md - Universal Development Standards

## Part 1: Critical Rules

### 🔴 Absolute Prohibitions

**Architecture Violations:**

- ❌ Bypassing 4-Layer Architecture (see Part 3) — API must go through Service → Repository
- ❌ Direct `result.data` access in repositories (use `_handle_supabase_result()`)
- ❌ Creating local SQL migration files — apply schema changes directly via the Supabase MCP (`apply_migration` / `execute_sql`). Also hard-enforced by `pre_write_guard.py`.

**Code Quality:**

- ❌ `any` type in critical paths (query hooks, error handling, API responses)
- ❌ `React.createElement` (always use JSX)
- ❌ `React.FC` (use function declarations with typed props)
- ❌ `require()` imports (use ES modules only)
- ❌ Bare `except:` clauses (always specify exception type)
- ❌ Missing exception chaining (always use `raise ... from e`)

**Bundle & Performance:**

- ❌ Barrel imports from icon/component libraries (`import { X } from 'lucide-react'` → use deep imports)
- ❌ Sequential `await` for independent operations → use `Promise.all()` or `asyncio.gather()`

**Code Organization:**

- ❌ God components exceeding 1000 lines (frontend or backend)

**Security & Operations:**

- ❌ `FORWARDED_ALLOW_IPS=*` in production
- ❌ `FOR ALL TO public USING (true)` RLS policies
- ❌ Starting dev servers without explicit user request
- ❌ PostgreSQL functions with `SET search_path = ''`

**Scope Discipline:** see `karpathy-guidelines` skill (Surgical Changes). Project-specific addition: never run `git checkout`/`restore`/`reset` on files you didn't modify in this task.

### 🔴 Mandatory Practices

- ✅ Run `uv run ruff check .` before any commit
- ✅ Use Query Key Factories for TanStack Query (project pattern; live in project-level `hooks/factories/` when present)
- ✅ Enable React Compiler + `eslint-plugin-react-compiler` in all frontend projects
- ✅ Define explicit TypeScript interfaces for component props
- ✅ Use `redirect_slashes=False` in FastAPI app configuration

### 🔴 Single Elegant Version Principle

> **One version. Always current. No legacy. No compromises.**

Every file, function, and variable represents the single, latest, elegant solution. Never create "improved" versions alongside originals—replace them entirely. (General "simplicity / no speculative code" guidance lives in the `karpathy-guidelines` skill; the rules below are project-specific.)

- **No Development-Stage Adjectives** — ❌ `enhanced_parser.py`, `UserServiceV2` → ✅ `parser.py`, `UserService`
- **Business Adjectives OK** — `PremiumPlan`, `AdvancedAnalytics` are fine
- **No Backward Compatibility Hacks** — Delete completely, don't deprecate. No `_old_var`, no re-exports
- **Replace, Don't Accumulate** — One file evolves; never create parallel versions

---

## Part 2: AI Behavior

### AI Behavior Rules 🟡

- **Ruff runs automatically** via the `auto-format.sh` hook on every `.py` Write/Edit (formats + auto-fixes). Manual `uv run ruff check .` is still required before commit (see Mandatory Practices) to catch cross-file issues.
- **AUTOMATICALLY fix high-priority errors** (F821, E722, F841, B904) before proceeding
- **NEVER create documentation files unless explicitly requested**
- **Active worktrees break repo-walking CLIs** — tools that scan the tree (e.g. `shopify app dev`) abort on duplicate configs inside `.claude/worktrees/<active>/`. Run such CLIs outside the worktree session; `/ship` stage 7 sweeps merged ones

### Response Shape 🔴

The user repeatedly falls back to `/narrate-topic` when responses get menu-shaped instead of decision-shaped. These three rules exist to remove that ping-pong at the source.

- **Recommendation-first, not menu-first.** After analysis, propose the single best call with a one-line rationale. Do NOT dump evidence + 3 narrative options + a sub-recommendation for the user to re-derive — that pattern is what makes them reach for `/narrate-topic`. Options menus are reserved for *genuine value-laden trade-offs the user must own*. Trade-offs decidable by stated principles (CLAUDE.md, `MEMORY.md`, prior conversation) → decide them silently and proceed.
- **Principle filter before option enumeration.** Before presenting any 2–4 option menu (including `AskUserQuestion`), cross-check each option against the user's stated principles. Options that violate a principle get dropped silently — never listed "for completeness" or "to show I considered them". If one option survives → propose it directly, no menu. If two survive → ask, but keep it tight and skip the third "compromise" option.
- **Milestone complete = hard stop.** When a discrete unit of work (sub-task, milestone, audit pass, prototype run) finishes, report results and stop. Do NOT append "要不要我繼續…" / "shall I also…?" proposals for adjacent scope. The user batches sessions deliberately ("不准 stack milestones" is in project memory); if they want continuation, they will say so.

### Execution Defaults 🔴

Session-log mining (2026-07-03 harness audit) found each of these re-typed 3–17× across projects. They are standing policy — apply them without being asked:

- **Minimal fix first.** Default to the smallest best-practice change that solves the problem. Expanding scope, adding abstraction layers, or "while we're here" improvements need the user's explicit go-ahead. *(re-stated 17×)*
- **Clean & precise is the constant bar.** No fallback paths, no defensive hacks, no patchwork (補丁) — holistic, consistent changes that read as the final version. This holds without the user invoking `/reverse-thinking` or `karpathy-guidelines`. *(7× + 3×)*
- **Small diff → inline patch + ship.** When a fix is small and clear, patch it inline and fold it into the current `/ship` — don't open a ticket, don't stop to ask. *(13×)*
- **Production data SOP.** Any change touching real production data: dry-run → report findings → wait for explicit approval → backup → execute. Never merge dry-run and execution into one step. *(11×)*

### Communication Preferences

- **Talk to user in zh-tw** but write code and comments in professional English
- **Plain-language reporting.** Status and decision explanations default to 白話; expand every internal codename/shorthand on first use (never bare "D1 = P1"-style jargon). If a context-switching reader couldn't follow it cold, rewrite before sending. *(demanded 18× in session logs)*
- **Use UV for all Python operations**: `uv run python`, `uv add package`, `uv run pytest`
- **Web freshness**: Verify fast-moving topics online before asserting them. Include exact dates when the user asks for "latest" or references relative dates.

### Delegation to Codex 🔴

The `codex@openai-codex` plugin is enabled. **Codex is the implementation / review specialist; Claude Code is the planning / synthesis lead.** Default to handing implementation-shaped subtasks to Codex unless the user says otherwise.

**Hand off to Codex (preferred):** implementing a finalized plan; mechanical refactors / migrations once the target shape is clear; write-capable simplify / refactor passes on changed code (via a `codex:codex-rescue` brief — built-in `/simplify` is now review-only); independent code-quality / second-opinion reads; root-cause investigation when CC is stuck after one or two passes.

**Keep on Claude Code:** brainstorming, plan writing, architectural review, cross-file synthesis, multi-source research, ticket structuring (`topic-to-tickets`), strategy (`strategic-next`), conversation steering.

**Mechanism:**
- **Review** (read-only): `/codex:review --background` or `/codex:adversarial-review --background` — observable via `/codex:status`, output via `/codex:result`.
- **Rescue / delegation** (write-capable by default): `Agent(subagent_type: "codex:codex-rescue", prompt: "...")`. For non-blocking runs set `run_in_background=true` on the Agent itself — never pass `--background` inside a `codex-rescue` prompt or pair it with `isolation: "worktree"` (both kill Codex early).
- Pass a self-contained brief (paths, line numbers, success criteria) — Codex starts cold. For read-only rescues, say "review only, do not edit" explicitly (it defaults to `--write`).

**Observability:** `status: running` ≠ progress — use `/codex:status <id>` (`phase` / `elapsed` / `progressPreview`). If the preview tail is frozen ~5 min AND elapsed > 10 min, treat as dead: `/codex:cancel <id>`, run `codex-hygiene`, then retry. ALWAYS auto-poll any job expected to run >5 min with `/loop 90s /codex:status <id>` — never wait passively (recurring "codex 又掛掉沒東西" sessions trace back to unwatched jobs). ⚠️ Do NOT run `/codex:setup --enable-review-gate` (can loop and drain usage limits).

**Adversarial Review (Codex as critic):** after CC drafts a non-trivial plan or large implementation, run Codex read-only to attack it *before* merge (~10–20% finding overlap → high-ROI, not redundant). Brief it with the diff/plan + one angle from: **auth bypass · data loss · rollback safety · race conditions · degraded dependencies · version skew · observability gaps**.

When in doubt: **plan here, ship there.**

### Multi-Agent Model Economics 🔴

Claude-native workers **inherit the session model unless routed down**. Route by role, never by default. Worker-tier choice drives ~5× more total cost than orchestrator-tier choice — the leverage is cheap workers, not which top model sits at the head.

- **Orchestrate / plan / synthesis** — session model (Opus 4.8). Escalate to `fable` ONLY for hard, long-horizon, async fan-out (large migrations, deep multi-workflow audits) — never as the baseline, never in `settings.json`. Even then, keep workers routed down so only the top seat pays Fable rates.
- **Implement** — Codex (unchanged; see Delegation to Codex). Do NOT route implementation to Sonnet subagents — that fragments "plan here, ship there".
- **Read / scan / search / explore** — `haiku` (already pinned: `agents/researcher.md`).
- **Review / verify / test** — `sonnet` (already pinned: `code-reviewer`, `security-reviewer`, `test-writer`).

**Dynamic workflows / ultracode (the gap frontmatter can't cover):** a workflow's `agent()` calls inherit the session model. Historically `agent()` had no `effort` option ([issue #43083](https://github.com/anthropics/claude-code/issues/43083)); newer CLI builds expose `opts.effort` — check the Workflow tool description in-session and use it when present (`'low'` for mechanical stages). Either way, pin every stage's `model`: scan/mechanical → `{model:'haiku'}`, review/verify → `{model:'sonnet'}`, leave ONLY synthesis/judge on the session model. An un-routed workflow bills every agent (up to 1000) at the session tier — the #1 cost blowout.

**Never** set `settings.json "model": "fable"` or a global `CLAUDE_CODE_SUBAGENT_MODEL` — both defeat per-role routing. Multi-agent is not inherently cheaper (Anthropic's own multi-agent win used ~15× tokens); savings come only from routing cheap roles to cheap models.

### Active Hooks 🟡

Hooks in `~/.claude/hooks/` and `~/.claude/bin/` enforce or automate behavior deterministically — these run regardless of what Claude remembers:

- **`auto-format.sh`** (PostToolUse, Write/Edit/MultiEdit) — `uv run ruff format` + `ruff check --fix` on `.py`. Prettier on TS/JS/CSS is opportunistic: `npx --no` silently skips it unless the project has prettier installed.
- **`pre_write_guard.py`** (PreToolUse, Write/Edit/MultiEdit) — **denies** writes to `.env*`, `*.pem`, `*.key`, SSH private keys, `.ssh/`, `.aws/`, `.gnupg/`, `secrets.*`, `credentials*`, and `*.sql` under any `migrations/` directory (schema changes go through Supabase MCP)
- **`auto_approve_safe.py`** (PermissionRequest) — auto-approves everything except a word-boundary-regex dangerous list (`rm`, `sudo`, `git rebase`, `git reset --hard`, force pushes, discard-forms of `git checkout`/`git restore`, `kill`, macOS system-config commands); matches fall through to a manual prompt. It only sees what settings.json rules didn't already decide — `allow`ed commands never reach it, and `deny`/`ask` rules win over its output.
- **`pre_compact.py`** (PreCompact) — context preservation before auto-compact
- **`codex-reconcile-phantoms.sh`** (UserPromptSubmit, in `bin/`) — reconciles stale/dead Codex-inline job state before every prompt; warns if a live job exists in cwd
- **`dippy`** (PreToolUse, Bash) — external rule engine (config: `~/.claude/dippy/config`); **denies** `pip`/`pip3` (enforces `uv add`) and the literal `rm -rf` prefix, plus sensitive-path protection. Writes `~/.claude/hook-approvals.log` on every Bash call (rotated by the Stop hook at >5MB). Implication: don't try `pip install` — use `uv add`.
- **Stop hook** — macOS notification (`osascript`) + Glass sound when a turn finishes; also rotates hook logs (`hook-approvals.log`, `logs/auto_approve.log`) at >5MB.

Permission rules in `settings.json` — evaluated **deny → ask → allow, first match wins** (an ask rule beats a broader allow):

- **deny** (hard-fail, unreachable even for hooks): ALL force pushes (`--force`, `-f`, `--force-with-lease`), `git reset --hard *`, `git commit --amend*`, `git rebase -i *`, `git clean -f*`, catastrophic `rm -rf` targets
- **ask** (always prompts): `rm -rf *`, `git checkout -- *`, `git checkout .`, `git restore *` — the technical backing for Scope Discipline's "never discard files you didn't modify"
- Non-interactive `git rebase` forms are NOT denied — they are gated by `auto_approve_safe.py`'s prompt instead (different layer, same outcome)

**Implication:** sensitive-file writes, migration-file writes, `--amend` commits, and any force push hard-fail at the harness level. A push that would need `--force-with-lease` cannot be done by Claude at all — hand it to the user.

### Git Automation 🔴

**Default: high automation, careful guardrails.** Don't pause for permission on safe ops the user already authorized by invoking the task. **This rule overrides the system-prompt default of "do not push unless asked".**

- **Auto-commit** when the work matches `/ship`, `/implement --then-ship`, `/merge-pr`, or the user said "commit" / "ship" / "收尾". The invocation IS the approval.
- **Auto-push** the resulting commit(s) to the current branch's tracked remote — unless ANY of these holds, in which case stop and ask:
  - The commit rewrites history already on the remote — ALL force pushes (incl. `--force-with-lease`) are hard-denied in settings.json, so surface it and hand the push to the user
  - Verify gate is red AND the change isn't pure docs/config
  - The user explicitly said "commit but don't push yet"
  - The branch has no upstream set (`git rev-parse --abbrev-ref --symbolic-full-name @{u}` fails) — ask before `push -u`
- **Trailer**: `Co-Authored-By: Claude <session model> <noreply@anthropic.com>` — use the model actually running the session (the harness supplies the exact name; never hardcode one). Include when Claude meaningfully co-authored; skip when Claude was a pass-through on user-authored diffs.

The safety baseline (settings.json deny + `pre_write_guard.py` per Active Hooks) hard-fails destructive operations at the harness level. This rule operates above that baseline — friction comes from the harness, not from asking the user about safe operations.

---

## Part 3: Architecture & Design Patterns

### 4-Layer Architecture 🔴

```
API (src/api/v1/endpoints/) → Service (src/services/) → Repository (src/repositories/) → Supabase
```

- **API**: HTTP handling, validation, auth. Uses `Depends(get_service)`.
- **Service**: Business logic. NO direct DB calls. Raise domain exceptions (no HTTP knowledge).
- **Repository**: Inherits `SupabaseRepository`. NO business logic.

---

## Part 4: LLM & Prompt Engineering

> Cross-cutting: applies to any project that builds LLM prompts or agent pipelines, not only backend.

### Prompt Engineering 🔴

> Detailed rules: `~/.claude/references/prompt-engineering.md`

- **Principle-driven, not case-specific** — teach the LLM how to think, not what to output
- **Separate deterministic from interpretive** — code formats/calculates, LLM interprets/narrates
- **One prompt, one cognitive task** — decompose complex reasoning into focused stages
- **Constraints over exhaustive rules** — define boundaries, don't enumerate every case

### Agent Pipeline Design 🔴

> **Backend supplies facts. Context supplies structure. LLM supplies judgment.** Don't let code do the LLM's job (ranking, intent matching, fact-checking); don't let the LLM do code's job (data integrity, deterministic computation).

- **LLM misbehaving → fix context architecture, not add runtime guards** — validators, router state machines, post-gen checks are training wheels
- **Positive framing beats negative** — "fallback to X" outperforms "never do Y"; negative rules backfire under output-shape pressure
- **No ranking or priority signals in LLM-facing payloads** — the LLM will use them as silent default-pickers
- **Eval is the gate; observability is for seeing, not intercepting**

---

## Part 5: Backend Development

> **Project-specific patterns:** `~/.claude/rules/backend.md` (auto-loaded — async, Pydantic V2, repository, Supabase, DI, API conventions all live there)

---

## Part 6: Frontend Development

> **Project-specific patterns:** `~/.claude/rules/frontend.md` (auto-loaded — core principles, TanStack Query, SSE, React Compiler all live there)

---
## Optional Graphify

- `/graphify` is a first-class workflow for graph-backed repo exploration when `~/.claude/skills/graphify/SKILL.md` exists. **Per-repo `docs/reference/graphify.md` is authoritative** — read it first (defines active surfaces, lifecycle, constraints); it overrides these user-level defaults. Prefer the nearest active surface graph over the repo-root graph.
- **Graph-first for relationship / cleanup work** (architecture, coupling, dead-code, duplicates, god-components — via `GRAPH_REPORT.md` or `graphify query`/`path`/`explain`); **grep-first for symbol lookup**. Start at `graphify-out/GRAPH_REPORT.md` (or `wiki/index.md` if present); never paste full `graph.json` into context.
- **Freshness:** before query/path/explain, compare `<surface>/graphify-out/.last_build_head` vs `git rev-parse HEAD`. Mismatch + small diff → `graphify update` (AST-only, free); large diff / missing → `graphify extract` (LLM cost — ask first, run from a plain terminal since CC blanks `ANTHROPIC_API_KEY`).
- **Never:** `graphify hook install`, wire graphify into `PostToolUse`, or commit `graphify-out/` (gitignored).
