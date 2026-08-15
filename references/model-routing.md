# Multi-Agent Model Routing Reference

Read this before authoring a workflow or agent fan-out. Resolve available model names, effort levels,
and limits from the current runtime; this file defines roles, not a cached catalog.

## Route by work

- Keep orchestration, planning, cross-source synthesis, and final judgment in the main session.
- Use the least expensive current tier that has proven adequate for bounded search, inventory, and
  mechanical validation.
- Route substantial implementation or rescue work to Codex when it can access the required evidence.
- Keep code review independent from the implementer. Prefer Codex for Claude-authored changes; use a
  same-provider reviewer only when Codex cannot reach essential evidence, and disclose the loss of
  independence.

## Control the fan-out

1. Inspect the runtime's current models, effort controls, workflow surface, and active routing hook.
2. Pin each worker to an explicit supported tier when the surface permits it. Do not set a global
   worker override that defeats per-role routing.
3. Bound concurrency and give every worker one owned result with a checkable completion criterion.
4. If the active hook rejects named workflows, use the supported explicitly routed script form.
5. Record the runtime choice and evidence in the workflow result, not in this reference.

Routing is complete when every worker has an explicit role, supported runtime choice, ownership
boundary, and completion criterion, and the reviewer is independent where the evidence permits.
