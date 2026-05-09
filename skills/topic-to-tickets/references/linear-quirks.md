# Linear MCP `save_issue` Gotchas

These are non-negotiable; ignore them and your re-save will silently lose content.

## Description content stripping

**`save_issue` strips multi-row markdown tables AND multi-item bullet lists when re-saving an existing issue's description.**

Symptoms: you write a beautiful description with tables and bullet lists; first save looks fine; later edit (even unrelated) silently strips them.

Workaround: **wrap all structured content in code fences**.

```
✅ Use this pattern:

\```
| col1 | col2 |
|---|---|
| a | b |
\```

\```
- bullet 1
- bullet 2
- bullet 3
\```

❌ Not these:

| col1 | col2 |
|---|---|
| a | b |

- bullet 1
- bullet 2
```

The code-fence content survives re-save. The downside: it renders as monospace, not as a real markdown table. Acceptable trade for stability.

Single-item bullet points (one `-`) survive. Tables of fewer than 2 data rows survive. But don't rely on edge cases — wrap structured content unconditionally.

This is documented in NexRex MEMORY.md ("Linear `save_issue` description quirk"). The original session that found this lost a full task table.

## Block-chain rewiring

`blockedBy` is **append-only**:

> "Append-only; existing relations are never removed"

To rewire from `A blocks B` to `A blocks C`:

```python
# Wrong (just adds C; B still blocked):
save_issue(id=B, blockedBy=["C"])

# Right:
save_issue(id=B, removeBlockedBy=["A"])
save_issue(id=C, blockedBy=["A"])
```

Or in one call (works because removeBlockedBy and blockedBy are independent fields):

```python
save_issue(
  id=B,
  removeBlockedBy=["A"],
)
save_issue(
  id=C,
  blockedBy=["A"],
)
```

Same applies to `blocks`, `relatedTo`. All append-only. Use the matching `remove*` field.

## Closing as duplicate

To close NEX-XXX as a duplicate of NEX-YYY:

```python
save_issue(
  id="NEX-XXX",
  state="Duplicate",
  duplicateOf="NEX-YYY",
)
```

Linear sets `statusType="canceled"`, populates `canceledAt`, and back-references in the target issue's "Duplicates" section. The duplicate's description is preserved (visible if you open it directly), but it disappears from default backlog views.

If you want to preserve scope, **merge it into NEX-YYY's description first**, then close NEX-XXX as duplicate.

## Assignee resolution

Use the `assignee` field (NOT `assigneeId`):

```python
save_issue(
  id="NEX-XXX",
  assignee="8d11c626-4366-4356-92ae-832851384f65",  # user ID
  # or "steven.wu@nexrex.ai"  (email)
  # or "Steven Wu"            (name)
  # or "me"                   (current user)
)
```

`assigneeId` is in the response payload from `get_issue` but is NOT a valid input parameter to `save_issue`. Easy mistake — Linear will silently ignore it.

## Comments vs. description

When the change context is large (decision rationale, audit reports, Codex transcripts), prefer:

- **Description**: the durable contract for implementing engineer (what / why / acceptance)
- **Comment**: the audit trail (when / who decided / what was rejected and why)

`save_comment` accepts the same markdown rules but is NOT subject to the table-stripping bug — comments preserve tables and bullet lists faithfully.

## Append-only relations summary

| Field | Add via | Remove via |
|---|---|---|
| `blockedBy` | `blockedBy` | `removeBlockedBy` |
| `blocks` | `blocks` | `removeBlocks` |
| `relatedTo` | `relatedTo` | `removeRelatedTo` |
| `links` | `links` | (no remove field) |

Links are forever — be careful adding link attachments you might want to remove later.

## Save flow for a typical restructure

```
1. get_issue on each ticket (cache the current state)
2. For each ticket, compose new description (code-fence the structured content)
3. save_issue in parallel for description / title / priority / assignee
4. Re-wire blocks: removeBlockedBy → blockedBy (sequenced per ticket)
5. Close duplicates last (so duplicateOf target's description is final)
6. get_issue again on each ticket to verify (especially the description survived)
```

Step 6 is the cheap insurance against the table-strip bug.
