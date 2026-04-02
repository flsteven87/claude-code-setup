# CLAUDE.md - Universal Development Standards

## Part 1: Critical Rules

> **Read this section first.** These rules have zero tolerance for violations.

### Priority System

- 🔴 **CRITICAL**: Security issues, data corruption, architectural violations - ZERO TOLERANCE
- 🟡 **IMPORTANT**: Code quality, maintainability - MUST FIX
- 🟢 **RECOMMENDED**: Developer experience - SHOULD FOLLOW

### 🔴 Absolute Prohibitions

**Architecture Violations:**

- ❌ API layer calling database directly (must go through Service → Repository)
- ❌ Business logic in Repository layer (belongs in Service layer)
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
- ✅ Use `raise HTTPException(...) from e` for exception chaining
- ✅ Inherit from `SupabaseRepository` base class for all repositories
- ✅ Use Query Key Factories for TanStack Query
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
API Layer (FastAPI) → Service Layer (Business Logic) → Repository Layer (Data Access) → Database
```

- **API** (`src/api/v1/endpoints/`): HTTP handling, validation, auth, uses `Depends(get_service)`
- **Service** (`src/services/`): Business logic, orchestration, NO direct DB calls
- **Repository** (`src/repositories/`): Database queries, inherits `SupabaseRepository`
- **Database**: Supabase/PostgreSQL

### Design Patterns 🟡

- **Strategy Pattern** — Runtime-selectable algorithms via ABC. Use when multiple implementations needed.
- **Aggregate Root** — Manage dependent entities through parent repository (e.g., `OrderRepository` manages orders AND items)

### Naming Rules 🟡

> Detailed tables: `~/.claude/rules/naming-conventions.md`

- **File name = Primary export name** — no mismatches
- **Class naming:** Handler (stateful workflow), Processor (stateless transform), Service (business logic)
- **Frontend events:** Props `onSubmit`/`onClick`, Handlers `handleSubmit`/`handleClick`

---

## Part 4: Backend Development

> **Detailed backend patterns:** `~/.claude/rules/backend.md`

### Key Backend Rules 🔴

- **Async discipline:** `async def` must await ALL I/O. Blocking calls freeze the event loop.
- **Pydantic V2 only:** `@field_validator`, `model_config = ConfigDict(...)`, `.model_dump()` — never V1 syntax
- **DI:** Use `Annotated` type aliases for `Depends()`. Use `pydantic-settings` + `@lru_cache` — never `os.getenv()`
- **Repository:** Inherit `SupabaseRepository`, use `_handle_supabase_result()` — never `result.data[0]`
- **Supabase RLS:** Use `(select auth.uid())` subquery (cached, 30-70% faster). Functions: `SECURITY DEFINER` + `SET search_path = 'public'`
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

---

## Part 5: Frontend Development

> **Detailed frontend patterns:** `~/.claude/rules/frontend.md`
> **Frontend philosophy tables:** `~/.claude/references/frontend-principles.md`

### Core Principles 🔴

- **Hyper-Minimalist UI** — Less, but better. Every element must earn its place.
- **Use Project Systems First** — Discover before creating. Search `components/`, `hooks/`, `lib/` first.
- **State Hierarchy** — URL State > Server State (TanStack Query) > Local State > Global State (Zustand)

---

## Part 6: Quality & Operations

### Testing 🟡

- **Create unit tests** in `/tests` mirroring app structure
- **Include for each feature:** 1 expected case, 1 edge case, 1 failure case
- **Update tests when logic changes**

### Linting 🔴

**Zero tolerance errors:** F821 (undefined name), F841 (unused variable), E722 (bare except), B904 (missing exception chaining)

### Server Management 🟡

- **NEVER start dev servers without explicit user request** (port conflicts, user manages lifecycle)
