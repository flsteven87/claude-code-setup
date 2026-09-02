---
name: fugu-worker
description: "Delegate one bounded implementation task to Fugu Ultra, then inspect and validate its work."
argument-hint: "[bounded implementation task]"
disable-model-invocation: true
---

# Fugu Worker

Delegate execution while Claude retains scope, review, and integration. The typed
`/fugu-worker` invocation is the authorization for one paid, file-writing run.

## Bound the assignment

Establish one objective, exhaustive acceptance criteria, exclusive file ownership, applicable
instructions, existing work to preserve, validation commands, and the authority boundary. Keep
overlapping files under one owner and leave worker-owned paths untouched while the worker runs.

## Preflight

Run `codex-fugu preflight`. It makes no provider request and validates the live Codex capabilities,
Fugu catalog, Sakana credential source, apps toggle, and MCP inventory. On failure, report the exact
error; no retry and no substitute model.

## Dispatch one worker

Create one session scratch directory and write a self-contained assignment:

```text
Implement this bounded assignment as the execution owner.

Objective:
<one concrete result>

Acceptance criteria:
<exhaustive, checkable criteria>

Ownership:
<exact files, directories, or modules>

Instructions and evidence:
<applicable instruction and source paths>

Existing work to preserve:
<relevant dirty or concurrent changes>

Validation:
<commands or observable checks>

Authority boundary:
<authorized local and external actions>

Return exactly these sections:
Outcome
Files changed
Validation
Risks or blockers
```

Launch in one background call:

```bash
exec codex-fugu run --mode worker \
  --cwd "<workspace root>" \
  --assignment "$SCRATCH/assignment.md" \
  --events "$SCRATCH/events.jsonl" \
  --report "$SCRATCH/report.md"
```

The launcher owns provider config, credential loading, MCP and apps isolation, approval policy, and
sandbox selection; it and current CLI help are the source of truth, so add no version gates or
duplicate flags here.

## Supervise, inspect, and validate

Keep working while it runs. Check event-file growth every few minutes; ten minutes without growth
is stalled, so terminate the exact task-local process. Allow a streaming run up to one hour. Do not
create a new worker after failure or quota exhaustion.

Inspect every owned change and run the stated validation. For an in-scope defect, read the session
id from `thread.started`, write one focused correction assignment with unchanged ownership, and run
the launcher again with `--resume <session-id>`.

Keep accepted work and report outcome, files, validation, skipped checks, remaining risks, and that
Fugu Ultra performed the work. Never attribute an incomplete or Claude-authored result to Fugu.
