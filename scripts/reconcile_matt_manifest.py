#!/usr/bin/env python3
"""Materialize the self-hosted Matt skills runtime from its marketplace source."""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
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


def skill_relative_path(skill: str) -> Path:
    if not skill.startswith("./skills/"):
        raise ReconciliationError(f"skill path must stay under ./skills: {skill}")
    relative = Path(skill.removeprefix("./"))
    if relative.is_absolute() or ".." in relative.parts:
        raise ReconciliationError(f"unsafe skill path: {skill}")
    return relative


def validate_source_layout(upstream_root: Path, skills: list[str]) -> None:
    resolved_root = upstream_root.resolve()
    names = [Path(skill).name for skill in skills]
    if len(names) != len(set(names)):
        raise ReconciliationError("desired skill names are not unique")

    for skill in skills:
        relative = skill_relative_path(skill)
        source = upstream_root / relative
        try:
            source.resolve().relative_to(resolved_root)
        except ValueError as error:
            raise ReconciliationError(f"skill source escapes marketplace root: {skill}") from error
        if source.is_symlink() or not source.is_dir():
            raise ReconciliationError(f"missing skill source directory: {source}")
        skill_file = source / "SKILL.md"
        if not skill_file.is_file() or skill_file.is_symlink():
            raise ReconciliationError(f"missing SKILL.md for {skill}: {skill_file}")
        for entry in source.rglob("*"):
            if entry.is_symlink():
                raise ReconciliationError(
                    f"skill source contains a symlink and cannot be self-contained: {entry}"
                )
            if not entry.is_dir() and not entry.is_file():
                raise ReconciliationError(
                    f"skill source contains an unsupported file type: {entry}"
                )


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


def expected_skill_entries(
    upstream_root: Path, skills: list[str]
) -> dict[Path, Path | None]:
    expected: dict[Path, Path | None] = {}

    def add(relative: Path, source: Path | None) -> None:
        previous = expected.get(relative)
        if previous is not None and previous != source:
            raise ReconciliationError(f"skill sources collide at runtime path: {relative}")
        if relative in expected and expected[relative] is None and source is not None:
            raise ReconciliationError(f"file collides with runtime directory: {relative}")
        expected[relative] = source

    for skill in skills:
        source_root = upstream_root / skill_relative_path(skill)
        runtime_root = skill_relative_path(skill).relative_to("skills")
        for parent in (runtime_root, *runtime_root.parents):
            if parent != Path("."):
                add(parent, None)
        for source in source_root.rglob("*"):
            relative = runtime_root / source.relative_to(source_root)
            add(relative, None if source.is_dir() else source)
    return expected


def validate_materialized_runtime(
    local_plugin: Path,
    upstream_root: Path,
    expected_manifest: dict[str, Any],
    skills: list[str],
) -> None:
    if local_plugin.is_symlink() or not local_plugin.is_dir():
        raise ReconciliationError(f"runtime plugin is not a real directory: {local_plugin}")

    root_entries = {entry.name for entry in local_plugin.iterdir()}
    if root_entries != {".claude-plugin", "skills"}:
        raise ReconciliationError(
            "runtime plugin has unexpected root entries "
            f"(found={sorted(root_entries)})"
        )

    metadata = local_plugin / ".claude-plugin"
    if metadata.is_symlink() or not metadata.is_dir():
        raise ReconciliationError("runtime plugin metadata must be a real directory")
    metadata_entries = {entry.name for entry in metadata.iterdir()}
    if metadata_entries != {"plugin.json"}:
        raise ReconciliationError("runtime plugin metadata layout differs")
    manifest_path = metadata / "plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ReconciliationError("runtime manifest must be a real file")
    if load_object(manifest_path) != expected_manifest:
        raise ReconciliationError("runtime manifest differs")

    local_skills = local_plugin / "skills"
    if local_skills.is_symlink() or not local_skills.is_dir():
        raise ReconciliationError("runtime skills must be a real directory")

    expected = expected_skill_entries(upstream_root, skills)
    actual: dict[Path, Path | None] = {}
    for entry in local_skills.rglob("*"):
        relative = entry.relative_to(local_skills)
        if entry.is_symlink():
            raise ReconciliationError(f"runtime contains a symlink: {relative}")
        if entry.is_dir():
            actual[relative] = None
        elif entry.is_file():
            actual[relative] = entry
        else:
            raise ReconciliationError(f"runtime contains an unsupported file: {relative}")

    if actual.keys() != expected.keys():
        missing = sorted(str(path) for path in expected.keys() - actual.keys())
        extra = sorted(str(path) for path in actual.keys() - expected.keys())
        raise ReconciliationError(
            f"runtime skill tree differs (missing={missing}, extra={extra})"
        )

    for relative, source in expected.items():
        materialized = actual[relative]
        if source is None:
            if materialized is not None:
                raise ReconciliationError(f"runtime path should be a directory: {relative}")
            continue
        if materialized is None or not filecmp.cmp(source, materialized, shallow=False):
            raise ReconciliationError(f"runtime file differs from marketplace: {relative}")
        if (source.stat().st_mode & 0o111) != (materialized.stat().st_mode & 0o111):
            raise ReconciliationError(
                f"runtime executable mode differs from marketplace: {relative}"
            )


