---
description: Deliver a reviewed local commit through the shared ship contract when the user asks to ship, deliver, or merge.
---

# /ship

Read `/Users/po-chi/.agents/skills/ship/SKILL.md` completely before any delivery action and execute
it as the canonical ship contract. Resolve `skill_dir` and bundled scripts from
`/Users/po-chi/.agents/skills/ship`, not from this adapter.

Claude command mappings:

- `$ship` → `/ship`
- `$implement` → `/mattpocock-skills:implement`
- `$code-review` → read `/Users/po-chi/.agents/skills/code-review/SKILL.md`
- `$git-converge-main` → `/git-converge-main`
- `$setup-matt-pocock-skills` → `/mattpocock-skills:setup-matt-pocock-skills`

`$implement` and `$setup-matt-pocock-skills` are user-only: name the standalone command for the
human to invoke. `/ship` runs on the user's request to ship, deliver, or merge, whether typed as a
command or written in prose; it never starts without that request.

This adapter contains no delivery policy. When it conflicts with the canonical contract, the
canonical contract wins. Completion is exactly the canonical contract's completion criterion.
