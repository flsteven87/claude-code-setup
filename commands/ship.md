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
- `$code-review` → `/mattpocock-skills:code-review`
- `$git-converge-main` → `/git-converge-main`

This adapter contains no delivery policy. When it conflicts with the canonical contract, the
canonical contract wins. Completion is exactly the canonical contract's completion criterion.
