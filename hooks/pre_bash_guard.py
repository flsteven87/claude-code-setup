#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PreToolUse hook: the single Bash gate. Tokenizes argv instead of glob-matching.

Replaces dippy (retired 2026-07-27). dippy matched command prefixes, so its rules
drifted out of sync with settings.json, it asked on harmless things it had no rule
for (`git clone`, `git log`, scratchpad redirects), and it returned `allow` for
every force-push spelling. Everything it enforced lives here now, in one rule
language the repo owns.

Three rules, each denying with an alternative rather than stopping to ask. The
user trusts the agent, so a guardrail earns its place only when it can keep an
operation reversible without costing an interruption:

  force push   -> hand to the user (CLAUDE.md: Claude never runs one)
  rm / rmdir   -> `trash`, so a wrong deletion is recoverable from the Trash
  pip / pip3   -> `uv`, per CLAUDE.md's Python tooling rule

`git rm` is exempt: it stages a removal the repo can restore. Deletions under the
temp directories are exempt too — they are ephemeral by definition, and routing
them to the Trash would just fill it with build noise.

Wire-up: register at PreToolUse with matcher "Bash".

Output contract (Claude Code hooks schema):
  - Exit 0 + JSON with hookSpecificOutput.permissionDecision="deny" → blocks tool
  - Exit 0 with no JSON → falls through (allow)
"""

import json
import re
import shlex
import sys

# Shell operators that start a fresh command; a guarded call hidden after any of
# them must still be caught (`npm test && git push --force`).
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;\n|]")

# A heredoc body is data being written, not commands being run — a script that
# merely mentions `rm` in a string must not be mistaken for one that deletes.
HEREDOC_BODY = re.compile(r"<<-?\s*(['\"]?)(\w+)\1(.*?)^\s*\2\s*$", re.S | re.M)

# git global options consumed before the subcommand. The value-taking ones eat
# the following token when written space-separated.
GLOBAL_OPTS_WITH_VALUE = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
GLOBAL_OPTS_FLAG = {"-p", "--paginate", "--no-pager", "--bare", "--literal-pathspecs", "--no-replace-objects"}

FORCE_LONG_OPTS = {"--force", "--force-with-lease", "--mirror"}

DELETE_COMMANDS = {"rm", "rmdir"}
# `find -delete` deletes without ever naming rm, so it needs its own token.
DELETE_FLAGS = {"-delete"}
TEMP_PREFIXES = ("/tmp/", "/private/tmp/", "/var/folders/", "/private/var/folders/")

PIP_COMMANDS = {"pip", "pip3"}


def _force_reason(args: list[str]) -> str | None:
    """Return why these `git push` arguments force, or None if they don't."""
    for arg in args:
        if arg == "--":
            break

        if arg.split("=", 1)[0] in FORCE_LONG_OPTS:
            return f"`{arg}`"

        # Short-option bundle: -f, -uf, -fu. Of git push's short options only
        # -f means force, so an `f` anywhere in the bundle is decisive.
        if len(arg) > 1 and arg[0] == "-" and arg[1] != "-" and "f" in arg[1:]:
            return f"`{arg}` (short-option bundle containing -f)"

        # A leading + on a refspec forces that ref: `git push origin +main`.
        if arg.startswith("+") and len(arg) > 1:
            return f"`{arg}` (leading + forces this refspec)"

    return None


def _check_force_push(tokens: list[str]) -> str | None:
    """Return a deny reason if this segment is a forced git push."""
    i = 0
    while i < len(tokens) and "=" in tokens[i] and not tokens[i].startswith("-"):
        i += 1  # drop leading VAR=value environment assignments

    if i >= len(tokens) or tokens[i] != "git":
        return None
    i += 1

    while i < len(tokens):  # skip git's global options to reach the subcommand
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

    reason = _force_reason(tokens[i + 1 :])
    if not reason:
        return None
    return (
        f"Force push blocked: {reason}. Per CLAUDE.md, a push needing any force flag is "
        "handed to the user — Claude does not run it, and --force-with-lease is not an "
        "exception. Ask the user to run it."
    )


def _check_delete(tokens: list[str]) -> str | None:
    """Return a deny reason if this segment deletes outside the temp directories.

    Matches on token equality rather than a substring search, so `find … -exec rm`
    and `xargs rm` are caught while `echo 'run rm manually'` is not — shlex keeps
    a quoted phrase as one token, which never equals "rm".
    """
    for idx, tok in enumerate(tokens):
        if tok not in DELETE_COMMANDS and tok not in DELETE_FLAGS:
            continue
        if idx and tokens[idx - 1] == "git":
            continue  # `git rm` stages a removal the repo can restore

        # For `find … -delete` the paths precede the flag; for rm they follow it.
        scope = tokens[:idx] if tok in DELETE_FLAGS else tokens[idx + 1 :]
        targets = [t for t in scope if not t.startswith("-") and t not in ("find", "{}", ";")]
        if targets and all(t.startswith(TEMP_PREFIXES) for t in targets):
            continue  # ephemeral by definition; trashing these is just noise

        return (
            f"`{tok}` is not recoverable. Use `trash <path>` instead — it moves the target to "
            "the macOS Trash, so a wrong deletion can be undone. `trash` takes paths only (no "
            "-r/-f flags) and removes directories as-is. Deletions under /tmp are exempt, and "
            "`git rm` is fine for tracked files."
        )

    return None


def _check_pip(tokens: list[str]) -> str | None:
    """Return a deny reason if this segment invokes pip directly."""
    for idx, tok in enumerate(tokens):
        if tok.split("/")[-1] not in PIP_COMMANDS:
            continue
        if idx and tokens[idx - 1] in {"uv", "uvx"}:
            continue  # `uv pip …` is the sanctioned escape hatch
        return (
            f"`{tok}` is not this project's Python tooling. Use `uv add <pkg>` to add a "
            "dependency, `uv run <cmd>` to run one, or `uv pip …` if you genuinely need the "
            "pip interface."
        )
    return None


CHECKS = (_check_force_push, _check_delete, _check_pip)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed → fall through, don't break the tool call

    if data.get("tool_name") != "Bash":
        return 0

    command = (data.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return 0

    command = HEREDOC_BODY.sub("<<HEREDOC", command)

    for segment in SEGMENT_SPLIT.split(command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            # Unbalanced quote, or a dangling escape left behind by the split —
            # `find … -exec rm {} \;` becomes a segment ending in a lone backslash.
            # Skipping on a tokenizer error fails open, so fall back to a coarse
            # split and let the checks run against that instead.
            tokens = segment.replace("\\", " ").split()
        if not tokens:
            continue
        for check in CHECKS:
            reason = check(tokens)
            if reason:
                print(
                    json.dumps(
                        {
                            "hookSpecificOutput": {
                                "hookEventName": "PreToolUse",
                                "permissionDecision": "deny",
                                "permissionDecisionReason": reason,
                            }
                        }
                    )
                )
                return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
