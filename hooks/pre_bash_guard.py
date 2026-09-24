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
language the repo owns, and settings.json carries no parallel push rules.

Three rules, each denying with an alternative rather than stopping to ask. The
user trusts the agent, so a guardrail earns its place only when it can keep an
operation reversible without costing an interruption:

  force push   -> `--force-with-lease`, which refuses to overwrite commits the
                  pusher has not seen; the lease form itself runs unprompted, and
                  each repository's branch protection decides which branches
                  accept any force push at all
  rm / rmdir   -> `trash`, so a wrong deletion is recoverable from the Trash
  pip / pip3   -> `uv`, per CLAUDE.md's Python tooling rule

A rule fires only where the guarded word runs as a command, so an argument
never trips it: `git rm` stages a removal the repo can restore, `orca worktree rm`
and `docker rm` remove managed objects, and `grep rm file` only mentions it.
Deletions under the temp directories are exempt too — they are ephemeral
by definition, and routing them to the Trash would just fill it with build noise.

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
# them must still be caught (`npm test && git push --force`). They are split out
# by the tokenizer, not a regex, so an operator character inside quotes
# (`grep -E "a|rm|b"`) stays part of its argument.
OPERATOR_CHARS = ";&|\n"

# Words that run the next word as a command: `sudo rm x`, `xargs -0 rm`.
COMMAND_PREFIXES = {"sudo", "command", "exec", "env", "nice", "time", "nohup", "xargs"}
# `find … -exec rm {} \;` runs rm too.
EXEC_FLAGS = {"-exec", "-execdir", "-ok", "-okdir"}

ASSIGNMENT = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
VAR_REF = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")

# A heredoc body is data being written, not commands being run — a script that
# merely mentions `rm` in a string must not be mistaken for one that deletes.
HEREDOC_BODY = re.compile(r"<<-?\s*(['\"]?)(\w+)\1(.*?)^\s*\2\s*$", re.S | re.M)

# git global options consumed before the subcommand. The value-taking ones eat
# the following token when written space-separated.
GLOBAL_OPTS_WITH_VALUE = {
    "-c",
    "-C",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--exec-path",
}
GLOBAL_OPTS_FLAG = {
    "-p",
    "--paginate",
    "--no-pager",
    "--bare",
    "--literal-pathspecs",
    "--no-replace-objects",
}

# Force spellings that overwrite the remote without checking what is there.
# `--force-with-lease` and `--force-if-includes` are the safe forms and pass.
FORCE_LONG_OPTS = {"--force", "--mirror"}

DELETE_COMMANDS = {"rm", "rmdir"}
# `find -delete` deletes without ever naming rm, so it needs its own token.
DELETE_FLAGS = {"-delete"}
TEMP_PREFIXES = ("/tmp/", "/private/tmp/", "/var/folders/", "/private/var/folders/")

PIP_COMMANDS = {"pip", "pip3"}


def _force_reason(args: list[str]) -> str | None:
    """Return why these `git push` arguments force blindly, or None if they don't."""
    for arg in args:
        if arg == "--":
            break

        if arg == "--mirror":
            return "`--mirror` (overwrites every remote ref; push explicit refspecs instead)"
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


def _check_force_push(tokens: list[str], _env: dict[str, str]) -> str | None:
    """Return a deny reason if this segment force-pushes without a lease."""
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
        f"Blind force push blocked: {reason}. Re-run it with `--force-with-lease` "
        "(and no `+` refspec), which proceeds without asking but refuses to overwrite "
        "remote commits you have not fetched. The repository's branch protection decides "
        "whether the target branch accepts it."
    )


def _runs_as_command(tokens: list[str], idx: int) -> bool:
    """True when tokens[idx] is executed rather than passed as an argument.

    `rm x`, `FOO=1 rm x`, `sudo rm x`, `xargs -0 rm`, and `find … -exec rm` run rm;
    `docker rm c`, `git rm f`, and `grep rm file` pass it as an argument.
    """
    j = idx - 1
    while j >= 0 and tokens[j].startswith("-") and tokens[j] not in EXEC_FLAGS:
        j -= 1  # skip a prefix command's own flags: `xargs -0 -r rm`
    if j < 0:
        return True
    prev = tokens[j]
    if prev in COMMAND_PREFIXES or prev in EXEC_FLAGS:
        return True
    if j == idx - 1 and all(ASSIGNMENT.match(t) for t in tokens[:idx]):
        return True  # only VAR=value assignments precede it
    return False


