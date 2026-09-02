---
name: fugu-advisor
description: "Get one read-only Fugu Ultra challenge, then reconcile it with Claude's assessment."
argument-hint: "[decision or artifact to challenge]"
disable-model-invocation: true
---

# Fugu Advisor

Buy one independent read without surrendering the Claude's decision. Keep the consultant blind to the
Claude's conclusion except for fragments needed to define the target. The typed `/fugu-advisor`
invocation is the authorization; record the tentative conclusion, strongest evidence, and important
unknowns before dispatch.

## Preflight

Run `codex-fugu preflight`. It validates the live Codex capabilities, Fugu catalog, Sakana
credential source, apps toggle, and MCP inventory without a provider request. On failure, report the
exact error and continue without a Fugu opinion; no retry and no substitute model.

## Dispatch exactly once

Create one session scratch directory and write a self-contained assignment:

```text
Act as an independent, read-only devil's advocate.

Topic or decision:
<bounded target>

Raw evidence and source paths:
<only evidence relevant to the target>

Constraints:
<task constraints>

Test assumptions, seek counterevidence, and identify failure modes. Do not delegate, edit files,
change external state, or request broader permissions.

Return a concise report with exactly these headings:
Assessment
Evidence
Challenges
Recommendation
Confidence and unknowns
```

Launch in one background call:

```bash
exec codex-fugu run --mode advisor \
  --cwd "<evidence root>" \
  --assignment "$SCRATCH/assignment.md" \
  --events "$SCRATCH/events.jsonl" \
  --report "$SCRATCH/report.md"
```

The launcher owns provider config, credential loading, MCP and apps isolation, approval policy, and
sandbox selection; it and current CLI help are the source of truth, so add no version gates or
duplicate flags here.

## Supervise and reconcile

Keep working while it runs. Check event-file growth every few minutes; ten minutes without growth
is stalled, so terminate the exact task-local process. Allow a streaming run up to one hour. Do not
retry failures or quota limits.

On success, reconcile `report.md` against the recorded baseline by evidence. Lead with the
integrated answer and append a compact `Fugu Ultra check`. Never attribute a view to Fugu without a
returned report.
