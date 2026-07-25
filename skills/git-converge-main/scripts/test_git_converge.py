import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("git_converge.py")
SPEC = importlib.util.spec_from_file_location("git_converge", SCRIPT)
assert SPEC and SPEC.loader
converge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = converge
SPEC.loader.exec_module(converge)


def command(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        list(args),
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return completed.stdout.strip()


def git(cwd: Path, *args: str) -> str:
    return command(cwd, "git", *args)


class RepoFixture:
    def __init__(self, root: Path):
        self.remote = root / "remote.git"
        self.repo = root / "repo"
        git(root, "init", "--bare", str(self.remote))
        git(root, "init", "-b", "main", str(self.repo))
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")
        (self.repo / "tracked.txt").write_text("initial\n")
        git(self.repo, "add", "tracked.txt")
        git(self.repo, "commit", "-m", "initial")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-u", "origin", "main")
        git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")
        git(self.repo, "remote", "set-head", "origin", "-a")

    def commit(self, message: str, text: str) -> str:
        (self.repo / "tracked.txt").write_text(text)
        git(self.repo, "add", "tracked.txt")
        git(self.repo, "commit", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")


class GitConvergeTests(unittest.TestCase):
    def test_audit_distinguishes_clean_tree_and_synced_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))

            state = converge.snapshot(fixture.repo)

            self.assertTrue(state["working_tree"]["clean"])
            self.assertTrue(state["default_synced"])
            self.assertFalse(state["edge_checks_run"])
            self.assertEqual(state["current_branch"], "main")
            self.assertEqual(len(state["worktrees"]), 1)

    def test_tidy_syncs_behind_main_and_deletes_reachable_branch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))
            git(fixture.repo, "branch", "stale")
            git(fixture.repo, "switch", "-c", "active")
            fixture.commit("advance", "advance\n")
            git(fixture.repo, "push", "origin", "HEAD:main")

            plan = converge.build_plan(fixture.repo, scope="tidy", remote_prefix="codex/")
            kinds = {(item["kind"], item["target"]) for item in plan["actions"]}

            self.assertIn(("sync-protected", "main"), kinds)
            self.assertIn(("delete-local", "stale"), kinds)

            result = converge.apply_plan(fixture.repo, plan)
            self.assertTrue(result["success"])
            self.assertEqual(
                git(fixture.repo, "rev-parse", "main"),
                git(fixture.repo, "rev-parse", "origin/main"),
            )
            self.assertNotIn("stale", git(fixture.repo, "branch", "--format=%(refname:short)"))

    def test_dirty_secondary_worktree_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = RepoFixture(root)
            git(fixture.repo, "branch", "merged-work")
            git(fixture.repo, "switch", "-c", "active")
            path = root / "secondary"
            git(fixture.repo, "worktree", "add", str(path), "merged-work")
            (path / "dirty.txt").write_text("dirty\n")

            plan = converge.build_plan(fixture.repo, scope="tidy", remote_prefix="codex/")

            self.assertTrue(
                any(item["target"] == str(path.resolve()) and "dirty" in item["reason"] for item in plan["blocked"]),
                plan,
            )
            self.assertFalse(any(item["kind"] == "remove-worktree" for item in plan["actions"]))

    def test_finish_pushes_current_and_removes_reachable_remote_branch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))
            git(fixture.repo, "push", "origin", "main:codex/merged")
            git(fixture.repo, "switch", "-c", "codex/active")
            fixture.commit("active", "active\n")

            merged_pr = {
                "number": 7,
                "headRefName": "codex/merged",
                "baseRefName": "main",
                "mergeCommit": {"oid": git(fixture.repo, "rev-parse", "origin/main")},
                "url": "https://example.invalid/pr/7",
            }
            with (
                mock.patch.object(converge, "open_pr_heads", return_value=(set(), None)),
                mock.patch.object(
                    converge,
                    "merged_prs",
                    side_effect=lambda _repo, branch: ([merged_pr], None)
                    if branch == "codex/merged"
                    else ([], None),
                ),
            ):
                plan = converge.build_plan(fixture.repo, scope="finish", remote_prefix="codex/")
            kinds = {(item["kind"], item["target"]) for item in plan["actions"]}

            self.assertIn(("push-current", "codex/active"), kinds)
            self.assertIn(("delete-remote", "codex/merged"), kinds, plan)

            with mock.patch.object(
                converge,
                "open_pr_heads",
                return_value=(set(), None),
            ):
                result = converge.apply_plan(fixture.repo, plan)
            self.assertTrue(result["success"])
            self.assertEqual(
                git(fixture.repo, "rev-parse", "codex/active"),
                git(fixture.repo, "rev-parse", "origin/codex/active"),
            )
            self.assertEqual(
                git(
                    fixture.repo,
                    "rev-parse",
                    "--abbrev-ref",
                    "--symbolic-full-name",
                    "@{upstream}",
                ),
                "origin/codex/active",
            )
            remote_refs = git(fixture.repo, "branch", "-r", "--format=%(refname:short)")
            self.assertNotIn("origin/codex/merged", remote_refs)

    def test_exact_pr_and_cumulative_patch_prove_squash_merge(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))
            git(fixture.repo, "switch", "-c", "codex/squashed")
            fixture.commit("one", "one\n")
            (fixture.repo / "second.txt").write_text("second\n")
            git(fixture.repo, "add", "second.txt")
            git(fixture.repo, "commit", "-m", "two")
            git(fixture.repo, "switch", "main")
            git(fixture.repo, "merge", "--squash", "codex/squashed")
            git(fixture.repo, "commit", "-m", "squash merge")
            merge_oid = git(fixture.repo, "rev-parse", "HEAD")
            git(fixture.repo, "push", "origin", "main")

            pr = {
                "number": 42,
                "headRefName": "codex/squashed",
                "baseRefName": "main",
                "mergeCommit": {"oid": merge_oid},
                "url": "https://example.invalid/pr/42",
            }
            with mock.patch.object(converge, "merged_prs", return_value=([pr], None)):
                proof, error = converge.merge_proof(
                    fixture.repo,
                    branch_name="codex/squashed",
                    branch_ref="codex/squashed",
                    default_branch="main",
                    default_ref="origin/main",
                )

            self.assertIsNone(error)
            self.assertIn("cumulative patch-id matches", proof)

    def test_finish_keeps_remote_branch_with_open_pr(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))
            git(fixture.repo, "push", "origin", "main:codex/open")
            git(fixture.repo, "switch", "-c", "active")

            with mock.patch.object(
                converge,
                "open_pr_heads",
                return_value=({"codex/open"}, None),
            ):
                plan = converge.build_plan(
                    fixture.repo,
                    scope="finish",
                    remote_prefix="codex/",
                )

            self.assertFalse(
                any(
                    item["kind"] == "delete-remote"
                    and item["target"] == "codex/open"
                    for item in plan["actions"]
                )
            )
            self.assertTrue(
                any(
                    item["target"] == "origin/codex/open"
                    and "open PR" in item["reason"]
                    for item in plan["blocked"]
                )
            )

    def test_apply_refuses_when_repository_changed_after_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))
            git(fixture.repo, "branch", "stale")
            plan = converge.build_plan(
                fixture.repo,
                scope="tidy",
                remote_prefix="codex/",
            )
            git(fixture.repo, "branch", "appeared-later")

            result = converge.apply_plan(fixture.repo, plan)

            self.assertFalse(result["success"])
            self.assertTrue(result["stale"])
            self.assertEqual(result["executed"], [])
            self.assertIn("stale", git(fixture.repo, "branch", "--format=%(refname:short)"))

    def test_action_guard_refuses_branch_that_moved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = RepoFixture(Path(temp_dir))
            git(fixture.repo, "branch", "stale")
            expected = git(fixture.repo, "rev-parse", "stale")
            git(fixture.repo, "switch", "stale")
            fixture.commit("move stale", "moved\n")
            action = {
                "kind": "delete-local",
                "target": "stale",
                "expected_oid": expected,
            }

            refusal = converge.verify_action(fixture.repo, action, "origin")

            self.assertEqual(refusal, "local branch target moved or disappeared")

    def test_action_guard_refuses_worktree_that_became_dirty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture = RepoFixture(root)
            git(fixture.repo, "branch", "linked")
            path = root / "linked"
            git(fixture.repo, "worktree", "add", str(path), "linked")
            expected = git(path, "rev-parse", "HEAD")
            (path / "dirty.txt").write_text("dirty\n")
            action = {
                "kind": "remove-worktree",
                "target": str(path),
                "expected_oid": expected,
            }

            refusal = converge.verify_action(fixture.repo, action, "origin")

            self.assertEqual(refusal, "worktree became dirty")


if __name__ == "__main__":
    unittest.main()
