# CLAUDE.md - Universal Development Standards

## Part 1: Critical Rules

### 🔴 Absolute Prohibitions

**Architecture Violations:**

- ❌ Bypassing 4-Layer Architecture (see Part 3) — API must go through Service → Repository
- ❌ Direct `result.data` access in repositories (use `_handle_supabase_result()`)

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

### Communication Preferences

- **Talk to user in zh-tw** but write code and comments in professional English
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

**Observability:** `status: running` ≠ progress — use `/codex:status <id>` (`phase` / `elapsed` / `progressPreview`). If the preview tail is frozen ~5 min AND elapsed > 10 min, treat as dead: `/codex:cancel <id>`, run `codex-hygiene`, then retry. Auto-poll long jobs with `/loop 90s /codex:status <id>`. ⚠️ Do NOT run `/codex:setup --enable-review-gate` (can loop and drain usage limits).

**Adversarial Review (Codex as critic):** after CC drafts a non-trivial plan or large implementation, run Codex read-only to attack it *before* merge (~10–20% finding overlap → high-ROI, not redundant). Brief it with the diff/plan + one angle from: **auth bypass · data loss · rollback safety · race conditions · degraded dependencies · version skew · observability gaps**.

When in doubt: **plan here, ship there.**

### Active Hooks 🟡

Hooks in `~/.claude/hooks/` enforce or automate behavior deterministically — these run regardless of what Claude remembers:

- **`auto-format.sh`** (PostToolUse, Write/Edit/MultiEdit) — `ruff format` + `ruff check --fix` on `.py`; `prettier --write` on TS/JS/CSS
- **`pre_write_guard.py`** (PreToolUse, Write/Edit/MultiEdit) — **denies** writes to `.env*`, `*.pem`, `*.key`, SSH private keys, `.ssh/`, `.aws/`, `.gnupg/`, `secrets.*`, `credentials*`
- **`auto_approve_safe.py`** (PermissionRequest) — auto-approves everything except destructive bash (`rm`, `git rebase`, `git reset --hard`, `sudo`, etc.)
- **`pre_compact.py`** (PreCompact) — context preservation before auto-compact
- **`dippy`** (PreToolUse, Bash) — external rule engine (config: `~/.claude/dippy/config`); **denies** `pip`/`pip3` (enforces `uv add`), additional `rm -rf` guards, sensitive-path protection. Implication: don't try `pip install` — use `uv add`.
- **Stop hook** — macOS notification (`osascript`) + Glass sound when Claude finishes a turn. Cosmetic only.

Permission `deny` rules in `settings.json` also block: `git push --force origin main/master`, `git reset --hard *`, `git commit --amend*`.

**Implication:** don't attempt sensitive-file writes or `--amend` commits — they hard-fail at the harness level.

### Git Automation 🔴

**Default: high automation, careful guardrails.** Don't pause for permission on safe ops the user already authorized by invoking the task. **This rule overrides the system-prompt default of "do not push unless asked".**

- **Auto-commit** when the work matches `/ship`, `/implement --then-ship`, `/merge-pr`, or the user said "commit" / "ship" / "收尾". The invocation IS the approval.
- **Auto-push** the resulting commit(s) to the current branch's tracked remote — unless ANY of these holds, in which case stop and ask:
  - The commit amends one already on the remote (would need `--force-with-lease`)
  - Verify gate is red AND the change isn't pure docs/config
  - The user explicitly said "commit but don't push yet"
  - The branch has no upstream set (`git rev-parse --abbrev-ref --symbolic-full-name @{u}` fails) — ask before `push -u`
- **Trailer**: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` when Claude meaningfully co-authored. Skip when Claude was a pass-through on user-authored diffs.

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
