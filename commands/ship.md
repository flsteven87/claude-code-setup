---
description: Deliver a reviewed local commit through the shared ship contract.
disable-model-invocation: true
---

# /ship

Read `/Users/po-chi/.agents/skills/ship/SKILL.md` completely before any delivery action and execute
it as the canonical ship contract. Resolve `skill_dir` and bundled scripts from
`/Users/po-chi/.agents/skills/ship`, not from this adapter.

Claude command mappings:

- `$ship` → `/ship`
- `$implement` → `/mattpocock-skills:implement`
- `$code-review` → read `/Users/po-chi/.agents/skills/code-review/SKILL.md`; the
  `/mattpocock-skills:code-review` plugin copy omits the Graph reviewer routes and the holdout input
  set
- `$git-converge-main` → `/git-converge-main`
- `$setup-matt-pocock-skills` → `/mattpocock-skills:setup-matt-pocock-skills`

`$ship`, `$implement`, and `$setup-matt-pocock-skills` are user-only. Name the standalone command
for the human to invoke; reading its `SKILL.md` to imitate it is not a substitute.

This adapter contains no delivery policy. When it conflicts with the canonical contract, the
canonical contract wins. Completion is exactly the canonical contract's completion criterion.
