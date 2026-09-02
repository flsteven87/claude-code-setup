---
name: rehydrate
description: "Reload codebase texture after context loss and confirm the queued step still aims at the project's endgame before it runs. Use after /compact, after a long idle, when a long delegation returns, or when the user says 「進入狀況」, \"rehydrate\", or 「再走一遍」."
argument-hint: "[active plan doc or task surface]"
---

# Rehydrate

Compaction keeps the narrative and loses the texture: exact signatures, the wording of a locked
invariant, the import shape of the neighbouring file, the evidence behind the queued step. Rebuild
that texture from files, confirm the queued step still serves the endgame, and hand off.

## What to recover

- The checkpoint as a file: the primary checkout's `MEMORY.md` entry that owns the active surface,
  read from disk this turn. The compaction summary is a lossy projection; the file wins.
- The task surface, without paraphrase: the plan document, the queued step, the files it touches,
  and the invariants and locked decisions governing them, each attributed to the file that owns it
  (`CLAUDE.md`, `AGENTS.md`, `CONTEXT.md`, an ADR, the plan).
- The local convention the next file must follow: read the files the step will change and the
  nearest neighbour of the same kind, so the new code reads as native.

## Endgame check

Hold each decision in the queued step against the project's stated endgame principle, or domain
best practice when none is stated, saying so. A transitional shim, parallel `v2` naming, deprecated
re-export, or speculative hook is a tension: state it in plain language with file and line evidence
as the user's decision, and wait only for that answer.

## Done

A confirmation of at most five zh-tw sentences: the plan document, the queued step, the single most
load-bearing invariant it preserves, any tension the user accepted, and the standalone command that
runs the step. Every claim in it was read from a file this turn.
