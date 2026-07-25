#!/usr/bin/env python3
"""Inspect, reconcile, and verify Git state with conservative proof rules."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(
    r"(github_pat_[A-Za-z0-9_]+|gh[opsur]_[A-Za-z0-9_]{10,}|"
    r"glpat-[A-Za-z0-9_-]{10,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"sk-[A-Za-z0-9]{20,})"
)
CREDENTIAL_URL_RE = re.compile(r"(https?://)[^/\s:@]+(?::[^/\s@]*)?@")
PROTECTED_RE = re.compile(r"^(main|master|develop|release(?:/.*)?)$")


@dataclass(frozen=True)
class Result:
    command: list[str]
    exit_code: int
    output: str


@dataclass(frozen=True)
class Action:
    kind: str
    target: str
    command: list[str]
    evidence: str
    priority: int
    expected_oid: str


def redact(text: str) -> str:
    text = CREDENTIAL_URL_RE.sub(r"\1<redacted>@", text)
    return TOKEN_RE.sub("<redacted-token>", text)


def run(
    args: list[str],
    *,
    cwd: Path,
    input_text: str | None = None,
    timeout: int = 180,
) -> Result:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd),
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
            env={**os.environ, "LC_ALL": "C"},
        )
        return Result(args, completed.returncode, redact((completed.stdout or "").strip()))
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        return Result(args, 124, redact(f"{output}\nTimed out after {timeout}s".strip()))


def git(args: list[str], *, cwd: Path, timeout: int = 180) -> Result:
    return run(["git", *args], cwd=cwd, timeout=timeout)


def output(args: list[str], *, cwd: Path) -> str:
    result = git(args, cwd=cwd)
    return result.output if result.exit_code == 0 else ""


def resolve_repo(path: Path) -> Path:
    result = git(["rev-parse", "--show-toplevel"], cwd=path)
    if result.exit_code != 0:
        raise RuntimeError(result.output or "Not a Git repository")
    return Path(result.output).resolve()


def default_remote_ref(repo: Path) -> tuple[str, str, str]:
    symbolic = git(
        ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        cwd=repo,
    )
    if symbolic.exit_code == 0 and "/" in symbolic.output:
        remote, branch = symbolic.output.split("/", 1)
        return remote, branch, symbolic.output

    for remote, branch in (("origin", "main"), ("origin", "master")):
        ref = f"{remote}/{branch}"
        if git(["rev-parse", "--verify", "--quiet", ref], cwd=repo).exit_code == 0:
            return remote, branch, ref
    raise RuntimeError("No default remote branch found (origin/HEAD, origin/main, origin/master)")


def status_counts(repo: Path) -> dict[str, Any]:
    result = git(["status", "--porcelain=v1", "-uall"], cwd=repo)
    staged = unstaged = untracked = 0
    entries: list[str] = []
    for line in result.output.splitlines():
        if not line:
            continue
        entries.append(line)
        if line.startswith("??"):
            untracked += 1
            continue
        if len(line) >= 2:
            staged += int(line[0] not in (" ", "?"))
            unstaged += int(line[1] not in (" ", "?"))
    return {
        "clean": staged == 0 and unstaged == 0 and untracked == 0,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "entries": entries,
    }


def parse_worktrees(repo: Path) -> list[dict[str, Any]]:
    raw = output(["worktree", "list", "--porcelain"], cwd=repo)
    records: list[dict[str, str | bool]] = []
    record: dict[str, str | bool] = {}
    for line in [*raw.splitlines(), ""]:
        if not line:
            if record:
                records.append(record)
                record = {}
            continue
        key, separator, value = line.partition(" ")
        record[key] = value if separator else True

    worktrees: list[dict[str, Any]] = []
    for item in records:
        path = Path(str(item["worktree"]))
        branch_ref = str(item.get("branch", ""))
        branch = branch_ref.removeprefix("refs/heads/") if branch_ref else ""
        dirty: dict[str, Any] | None
        if path.exists():
            dirty = status_counts(path)
        else:
            dirty = None
        worktrees.append(
            {
                "path": str(path),
                "head": str(item.get("HEAD", "")),
                "branch": branch,
                "detached": bool(item.get("detached", False)),
                "locked": bool(item.get("locked", False)),
                "prunable": bool(item.get("prunable", False)),
                "status": dirty,
            }
        )
    return worktrees


def ahead_behind(repo: Path, upstream: str, branch: str) -> tuple[int, int]:
    if not upstream:
        return 0, 0
    result = git(
        ["rev-list", "--left-right", "--count", f"{upstream}...{branch}"], cwd=repo
    )
    if result.exit_code != 0:
        return 0, 0
    left, right = result.output.split()
    return int(right), int(left)


def local_branches(repo: Path) -> list[dict[str, Any]]:
    raw = output(
        [
            "for-each-ref",
            "--format=%(refname:short)%09%(objectname)%09%(upstream:short)%09%(upstream:track)",
            "refs/heads",
        ],
        cwd=repo,
    )
    current = output(["branch", "--show-current"], cwd=repo)
    branches: list[dict[str, Any]] = []
    for line in raw.splitlines():
        name, oid, upstream, track = (line.split("\t") + ["", "", "", ""])[:4]
        ahead, behind = ahead_behind(repo, upstream, name)
        branches.append(
            {
                "name": name,
                "oid": oid,
                "upstream": upstream,
                "track": track,
                "ahead": ahead,
                "behind": behind,
                "current": name == current,
                "protected": bool(PROTECTED_RE.fullmatch(name)),
            }
        )
    return branches


def remote_branches(repo: Path, remote: str) -> list[dict[str, str]]:
    raw = output(
        [
            "for-each-ref",
            "--format=%(refname)%09%(objectname)",
            f"refs/remotes/{remote}",
        ],
        cwd=repo,
    )
    branches: list[dict[str, str]] = []
    for line in raw.splitlines():
        full_name, oid = (line.split("\t") + [""])[:2]
        prefix = f"refs/remotes/{remote}/"
        if full_name == f"{prefix}HEAD" or not full_name.startswith(prefix):
            continue
        short = full_name.removeprefix(prefix)
        branches.append({"name": short, "ref": f"{remote}/{short}", "oid": oid})
    return branches


def snapshot(repo: Path, *, edge_checks: bool = False) -> dict[str, Any]:
    remote, default_branch, default_ref = default_remote_ref(repo)
    head = output(["rev-parse", "HEAD"], cwd=repo)
    current = output(["branch", "--show-current"], cwd=repo) or "DETACHED"
    local = local_branches(repo)
    default_local = next((item for item in local if item["name"] == default_branch), None)
    default_sync = bool(default_local and default_local["oid"] == output(["rev-parse", default_ref], cwd=repo))
    stashes = output(
        ["stash", "list", "--date=iso", "--format=%gd%09%H%09%ci%09%s"], cwd=repo
    ).splitlines()
    remotes = output(["remote", "-v"], cwd=repo).splitlines()
    reflog = output(["reflog", "--date=iso", "-40"], cwd=repo).splitlines()
    shallow = output(["rev-parse", "--is-shallow-repository"], cwd=repo)
    edge: list[str] = []
    if edge_checks:
        edge = git(
            ["fsck", "--no-reflogs", "--unreachable", "--no-progress"],
            cwd=repo,
            timeout=240,
        ).output.splitlines()[:40]
    state = {
        "repo": str(repo),
        "head": head,
        "current_branch": current,
        "working_tree": status_counts(repo),
        "default_remote": remote,
        "default_branch": default_branch,
        "default_ref": default_ref,
        "default_synced": default_sync,
        "local_branches": local,
        "remote_branches": remote_branches(repo, remote),
        "stashes": stashes,
        "worktrees": parse_worktrees(repo),
        "remotes": [redact(line) for line in remotes],
        "reflog": reflog,
        "is_shallow": shallow,
        "edge_checks_run": edge_checks,
        "unreachable": edge,
    }
    state["state_token"] = state_token(state)
    return state


def state_token(state: dict[str, Any]) -> str:
    """Return a stable token for mutation-relevant repository state."""
    material = {
        "head": state["head"],
        "current_branch": state["current_branch"],
        "working_tree": state["working_tree"],
        "default_ref": state["default_ref"],
        "local_branches": state["local_branches"],
        "remote_branches": state["remote_branches"],
        "stashes": state["stashes"],
        "worktrees": state["worktrees"],
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return (
        git(["merge-base", "--is-ancestor", ancestor, descendant], cwd=repo).exit_code
        == 0
    )


def stable_patch_id(repo: Path, left: str, right: str) -> str:
    diff = subprocess.run(
        ["git", "diff", "--binary", left, right],
        cwd=str(repo),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if diff.returncode != 0 or not diff.stdout:
        return ""
    patch = subprocess.run(
        ["git", "patch-id", "--stable"],
        cwd=str(repo),
        input=diff.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if patch.returncode != 0 or not patch.stdout:
        return ""
    return patch.stdout.decode(errors="replace").split()[0]


@functools.lru_cache(maxsize=8)
def all_merged_prs(repo_text: str) -> tuple[dict[str, list[dict[str, Any]]], str | None]:
    repo = Path(repo_text)
    if shutil.which("gh") is None:
        return {}, "gh unavailable"
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "1000",
            "--json",
            "number,headRefName,baseRefName,mergeCommit,url",
        ],
        cwd=repo,
    )
    if result.exit_code != 0:
        return {}, f"gh failed: {result.output}"
    try:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for pr in json.loads(result.output or "[]"):
            grouped.setdefault(pr.get("headRefName", ""), []).append(pr)
        return grouped, None
    except json.JSONDecodeError:
        return {}, "gh returned invalid JSON"


def merged_prs(repo: Path, branch: str) -> tuple[list[dict[str, Any]], str | None]:
    grouped, error = all_merged_prs(str(repo))
    if error or grouped.get(branch):
        return grouped.get(branch, []), error
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--head",
            branch,
            "--limit",
            "10",
            "--json",
            "number,headRefName,baseRefName,mergeCommit,url",
        ],
        cwd=repo,
    )
    if result.exit_code != 0:
        return [], f"gh failed: {result.output}"
    try:
        return json.loads(result.output or "[]"), None
    except json.JSONDecodeError:
        return [], "gh returned invalid JSON"


@functools.lru_cache(maxsize=8)
def open_pr_heads(repo_text: str) -> tuple[set[str], str | None]:
    repo = Path(repo_text)
    if shutil.which("gh") is None:
        return set(), "gh unavailable"
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "1000",
            "--json",
            "headRefName",
        ],
        cwd=repo,
    )
    if result.exit_code != 0:
        return set(), f"gh failed: {result.output}"
    try:
        return {item["headRefName"] for item in json.loads(result.output or "[]")}, None
    except (json.JSONDecodeError, KeyError):
        return set(), "gh returned invalid open-PR JSON"


def merge_proof(
    repo: Path,
    *,
    branch_name: str,
    branch_ref: str,
    default_branch: str,
    default_ref: str,
    require_pr: bool = False,
) -> tuple[str | None, str | None]:
    reachable = is_ancestor(repo, branch_ref, default_ref)
    if reachable and not require_pr:
        return f"{branch_ref} is reachable from {default_ref}", None

    prs, error = merged_prs(repo, branch_name)
    if error:
        return None, error
    exact_prs = [
        pr
        for pr in prs
        if pr.get("headRefName") == branch_name
        and pr.get("baseRefName") == default_branch
    ]
    if reachable and exact_prs:
        return (
            f"PR #{exact_prs[0]['number']} merged exact head {branch_name}; "
            f"tip is reachable from {default_ref}",
            None,
        )
    merge_base = output(["merge-base", default_ref, branch_ref], cwd=repo)
    branch_patch = stable_patch_id(repo, merge_base, branch_ref) if merge_base else ""
    if not branch_patch:
        return None, "branch cumulative patch-id unavailable"

    for pr in exact_prs:
        merge_commit = (pr.get("mergeCommit") or {}).get("oid")
        if not merge_commit:
            continue
        if git(["cat-file", "-e", f"{merge_commit}^{{commit}}"], cwd=repo).exit_code != 0:
            continue
        merge_patch = stable_patch_id(repo, f"{merge_commit}^", merge_commit)
        if merge_patch and merge_patch == branch_patch:
            return (
                f"PR #{pr['number']} merged exact head {branch_name}; cumulative patch-id matches",
                None,
            )
    return None, "no exact merged PR with matching cumulative patch-id"


def remote_names_pointing_at(repo: Path, remote: str, oid: str) -> list[str]:
    raw = output(
        [
            "for-each-ref",
            f"--points-at={oid}",
            "--format=%(refname)",
            f"refs/remotes/{remote}",
        ],
        cwd=repo,
    )
    return [
        line.removeprefix(f"refs/remotes/{remote}/")
        for line in raw.splitlines()
        if line and line != f"refs/remotes/{remote}/HEAD"
    ]


def protected_sync_proof(
    repo: Path,
    *,
    branch: dict[str, Any],
    remote: str,
    default_branch: str,
    default_ref: str,
) -> tuple[str | None, str | None]:
    if branch["oid"] == output(["rev-parse", default_ref], cwd=repo):
        return "already synchronized", None
    if is_ancestor(repo, branch["name"], default_ref):
        return f"{branch['name']} is behind-only relative to {default_ref}", None
    errors: list[str] = []
    for remote_name in remote_names_pointing_at(repo, remote, branch["oid"]):
        proof, error = merge_proof(
            repo,
            branch_name=remote_name,
            branch_ref=branch["name"],
            default_branch=default_branch,
            default_ref=default_ref,
        )
        if proof:
            return f"local tip also equals {remote}/{remote_name}; {proof}", None
        if error:
            errors.append(f"{remote_name}: {error}")
    return None, "; ".join(errors) or "protected branch has unproven unique work"


def worktree_by_branch(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["branch"]: item
        for item in state["worktrees"]
        if item.get("branch")
    }


def build_plan(
    repo: Path,
    *,
    scope: str,
    remote_prefix: str,
) -> dict[str, Any]:
    state = snapshot(repo)
    remote = state["default_remote"]
    default_branch = state["default_branch"]
    default_ref = state["default_ref"]
    current = state["current_branch"]
    worktrees = worktree_by_branch(state)
    actions: list[Action] = []
    blocked: list[dict[str, str]] = []
    handled: set[str] = set()

    if state["is_shallow"] == "true":
        blocked.append({"target": str(repo), "reason": "shallow history cannot prove cleanup"})
        return {"scope": scope, "before": state, "actions": [], "blocked": blocked}

    for item in state["worktrees"]:
        path = Path(item["path"])
        if path.resolve() == repo.resolve():
            continue
        branch_name = item.get("branch", "")
        if item["detached"] or item["locked"] or item["prunable"] or item["status"] is None:
            blocked.append({"target": item["path"], "reason": "detached/locked/prunable/missing worktree"})
            continue
        if not item["status"]["clean"]:
            blocked.append({"target": item["path"], "reason": "dirty worktree"})
            continue
        if not branch_name or PROTECTED_RE.fullmatch(branch_name):
            blocked.append({"target": item["path"], "reason": "protected or unidentified worktree branch"})
            continue
        proof, error = merge_proof(
            repo,
            branch_name=branch_name,
            branch_ref=branch_name,
            default_branch=default_branch,
            default_ref=default_ref,
        )
        if not proof:
            blocked.append({"target": item["path"], "reason": error or "merge unproven"})
            continue
        force = not is_ancestor(repo, branch_name, default_ref)
        actions.extend(
            [
                Action("remove-worktree", item["path"], ["git", "worktree", "remove", item["path"]], proof, 30, item["head"]),
                Action("delete-local", branch_name, ["git", "branch", "-D" if force else "-d", branch_name], proof, 40, item["head"]),
            ]
        )
        handled.add(branch_name)

    for branch in state["local_branches"]:
        name = branch["name"]
        if name in handled or (name == current and not branch["protected"]):
            continue
        if branch["protected"]:
            target_ref = default_ref if name == default_branch else branch["upstream"]
            if not target_ref or branch["oid"] == output(["rev-parse", target_ref], cwd=repo):
                continue
            attached = worktrees.get(name)
            if attached and attached["status"] and not attached["status"]["clean"]:
                blocked.append({"target": name, "reason": "protected branch has a dirty worktree"})
                continue
            proof, error = protected_sync_proof(
                repo,
                branch=branch,
                remote=remote,
                default_branch=default_branch,
                default_ref=target_ref,
            )
            if proof:
                behind_only = is_ancestor(repo, name, target_ref)
                if attached:
                    if behind_only:
                        actions.append(
                            Action(
                                "sync-protected",
                                name,
                                ["git", "-C", attached["path"], "merge", "--ff-only", target_ref],
                                proof,
                                20,
                                branch["oid"],
                            )
                        )
                    else:
                        blocked.append(
                            {
                                "target": name,
                                "reason": "checked-out protected branch needs a non-fast-forward ref repair",
                            }
                        )
                else:
                    actions.append(Action("sync-protected", name, ["git", "branch", "-f", name, target_ref], proof, 20, branch["oid"]))
            else:
                blocked.append({"target": name, "reason": error or "sync proof unavailable"})
            continue

        if name in worktrees:
            blocked.append({"target": name, "reason": "branch remains attached to a worktree"})
            continue
        proof, error = merge_proof(
            repo,
            branch_name=name,
            branch_ref=name,
            default_branch=default_branch,
            default_ref=default_ref,
        )
        if proof:
            force = not is_ancestor(repo, name, default_ref)
            actions.append(Action("delete-local", name, ["git", "branch", "-D" if force else "-d", name], proof, 40, branch["oid"]))
        else:
            blocked.append({"target": name, "reason": error or "merge unproven"})

    if scope == "finish":
        current_branch = next(
            (item for item in state["local_branches"] if item["name"] == current), None
        )
        if current_branch and not current_branch["protected"]:
            if not state["working_tree"]["clean"]:
                blocked.append({"target": current, "reason": "current worktree is dirty; push skipped"})
            else:
                matching = f"{remote}/{current}"
                matching_exists = git(["rev-parse", "--verify", "--quiet", matching], cwd=repo).exit_code == 0
                if matching_exists:
                    if is_ancestor(repo, matching, current):
                        remote_is_behind = output(["rev-parse", matching], cwd=repo) != current_branch["oid"]
                        upstream_mismatch = current_branch["upstream"] != matching
                        if remote_is_behind or upstream_mismatch:
                            command = ["git", "push"]
                            if upstream_mismatch:
                                command.append("-u")
                            command.extend([remote, current])
                            evidence = (
                                f"{matching} is behind-only"
                                if remote_is_behind
                                else f"current upstream is {current_branch['upstream'] or 'unset'}"
                            )
                            actions.append(Action("push-current", current, command, evidence, 10, current_branch["oid"]))
                    elif not is_ancestor(repo, current, matching):
                        blocked.append({"target": current, "reason": f"{matching} diverged; push skipped"})
                elif not is_ancestor(repo, current, default_ref):
                    actions.append(Action("push-current", current, ["git", "push", "-u", remote, current], "clean feature branch has no matching upstream", 10, current_branch["oid"]))

        open_heads, open_error = open_pr_heads(str(repo))
        for item in state["remote_branches"]:
            name = item["name"]
            if name == current or name == default_branch or PROTECTED_RE.fullmatch(name):
                continue
            if remote_prefix and not name.startswith(remote_prefix):
                continue
            if open_error:
                blocked.append({"target": item["ref"], "reason": open_error})
                continue
            if name in open_heads:
                blocked.append({"target": item["ref"], "reason": "branch is the head of an open PR"})
                continue
            proof, error = merge_proof(
                repo,
                branch_name=name,
                branch_ref=item["ref"],
                default_branch=default_branch,
                default_ref=default_ref,
                require_pr=True,
            )
            if proof:
                actions.append(Action("delete-remote", name, ["git", "push", remote, "--delete", name], proof, 50, item["oid"]))
            else:
                blocked.append({"target": item["ref"], "reason": error or "merge unproven"})

    ordered = sorted(actions, key=lambda action: (action.priority, action.target))
    return {
        "scope": scope,
        "before": state,
        "actions": [asdict(action) for action in ordered],
        "blocked": blocked,
    }


def verify_action(repo: Path, action: dict[str, Any], remote: str) -> str | None:
    """Return a refusal reason if an action target changed after planning."""
    kind = action["kind"]
    target = action["target"]
    expected = action["expected_oid"]
    if kind == "remove-worktree":
        path = Path(target)
        if not path.exists() or output(["rev-parse", "HEAD"], cwd=path) != expected:
            return "worktree target moved or disappeared"
        if not status_counts(path)["clean"]:
            return "worktree became dirty"
    elif kind in {"delete-local", "sync-protected", "push-current"}:
        if output(["rev-parse", f"refs/heads/{target}"], cwd=repo) != expected:
            return "local branch target moved or disappeared"
        if kind == "push-current" and not status_counts(repo)["clean"]:
            return "current worktree became dirty"
    elif kind == "delete-remote":
        if output(["rev-parse", f"refs/remotes/{remote}/{target}"], cwd=repo) != expected:
            return "remote-tracking target moved or disappeared"
        open_pr_heads.cache_clear()
        open_heads, error = open_pr_heads(str(repo))
        if error:
            return error
        if target in open_heads:
            return "branch became the head of an open PR"
    return None


def apply_plan(repo: Path, plan: dict[str, Any]) -> dict[str, Any]:
    current = snapshot(repo)
    planned_token = plan["before"].get("state_token")
    if not planned_token or current["state_token"] != planned_token:
        return {
            **plan,
            "executed": [],
            "after": current,
            "success": False,
            "stale": True,
            "error": "repository state changed after planning; regenerate the plan",
        }
    executed: list[dict[str, Any]] = []
    for action in plan["actions"]:
        refusal = verify_action(repo, action, plan["before"]["default_remote"])
        if refusal:
            executed.append({**action, "exit_code": 5, "output": refusal})
            break
        result = run(action["command"], cwd=repo)
        executed.append({**action, "exit_code": result.exit_code, "output": result.output})
        if result.exit_code != 0:
            break
    return {
        **plan,
        "executed": executed,
        "after": snapshot(repo),
        "success": len(executed) == len(plan["actions"])
        and all(item["exit_code"] == 0 for item in executed),
        "stale": False,
    }


def fetch(repo: Path) -> Result:
    return git(["fetch", "--all", "--prune", "--tags"], cwd=repo)


def render(payload: dict[str, Any], command: str) -> str:
    state = payload.get("after") or payload.get("before") or payload
    tree = state["working_tree"]
    branches = state["local_branches"]
    current = next((item for item in branches if item["current"]), None)
    tree_summary = (
        "clean"
        if tree["clean"]
        else (
            f"{tree['staged']} staged, {tree['unstaged']} unstaged, "
            f"{tree['untracked']} untracked"
        )
    )
    lines = [
        "# Git Main Convergence",
        "",
        f"- Repo: {state['repo']}",
        f"- Current: {state['current_branch']} @ {state['head'][:10]}",
        f"- Working tree: {tree_summary}",
        f"- Current tracking: {current['upstream'] if current else 'detached'}"
        + (f" ({current['ahead']} ahead, {current['behind']} behind)" if current else ""),
        f"- Default branch synced: {state['default_synced']}",
        f"- Local / remote branches: {len(branches)} / {len(state['remote_branches'])}",
        f"- Stashes / worktrees: {len(state['stashes'])} / {len(state['worktrees'])}",
        f"- Recovery edge checks: {'run' if state['edge_checks_run'] else 'not run'}",
    ]
    if command in ("plan", "apply"):
        lines.extend(["", "## Actions"])
        actions = payload.get("actions", [])
        if not actions:
            lines.append("- none")
        for action in actions:
            result = ""
            if command == "apply":
                executed = next(
                    (item for item in payload.get("executed", []) if item["command"] == action["command"]),
                    None,
                )
                result = f" -> exit {executed['exit_code']}" if executed else " -> not run"
            lines.append(f"- {action['kind']}: {action['target']} ({action['evidence']}){result}")
        lines.extend(["", "## Remaining exceptions"])
        blocked = payload.get("blocked", [])
        if not blocked:
            lines.append("- none")
        else:
            lines.extend(f"- {item['target']}: {item['reason']}" for item in blocked)
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="Collect read-only repository state")
    audit.add_argument("path", nargs="?", default=os.getcwd())
    audit.add_argument("--fetch", action="store_true")
    audit.add_argument("--edge-checks", action="store_true")
    audit.add_argument("--json", action="store_true")
    for name in ("plan", "apply"):
        command = subparsers.add_parser(name, help=f"{name.title()} a reconciliation pass")
        command.add_argument("path", nargs="?", default=os.getcwd())
        command.add_argument("--scope", choices=("tidy", "finish"), required=True)
        command.add_argument("--remote-prefix", default="codex/")
        command.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        repo = resolve_repo(Path(args.path).resolve())
        if args.command == "audit":
            if args.fetch:
                fetched = fetch(repo)
                if fetched.exit_code != 0:
                    print(f"Fetch failed: {fetched.output}", file=sys.stderr)
                    return 3
            payload = snapshot(repo, edge_checks=args.edge_checks)
        else:
            fetched = fetch(repo)
            if fetched.exit_code != 0:
                print(f"Fetch failed: {fetched.output}", file=sys.stderr)
                return 3
            payload = build_plan(repo, scope=args.scope, remote_prefix=args.remote_prefix)
            if args.command == "apply":
                payload = apply_plan(repo, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else render(payload, args.command))
        if args.command == "apply" and not payload["success"]:
            return 4
        return 0
    except (RuntimeError, ValueError) as exc:
        print(redact(str(exc)), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
