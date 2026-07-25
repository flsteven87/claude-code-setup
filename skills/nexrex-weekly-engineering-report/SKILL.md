---
name: nexrex-weekly-engineering-report
description: Produce a factual one-page NexRex engineering report for a named contributor and multi-day window by reconciling Linear, Git mainline, PR, incident, delivery, and remaining-work evidence. Use for weekly or multi-day contributor reviews in Markdown or HTML; exclude daily standups.
---

# NexRex Weekly Engineering Report

Build a factual report from Linear and Git evidence.

## Workflow

1. Read the repository `AGENTS.md` cold-start chain before inspection.
2. Pin the scope:
   - contributor and every known Git author alias;
   - exact start, exclusive end, timezone, repository, and branch;
   - default to the previous seven calendar days through now in `Asia/Taipei` and `main`.
3. Resolve relative resource paths against the directory containing this `SKILL.md`. Discover aliases with `git shortlog -sne --all` for the window, then run `<skill-dir>/scripts/collect_git_activity.py` with explicit aliases and dates. Redirect its JSON to a temporary file and keep the full file list out of conversation context.
4. Use the connected Linear MCP as the issue-tracker source of truth:
   - resolve the contributor with `get_user` using their email; use `me` only when the authenticated Linear user is the contributor;
   - list all `NEX` team issues updated from the start boundary, paginate when needed, then apply the exclusive end boundary client-side and retain issues whose `createdBy` or `assignee` matches the contributor;
   - also list issues assigned to the contributor when workspace volume prevents a complete team scan;
   - read every issue referenced by an in-scope commit or PR body;
   - for incidents/debug work, follow only causal `parent`, `source`, `blockedBy`, and `relatedTo` links needed to recover the originating symptom and root cause;
   - read comments only when the description, relations, status, or attachments leave a material gap.
5. Reconcile PR identity as the deduplicated union of Git commit/body references, Linear PR attachments, and exact PR lookups when available.
6. Build an evidence ledger in memory with four fields per candidate topic:
   - observed problem or requested outcome;
   - confirmed root cause or design decision;
   - merged change, with NEX and PR identifiers;
   - current status and unresolved scope.
7. Verify claims against Git:
   - inspect the relevant commit body and first-parent diff;
   - distinguish the fix directly implemented by the diff from other symptoms mentioned in the ticket.
8. Before selecting, drafting, or rendering topics, read
   [the report contract](references/report-contract.md) completely. Apply every rule in that
   reference. Select a topic only after its evidence-ledger row is complete.
9. Prefer validation already recorded in PRs or tickets. Run targeted checks only to resolve a
   material claim gap.
10. Default to concise Markdown. For HTML or a visual report, load the `visualize` skill and render
    and visually inspect the one-page layout defined by the report contract.

## Failure handling

- If Linear is unavailable, authenticate or reconnect it before continuing.
- If Linear remains unavailable, stop and name the coverage gap. Do not silently substitute Git-only inference unless the user explicitly accepts it.
- If an author alias is uncertain, show the discovered identities and state which were included.

## Completion

Complete only when the report states its Linear and Git sources and exact date window, every selected
topic has a complete evidence-ledger row, every rule in the report contract has been applied, and
every remaining coverage gap is named. HTML output also requires the report contract's render checks.