def remove_runtime_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def materialize_runtime(
    claude_home: Path,
    upstream_root: Path,
    local_plugin: Path,
    manifest: dict[str, Any],
    skills: list[str],
) -> Path | None:
    staging = Path(
        tempfile.mkdtemp(prefix=f".{local_plugin.name}.stage-", dir=claude_home)
    )
    backup = claude_home / f".{local_plugin.name}.backup-{uuid.uuid4().hex}"
    existing_moved = False
    try:
        (staging / ".claude-plugin").mkdir()
        write_json_atomically(staging / ".claude-plugin/plugin.json", manifest)
        for skill in skills:
            relative = skill_relative_path(skill)
            source = upstream_root / relative
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, copy_function=shutil.copy2)

        validate_materialized_runtime(staging, upstream_root, manifest, skills)

        if os.path.lexists(local_plugin):
            os.replace(local_plugin, backup)
            existing_moved = True
        try:
            os.replace(staging, local_plugin)
        except OSError:
            if existing_moved and not os.path.lexists(local_plugin):
                os.replace(backup, local_plugin)
                existing_moved = False
            raise
        return backup if existing_moved else None
    except (OSError, shutil.Error) as error:
        raise ReconciliationError(f"could not replace the self-hosted runtime: {error}") from error
    finally:
        remove_runtime_path(staging)
        if existing_moved and os.path.lexists(backup) and not os.path.lexists(local_plugin):
            os.replace(backup, local_plugin)


def rollback_runtime(local_plugin: Path, backup: Path | None) -> None:
    try:
        remove_runtime_path(local_plugin)
        if backup is not None:
            os.replace(backup, local_plugin)
    except OSError as error:
        raise ReconciliationError(
            f"new runtime failed validation and rollback also failed: {error}"
        ) from error


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
    loading_errors = installed.get("errors")
    if isinstance(loading_errors, list) and loading_errors:
        raise ReconciliationError(
            f"runtime plugin reports {len(loading_errors)} loading errors: "
            f"{loading_errors[0]}"
        )
    install_path = installed.get("installPath")
    if (
        not isinstance(install_path, str)
        or Path(install_path).resolve() != local_plugin
    ):
        raise ReconciliationError(
            f"runtime plugin path differs: {install_path!r}, expected {str(local_plugin)!r}"
        )

    run_claude(claude_bin, "plugin", "validate", "--strict", str(local_plugin))
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
    upstream_root = upstream_path.parents[1]
    local_plugin = claude_home / LOCAL_PLUGIN
    upstream = load_object(upstream_path)
    local = load_object(local_path)
    skills = desired_skills(upstream)
    validate_source_layout(upstream_root, skills)
    expected = reconciled_manifest(local, upstream, skills)

    drift: list[str] = []
    if local != expected:
        drift.append("manifest differs")
    try:
        validate_materialized_runtime(local_plugin, upstream_root, expected, skills)
    except ReconciliationError as error:
        drift.append(str(error))

    if drift:
        if not write:
            raise ReconciliationError(
                "self-hosted runtime is stale: "
                + "; ".join(drift)
                + "; run reconcile_matt_manifest.py --write"
            )
        backup = materialize_runtime(
            claude_home, upstream_root, local_plugin, expected, skills
        )
        try:
            validate_materialized_runtime(local_plugin, upstream_root, expected, skills)
            if runtime:
                validate_runtime(claude_home, claude_bin, skills)
        except (ReconciliationError, OSError) as error:
            try:
                rollback_runtime(local_plugin, backup)
            except ReconciliationError as rollback_error:
                raise rollback_error from error
            raise
        if backup is not None:
            remove_runtime_path(backup)
        print(f"Materialized Matt runtime: {len(skills)} skills")
    else:
        print(f"Matt runtime is current: {len(skills)} skills")

    if runtime and not drift:
        validate_runtime(claude_home, claude_bin, skills)
    if runtime:
        print(f"Claude runtime inventory is current: {len(skills)} skills")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check", action="store_true", help="fail when the local runtime is stale"
    )
    mode.add_argument(
        "--write", action="store_true", help="materialize the reconciled local runtime"
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
