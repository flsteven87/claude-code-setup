#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PermissionRequest hook: Auto-approve everything EXCEPT destructive git ops and rm.

Strategy:
  - Static allow list in settings.json handles ~90% of cases
  - This hook catches EVERYTHING ELSE that slips through
  - Only git commit/push/rebase and rm/rmdir require manual confirmation

Output format (PermissionRequest):
  - Exit 0 + JSON with hookSpecificOutput.decision.behavior = "allow" | "deny"
  - Exit 0 without JSON = no decision, show normal prompt
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / "logs" / "auto_approve.log"

# Tools that REQUIRE manual user interaction (never auto-approve)
INTERACTIVE_TOOLS = [
    "AskUserQuestion",  # User must see and answer questions
    "EnterPlanMode",    # User must consent to plan mode
    "ExitPlanMode",     # User must review and approve plan
]

# Commands that REQUIRE manual confirmation (deny pattern = show prompt)
# NOTE: git add/commit/push removed to enable /autopilot auto-commit
DANGEROUS_BASH_PATTERNS = [
    "git rebase",
    "git reset --hard",
    "git push --force",
    "git push -f",
    "rm ",
    "rm\t",
    "rmdir ",
    "sudo ",
    "> /dev/",
    "chmod 777",
    "kill -9",
    "killall ",
    "pkill ",
    "shutdown",
    "reboot",
    "launchctl ",
    "defaults write",
    "networksetup",
    "csrutil",
    "spctl",
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
    """Check if a bash command requires manual confirmation."""
    cmd = command.strip()
    # Handle piped/chained commands - check each part
    for part in cmd.replace("&&", "|").replace("||", "|").replace(";", "|").split("|"):
        part = part.strip()
        for pattern in DANGEROUS_BASH_PATTERNS:
            if part.startswith(pattern) or part.startswith(f"'{pattern}"):
                return True
    return False


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
