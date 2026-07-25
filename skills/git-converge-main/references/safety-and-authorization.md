# Safety and Authorization Edges

Use this reference only for blocked or destructive edge cases. Apply the ownership, default
authorization, and completion boundaries from `SKILL.md`. Require mechanical proof from the bundled
helper or semantic proof from `semantic-convergence.md`; age, names, `[gone]`, subjects, and
`git cherry` are investigation leads, not deletion authority.

## Contents

- [Dirty merged branch rescue](#dirty-merged-branch-rescue)
- [Remote cleanup boundaries](#remote-cleanup-boundaries)

## Dirty merged branch rescue

Preserve the only copy before changing refs. Use `stash push -u`, apply rather than pop, verify the
new branch contains the complete staged/unstaged/untracked set, and retain the stash through commit
validation. Do not auto-generate a WIP commit unless committing was explicitly requested.

Avoid rebasing or merging a squash-merged source branch onto the default branch. Those operations
replay already-incorporated commits and obscure the new work. Move only the dirty delta to a fresh
branch based on the default remote.

## Remote cleanup boundaries

### Merged-head standing authorization

A bare `/git-converge-main`, or `/ship` finalizing its exact delivered PR, authorizes deletion of a
repository-hosted merged PR head only when all predicates below are freshly proven:

- authenticated provider login exactly equals the PR author;
- PR state is `MERGED`, and its merge commit is contained by the refreshed default branch;
- PR head repository is the configured repository remote;
- the live exact head ref still equals the PR's final full head OID;
- the ref is neither the default branch nor a protected branch.

Pin the login, PR number, head repository, exact ref, head OID, merge commit, and refreshed default
OID in the receipt. Delete only the exact ref. If any predicate is false or unavailable, preserve
the ref and record the failed predicate. Branch prefix, age, and naming conventions are not proof.

After deletion, fetch/prune and require `git ls-remote --heads <remote> <exact-ref>` to return no
matching ref. A provider-deleted ref satisfies the action only after the same absence check.

### Semantic or unmerged remote drops

Remote deletion outside the merged-head predicates requires explicit item-level intent. This
includes open or closed-unmerged PRs, post-merge branch movement, semantic supersession, and remote
refs without an exact merged PR. For semantic supersession or inferiority, run independent
Standards and Spec reviews and reconcile disagreement conservatively before mutation.

An explicit request to drop named PRs, or to drop the exact PRs just classified in the active
conversation, authorizes closing those PRs and deleting their exact head branches even outside the
owner scope. This is item-specific authority, not namespace-wide authority. Pin each PR's state,
head OID, and branch immediately before mutation; preserve that item if any value changed. Never
extend this authority to adjacent branches or another PR.

For an unmerged PR, close it with a concise evidence receipt before deleting the exact head. After
deletion, fetch/prune, confirm the intended PR state, and perform the exact absence check above.
