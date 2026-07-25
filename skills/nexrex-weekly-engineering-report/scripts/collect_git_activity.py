#!/usr/bin/env python3
"""Collect deterministic first-parent Git facts for a contributor report."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


FIELD = "\x1f"
RECORD = "\x1e"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--since", required=True, help="Inclusive ISO-8601 boundary with offset")
    parser.add_argument("--until", required=True, help="Exclusive ISO-8601 boundary with offset")
    parser.add_argument("--branch", default="main")
    parser.add_argument(
        "--author",
        action="append",
        required=True,
        help="Exact case-insensitive author name, email, or 'Name <email>'; repeatable",
    )
    return parser.parse_args()


def normalize_author(value: str) -> str:
    return " ".join(value.split()).casefold()


def parse_boundary(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"date boundary requires an explicit UTC offset: {value}")
    return parsed


def author_matches(name: str, email: str, aliases: set[str]) -> bool:
    candidates = {
        normalize_author(name),
        normalize_author(email),
        normalize_author(f"{name} <{email}>"),
    }
    return bool(candidates & aliases)


def conventional_type(subject: str) -> str:
    if subject.startswith("Merge pull request"):
        return "merge"
    match = re.match(r"([a-zA-Z][a-zA-Z0-9-]*)(?:\([^)]*\))?:", subject)
    return match.group(1).lower() if match else "other"


def top_level(path: str) -> str:
    """Return a stable top-level bucket for ordinary and rename numstat paths."""
    if " => " in path and "{" not in path:
        return "renames"
    prefix = path.split("{", 1)[0].rstrip("/")
    if prefix:
        return prefix.split("/", 1)[0]
    if path.startswith("{"):
        return "renames"
    return path.split("/", 1)[0]


def commit_numstat(repo: Path, sha: str, parents: str) -> str:
    if parents:
        first_parent = parents.split()[0]
        return git(repo, "diff", "--numstat", "--find-renames", first_parent, sha)
    return git(repo, "show", "--root", "--format=", "--numstat", "--find-renames", sha)


def baseline_before(repo: Path, branch: str, since: datetime) -> str:
    fmt = FIELD.join(["%H", "%aI"])
    raw = git(
        repo,
        "log",
        branch,
        "--first-parent",
        f"--until={since.isoformat()}",
        f"--format={fmt}",
    )
    for line in raw.splitlines():
        sha, date = line.split(FIELD, 1)
        if parse_boundary(date) < since:
            return sha
    return ""


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    since = parse_boundary(args.since)
    until = parse_boundary(args.until)
    if since >= until:
        raise ValueError("--since must be earlier than --until")
    aliases = {normalize_author(value) for value in args.author}
    fmt = FIELD.join(["%H", "%aI", "%an", "%ae", "%P", "%s", "%b"]) + RECORD
    git_since = (since - timedelta(seconds=1)).isoformat()
    raw = git(
        repo,
        "log",
        args.branch,
        "--first-parent",
        f"--since={git_since}",
        f"--until={args.until}",
        f"--format={fmt}",
    )

    commits: list[dict[str, object]] = []
    types: Counter[str] = Counter()
    top_levels: Counter[str] = Counter()
    unique_prs: set[int] = set()
    unique_tickets: set[str] = set()
    additions = deletions = file_entries = 0

    for record in raw.split(RECORD):
        record = record.strip("\n")
        if not record:
            continue
        sha, date, name, email, parents, subject, body = record.split(FIELD, 6)
        commit_date = parse_boundary(date)
        if not since <= commit_date < until:
            continue
        identity = f"{name} <{email}>"
        if not author_matches(name, email, aliases):
            continue

        numstat = commit_numstat(repo, sha, parents)
        changed_files: list[str] = []
        commit_add = commit_del = 0
        for line in numstat.splitlines():
            added, deleted, path = line.split("\t", 2)
            changed_files.append(path)
            top_levels[top_level(path)] += 1
            file_entries += 1
            if added.isdigit():
                commit_add += int(added)
            if deleted.isdigit():
                commit_del += int(deleted)

        additions += commit_add
        deletions += commit_del
        commit_type = conventional_type(subject)
        types[commit_type] += 1
        text = f"{subject}\n{body}"
        unique_prs.update(int(value) for value in re.findall(r"#(\d+)", text))
        unique_tickets.update(value.upper() for value in re.findall(r"\bNEX-\d+\b", text, re.I))
        commits.append(
            {
                "sha": sha,
                "date": date,
                "author": identity,
                "subject": subject,
                "type": commit_type,
                "additions": commit_add,
                "deletions": commit_del,
                "files": changed_files,
            }
        )

    baseline = baseline_before(repo, args.branch, since)
    output = {
        "scope": {
            "repo": str(repo),
            "branch": args.branch,
            "since": args.since,
            "until_exclusive": args.until,
            "author_patterns": args.author,
            "baseline": baseline,
        },
        "summary": {
            "mainline_commits": len(commits),
            "unique_prs_referenced": len(unique_prs),
            "pr_numbers": sorted(unique_prs),
            "ticket_ids_referenced": sorted(unique_tickets),
            "gross_additions": additions,
            "gross_deletions": deletions,
            "file_change_entries": file_entries,
            "commit_types": dict(types.most_common()),
            "top_level_file_entries": dict(top_levels.most_common()),
        },
        "commits": commits,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
