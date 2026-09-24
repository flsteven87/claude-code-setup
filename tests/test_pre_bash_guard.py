from __future__ import annotations

import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


HOOK = Path(__file__).parents[1] / "hooks" / "pre_bash_guard.py"
spec = importlib.util.spec_from_file_location("pre_bash_guard", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class GuardTests(unittest.TestCase):
    def decision(self, command: str) -> str | None:
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(payload)), redirect_stdout(output):
            self.assertEqual(hook.main(), 0)
        if not output.getvalue():
            return None
        return json.loads(output.getvalue())["hookSpecificOutput"]["permissionDecision"]

    def test_lease_forms_pass(self) -> None:
        for command in (
            "git push --force-with-lease",
            "git push --force-with-lease origin feat/x",
            "git push --force-with-lease=feat/x:abc123 --force-if-includes origin feat/x",
            "git push -u origin feat/x",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.decision(command))

    def test_blind_force_is_denied(self) -> None:
        for command in (
            "git push --force origin feat/x",
            "git push -f",
            "git push -uf origin feat/x",
            "git push origin +main",
            "git push --force-with-lease origin +feat/x",
            "git push --mirror",
            "npm test && git -C repo push --force",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")

    def test_arguments_and_temp_targets_pass(self) -> None:
        for command in (
            "docker rm abc",
            "docker container rm -f abc && docker volume rm v1",
            'grep -E "list|rm|show" notes.txt',
            'grep -n "rm" f.txt | head',
            "git rm stale.py",
            "orca worktree rm feat-x",
            'SP=/private/tmp/work; rm -rf "$SP/out"',
            'export WT=/tmp/wt && rm -rf "${WT}"',
            "rm /tmp/x /private/tmp/y",
            'T="gcloud|python|pip|jq"; echo "$T"',
            "uv pip install -e .",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.decision(command))

    def test_real_deletions_and_pip_are_denied(self) -> None:
        for command in (
            "rm ./build.log",
            "FOO=1 rm -rf dist",
            "sudo rm -rf /opt/x",
            "find . -name '*.pyc' -delete",
            "find . -name x -exec rm {} \\;",
            "ls | xargs -0 rm -f",
            'rm -rf "$UNKNOWN/out"',
            "cd repo && rmdir empty",
            "pip install requests",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")


if __name__ == "__main__":
    unittest.main()
