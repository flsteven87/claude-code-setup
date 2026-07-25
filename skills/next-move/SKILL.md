---
name: next-move
description: Choose the next repository move by reconciling the codebase, Linear priorities, Git history, and explicit recent-session checkpoints. Use when deciding which engineering workstream should happen next, whether to resume or redirect active work, or what must close before starting something new.
---

# Next Move

Make a read-only portfolio decision. Select one immediate move from current evidence, not from
session momentum.

## Evidence contract

Let each source own its claims:

- Current source and tests own implemented behavior and confirmed code risk.
- Git owns what changed, merged, or remains only in the worktree.
- Linear owns team priority, issue state, relationships, and recorded acceptance evidence.
- Live systems own rollout and production state.
- The current conversation, repository-root `MEMORY.md`, and explicitly supplied handoffs or task
  IDs own recent-session intent.

Treat a session checkpoint as one workstream's perspective. Reconcile it with the other sources
before treating its objective or dependency order as repository priority.

Keep the investigation read-only. Recommend external writes, deployments, tracker changes, or
memory repair only behind their normal authorization boundary.

## 1. Frame the decision

Resolve the exact repository root and read applicable agent instructions. Identify candidate
workstreams from the user's question, current conversation, root `MEMORY.md`, branch name, working
tree, and ticket IDs in recent commits. Use only explicit handoffs or task IDs for prior-session
history; when none exist, state that historical session coverage is limited.

After the initial scan, shortlist at most three decision-relevant workstreams. Expand beyond them
only when concrete evidence could change the winner or runner-up.

**Complete when:** every candidate has a concrete outcome and at least one source pointer, and
unrelated repository activity is outside the comparison.

## 2. Reconcile Git

Start with:

```bash
git status --short --branch
git rev-parse HEAD
git log --first-parent --oneline -20
git log --oneline -40
git diff --stat
git diff --cached --stat
```

Inspect the bodies, files, and stats of commits that can change a candidate's state. Extract issue
identifiers from branches and commits. Use local history unless the user asks for remote
synchronization, and state that freshness boundary.

**Complete when:** every candidate-affecting recent change is mapped to its workstream and
classified as worktree-only, committed, merged, rollout-only, or unrelated.

## 3. Reconcile Linear

Use the connected Linear surface as the tracker source of truth. Resolve exact issue IDs before
searching by topic. Read each candidate's issue, parent, active children, relations, current state,
priority, assignee, and latest decision or rollout comments. Query narrowly in batches; expand
only when a parent, blocker, or recent commit reveals another decision-relevant issue.

When Linear is unavailable, retain the candidate but mark priority and workflow state unverified.
When Git and Linear disagree, describe the drift instead of silently choosing one.

**Complete when:** every candidate has current tracker state, remaining acceptance evidence,
blockers, and parent-program context, or an explicit Linear validation gap.

## 4. Verify the remaining code and operational delta

Read the smallest current source, tests, docs, and issue evidence needed to determine what remains.
Use a structural index only when repository policy calls for it, then verify against source.

For a rollout or live incident, inspect the relevant live system read-only when access is available.
Distinguish:

- confirmed user or production impact;
- confirmed code risk without observed production impact;
- design hypothesis;
- already completed work with stale tracking.

Assess reversibility: lost or corrupted source data, security exposure, and unsafe live rollouts
outrank regenerable projections or speculative improvements at equal priority.

**Complete when:** every candidate has a verified remaining delta, impact class, reversibility
class, and evidence confidence.

## 5. Rank the portfolio

Apply this decision ladder in order, allowing a materially higher severity to override an earlier
rung:

1. **Closure:** close an unsafe or partially verified live rollout before opening another
   workstream.
2. **Irreversibility:** prevent unrecoverable loss, security harm, or authority corruption before
   repairing regenerable output.
3. **Incidence:** prefer confirmed production impact over confirmed code risk, and confirmed code
   risk over hypothesis.
4. **Momentum:** finish a small, well-bounded active slice before starting a broad program.
5. **Unblocking:** prefer the narrow move that unlocks several urgent successors.
6. **Separation:** keep different failure domains independent; architecture dependency does not
   automatically determine delivery priority.

Use tracker priority as product intent, then adjust only with explicit evidence such as completed
Git work, stale issue state, a hazardous open rollout, or a more severe confirmed incident.

**Complete when:** one candidate wins as the immediate move, the runner-up is named, and the reason
the runner-up loses now is explicit.

## 6. Challenge the winner

Try to overturn the choice:

- Check whether it merely continues the latest session's momentum.
- Check whether Git already completed it while Linear remained stale.
- Check whether its supposed dependency mixes unrelated failure domains.
- Check whether another candidate has more irreversible or better-confirmed harm.
- Check whether the move can finish without new authority.
- Check whether its completion gate is observable.

Collect more evidence only when it could change the winner.

**Complete when:** no unresolved evidence is likely to flip the top two candidates, or the decision
is explicitly conditional on the named gap.

## 7. Report the next move

Reply in the user's language with:

- **Next move:** one bounded action, not a program slogan.
- **Why now:** the decisive Git, Linear, code, session, and live-state evidence.
- **Finish gate:** observable conditions that end the move.
- **Defer:** the important work that should not start yet and why.
- **After this:** the likely runner-up, clearly labeled as provisional.
- **Confidence:** verified facts, inference, freshness limits, and access gaps.

Use exact issue links and clickable local file pointers. Keep the evidence compact enough that the
user can approve, redirect, or execute immediately.

If the user also requested execution, finish this decision first, then use the applicable
implementation or operational skill under the original authorization boundary.
