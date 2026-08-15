#!/usr/bin/env python3
"""Reconcile the self-hosted Matt skills manifest with its marketplace source."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

UPSTREAM_MANIFEST = Path("plugins/marketplaces/mattpocock/.claude-plugin/plugin.json")
LOCAL_PLUGIN = Path("skills/mattpocock-skills")
LOCAL_MANIFEST = LOCAL_PLUGIN / ".claude-plugin/plugin.json"
EXCLUDED_SKILLS = {"./skills/productivity/handoff"}
LOCAL_PLUGIN_ID = "mattpocock-skills@skills-dir"
SHADOWING_PLUGIN_ID = "mattpocock-skills@mattpocock"


class ReconciliationError(RuntimeError):
    """Raised when the Matt skill source, manifest, or runtime is inconsistent."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ReconciliationError(f"missing manifest: {path}") from error
    except json.JSONDecodeError as error:
        raise ReconciliationError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ReconciliationError(f"manifest must contain a JSON object: {path}")
    return value


def desired_skills(upstream: dict[str, Any]) -> list[str]:
    skills = upstream.get("skills")
    if not isinstance(skills, list) or not all(
        isinstance(skill, str) for skill in skills
    ):
        raise ReconciliationError("upstream manifest has no valid skills list")
    desired = [skill for skill in skills if skill not in EXCLUDED_SKILLS]
    if len(desired) != len(set(desired)):
        raise ReconciliationError("upstream manifest contains duplicate skill paths")
    return desired


def validate_source_layout(claude_home: Path, skills: list[str]) -> None:
    upstream_skills = (claude_home / UPSTREAM_MANIFEST).parents[1] / "skills"
    local_skills = claude_home / LOCAL_PLUGIN / "skills"
    if not local_skills.is_symlink():
        raise ReconciliationError(f"expected a skills symlink: {local_skills}")
    if local_skills.resolve() != upstream_skills.resolve():
        raise ReconciliationError(
            f"skills symlink points to {local_skills.resolve()}, expected {upstream_skills.resolve()}"
        )

    for skill in skills:
        relative = Path(skill.removeprefix("./"))
        skill_file = claude_home / LOCAL_PLUGIN / relative / "SKILL.md"
        if not skill_file.is_file():
            raise ReconciliationError(f"missing SKILL.md for {skill}: {skill_file}")


def reconciled_manifest(
    local: dict[str, Any], upstream: dict[str, Any], skills: list[str]
) -> dict[str, Any]:
    version = upstream.get("version")
    if not isinstance(version, str) or not version:
        raise ReconciliationError("upstream manifest has no valid version")
    reconciled = dict(local)
    reconciled["version"] = version
    reconciled["skills"] = skills
    return reconciled


def write_json_atomically(path: Path, value: dict[str, Any]) -> None:
    serialized = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as temporary:
        temporary.write(serialized)
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def run_claude(claude_bin: str, *arguments: str) -> str:
    try:
        result = subprocess.run(
            [claude_bin, *arguments], text=True, capture_output=True, check=False
        )
    except FileNotFoundError as error:
        raise ReconciliationError(f"Claude Code CLI not found: {claude_bin}") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ReconciliationError(f"claude {' '.join(arguments)} failed: {detail}")
    return result.stdout


def validate_runtime(
    claude_home: Path, claude_bin: str, expected_skills: list[str]
) -> None:
    local_plugin = (claude_home / LOCAL_PLUGIN).resolve()
    plugin_list_output = run_claude(claude_bin, "plugin", "list", "--json")
    try:
        plugins = json.loads(plugin_list_output)
    except json.JSONDecodeError as error:
        raise ReconciliationError(
            "claude plugin list --json returned invalid JSON"
        ) from error
    if not isinstance(plugins, list):
        raise ReconciliationError(
            "claude plugin list --json returned an unexpected value"
        )

    if any(
        plugin.get("id") == SHADOWING_PLUGIN_ID
        for plugin in plugins
        if isinstance(plugin, dict)
    ):
        raise ReconciliationError(
            f"shadowing marketplace plugin is installed: {SHADOWING_PLUGIN_ID}"
        )
    installed = next(
        (
            plugin
            for plugin in plugins
            if isinstance(plugin, dict) and plugin.get("id") == LOCAL_PLUGIN_ID
        ),
        None,
    )
    if installed is None or installed.get("enabled") is not True:
        raise ReconciliationError(
            f"runtime plugin is missing or disabled: {LOCAL_PLUGIN_ID}"
        )
    install_path = installed.get("installPath")
    if (
        not isinstance(install_path, str)
        or Path(install_path).resolve() != local_plugin
    ):
        raise ReconciliationError(
            f"runtime plugin path differs: {install_path!r}, expected {str(local_plugin)!r}"
        )

    run_claude(claude_bin, "plugin", "validate", str(local_plugin))
    details = run_claude(claude_bin, "plugin", "details", LOCAL_PLUGIN_ID)
    inventory = re.search(r"^\s*Skills \((\d+)\)\s+([^\n]+)$", details, re.MULTILINE)
    if inventory is None:
        raise ReconciliationError("could not read the runtime skill inventory")
    reported_count = int(inventory.group(1))
    reported_names = {
        name.strip() for name in inventory.group(2).split(",") if name.strip()
    }
    expected_names = {Path(skill).name for skill in expected_skills}
    if reported_count != len(expected_names) or reported_names != expected_names:
        missing = sorted(expected_names - reported_names)
        extra = sorted(reported_names - expected_names)
        raise ReconciliationError(
            "runtime skill inventory differs from manifest "
            f"(expected={len(expected_names)}, reported={reported_count}, "
            f"missing={missing}, extra={extra})"
        )


def reconcile(
    claude_home: Path, *, write: bool, runtime: bool, claude_bin: str
) -> None:
    upstream_path = claude_home / UPSTREAM_MANIFEST
    local_path = claude_home / LOCAL_MANIFEST
    upstream = load_object(upstream_path)
    local = load_object(local_path)
    skills = desired_skills(upstream)
    validate_source_layout(claude_home, skills)
    expected = reconciled_manifest(local, upstream, skills)

    if local != expected:
        if not write:
            raise ReconciliationError(
                "manifest is stale: run reconcile_matt_manifest.py --write"
            )
        write_json_atomically(local_path, expected)
        local = load_object(local_path)
        if local != expected:
            raise ReconciliationError("manifest remained stale after reconciliation")
        print(f"Reconciled Matt manifest: {len(skills)} skills")
    else:
        print(f"Matt manifest is current: {len(skills)} skills")

    if runtime:
        validate_runtime(claude_home, claude_bin, skills)
        print(f"Claude runtime inventory is current: {len(skills)} skills")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check", action="store_true", help="fail when the local manifest is stale"
    )
    mode.add_argument(
        "--write", action="store_true", help="write the reconciled local manifest"
    )
    parser.add_argument(
        "--claude-home",
        type=Path,
        default=Path.home() / ".claude",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--runtime", action="store_true", help="verify Claude's loaded inventory"
    )
    parser.add_argument("--claude-bin", default="claude", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        reconcile(
            arguments.claude_home.expanduser().resolve(),
            write=arguments.write,
            runtime=arguments.runtime,
            claude_bin=arguments.claude_bin,
        )
    except ReconciliationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
