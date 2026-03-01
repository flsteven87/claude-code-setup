# Backend Development Rules

> Extracted from CLAUDE.md. These rules apply to all backend (Python/FastAPI/Supabase) development.

## Async/Sync Discipline 🔴

**Rule:** `async def` must await ALL I/O. Blocking calls freeze the entire event loop.

| Context        | ❌ Wrong           | ✅ Correct                        |
| -------------- | ------------------ | --------------------------------- |
| HTTP calls     | `requests.get()`   | `await httpx.AsyncClient().get()` |
| Database       | `db.query().all()` | `await async_session.execute()`   |
| File I/O       | `open().read()`    | `await aiofiles.open()`           |
| Multiple calls | Sequential awaits  | `await asyncio.gather(...)`       |

**When to use `def`:** CPU-bound work, sync-only libraries (FastAPI runs these in threadpool automatically).

## Pydantic V2 Standards 🔴

**Always V2 syntax — never V1:**
- ❌ `@validator` → ✅ `@field_validator` + `@classmethod`
- ❌ `@root_validator` → ✅ `@model_validator(mode='after')`
- ❌ `class Config:` → ✅ `model_config = ConfigDict(...)`
- ❌ `.dict()` / `.json()` → ✅ `.model_dump()` / `.model_dump_json()`
- ❌ `orm_mode = True` → ✅ `from_attributes=True`
- ⚠️ `model_dump()` keeps Python types (UUID, Enum as objects) — use `model_dump(mode='json')` for external APIs / JSON output

## Error Handling 🟡

**Pattern:** Domain exceptions in service layer → Global handler converts to HTTP responses.

| Layer     | Responsibility                                          |
| --------- | ------------------------------------------------------- |
| Service   | Raise `NotFoundError("User", id)` - no HTTP knowledge   |
| App setup | `@app.exception_handler(AppException)` → `JSONResponse` |
| Endpoint  | Clean code, no try/except clutter                       |

## Repository Pattern 🔴

- ✅ Inherit `SupabaseRepository`, call `super().__init__(table_name=..., model_class=...)`
- ✅ Use `_handle_supabase_result()` for all queries, `_build_model()` for single results
- ❌ Never access `result.data[0]` directly — bypasses error handling
- ❌ Never add business logic in repository methods
- ❌ Never ignore base class CRUD methods

## Supabase Best Practices 🔴

- ✅ RLS policies: use `(select auth.uid())` subquery (cached) instead of `auth.uid()` direct call (30-70% faster)
- ✅ RPC scalar returns (`RETURNS UUID`): `result.data` is direct value, NOT a list
- ✅ RPC table returns (`RETURNS SETOF`): use `_handle_supabase_result()` → list of dicts
- ✅ PostgreSQL functions: always `SECURITY DEFINER` + `SET search_path = 'public'`
