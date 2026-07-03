#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PreToolUse hook: Block Write/Edit/MultiEdit on sensitive files.

Catches what settings.json deny rules can't easily express:
  - .env / .env.* files anywhere in the tree
  - SSH private keys (id_rsa, id_ed25519, *.pem, *.key)
  - AWS credentials (~/.aws/credentials, ~/.aws/config)
  - GPG (~/.gnupg/)
  - secrets.* basenames
  - SQL files under any migrations/ directory (project convention: schema
    changes go through the Supabase MCP, never local migration files)

Wire-up: register at PreToolUse with matcher "Write|Edit|MultiEdit".

Output contract (Claude Code hooks schema):
  - Exit 0 + JSON with hookSpecificOutput.permissionDecision="deny" → blocks tool
  - Exit 0 with no JSON → falls through (allow)
"""

import json
import re
import sys
from pathlib import Path

# Path segments anywhere in the path that mark a sensitive directory
SENSITIVE_DIR_SEGMENTS = {".ssh", ".aws", ".gnupg"}

# Full-path suffix matches (anchored to end of resolved path)
SENSITIVE_PATH_SUFFIXES = (
    "/.aws/credentials",
    "/.aws/config",
)

# Basename regex patterns — match against filename only
SENSITIVE_BASENAME_PATTERNS = [
    re.compile(r"^\.env(\..+)?$"),  # .env, .env.local, .env.production
    re.compile(r".+\.pem$"),  # *.pem
    re.compile(r".+\.key$"),  # *.key
    re.compile(r"^id_(rsa|ed25519|ecdsa|dsa)$"),  # SSH private keys (skip .pub)
    re.compile(r"^secrets?\..+$", re.IGNORECASE),  # secret.json, secrets.yaml, etc.
    re.compile(r"^credentials(\..+)?$", re.IGNORECASE),  # credentials, credentials.json
]


def is_sensitive(file_path: str) -> tuple[bool, str]:
    """Return (is_sensitive, human_reason)."""
    if not file_path:
        return False, ""

    try:
        path = Path(file_path).expanduser()
    except (OSError, ValueError):
        path = Path(file_path)

    normalized = str(path)
    basename = path.name
    parts = set(path.parts)

    for suffix in SENSITIVE_PATH_SUFFIXES:
        if normalized.endswith(suffix):
            return True, f"path ends with {suffix}"

    for seg in SENSITIVE_DIR_SEGMENTS:
        if seg in parts:
            return True, f"path contains {seg}/ segment"

    for pattern in SENSITIVE_BASENAME_PATTERNS:
        if pattern.match(basename):
            return True, f"basename matches /{pattern.pattern}/"

    if basename.endswith(".sql") and "migrations" in parts:
        return (
            True,
            "SQL migration file — apply schema changes via Supabase MCP instead",
        )

    return False, ""


def collect_file_paths(tool_input: dict) -> list[str]:
    """Extract every file_path from Write/Edit/MultiEdit tool_input shapes."""
    paths: list[str] = []
    fp = tool_input.get("file_path")
    if isinstance(fp, str):
        paths.append(fp)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                ep = edit.get("file_path")
                if isinstance(ep, str):
                    paths.append(ep)
    return paths


def emit_deny(reason: str) -> None:
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(response))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed → fall through, don't break the tool call

    tool_input = data.get("tool_input", {}) or {}
    for fp in collect_file_paths(tool_input):
        hit, reason = is_sensitive(fp)
        if hit:
            emit_deny(f"Blocked write to sensitive file: {fp} ({reason})")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
