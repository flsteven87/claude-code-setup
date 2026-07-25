---
name: git-converge-main
description: Converge the invoking user's and Codex-owned Git artifacts into a clean, current default branch. Use to audit or reconcile branches, worktrees, stashes, recovery commits, and PRs; remove local and remote branches integrated into main; or salvage and deliver valuable survivors. Treat unowned work as external unless explicitly named.
---

# Git Main Convergence

Make the protected default branch the truthful terminal state. Own the whole reconciliation loop so
the user does not need separate audit, hygiene, and cleanup workflows.

## Default behavior

Infer intent instead of offering modes:

- An explicit audit, explanation, or plan request is read-only except for fetch when current remote
  truth was requested.
- A bare `/git-converge-main` refreshes remote truth, fast-forwards a safe behind-only default
  branch, removes mechanically proven merged owned local branches/worktrees, deletes eligible owned
  remote heads of merged PRs, and deeply classifies every owned survivor.
- Treat proof of merge as the `DROP` decision and perform the authorized local cleanup. For a
  repository-hosted PR head, also perform remote cleanup when the merged-head predicates in
  [references/safety-and-authorization.md](references/safety-and-authorization.md) are all proven.
- Treat an owned local recovery snapshot as `DROP` without reconfirmation when a later successor is
  proven to be the landed result and complete patch review finds no valuable semantic unique to the
  snapshot. Record the whole rewrite family in one receipt, create no rescue ref, and leave
  unreferenced objects to normal Git garbage collection. This standing authorization does not
  authorize reflog rewriting or immediate garbage collection.
- An explicit request to execute, finish, merge, or leave `main` clean authorizes the normal local
  cleanup and feature-branch delivery needed to reach the terminal invariant.
- Unmerged remote deletion requires explicit item-level intent. Never generalize merged-head
  cleanup into namespace-wide deletion.

## Ownership boundary

Default to the joint work of the invoking user and Codex acting for that user. Establish ownership
before deep review or mutation:

- Resolve the current authenticated GitHub login from authoritative account metadata. Treat an
  exact PR-author match to that verified login as user-owned; for a PR, author identity is
  authoritative.
- Resolve local commit identities from the repository's effective Git configuration and any exact
  aliases explicitly supplied by the user or repository instructions. A user's commit inside a
  third-party-authored PR does not by itself make that PR user-owned.
- Treat a Codex branch/worktree as jointly owned only when current task records, reflog, or PR
  metadata proves Codex created it for this user. A `codex/` prefix alone is not ownership proof.
- Accept another alias only through verified GitHub identity metadata, effective Git configuration,
  or an explicit user declaration. Never infer ownership from a display name, organization
  membership, topic overlap, branch name, or the user's interest in it.

Inventory other-authored items only to avoid unsafe cleanup. Mark them `EXTERNAL` and stop after
minimal metadata unless they directly conflict with or block owned work. Do not automatically read
their full patch, investigate their CI, run Standards/Spec review, take them over, assign `ADAPT` or
`FINISH`, comment, close, merge, or delete their refs. If they affect owned work, inspect only the
narrow overlap needed and report them as dependencies. An explicit user request naming a
third-party PR or branch expands scope only to that exact item.

Never infer permission to force-push, reset unique work, delete a stash or recovery-only copy,
touch another author's PR, bypass protection, or run immediate garbage collection.

## 1. Establish safe control

Read repository instructions and identify the canonical default branch and its upstream. Snapshot
the current branch, status, operation state, remotes, branches, worktrees, stashes, and shallow flag
before switching or mutating anything.

Preserve dirty work in place. Do not switch, stash, clean, reset, commit, or move it merely to reach
the default branch. Stop the affected action on a merge/rebase in progress, shallow history, locked
or missing worktree, unresolved ownership, or missing credentials; continue independent read-only
classification when safe.

## 2. Refresh truth

Fetch all remote references and tags with prune. This integrates references, not code. Synchronize
only the canonical default branch with its configured upstream:

