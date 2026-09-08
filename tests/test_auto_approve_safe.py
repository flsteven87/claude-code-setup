from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


HOOK = Path(__file__).parents[1] / "hooks" / "auto_approve_safe.py"
spec = importlib.util.spec_from_file_location("auto_approve_safe", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class PermissionHookTests(unittest.TestCase):
    def run_hook(self, payload: str) -> str:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with (
                patch.object(hook, "LOG_FILE", Path(directory) / "audit.log"),
                patch("sys.stdin", io.StringIO(payload)),
                redirect_stdout(output),
                self.assertRaises(SystemExit) as stopped,
            ):
                hook.main()
            self.assertEqual(stopped.exception.code, 0)
            return output.getvalue()

    def decision(self, name: str, command: str = "") -> str:
        return self.run_hook(json.dumps({
            "tool_name": name, "tool_input": {"command": command},
        }))

    def test_unknown_and_external_tools_defer_to_runtime(self):
        for name in ("FutureTool", "mcp__mail__send", "mcp__context7__query", ""):
            with self.subTest(name=name):
                self.assertEqual(self.decision(name), "")

    def test_interactive_tools_still_require_user_input(self):
        for name in ("AskUserQuestion", "EnterPlanMode", "ExitPlanMode"):
            with self.subTest(name=name):
                self.assertEqual(self.decision(name), "")

    def test_existing_native_automation_is_preserved(self):
        for name in ("Read", "Write", "Edit", "Glob", "Grep", "Task", "Agent",
                     "NotebookEdit", "WebFetch", "WebSearch", "Skill"):
            with self.subTest(name=name):
                result = json.loads(self.decision(name))
                self.assertEqual(
                    result["hookSpecificOutput"]["decision"]["behavior"], "allow"
                )

    def test_safe_bash_including_null_redirection_remains_automatic(self):
        result = json.loads(self.decision("Bash", "git status 2>/dev/null"))
        self.assertEqual(result["hookSpecificOutput"]["decision"]["behavior"], "allow")

    def test_destructive_and_machine_commands_still_defer(self):
        for command in ("cd repo && git reset --hard", "git restore file",
                        "git checkout -- file", "command sudo ls", "echo x > /dev/disk2",
                        "shutdown now", "reboot", "csrutil disable", "spctl --master-disable"):
            with self.subTest(command=command):
                self.assertEqual(self.decision("Bash", command), "")

    def test_malformed_payload_never_grants_permission(self):
        for payload in ("{", "null", "[]", '{"tool_name":"Bash","tool_input":null}'):
            with self.subTest(payload=payload):
                self.assertEqual(self.run_hook(payload), "")


if __name__ == "__main__":
    unittest.main()
