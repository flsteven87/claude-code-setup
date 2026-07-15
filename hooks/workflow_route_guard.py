#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PreToolUse hook: Block un-routed named/built-in Workflow launches.

Named workflows (Workflow({name: ...})) resolve to built-in scripts that pin
no per-stage models, so every agent bills at the session tier — the #1 cost
blowout per CLAUDE.md Multi-Agent Model Economics. (2026-07-07: un-routed
deep-research billed 74 agents at session tier.)

The Workflow tool resolves scriptPath > script > name, so `name` is only
denied when it is the effective launch source.

Wire-up: register at PreToolUse with matcher "Workflow".

Output contract (Claude Code hooks schema):
  - Exit 0 + JSON with hookSpecificOutput.permissionDecision="deny" → blocks tool
  - Exit 0 with no JSON → falls through (allow)
"""

import json
import sys

DENY_REASON = (
    "Named workflows are un-routed — every agent() inherits the session model "
    "and bills at top tier. Use the routed copy via scriptPath (for example, "
    "~/.claude/workflows/deep-research.js), or resolve the built-in script, "
    "pin per-stage models per CLAUDE.md Multi-Agent Model Economics (haiku "
    "scan/fetch, sonnet review/verify, session model for synthesis only), then "
    "launch via scriptPath."
)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed → fall through, don't break the tool call

    tool_input = data.get("tool_input", {}) or {}
    name = tool_input.get("name")
    script = tool_input.get("script")
    script_path = tool_input.get("scriptPath")

    if isinstance(name, str) and name.strip() and not (script or script_path):
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": DENY_REASON,
                    }
                }
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
