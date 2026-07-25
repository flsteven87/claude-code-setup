from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import collect_git_activity as collector


SCRIPT = Path(__file__).with_name("collect_git_activity.py")


class AuthorMatchingTests(unittest.TestCase):
    def test_matches_exact_name_email_or_identity_case_insensitively(self) -> None:
        aliases = {
            collector.normalize_author("Po-Chi"),
            collector.normalize_author("dev@example.com"),
            collector.normalize_author("Other Person <other@example.com>"),
        }

        self.assertTrue(collector.author_matches("po-chi", "unused@example.com", aliases))
        self.assertTrue(collector.author_matches("Unknown", "DEV@example.com", aliases))
        self.assertTrue(
            collector.author_matches("Other Person", "other@example.com", aliases)
        )

    def test_does_not_treat_alias_as_regex(self) -> None:
        aliases = {collector.normalize_author("dev+git@example.com")}

        self.assertFalse(collector.author_matches("Dev", "devXgit@example.com", aliases))


class NumstatTests(unittest.TestCase):
    def test_top_level_handles_rename_shapes(self) -> None:
        self.assertEqual(collector.top_level("src/{old.py => new.py}"), "src")
        self.assertEqual(collector.top_level("{old => new}/file.py"), "renames")
        self.assertEqual(collector.top_level("old/file.py => new/file.py"), "renames")


class CollectorIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.com")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def git(
        self,
        *args: str,
        author: str = "Test User",
        email: str = "test@example.com",
        date: str | None = None,
    ) -> str:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = author
        env["GIT_AUTHOR_EMAIL"] = email
        env["GIT_COMMITTER_NAME"] = author
        env["GIT_COMMITTER_EMAIL"] = email
        if date:
            env["GIT_AUTHOR_DATE"] = date
            env["GIT_COMMITTER_DATE"] = date
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout

    def commit_file(
        self,
        path: str,
        content: str,
        message: str,
        *,
        author: str,
        email: str,
        date: str,
    ) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        self.git("add", path)
        self.git("commit", "-m", message, author=author, email=email, date=date)

    def collect(self, *, since: str, until: str, author: str) -> dict[str, object]:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--repo",
                str(self.repo),
                "--since",
                since,
                "--until",
                until,
                "--branch",
                "main",
                "--author",
                author,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_excludes_end_boundary_and_other_authors(self) -> None:
        self.commit_file(
            "base.txt",
            "base\n",
            "chore: baseline",
            author="Other",
            email="other@example.com",
            date="2025-12-31T12:00:00+08:00",
        )
        baseline = self.git("rev-parse", "HEAD").strip()
        self.commit_file(
            "start.txt",
            "start\n",
            "feat: inclusive start",
            author="Alice",
            email="alice@example.com",
            date="2026-01-01T00:00:00+08:00",
        )
        self.commit_file(
            "inside.txt",
            "inside\n",
            "feat: inside window",
            author="Alice",
            email="alice@example.com",
            date="2026-01-02T12:00:00+08:00",
        )
        self.commit_file(
            "other.txt",
            "other\n",
            "fix: other author",
            author="Other",
            email="other@example.com",
            date="2026-01-03T12:00:00+08:00",
        )
        self.commit_file(
            "boundary.txt",
            "boundary\n",
            "feat: exclusive end",
            author="Alice",
            email="alice@example.com",
            date="2026-01-08T00:00:00+08:00",
        )

        output = self.collect(
            since="2026-01-01T00:00:00+08:00",
            until="2026-01-08T00:00:00+08:00",
            author="alice@example.com",
        )

        self.assertEqual(output["summary"]["mainline_commits"], 2)
        self.assertEqual(output["scope"]["baseline"], baseline)
        self.assertEqual(
            [commit["subject"] for commit in output["commits"]],
            ["feat: inside window", "feat: inclusive start"],
        )

    def test_counts_first_parent_merge_rename(self) -> None:
        self.commit_file(
            "src/old.py",
            "value = 1\n",
            "chore: baseline",
            author="Other",
            email="other@example.com",
            date="2026-01-01T00:00:00+08:00",
        )
        self.git("checkout", "-b", "feature")
        self.git("mv", "src/old.py", "src/new.py")
        self.git(
            "commit",
            "-m",
            "refactor: rename",
            author="Alice",
            email="alice@example.com",
            date="2026-01-02T12:00:00+08:00",
        )
        self.git("checkout", "main")
        self.git(
            "merge",
            "--no-ff",
            "feature",
            "-m",
            "Merge pull request #42",
            author="Alice",
            email="alice@example.com",
            date="2026-01-03T12:00:00+08:00",
        )

        output = self.collect(
            since="2026-01-02T00:00:00+08:00",
            until="2026-01-04T00:00:00+08:00",
            author="Alice <alice@example.com>",
        )

        self.assertEqual(output["summary"]["mainline_commits"], 1)
        self.assertEqual(output["summary"]["file_change_entries"], 1)
        self.assertEqual(output["summary"]["commit_types"], {"merge": 1})
        self.assertEqual(output["summary"]["pr_numbers"], [42])

    def test_empty_window_returns_zeroed_summary(self) -> None:
        self.commit_file(
            "base.txt",
            "base\n",
            "chore: baseline",
            author="Other",
            email="other@example.com",
            date="2026-01-01T00:00:00+08:00",
        )

        output = self.collect(
            since="2026-02-01T00:00:00+08:00",
            until="2026-02-08T00:00:00+08:00",
            author="alice@example.com",
        )

        self.assertEqual(output["summary"]["mainline_commits"], 0)
        self.assertEqual(output["summary"]["file_change_entries"], 0)
        self.assertEqual(output["commits"], [])


if __name__ == "__main__":
    unittest.main()
