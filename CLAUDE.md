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

- ❌ Barrel imports from icon/component libraries (`import { X } from 'lucide-react'` → use `lucide-react/dist/esm/icons/x`)
- ❌ Sequential `await` for independent operations → use `Promise.all()` or `asyncio.gather()`

**Code Organization:**

- ❌ God components exceeding 1000 lines (frontend or backend)

**Security & Operations:**

- ❌ `FORWARDED_ALLOW_IPS=*` in production
- ❌ `FOR ALL TO public USING (true)` RLS policies
- ❌ Starting dev servers without explicit user request
- ❌ PostgreSQL functions with `SET search_path = ''`

**Legacy Patterns:**

- ❌ `pip install` → Use `uv add`
- ❌ `python script.py` → Use `uv run python script.py`
- ❌ `source .venv/bin/activate` → UV handles environment automatically
- ❌ `requirements.txt` → Use `pyproject.toml` + `uv.lock`
- ❌ Manual `useMemo`/`useCallback`/`memo()` → React Compiler handles automatically

**Scope Discipline (multi-agent safety):** 🔴

- ❌ Reverting, modifying, or deleting code that is outside your current task scope
- ❌ "Cleaning up" or "fixing" unrelated code you encounter while working on your task
- ❌ Undoing changes made by other agents or previous sessions without explicit user request
- ❌ Running `git checkout`, `git restore`, or `git reset` on files you didn't modify in this session
- ✅ Only touch files and code directly required by your current task
- ✅ If you notice issues in unrelated code, report them to the user — do NOT fix them silently

### 🔴 Mandatory Practices

**Always Do:**

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

**1. One-Shot Excellence** — Write the elegant solution now, not "fix it later". Design clean upfront.

**2. No Development-Stage Adjectives** — Never name by comparing to previous versions:
- ❌ `enhanced_parser.py`, `optimized_query()`, `UserServiceV2`
- ✅ `parser.py`, `query()`, `UserService`

**3. Business Adjectives Are Acceptable** — Product/domain adjectives OK: `PremiumPlan`, `AdvancedAnalytics`

**4. No Backward Compatibility Hacks** — Delete completely, don't deprecate:
- ❌ `_old_var`, re-exporting removed functions, `# TODO: remove after migration`
- ✅ Delete unused code immediately and completely

**5. No Over-Defensive Coding** — Validate at boundaries, trust internal code:
- ❌ Fallbacks "just in case", null checks on guaranteed non-null values
- ✅ Validate user input and external APIs only

**6. Replace, Don't Accumulate** — One file evolves; never create parallel versions.

---

## Part 2: AI Behavior

### AI Behavior Rules 🟡

- **Never assume missing context** - ask questions if uncertain
- **Never hallucinate libraries or functions** - only use verified packages
- **Always confirm file paths and module names** exist before referencing
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

| Layer          | Location                | Responsibility                                               |
| -------------- | ----------------------- | ------------------------------------------------------------ |
| **API**        | `src/api/v1/endpoints/` | HTTP handling, validation, auth, uses `Depends(get_service)` |
| **Service**    | `src/services/`         | Business logic, orchestration, NO direct DB calls            |
| **Repository** | `src/repositories/`     | Database queries, inherits `SupabaseRepository`              |
| **Database**   | Supabase/PostgreSQL     | Data storage                                                 |

### Design Patterns 🟡

- **Strategy Pattern** — Runtime-selectable algorithms via ABC. Use when multiple implementations needed.
- **Aggregate Root** — Manage dependent entities through parent repository (e.g., `OrderRepository` manages orders AND items)

### Class Naming Conventions 🟡

| Pattern       | Use When                        | Example                           |
| ------------- | ------------------------------- | --------------------------------- |
| **Handler**   | Stateful workflow orchestration | `PaymentHandler`, `UploadHandler` |
| **Processor** | Stateless data transformation   | `ImageProcessor`, `CSVProcessor`  |
| **Service**   | Business logic encapsulation    | `OrderService`, `AuthService`     |

### Naming Conventions 🟡

**Files & Directories:**

| Type                 | Frontend                           | Backend         |
| -------------------- | ---------------------------------- | --------------- |
| Components           | `PascalCase.tsx`                   | -               |
| Hooks                | `useCamelCase.ts`                  | -               |
| Utilities/lib        | `kebab-case.ts`                    | `snake_case.py` |
| Directories          | `kebab-case/`                      | `snake_case/`   |
| shadcn/ui components | `lowercase.tsx` (their convention) | -               |

