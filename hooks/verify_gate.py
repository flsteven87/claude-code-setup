#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Stop hook + CLI: deterministic "done = observed" gate.

Official pattern (code.claude.com/docs/en/best-practices): a Stop hook that
blocks the turn from ending until a verification check passes is what lets
unattended/pipeline work finish *correctly* — an in-prompt rule alone is the
weakest tier of the verification ladder. Claude Code force-ends the turn after
8 consecutive blocks, so a stuck gate is bounded by the platform.

Gates are cwd-scoped (no session id is available to the Bash tool), so
concurrent sessions in worktrees (distinct cwds) never cross-block.

CLI (used by /ship, /merge-pr, or ad hoc):
  uv run ~/.claude/hooks/verify_gate.py arm "<task>" "<check1>" ["<check2>" ...]
  uv run ~/.claude/hooks/verify_gate.py clear     # after observing the end state
  uv run ~/.claude/hooks/verify_gate.py status

Hook mode (no argv, reads hook JSON on stdin):
  - no gate for this cwd            -> exit 0, silent
  - gate older than TTL (6h)        -> drop it, exit 0 (aborted/dead task)
  - armed gate                      -> {"decision":"block","reason":...}
"""

import hashlib
import json
import sys
import time
from pathlib import Path

GATE_DIR = Path.home() / ".claude" / "state" / "verify-gates"
TTL_SECONDS = 6 * 3600


def gate_path(cwd: str) -> Path:
    return GATE_DIR / (hashlib.sha1(cwd.encode()).hexdigest()[:16] + ".json")


def cmd_arm(task: str, checks: list[str], cwd: str) -> int:
    GATE_DIR.mkdir(parents=True, exist_ok=True)
    gate_path(cwd).write_text(
        json.dumps(
            {"task": task, "checks": checks, "cwd": cwd, "armed_at": time.time()},
            ensure_ascii=False,
        )
    )
    print(f"verify-gate armed for {cwd}: {len(checks)} check(s)")
    return 0


def cmd_clear(cwd: str) -> int:
    p = gate_path(cwd)
    if p.exists():
        p.unlink()
        print("verify-gate cleared")
    else:
        print("no verify-gate armed for this directory")
    return 0


def cmd_status(cwd: str) -> int:
    p = gate_path(cwd)
    if not p.exists():
        print("no verify-gate armed for this directory")
        return 0
    print(p.read_text())
    return 0


def hook_mode() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed -> fall through, never break turn end

    cwd = data.get("cwd") or str(Path.cwd())
    p = gate_path(cwd)
    if not p.exists():
        return 0

    try:
        gate = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        p.unlink(missing_ok=True)
        return 0

    age = time.time() - gate.get("armed_at", 0)
    if age > TTL_SECONDS:
        p.unlink(missing_ok=True)
        return 0

    checks = "\n".join(f"  - {c}" for c in gate.get("checks", []))
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": (
                    "verify-gate is armed — done = observed has not been confirmed for: "
                    f"\"{gate.get('task', '?')}\" (armed {int(age / 60)}m ago).\n"
                    f"Unobserved end-state checks:\n{checks}\n"
                    "Observe each check now (run the command / load the page / screenshot), "
                    "then clear with: uv run ~/.claude/hooks/verify_gate.py clear\n"
                    "If the task was deliberately aborted with the user's knowledge, clear the "
                    "gate with the same command and say so in your report."
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        return hook_mode()
    cwd = str(Path.cwd())
    if argv[0] == "arm" and len(argv) >= 3:
        return cmd_arm(argv[1], list(argv[2:]), cwd)
    if argv[0] == "clear":
        return cmd_clear(cwd)
    if argv[0] == "status":
        return cmd_status(cwd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
