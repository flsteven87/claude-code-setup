---
name: fugu-advisor
description: "Get one read-only Fugu Ultra challenge, then reconcile it with Claude's assessment."
argument-hint: "[decision or artifact to challenge]"
disable-model-invocation: true
---

# Fugu Advisor

Buy one independent read without surrendering Claude's decision. Keep the
consultant blind to Claude's conclusion unless a fragment is necessary to
define the target.

## 1. Qualify and baseline

Require an explicit Fugu invocation and a bounded decision or artifact. Record
Claude's tentative conclusion, strongest evidence, and important unknowns
before dispatch.

## 2. Preflight

Run `codex-fugu preflight`. It validates the live Codex capabilities, Fugu
catalog, Sakana credential source, apps toggle, and MCP inventory without a
provider request. On failure, report the exact error and continue without a
Fugu opinion. Do not retry or substitute another model.

## 3. Dispatch exactly once

Create one session scratch directory and write a self-contained assignment:

```text
Act as an independent, read-only devil's advocate.

Topic or decision:
<bounded target>

Raw evidence and source paths:
<only evidence relevant to the target>

Constraints:
<task constraints>

Test assumptions, seek counterevidence, and identify failure modes. Do not
delegate, edit files, change external state, or request broader permissions.

Return a concise report with exactly these headings:
Assessment
Evidence
Challenges
Recommendation
Confidence and unknowns
```

Launch in one background Bash call:

```bash
exec codex-fugu run --mode advisor \
  --cwd "<evidence root>" \
  --assignment "$SCRATCH/assignment.md" \
  --events "$SCRATCH/events.jsonl" \
  --report "$SCRATCH/report.md"
```

The launcher owns provider config, credential loading, MCP/apps isolation,
approval policy, and sandbox selection. Treat it and current CLI help as the
source of truth; do not add version gates or duplicate its flags here.

## 4. Supervise and reconcile

Poll event-file growth roughly every minute. Update the user about every three
minutes. Ten minutes without growth is stalled; terminate the exact task-local
process. Allow a streaming run up to one hour. Do not retry failures or quota
limits.

On success, reconcile `report.md` against Claude's baseline by evidence. Lead
with the integrated answer and append a compact `Fugu Ultra check`. Never
attribute a view to Fugu without a returned report.
