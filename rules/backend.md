---
paths:
  - "**/*.py"
---

# Python Backend Rules

Apply the repository's local architecture, framework, database, migration, and validation rules.
Keep stack and schema workflow decisions repository-local.

- Preserve the repository's sync or async design. In async code, await I/O and run independent I/O
  concurrently only when ordering and failure semantics permit it.
- Translate exceptions at the owning boundary, catch specific exception types, and preserve the
  cause with exception chaining when adding context.
- Use the repository's configured Python environment, formatter, linter, type checker, and tests.
  Prefer `uv` when the repository uses it.
- Treat schema and production-data changes as repository-specific operations governed by the active
  instructions and authorization boundary.

The change is complete when it follows the nearest repository standards and the relevant configured
checks pass or the validation gap is reported.