- fast-forward when behind-only and its worktree is clean;
- do nothing when equal;
- preserve and investigate local-only or diverged default-branch commits.

Fetch again after merges because bots or release automation may advance the branch.

## 3. Produce the mechanical plan

Resolve this skill's directory and use the bundled helper for inventory and proof-based actions:

```bash
skill_dir="$HOME/.claude/skills/git-converge-main"   # Codex: $HOME/.codex/skills/git-converge-main
python3 "$skill_dir/scripts/git_converge.py" audit "$repo" --fetch --edge-checks --json
python3 "$skill_dir/scripts/git_converge.py" plan "$repo" --scope tidy --json
```

The helper may prove integration by reachability or an exact merged PR plus matching cumulative
patch. Review the structured plan, then immediately use `apply` for proven-merged local actions
within the authorization above; do not ask the user to reconfirm them. `apply` refuses a stale plan
if mutation-relevant repository state changed after planning.

```bash
python3 "$skill_dir/scripts/git_converge.py" apply "$repo" --scope tidy --json
```

Do not substitute age, `[gone]`, names, subjects, `git cherry`, or similar shortstats for proof.
Use exact paths and ref names; never branch globs.

Separately enumerate repository-hosted PR head refs authored by the verified login. Classify every
still-live merged head against the merged-head predicates in
[references/safety-and-authorization.md](references/safety-and-authorization.md); the helper's
local plan does not replace this provider check.

## 4. Resolve every survivor

When any owned item survives mechanical cleanup, read
[references/semantic-convergence.md](references/semantic-convergence.md) completely. Read
[references/safety-and-authorization.md](references/safety-and-authorization.md) before any
destructive edge case or remote deletion.

Use the semantic protocol to maintain one decision record per survivor and assign exactly one of
`DROP`, `ADAPT`, `FINISH`, `RETAIN`, `BLOCKED`, or `EXTERNAL`. Do not act on a survivor until the
protocol's evidence and disposition criteria are complete.

## 5. Salvage and deliver valuable work

For `ADAPT` or noisy `FINISH`, start a fresh `codex/` branch from the refreshed default upstream.
Extract requirements and behavior rather than reviving stale topology. Prefer a minimal
reimplementation; cherry-pick only an isolated, current, non-duplicative commit.

Add focused regression tests, follow repository gates, and use `/code-review` when applicable.
Commit only the targeted delta, push, open or update the PR, resolve required checks, and merge
through the repository's normal policy when terminal delivery was authorized. Never use admin
bypasses.

## 6. Converge and prove completion

After every delivery, fetch/prune again, fast-forward the local default branch, remove the delivered
local branch/worktree, prune its eligible merged remote head, and re-run inventory. Continue until a
full pass produces no new actionable item.

For every eligible merged remote head:

1. Read the safety reference, then refresh and pin every input its merged-head contract requires.
2. Execute only when every predicate passes; otherwise preserve the ref with the failed predicate.
3. Delete the exact head ref and complete the reference's post-deletion absence proof. Record a
   provider-deleted ref only after the same proof passes.

For a semantic remote `DROP` that is open, closed-unmerged, moved after merge, or otherwise outside
the merged-head predicates, require explicit item-level authorization and follow the independent
review and closure protocol in the safety reference.

Declare completion only when:

- every worktree is clean, intentional, unlocked, and non-prunable;
- local default equals its refreshed upstream (`0/0` ahead/behind);
- no proven-merged disposable local branch/worktree remains;
- no eligible owned merged PR head remains on the repository remote;
- every stash, detached/reflog-only commit, and unreachable commit has a recorded disposition;
- delivered PRs and required CI are terminal;
- every remote deletion is verified after prune;
- remaining refs are explicitly active, other-owned, retained, or blocked.

Report compact before/after counts for owned artifacts, the owned decision table,
delivery/deletion receipts, unresolved owners or blockers, and whether recovery-edge checks ran.
Summarize external artifacts separately without turning them into work. Never call the repository
clean when only the current working tree is clean.
