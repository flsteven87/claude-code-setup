"""Decide the single next step for an unattended ticket batch.

One batch = one Linear parent ticket carrying the queue label, whose children
`to-tickets` published with their blocking edges. The human applies that one
label and leaves; every ticket lands as a commit on one shared batch branch,
in dependency order, and the batch ends as one pull request.

Shared by the Orca automation's precheck (exit 0 = there is a step to take)
and by the /batch-step command that then takes it, so the two can never
disagree about what state the batch is in.

Why one branch and not a worker per ticket: parallel workers buy wall-clock
time, and wall-clock time is worth nothing while the human is asleep. What it
costs is real - two workers branched from the same tip merge cleanly whenever
they touch different lines, even when they made incompatible assumptions about
a shared schema, so the merged tree neither worker tested can be green and
wrong. A single writer removes that failure mode rather than policing it.

"Landed" is therefore a git fact, never a Linear state: the ticket's commit is
reachable from the batch branch. Linear states can be edited by anyone and lag
reality; the branch is the ground truth the pull request will actually carry.

Emits one JSON decision. Exit 0 when an action is due, 1 when the batch is
idle or absent, 2 on a real failure - a batch that cannot be read must never
look like a batch with nothing to do.
"""

import argparse
import json
import subprocess
import sys

QUEUE_LABEL = "agent-queue"
CHILD_LABEL = "ready-for-agent"
CLAIMED_STATE_TYPE = "started"


def orca(*args: str) -> dict:
    proc = subprocess.run(["orca", *args, "--json"], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(f"orca {' '.join(args)} exited {proc.returncode}: {proc.stderr.strip()}")
    payload = json.loads(proc.stdout)
    if not payload.get("ok"):
        raise RuntimeError(f"orca {' '.join(args)}: {json.dumps(payload.get('error'))}")
    return payload["result"]


def git(repo: str, *args: str) -> str:
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=30)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def state_of(issue: dict) -> tuple[str, str]:
    state = issue.get("state") or {}
    if isinstance(state, str):
        return state, ""
    return state.get("name") or "", state.get("type") or ""


def labels_of(issue: dict) -> set[str]:
    names = (
        (label.get("name") if isinstance(label, dict) else label)
        for label in (issue.get("labels") or [])
    )
    return {name for name in names if name}


def has_landed(repo: str, branch: str, identifier: str) -> bool:
    """True when a commit naming this ticket is reachable from the batch branch.

    Requires the worker to put the Linear identifier in its commit subject or
    trailer, which the repo's own convention already asks for. Matching on the
    identifier rather than on a recorded SHA survives an amend or a squash.
    """
    if not git(repo, "rev-parse", "--verify", branch):
        return False
    return bool(git(repo, "log", branch, f"--grep={identifier}", "--format=%H", "-1"))


def pr_url_for(repo: str, branch: str) -> str:
    """The open pull request for the batch branch, if there is one."""
    proc = subprocess.run(
        ["gh", "pr", "list", "--head", branch, "--state", "open",
         "--json", "url", "--jq", ".[0].url"],
        cwd=repo, capture_output=True, text=True, timeout=30,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def blockers_of(identifier: str) -> list[dict]:
    """Blocking issues for one ticket.

    Relations hang off result.relations, beside result.issue rather than inside
    it; reading them off the issue object yields an empty list, which would
    turn a dependency graph into no dependencies at all and release the whole
    batch at once. Linear stores each edge twice - `blocks` on the blocker and
    `blockedBy` on the blocked issue - so read one direction only.
    """
    relations = orca("linear", "issue", identifier, "--relations").get("relations") or []
    return [
        relation.get("relatedIssue") or {}
        for relation in relations
        if relation.get("relationship") == "blockedBy"
    ]


def decide(args) -> tuple[dict, int]:
    parents = [
        issue
        for issue in orca(
            "linear", "list-issues", "--team", args.team, "--label", args.label, "--limit", "20"
        ).get("issues") or []
        if state_of(issue)[1] not in {"completed", "canceled"}
    ]
    if not parents:
        return {"action": "none", "reason": f"no open ticket carries the {args.label} label"}, 1

    # One batch at a time. Serialising batches costs nothing the human is
    # waiting for and keeps one branch, one PR, one thing to reason about.
    parent = sorted(parents, key=lambda i: i["identifier"])[0]
    batch = parent["identifier"]
    branch = f"agent/{batch.lower()}"

    children = [
        issue
        for issue in orca(
            "linear", "list-issues", "--parent-id", batch, "--limit", "100"
        ).get("issues") or []
        if CHILD_LABEL in labels_of(issue)
    ]
    if not children:
        return {"action": "none", "batch": batch,
                "reason": f"{batch} has no {CHILD_LABEL} children - run to-tickets first"}, 1

    landed, in_progress, pending = [], [], []
    for child in children:
        identifier = child["identifier"]
        if has_landed(args.repo, branch, identifier):
            landed.append(identifier)
        elif state_of(child)[1] == CLAIMED_STATE_TYPE:
            in_progress.append(identifier)
        else:
            pending.append(child)

    common = {
        "batch": batch, "branch": branch, "repo": args.repo,
        "landed": landed, "inProgress": in_progress,
        "pending": [c["identifier"] for c in pending],
    }

    # A claimed-but-unlanded ticket means a worker is mid-flight. One writer at
    # a time is the whole safety argument, so nothing else may start.
    if in_progress:
        return {**common, "action": "none",
                "reason": f"worker running on {', '.join(in_progress)}"}, 1

    frontier, stuck = [], []
    for child in pending:
        unmet = [
            blocker.get("identifier")
            for blocker in blockers_of(child["identifier"])
            if blocker.get("identifier") not in landed
        ]
        (stuck if unmet else frontier).append(
            {"identifier": child["identifier"], "title": child.get("title"),
             "priority": child.get("priority"), "blockedBy": unmet}
        )

    if frontier:
        frontier.sort(key=lambda t: (t["priority"] or 99, t["identifier"]))
        return {**common, "action": "implement", "ticket": frontier[0],
                "ready": [t["identifier"] for t in frontier]}, 0

    if not landed:
        return {**common, "action": "none",
                "reason": "nothing landed and nothing startable - check the blocking edges"}, 1

    # Check for the PR here, not in the caller. A five-minute poll reaches this
    # branch on every tick once the batch is complete, so a delivery that does
    # not notice its own pull request opens a second one every five minutes.
    if pr_url_for(args.repo, branch):
        return {**common, "action": "none", "reason": "pull request already open"}, 1

    # Frontier empty with work landed: the batch is as complete as it will get.
    # Stuck tickets are reported, never silently dropped - a partial batch that
    # is presented as finished is the one failure the human cannot catch.
    if stuck:
        return {**common, "action": "deliver_partial", "stuck": stuck}, 0
    return {**common, "action": "deliver"}, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", required=True, help="Linear team key, e.g. NEX")
    parser.add_argument("--repo", required=True, help="path to the batch worktree")
    parser.add_argument("--label", default=QUEUE_LABEL,
                        help="queue label, applied to the PARENT ticket of a batch")
    parser.add_argument("--pr-open", action="store_true",
                        help="caller already knows a PR exists for the batch branch")
    args = parser.parse_args()

    decision, code = decide(args)
    print(json.dumps(decision, ensure_ascii=False))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # noqa: BLE001 - a precheck must fail loudly
        print(json.dumps({"action": "error", "error": str(error)}, ensure_ascii=False))
        print(f"linear_frontier: {error}", file=sys.stderr)
        sys.exit(2)