**Code Identifiers:**

| Element              | TypeScript        | Python            |
| -------------------- | ----------------- | ----------------- |
| Variables, functions | `camelCase`       | `snake_case`      |
| Classes, Components  | `PascalCase`      | `PascalCase`      |
| Constants            | `SCREAMING_SNAKE` | `SCREAMING_SNAKE` |
| Types, Interfaces    | `PascalCase`      | `PascalCase`      |
| Env variables        | `SCREAMING_SNAKE` | `SCREAMING_SNAKE` |

**Frontend Events:**

- Props: `onSubmit`, `onClick`, `onChange` (what happens)
- Handlers: `handleSubmit`, `handleClick` (how to handle)

**Core Rule:** File name = Primary export name. No mismatches.

---

## Part 4: Backend Development

### Python & UV Conventions 🟡

```bash
# Execution
uv run python script.py
uv run pytest tests/
uv run ruff check .

# Package management
uv add package          # production
uv add --dev package    # development
uv sync                 # install all dependencies
```

### Async/Sync Discipline 🔴

**Rule:** `async def` must await ALL I/O. Blocking calls freeze the entire event loop.

| Context        | ❌ Wrong           | ✅ Correct                        |
| -------------- | ------------------ | --------------------------------- |
| HTTP calls     | `requests.get()`   | `await httpx.AsyncClient().get()` |
| Database       | `db.query().all()` | `await async_session.execute()`   |
| File I/O       | `open().read()`    | `await aiofiles.open()`           |
| Multiple calls | Sequential awaits  | `await asyncio.gather(...)`       |

**When to use `def`:** CPU-bound work, sync-only libraries (FastAPI runs these in threadpool automatically).

### Pydantic V2 Standards 🔴

**Always V2 syntax — never V1:**
- ❌ `@validator` → ✅ `@field_validator` + `@classmethod`
- ❌ `@root_validator` → ✅ `@model_validator(mode='after')`
- ❌ `class Config:` → ✅ `model_config = ConfigDict(...)`
- ❌ `.dict()` / `.json()` → ✅ `.model_dump()` / `.model_dump_json()`
- ❌ `orm_mode = True` → ✅ `from_attributes=True`
- ⚠️ `model_dump()` keeps Python types (UUID, Enum as objects) — use `model_dump(mode='json')` for external APIs / JSON output

### Dependency Injection 🔴

- ✅ Use `Annotated` type aliases: `UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]`
- ✅ Use `pydantic-settings` BaseSettings + `@lru_cache` for config — never `os.getenv()`
- ❌ Avoid inline `Depends()` in function signatures (verbose, duplicated, hard to test)

### Error Handling 🟡

**Pattern:** Domain exceptions in service layer → Global handler converts to HTTP responses.

| Layer     | Responsibility                                          |
| --------- | ------------------------------------------------------- |
| Service   | Raise `NotFoundError("User", id)` - no HTTP knowledge   |
| App setup | `@app.exception_handler(AppException)` → `JSONResponse` |
| Endpoint  | Clean code, no try/except clutter                       |

### Repository Pattern 🔴

- ✅ Inherit `SupabaseRepository`, call `super().__init__(table_name=..., model_class=...)`
- ✅ Use `_handle_supabase_result()` for all queries, `_build_model()` for single results
- ❌ Never access `result.data[0]` directly — bypasses error handling
- ❌ Never add business logic in repository methods
- ❌ Never ignore base class CRUD methods

### Supabase Best Practices 🔴

- ✅ RLS policies: use `(select auth.uid())` subquery (cached) instead of `auth.uid()` direct call (30-70% faster)
- ✅ RPC scalar returns (`RETURNS UUID`): `result.data` is direct value, NOT a list
- ✅ RPC table returns (`RETURNS SETOF`): use `_handle_supabase_result()` → list of dicts
- ✅ PostgreSQL functions: always `SECURITY DEFINER` + `SET search_path = 'public'`

### API Conventions 🟡

- **Use snake_case for all API fields** (backend Pydantic + frontend TypeScript)
- **Define root routes as `@router.get("")`** not `@router.get("/")`
- **Include CORS origins for exact frontend domains**

---

## Part 5: Frontend Development

