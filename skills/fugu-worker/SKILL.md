---
name: fugu-worker
description: "Delegate one bounded implementation task to Fugu Ultra, then inspect and validate its work."
argument-hint: "[bounded implementation task]"
disable-model-invocation: true
---

# Fugu Worker

Delegate execution while Claude retains scope, review, and integration.

## 1. Bound the assignment

Establish one objective, exhaustive acceptance criteria, exclusive ownership,
applicable instructions, existing work to preserve, validation commands, and
the authority boundary. Keep overlapping files under one owner and do not edit
worker-owned paths while the worker runs.

## 2. Preflight

Run `codex-fugu preflight`. It makes no provider request and validates the live
Codex capabilities, Fugu catalog, Sakana credential source, apps toggle, and
MCP inventory. On failure, report the exact error and do not retry or substitute
another model.

## 3. Dispatch one worker

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

Launch in one background Bash call:

```bash
exec codex-fugu run --mode worker \
  --cwd "<workspace root>" \
  --assignment "$SCRATCH/assignment.md" \
  --events "$SCRATCH/events.jsonl" \
  --report "$SCRATCH/report.md"
```

The launcher owns provider config, credential loading, MCP/apps isolation,
approval policy, and sandbox selection. Treat it and current CLI help as the
source of truth; do not add version gates or duplicate its flags here.

## 4. Supervise, inspect, and validate

Poll event-file growth roughly every minute and update the user about every
three minutes. Ten minutes without growth is stalled; terminate the exact
task-local process. Allow a streaming run up to one hour. Do not create a new
worker after failure or quota exhaustion.

Inspect every owned change and run the stated validation. For an in-scope
defect, read the session id from `thread.started`, write one focused correction
assignment with unchanged ownership, and run the launcher again with
`--resume <session-id>`.

Keep accepted work and report outcome, files, validation, skipped checks,
remaining risks, and that Fugu Ultra performed the work. Never attribute an
incomplete or Claude-authored result to Fugu.