def _check_delete(tokens: list[str], env: dict[str, str]) -> str | None:
    """Return a deny reason if this segment deletes outside the temp directories.

    Matches on token equality rather than a substring search, and only where the
    token runs as a command, so `find … -exec rm` and `xargs rm` are caught while
    `docker rm`, `grep rm`, and `echo 'run rm manually'` are not. Targets written
    through a variable assigned earlier in the same command (`SP=/tmp/x; rm "$SP/a"`)
    are resolved before the temp-directory check.
    """
    for idx, tok in enumerate(tokens):
        if tok in DELETE_COMMANDS:
            if not _runs_as_command(tokens, idx):
                continue
        elif tok not in DELETE_FLAGS:
            continue

        # For `find … -delete` the paths precede the flag; for rm they follow it.
        scope = tokens[:idx] if tok in DELETE_FLAGS else tokens[idx + 1 :]
        targets = [
            _expand(t, env)
            for t in scope
            if not t.startswith("-") and t not in ("find", "{}", ";", "+")
        ]
        if targets and all(t and t.startswith(TEMP_PREFIXES) for t in targets):
            continue  # ephemeral by definition; trashing these is just noise

        return (
            f"`{tok}` is not recoverable. Use `trash <path>` instead — it moves the target to "
            "the macOS Trash, so a wrong deletion can be undone. `trash` takes paths only (no "
            "-r/-f flags) and removes directories as-is. Deletions under /tmp are exempt, and "
            "`git rm` is fine for tracked files."
        )

    return None


def _check_pip(tokens: list[str], _env: dict[str, str]) -> str | None:
    """Return a deny reason if this segment invokes pip directly."""
    for idx, tok in enumerate(tokens):
        if tok.split("/")[-1] not in PIP_COMMANDS:
            continue
        if idx and tokens[idx - 1] in {"uv", "uvx"}:
            continue  # `uv pip …` is the sanctioned escape hatch
        if not _runs_as_command(tokens, idx):
            continue  # `grep pip requirements.txt` only mentions it
        return (
            f"`{tok}` is not this project's Python tooling. Use `uv add <pkg>` to add a "
            "dependency, `uv run <cmd>` to run one, or `uv pip …` if you genuinely need the "
            "pip interface."
        )
    return None


CHECKS = (_check_force_push, _check_delete, _check_pip)


def _expand(token: str, env: dict[str, str]) -> str | None:
    """Substitute variables assigned earlier in the command; None if any is unknown."""
    unknown = False

    def repl(match: re.Match[str]) -> str:
        nonlocal unknown
        name = match.group(1) or match.group(2)
        if name not in env:
            unknown = True
            return ""
        return env[name]

    expanded = VAR_REF.sub(repl, token)
    return None if unknown else expanded


def _segments(command: str) -> list[list[str]]:
    """Split a command line into simple commands, respecting quotes."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=OPERATOR_CHARS)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    segments: list[list[str]] = [[]]
    for token in lexer:
        if token and set(token) <= set(OPERATOR_CHARS):
            segments.append([])
        else:
            segments[-1].append(token)
    return [s for s in segments if s]


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

    try:
        segments = _segments(command)
    except ValueError:
        # Unbalanced quote. Skipping on a tokenizer error fails open, so fall back
        # to a coarse split and let the checks run against that instead.
        segments = [
            part.replace("\\", " ").split() for part in re.split(r"[;&|\n]+", command)
        ]

    env: dict[str, str] = {}
    for tokens in segments:
        if not tokens:
            continue
        for tok in tokens[1:] if tokens[0] == "export" else tokens:
            match = ASSIGNMENT.match(tok)
            if not match:
                break  # assignments only count before the command word
            env[match.group(1)] = _expand(match.group(2), env) or ""
        for check in CHECKS:
            reason = check(tokens, env)
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
