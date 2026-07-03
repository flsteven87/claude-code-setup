#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PermissionRequest hook: Auto-approve everything EXCEPT destructive commands.

Strategy:
  - Static allow list in settings.json handles ~90% of cases
  - This hook catches EVERYTHING ELSE that slips through
  - Dangerous patterns fall through to a manual prompt (no JSON = normal flow)

Layering (deny > ask > allow > this hook):
  - settings.json deny already hard-blocks force pushes and `git reset --hard *`;
    the equivalent patterns below still matter for compound/wrapped forms the
    prefix-style permission rules don't match (e.g. `cd x && git reset --hard`).
  - Patterns are word-boundary regexes searched ANYWHERE in the command, so
    wrapper prefixes (`command sudo ls`, `env sudo ...`) cannot bypass them.
    False positives cost one prompt; false negatives cost an auto-approval.

Output format (PermissionRequest):
  - Exit 0 + JSON with hookSpecificOutput.decision.behavior = "allow" | "deny"
  - Exit 0 without JSON = no decision, show normal prompt
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / "logs" / "auto_approve.log"

# Tools that REQUIRE manual user interaction (never auto-approve)
INTERACTIVE_TOOLS = [
    "AskUserQuestion",  # User must see and answer questions
    "EnterPlanMode",  # User must consent to plan mode
    "ExitPlanMode",  # User must review and approve plan
]

# Commands that REQUIRE manual confirmation (match = show prompt)
# NOTE: git add/commit/push removed to enable /autopilot auto-commit
DANGEROUS_BASH_PATTERNS = [
    r"\bgit\s+rebase\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+push\s+(--force|-f)\b",
    r"\bgit\s+checkout\s+(--\s|\.(\s|$))",  # discard-changes forms (Scope Discipline)
    r"\bgit\s+restore\b",
    r"\brm\b",
    r"\brmdir\b",
    r"\bsudo\b",
    r">\s*/dev/",
    r"\bchmod\s+777\b",
    r"\bkill\s+-9\b",
    r"\bkillall\b",
    r"\bpkill\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\blaunchctl\b",
    r"\bdefaults\s+write\b",
    r"\bnetworksetup\b",
    r"\bcsrutil\b",
    r"\bspctl\b",
]


def log_decision(tool: str, decision: str, reason: str) -> None:
    """Append decision to audit log."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} | {decision:5} | {tool:30} | {reason}\n")
    except OSError:
        pass


def make_allow_response() -> dict:
    """Return PermissionRequest allow decision."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": "allow",
            },
        }
    }


def is_dangerous_bash(command: str) -> bool:
    """Check if a bash command requires manual confirmation.

    Word-boundary regex search over the WHOLE command string — covers chained,
    piped, and wrapper-prefixed forms without fragile segment splitting.
    """
    return any(re.search(pattern, command) for pattern in DANGEROUS_BASH_PATTERNS)


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # Interactive tools: always show to user (never auto-approve)
        if tool_name in INTERACTIVE_TOOLS:
            log_decision(tool_name, "ASK", "Interactive tool - requires user input")
            sys.exit(0)

        # Bash: only block dangerous commands, allow everything else
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_dangerous_bash(command):
                log_decision(f"Bash:{command[:40]}", "ASK", "Dangerous pattern")
                # Exit 0 with no JSON = normal permission flow (show prompt)
                sys.exit(0)
            else:
                log_decision(f"Bash:{command[:40]}", "ALLOW", "Auto-approved")
                print(json.dumps(make_allow_response()))
                sys.exit(0)

        # Everything else: auto-approve
        # (Read, Write, Edit, MCP tools, Task, WebFetch, etc.)
        log_decision(tool_name, "ALLOW", "Auto-approved (non-bash)")
        print(json.dumps(make_allow_response()))
        sys.exit(0)

    except Exception:
        # On error, fall through to normal permission flow
        sys.exit(0)


if __name__ == "__main__":
    main()