> Detailed frontend philosophy tables: `~/.claude/references/frontend-principles.md`

### Hyper-Minimalist UI 🔴 — Less, but better. Every element must earn its place.

### Use Project Systems First 🔴 — Discover before creating. Search `components/`, `hooks/`, `lib/` before writing new code.

### State Management Hierarchy 🔴 — URL State > Server State (TanStack Query) > Local State (`useState`) > Global State (Zustand).

### TypeScript Standards 🔴

- Zero tolerance for `any` in query hooks, error handling, API responses
- Always explicit `interface Props` with `readonly` for immutable props
- ES modules only — never `require()`

### TanStack Query Patterns 🟡

- **Query Key Factory required**: use `hooks/factories/` — never hardcode query keys
- **Invalidation**: granular (`userKeys.detail(id)`) over nuclear (`userKeys.all`)
- **Mutations**: always include `onSettled` for cache consistency
- **Race Conditions**: `enabled: !!param`, set `staleTime`, never fire with undefined params

### Component Standards 🟡

| Rule                           | Rationale                                         |
| ------------------------------ | ------------------------------------------------- |
| Max 1000 lines per component   | Split into sub-components                         |
| Explicit prop interfaces       | No `React.ComponentProps<'div'>`                  |
| Composition over configuration | Prefer children/slots over many boolean props     |
| Collocate related code         | Keep hook + component + types together when small |

### SSE (Server-Sent Events) 🟡

- Backend: `EventSourceResponse` with `X-Accel-Buffering: no` header
- Frontend: `EventSource` + cleanup in `useEffect` return
- Close on terminal events (`completed`, `failed`, `cancelled`)

### React Compiler 🔴

- ✅ Required: `babel-plugin-react-compiler` + `eslint-plugin-react-compiler` in all projects
- ❌ No manual `useMemo`/`useCallback`/`memo()` — Compiler handles automatically
- Escape hatch: `"use no memo"` directive — use sparingly, investigate root cause
- ⚠️ TanStack Table/Query interior mutability may cause stale UI — add `"use no memo"` if needed

### useEffect & Race Condition Prevention 🔴

**Every useEffect with async/timers/listeners MUST return cleanup:**

| Resource | Cleanup Pattern |
| -------- | --------------- |
| fetch/async | `AbortController` → `return () => controller.abort()` |
| `setTimeout`/`setInterval` | Store IDs → `return () => ids.forEach(clearTimeout)` |
| `addEventListener` | Same ref → `return () => removeEventListener(type, handler)` |
| `EventSource` (SSE) | `return () => { es.close(); ref.current = null }` |

- ✅ Unstable callbacks in deps: use ref pattern (`cbRef.current = callback`) to avoid re-runs
- ❌ Never mutate state arrays/objects — Compiler assumes immutability (`toSorted()`, spread)
- ❌ Never read/write refs during render — move to `useEffect` or event handler
- ❌ Never use dual completion sources (SSE + polling) without `ref.current.handled` guard
- ❌ Never fire fetch/mutation without checking if component is still mounted or request is current

---

## Part 6: Quality & Operations

### Testing 🟡

- **Create unit tests for new features** in `/tests` mirroring app structure
- **Include for each feature:** 1 expected case, 1 edge case, 1 failure case
- **Update tests when logic changes**

```bash
uv run pytest tests/                    # Run all tests
uv run pytest tests/unit/ -v            # Verbose unit tests
uv run pytest -k "test_user" --tb=short # Filter by name
```

### Linting 🔴

**Mandatory before commit:**

```bash
uv run ruff check .     # Backend
npm run lint            # Frontend
npx tsc --noEmit        # TypeScript type check
```

**Zero tolerance errors:**

| Code | Description                |
| ---- | -------------------------- |
| F821 | Undefined name             |
| F841 | Unused variable            |
| E722 | Bare except                |
| B904 | Missing exception chaining |

### Deployment 🔴

- **ALWAYS:** `redirect_slashes=False` in FastAPI
- **ALWAYS:** Define root routes as `@router.get("")`
- **NEVER:** `FORWARDED_ALLOW_IPS=*`
- **ENSURE:** CORS origins include exact frontend domains

### Server Management 🟡

- **NEVER start dev servers without explicit user request**
- **Reason:** Port conflicts and user manages server lifecycle
- Commands to avoid unless requested: `npm run dev`, `uv run uvicorn`
