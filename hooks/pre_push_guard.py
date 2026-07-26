#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PreToolUse hook: Block every force-push spelling, by parsing git's argv.

settings.json deny rules are globs with no awareness of git's argument grammar,
so they cannot express "a force flag anywhere in this push". Adding patterns
until the common spellings are covered leaves exotic ones (`-fu` bundles,
`git -c k=v push --force`) reachable, and each extra pattern raises the risk of
blocking a legitimate push. This hook tokenizes instead: skip git's global
options, find the `push` subcommand, then classify the remaining arguments.

CLAUDE.md: "A push needing any force flag cannot be done by Claude at all."
harness.md: "When a rule must hold every time, add a hook rather than a prompt
instruction." This is that hook.

Wire-up: register at PreToolUse with matcher "Bash".

Output contract (Claude Code hooks schema):
  - Exit 0 + JSON with hookSpecificOutput.permissionDecision="deny" → blocks tool
  - Exit 0 with no JSON → falls through (allow)
"""

import json
import re
import shlex
import sys

# Shell operators that start a fresh command; a force push hidden after any of
# them must still be caught (`npm test && git push --force`).
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;\n|]")

# git global options consumed before the subcommand. The value-taking ones eat
# the following token when written space-separated.
GLOBAL_OPTS_WITH_VALUE = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
GLOBAL_OPTS_FLAG = {"-p", "--paginate", "--no-pager", "--bare", "--literal-pathspecs", "--no-replace-objects"}

FORCE_LONG_OPTS = {"--force", "--force-with-lease", "--mirror"}


def _force_reason(args: list[str]) -> str | None:
    """Return why these `git push` arguments force, or None if they don't."""
    for arg in args:
        if arg == "--":
            break

        base = arg.split("=", 1)[0]
        if base in FORCE_LONG_OPTS:
            return f"`{arg}`"

        # Short-option bundle: -f, -uf, -fu. Of git push's short options only
        # -f means force, so an `f` anywhere in the bundle is decisive.
        if len(arg) > 1 and arg[0] == "-" and arg[1] != "-" and "f" in arg[1:]:
            return f"`{arg}` (short-option bundle containing -f)"

        # A leading + on a refspec forces that ref: `git push origin +main`.
        if arg.startswith("+") and len(arg) > 1:
            return f"`{arg}` (leading + forces this refspec)"

    return None


def _check_segment(tokens: list[str]) -> str | None:
    """Return a deny reason if this command segment is a forced git push."""
    # Drop leading VAR=value environment assignments.
    i = 0
    while i < len(tokens) and "=" in tokens[i] and not tokens[i].startswith("-"):
        i += 1

    if i >= len(tokens) or tokens[i] != "git":
        return None
    i += 1

    # Skip git's global options to reach the subcommand.
    while i < len(tokens):
        tok = tokens[i]
        if tok in GLOBAL_OPTS_WITH_VALUE:
            i += 2
        elif tok.split("=", 1)[0] in GLOBAL_OPTS_WITH_VALUE or tok in GLOBAL_OPTS_FLAG:
            i += 1
        elif tok.startswith("-"):
            i += 1
        else:
            break

    if i >= len(tokens) or tokens[i] != "push":
        return None

    return _force_reason(tokens[i + 1 :])


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed → fall through, don't break the tool call

    if data.get("tool_name") != "Bash":
        return 0

    command = (data.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or "push" not in command:
        return 0

    for segment in SEGMENT_SPLIT.split(command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue  # unbalanced quotes → not something we can judge
        reason = _check_segment(tokens)
        if reason:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": (
                                f"Force push blocked: {reason}. Per CLAUDE.md, a push needing any "
                                "force flag is handed to the user — Claude does not run it, and "
                                "--force-with-lease is not an exception. Ask the user to run it."
                            ),
                        }
                    }
                )
            )
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
