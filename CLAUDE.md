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

**Hand off to Codex (preferred):**
- Implementing a finalized plan (instead of `superpowers:executing-plans` running locally)
- Mechanical refactors / migrations once the target shape is clear
- Write-capable simplify / refactor passes on changed code (via a `codex:codex-rescue` brief — Claude Code's built-in `/simplify` was renamed to `/code-review` and made review-only in 2.1.147, so this is the path that still mutates code)
- Independent code-quality review / second-opinion implementation read
- Root-cause investigation when Claude Code is stuck after one or two passes

**Keep on Claude Code:**
- Brainstorming, plan writing, architectural review, ADR drafting
- Cross-file synthesis, multi-source research consolidation
- Ticket structuring (`topic-to-tickets`), strategy decisions (`strategic-next`)
- Conversation steering and direct discussion with the user

**Mechanism:**
- **Review** (read-only, no edits): `/codex:review --background` or `/codex:adversarial-review --background` — README-blessed pattern. Runs in main-session background, observable via `/codex:status`, final output via `/codex:result`.
- **Rescue / delegation** (write-capable by default): `Agent(subagent_type: "codex:codex-rescue", prompt: "...")`. The subagent runs Codex with `--wait` internally and returns Codex's output verbatim. Add `run_in_background=true` on the Agent call itself when you want non-blocking execution with harness notification on completion.
- Pass a self-contained brief (paths, line numbers, success criteria) — Codex starts cold.
- For read-only rescues, frame the brief explicitly as "review only, do not edit" — `codex:codex-rescue` defaults to `--write` otherwise.
- ⚠️ **Pattern traps** (will silently break):
  - `Agent(subagent_type: "codex:codex-rescue", prompt: "--background ...")` — SessionEnd hook kills Codex when the subagent exits ([#345](https://github.com/openai/codex-plugin-cc/issues/345)). Use `run_in_background=true` on the Agent itself instead.
  - `Agent(isolation: "worktree", prompt: "... --background")` — worktree is cleaned before Codex finishes ([#198](https://github.com/openai/codex-plugin-cc/issues/198)).
  - `/codex:rescue --background` — routes through the same buggy subagent path as #345.

**Observability (long runs are fine; silently-stuck runs are not):**
- `"status: running"` does NOT prove progress. Use `/codex:status <job-id>` to see `phase`, `elapsed`, and `progressPreview` (tail of recent activity).
- **Stuck heuristic** ([#49](https://github.com/openai/codex-plugin-cc/issues/49), [#164](https://github.com/openai/codex-plugin-cc/issues/164), [#277](https://github.com/openai/codex-plugin-cc/issues/277)): if `progressPreview` tail hasn't advanced in ~5 min AND elapsed > 10 min, treat as silently dead — `/codex:cancel <id>`, then run `codex-hygiene` (kills orphan codex / companion processes + clears stale `jobs/*` state) before retrying. Job-state file doesn't transition on process death. Pipe/handle contamination also accumulates within one CC process → restart CC (not `/clear`) before a planned series of background Codex jobs.
- For long jobs, auto-poll with `/loop 90s /codex:status <id>` while doing other work.
- `/codex:result <id>` returns the stored final payload for completed / failed / cancelled jobs.
- ⚠️ **Do NOT** run `/codex:setup --enable-review-gate` — official warning: can create Claude/Codex loops and drain usage limits quickly. Only enable when you plan to actively monitor.

**Adversarial Review (Codex as critic):**
- After CC drafts a non-trivial plan or substantial implementation, run Codex in read-only review mode to attack the work *before* merge. Their findings have low overlap (~10–20%) with CC's, so this is high-ROI rather than redundant.
- Especially valuable for: security-sensitive changes, architectural plans before execution, large refactors, anything touching auth / RLS / data integrity.
- Brief Codex with the diff or plan + an angle. Don't ask for "general review" — pick from the seven attack surfaces: **auth bypass · data loss · rollback safety · race conditions · degraded dependencies · version skew · observability gaps**.

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
- **Trailer**: `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>` when Claude meaningfully co-authored. Skip when Claude was a pass-through on user-authored diffs.

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

- If `~/.claude/skills/graphify/SKILL.md` exists, treat `/graphify` as a first-class workflow for graph-backed repo exploration.
- **Per-repo policy overrides user-level defaults.** When a repo has `docs/reference/graphify.md`, read that first — it defines the active surfaces, lifecycle (Agent-Local Lazy vs other), and any repo-specific constraints. Repos without it fall back to the defaults below.
- When a repository already has a graphify graph, prefer the nearest active surface graph over the repo-root graph.
- Start with `graphify-out/GRAPH_REPORT.md`. If `graphify-out/wiki/index.md` exists, navigate the wiki before reading raw files.
- **Graph-first for relationship / cleanup work; grep-first for symbol lookup.** Use graph (`GRAPH_REPORT.md` sections: God Nodes / Surprising Connections / Hyperedges / Community fan-in; or `graphify query`/`path`/`explain`) for architecture, coupling, dead-code, duplicate-detection, or god-component questions. Use grep / IDE for "where is `foo` defined" or exact string search. Never paste full `graph.json` into context.
- **Freshness gate (Agent-Local Lazy).** Before `graphify query` / `path` / `explain`, compare `<surface>/graphify-out/.last_build_head` with `git rev-parse HEAD`. Match → use directly. Mismatch + small diff → run `graphify update <path>` (free, AST-only); prefer the repo wrapper if present (`./scripts/graphify.sh update <surface>`). Mismatch + large diff or missing graph → `graphify extract <path>` (LLM cost; ask before running). **Note:** `extract` needs an LLM API key in env, but Claude Code intentionally blanks `ANTHROPIC_API_KEY` to avoid double-billing — `extract` must be run from a plain terminal, not from inside Claude Code. `update` (AST-only) works fine from anywhere.
- **Anti-patterns (never do).** Never `graphify hook install` (git hooks), never wire graphify into Claude `PostToolUse` (caused CPU saturation in production), never commit `graphify-out/` (always L3 / gitignored). These are explicit bans in repo policy docs.
