#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PermissionRequest hook: auto-approve everything except what a prompt can still save.

Where this sits (settings.json deny > ask > allow, then this hook):
  - settings.json settles 26% of Bash calls outright (measured 2026-07-27); the
    rest arrive here.
  - pre_bash_guard.py runs earlier, at PreToolUse, and denies deletions, force
    pushes, and pip with a recoverable alternative. Those never reach this hook,
    so they never cost a prompt.
  - What is left is the narrow list below. Matching one emits no JSON, which
    Claude Code reads as "no decision" and turns into the normal prompt.

Patterns are word-boundary regexes over the whole command, so wrapper prefixes
(`command sudo ls`, `env sudo ...`) and compound forms (`cd x && git reset --hard`)
cannot slip past the prefix-style permission rules.

Keep them narrow. A pattern that fires on a common idiom is not a cheap false
positive: the old `/dev/` write rule matched every `2>/dev/null` and caused 91% of
all prompts, undetected for months because the audit log truncated each command
before the point that matched.

Output: exit 0 with an allow decision, or exit 0 with no JSON to fall through to
the prompt. This hook never denies — denials belong in pre_bash_guard.py, where
they can carry an alternative for the agent to take instead.
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

# Commands that REQUIRE manual confirmation (match = show prompt).
#
# The bar (2026-07-27): a prompt is worth an interruption only when the command
# destroys something no layer can give back. Everything reversible was dropped —
# `git rebase` (reflog), `kill -9` / `killall` / `pkill` (restart it), `chmod 777`,
# `launchctl` / `defaults write` / `networksetup` (change it back). Deletions and
# force pushes moved to pre_bash_guard.py, which denies them with a recoverable
# alternative (`trash`, hand-to-user) instead of costing a prompt.
#
# What is left destroys UNCOMMITTED work — the one thing the reflog cannot
# restore — or reconfigures the machine itself.
DANGEROUS_BASH_PATTERNS = [
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+checkout\s+(--\s|\.(\s|$))",  # discard-changes forms (Scope Discipline)
    r"\bgit\s+restore\b",
    r"\bsudo\b",  # NOPASSWD sudoers entries would otherwise run unprompted
    # Writing to a device node can destroy a disk; writing to the pseudo-devices
    # cannot. Without this exclusion `2>/dev/null` — the most common idiom in the
    # shell — reads as destructive and prompts (91% of all prompts, 2026-07-27).
    r">\s*/dev/(?!null\b|stdout\b|stderr\b|tty\b|fd/)",
    r"\bshutdown\b",
    r"\breboot\b",
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

    Regex over the whole string is enough for this list, because every pattern
    names a command that is dangerous wherever it appears. Rules that must
    distinguish argument positions — a force flag anywhere in a push, `rm` as a
    command versus `rm` inside a quoted string — belong in pre_bash_guard.py,
    which tokenizes instead.
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

        # Bash: prompt on the narrow dangerous list, auto-approve everything else
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_dangerous_bash(command):
                log_decision(f"Bash:{command[:200]}", "ASK", "Dangerous pattern")
                # Exit 0 with no JSON = normal permission flow (show prompt)
                sys.exit(0)
            else:
                log_decision(f"Bash:{command[:200]}", "ALLOW", "Auto-approved")
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
