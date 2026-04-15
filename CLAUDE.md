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

**Scope Discipline (multi-agent safety):** 🔴

- ❌ Reverting, modifying, or deleting code outside your current task scope
- ❌ "Cleaning up" or "fixing" unrelated code you encounter
- ❌ Undoing changes by other agents/sessions without explicit user request
- ❌ Running `git checkout`/`git restore`/`git reset` on files you didn't modify
- ✅ Only touch files and code directly required by your current task
- ✅ If you notice issues in unrelated code, report them — do NOT fix silently

### 🔴 Mandatory Practices

- ✅ Run `uv run ruff check .` before any commit
- ✅ Use Query Key Factories for TanStack Query (see `hooks/factories/`)
- ✅ Enable React Compiler + `eslint-plugin-react-compiler` in all frontend projects
- ✅ Define explicit TypeScript interfaces for component props
- ✅ Use `redirect_slashes=False` in FastAPI app configuration

### 🔴 Single Elegant Version Principle

> **One version. Always current. No legacy. No compromises.**

Every file, function, and variable represents the single, latest, elegant solution. Never create "improved" versions alongside originals—replace them entirely.

- **One-Shot Excellence** — Write the elegant solution now, not "fix it later"
- **No Development-Stage Adjectives** — ❌ `enhanced_parser.py`, `UserServiceV2` → ✅ `parser.py`, `UserService`
- **Business Adjectives OK** — `PremiumPlan`, `AdvancedAnalytics` are fine
- **No Backward Compatibility Hacks** — Delete completely, don't deprecate. No `_old_var`, no re-exports
- **No Over-Defensive Coding** — Validate at boundaries, trust internal code
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

---

## Part 3: Architecture & Design Patterns

### 4-Layer Architecture 🔴

```
API (src/api/v1/endpoints/) → Service (src/services/) → Repository (src/repositories/) → Supabase
```

- **API**: HTTP handling, validation, auth. Uses `Depends(get_service)`.
- **Service**: Business logic. NO direct DB calls. Raise domain exceptions (no HTTP knowledge).
- **Repository**: Inherits `SupabaseRepository`. NO business logic.

### Naming Rules 🟡

- **File name = Primary export name** — no mismatches
- **Class naming:** Handler (stateful workflow), Processor (stateless transform), Service (business logic)

---

## Part 4: Backend Development

### Key Backend Rules 🔴

- **Async discipline:** `async def` must await ALL I/O. Blocking calls freeze the event loop.
- **Pydantic V2 only:** `@field_validator`, `model_config = ConfigDict(...)`, `.model_dump()` — never V1 syntax
- **DI:** Use `Annotated` type aliases for `Depends()`. Use `pydantic-settings` + `@lru_cache` — never `os.getenv()`
- **Repository:** Inherit `SupabaseRepository`, call `super().__init__(table_name=..., model_class=...)`. Use `_handle_supabase_result()` for queries, `_build_model()` for single results — never `result.data[0]`
- **Supabase RLS:** Use `(select auth.uid())` subquery (cached, 30-70% faster). Functions: `SECURITY DEFINER` + `SET search_path = 'public'`
- **Supabase RPC:** Scalar returns (`RETURNS UUID`): `result.data` is direct value, NOT a list. Table returns (`RETURNS SETOF`): use `_handle_supabase_result()`
- **Error handling:** Domain exceptions in service layer → global handler converts to HTTP responses

### API Conventions 🟡

- **Use snake_case for all API fields** (backend Pydantic + frontend TypeScript)
- **Define root routes as `@router.get("")`** not `@router.get("/")`
- **Include CORS origins for exact frontend domains**

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

> **Project-specific patterns:** `~/.claude/rules/frontend.md`

### Core Principles 🔴

- **Hyper-Minimalist UI** — Less, but better. Every element must earn its place.
- **Use Project Systems First** — Discover before creating. Search `components/`, `hooks/`, `lib/` first.
- **State Hierarchy** — URL State > Server State (TanStack Query) > Local State > Global State (Zustand)

---
## Optional Graphify

- If `~/.claude/skills/graphify/SKILL.md` exists, treat `/graphify` as a first-class workflow for graph-backed repo exploration.
- When a repository already has a graphify graph, prefer the nearest active surface graph over the repo-root graph.
- Start with `graphify-out/GRAPH_REPORT.md`. If `graphify-out/wiki/index.md` exists, navigate the wiki before reading raw files.
- Use graph queries or explanations for relationship questions. Do not paste the full `graph.json` into context.
- Optional user-level hooks may refresh graphs after `Write|Edit|MultiEdit`. If hooks are unavailable, run `/graphify <path> --update` manually when freshness matters.
