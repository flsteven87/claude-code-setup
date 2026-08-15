from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "reconcile_matt_manifest.py"


class ReconcileMattManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.claude_home = Path(self.tempdir.name) / ".claude"
        self.upstream = self.claude_home / "plugins/marketplaces/mattpocock"
        self.local = self.claude_home / "skills/mattpocock-skills"
        (self.upstream / ".claude-plugin").mkdir(parents=True)
        (self.local / ".claude-plugin").mkdir(parents=True)

        self.desired_paths = [
            "./skills/engineering/code-review",
            "./skills/productivity/wait-what",
        ]
        upstream_paths = [*self.desired_paths, "./skills/productivity/handoff"]
        self._write_json(
            self.upstream / ".claude-plugin/plugin.json",
            {"name": "mattpocock-skills", "version": "2.0.0", "skills": upstream_paths},
        )
        for skill_path in upstream_paths:
            directory = self.upstream / skill_path.removeprefix("./")
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(
                "---\nname: test\n---\n", encoding="utf-8"
            )

        self.local_manifest = {
            "$schema": "https://example.invalid/plugin.schema.json",
            "name": "mattpocock-skills",
            "version": "1.0.0",
            "description": "Local policy description",
            "skills": ["./skills/engineering/code-review"],
        }
        self._write_json(self.local / ".claude-plugin/plugin.json", self.local_manifest)
        os.symlink(self.upstream / "skills", self.local / "skills")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--claude-home",
                str(self.claude_home),
                *arguments,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_check_rejects_a_stale_local_manifest(self) -> None:
        result = self._run("--check")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manifest is stale", result.stderr)

    def test_write_reconciles_version_and_skills_but_preserves_local_policy(
        self,
    ) -> None:
        write_result = self._run("--write")
        check_result = self._run("--check")
        manifest = json.loads((self.local / ".claude-plugin/plugin.json").read_text())

        self.assertEqual(write_result.returncode, 0, write_result.stderr)
        self.assertEqual(check_result.returncode, 0, check_result.stderr)
        self.assertEqual(manifest["version"], "2.0.0")
        self.assertEqual(manifest["skills"], self.desired_paths)
        self.assertEqual(manifest["description"], "Local policy description")
        self.assertEqual(
            manifest["$schema"], "https://example.invalid/plugin.schema.json"
        )

    def test_check_rejects_a_manifest_entry_without_skill_source(self) -> None:
        missing_skill = self.upstream / "skills/productivity/wait-what/SKILL.md"
        missing_skill.unlink()

        result = self._run("--write")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing SKILL.md", result.stderr)

    def test_runtime_check_rejects_inventory_drift(self) -> None:
        self.assertEqual(self._run("--write").returncode, 0)
        fake_claude = Path(self.tempdir.name) / "claude"
        fake_claude.write_text(
            f"#!/bin/sh\n"
            "if [ \"$1 $2\" = 'plugin list' ]; then\n"
            f'  printf \'[{{"id":"mattpocock-skills@skills-dir","enabled":true,'
            f'"installPath":"{self.local}"}}]\\n\'\n'
            "else\n"
            "  printf 'Component inventory\\n  Skills (1)  code-review\\n'\n"
            "fi\n",
            encoding="utf-8",
        )
        fake_claude.chmod(0o755)

        result = self._run("--check", "--runtime", "--claude-bin", str(fake_claude))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime skill inventory differs", result.stderr)


if __name__ == "__main__":
    unittest.main()
