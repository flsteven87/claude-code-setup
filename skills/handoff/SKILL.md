---
name: handoff
description: End-of-session continuity capture — update MEMORY.md's current-state section (sole WIP + next direction + active blocker) so the next session resumes in 30 seconds without re-reading the conversation. Use when the user says /handoff, '收一收', '今天到這', '寫個 handoff', '收尾', 'end of session', 'wrap up', or before closing a session that has produced state worth resuming from. NOT a session journal — focus on what the next decision needs, not what just happened. Respects the same focus-over-completeness principle as /latest: ship history goes to CHANGELOG / git log (not MEMORY.md); session-specific reasoning evaporates with the session unless it generalized into a reusable rule (then it goes to the appropriate topic file, not MEMORY.md proper). Replaces, never appends. Defers to /latest when memory needs a full sync + restructure rather than a small end-of-session update.
---

# /handoff

End-of-session capture. Goal: when you open the next session, you can pick up in 30 seconds without re-reading any conversation.

## The principle

**Handoff updates working memory, not a journal.** The output is a small, surgical edit to MEMORY.md's current-state section — sole WIP, next direction, and any blocker not obvious from `git status`. Everything else (completed work, decisions made, files touched, things tried) belongs elsewhere: CHANGELOG / commit messages / topic files. If a session-level lesson generalized into a reusable rule, that goes to the appropriate topic file (cross-session lessons / implicit conventions / etc.), not into MEMORY.md proper.

The wrong question is "what did I do this session?" The right question is "what does the next session need loaded to resume safely?"

## What belongs in a handoff (and what doesn't)

**Belongs in MEMORY.md after handoff:**
- **Sole / primary WIP** — one ticket or task, what state it's in, where the PR is if open
- **Next direction** — single sentence on what to pick up first
- **Active blocker** — only if not obvious from `git status` / open PRs (e.g. "waiting on Jeffrey to set CONTRACT_REPO_TOKEN before merge")
- **Newly-OK'd Locked Decision** — only if the user explicitly said "this is the rule going forward". Goes in the Locked Decisions section, not the current-state section

**Does NOT belong (drop or extract):**
- "Completed today" lists — `git log --since=<session-start>` is the SSOT
- File-touched lists — `git diff --stat` is the SSOT
- Decisions made during exploration that didn't land in code — if they mattered, they'd be in code
- Multi-paragraph narratives of what was tried — pure session journal; evaporates with the session
- Ship lessons unless they generalize beyond this incident (then → topic file, with a 1-line pointer added to Memory Index if not already there)
- Status of things you didn't actively work on — handoff is about YOUR session, not the project (use `/latest` for full sync)

**Operational test:** if a candidate handoff line is "accurate but the next session could rebuild it from `git log` / `gh pr list` / Linear in 5 seconds" → don't write it.

## Workflow

1. **Detect MEMORY.md location** — usually `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md` (path encodes the project root with `/` replaced by `-`). If no MEMORY.md exists and the project has its own convention (HANDOFF.md, `.claude/MEMORY.md`, `docs/handoff/`), use that. If nothing exists, output the handoff paragraph in chat and ask before creating new persistence files.

2. **Detect what changed this session** — `git log --oneline` since the session start, `git status`, and which tickets the conversation explicitly touched. **This is context for you**, not text to copy into memory verbatim.

3. **Identify the WIP + next direction** — usually one obvious answer. If ambiguous, ask: "本次 session 的下個 pick-up 是 X 還是 Y？" Don't guess.

4. **Update the current-state section in place** — find the existing paragraph (often labeled "Now", "Current Phase", "Current State", or similar). **Replace its contents** with the new state. Do NOT append a new "Session YYYY-MM-DD" block — that's how MEMORY.md bloats into a journal.

5. **Size check** — if MEMORY.md is over 200 lines after your edit, you kept too much (the auto-memory system silently truncates past line ~200). Trim by running the "What belongs" filter again. If the file was already bloated before this session, surface that and suggest `/latest` for a full consolidation pass — `/handoff` is a small edit, not a restructure.

6. **Output the handoff paragraph** to the user — two or three sentences. This is the deliverable.

## /handoff vs /latest

| Situation | Tool |
|---|---|
| Just finished a session, want the next pickup to be fast | `/handoff` (small surgical update) |
| Memory has been accumulating across sessions, feels stale or bloated | `/latest` (full sync + restructure) |
| Multiple repos / Linear states / CHANGELOG drift to reconcile | `/latest` |
| Just need MEMORY.md to reflect "I shipped X, next is Y" | `/handoff` |

If during `/handoff` you notice memory has gone significantly stale beyond your own session's footprint — stale ticket states elsewhere, ship history accumulated over multiple sessions, transient state from weeks ago — say so and suggest `/latest`. Don't quietly expand `/handoff` into a full consolidation pass.

## Anti-patterns

| Mistake | Fix |
|---|---|
| Writing a 10-bullet "Completed work" list | `git log` / CHANGELOG already have it — don't duplicate |
| Listing every file touched | `git diff --stat` is SSOT — drop |
| Appending a new dated section every handoff | Replace the "Now" section in place. Stacking sessions = bloat = truncation |
| Capturing exploration reasoning | If it didn't land in code, it's not durable. Drop |
| "Save everything just in case" | The cost of bloat is silent truncation of the Memory Index next session. Less is more |
| Adding ship lessons to MEMORY.md directly | If it's a one-off, drop it. If it generalizes, extract to a topic file (e.g. `project_cross_session_lessons.md`) and add a pointer line in Memory Index |
| Creating HANDOFF.md when MEMORY.md already exists | One durable surface, not two. Update what's there |
| Running `/handoff` when MEMORY.md is already bloated | Suggest `/latest` first — small edits don't fix structural bloat |

## Output

Two or three sentences in the user's session language (default zh-tw for Chinese-speaking users; mirror what was used in conversation). Anchor on three things: where you are, what's open, what to pick up next. Example shape:

> 你現在 main 是 `<SHA>`，clean tree。Sole WIP 是 [<PR title>](url) (<ticket>) — <state, e.g. "Codex review in flight">。下個 pick-up：<one sentence>。<blocker if any, omit if none>.

The closing sentence is the actual deliverable. Everything before it is orientation.
