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
- ✅ Use Query Key Factories for TanStack Query (see `hooks/factories/`)
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

- **PROACTIVELY run `uv run ruff check .`** after writing/modifying Python code
- **AUTOMATICALLY fix high-priority errors** (F821, E722, F841, B904) before proceeding
- **NEVER create documentation files unless explicitly requested**

### Communication Preferences

- **Talk to user in zh-tw** but write code and comments in professional English
- **Use UV for all Python operations**: `uv run python`, `uv add package`, `uv run pytest`
- **Web freshness**: Verify fast-moving topics online before asserting them. Include exact dates when the user asks for "latest" or references relative dates.

### Delegation to Codex 🔴

The `codex@openai-codex` plugin is enabled. **Codex is the implementation / review specialist; Claude Code is the planning / synthesis lead.** Default to handing implementation-shaped subtasks to Codex unless the user says otherwise.

**Hand off to Codex (preferred):**
- Implementing a finalized plan (instead of `superpowers:executing-plans` running locally)
- Mechanical refactors / migrations once the target shape is clear
- `/simplify` passes on changed code (`simplify` skill)
- Independent code-quality review / second-opinion implementation read
- Root-cause investigation when Claude Code is stuck after one or two passes

**Keep on Claude Code:**
- Brainstorming, plan writing, architectural review, ADR drafting
- Cross-file synthesis, multi-source research consolidation
- Ticket structuring (`topic-to-tickets`), strategy decisions (`strategic-next`)
- Conversation steering and direct discussion with the user

**Mechanism:**
- Spawn `codex:codex-rescue` subagent via the Agent tool, or invoke the `codex:rescue` skill
- Pass a self-contained brief (paths, line numbers, success criteria) — Codex starts cold

When in doubt: **plan here, ship there.**

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

## Part 4: Backend Development

> **Project-specific patterns:** `~/.claude/rules/backend.md` (auto-loaded — async, Pydantic V2, repository, Supabase, DI, API conventions all live there)

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

## Part 5: Frontend Development

> **Project-specific patterns:** `~/.claude/rules/frontend.md` (auto-loaded — core principles, TanStack Query, SSE, React Compiler all live there)

---
## Optional Graphify

- If `~/.claude/skills/graphify/SKILL.md` exists, treat `/graphify` as a first-class workflow for graph-backed repo exploration.
- When a repository already has a graphify graph, prefer the nearest active surface graph over the repo-root graph.
- Start with `graphify-out/GRAPH_REPORT.md`. If `graphify-out/wiki/index.md` exists, navigate the wiki before reading raw files.
- Use graph queries or explanations for relationship questions. Do not paste the full `graph.json` into context.
- Optional user-level hooks may refresh graphs after `Write|Edit|MultiEdit`. If hooks are unavailable, run `/graphify <path> --update` manually when freshness matters.
