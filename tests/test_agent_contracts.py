from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


CLAUDE_HOME = Path(__file__).parents[1]
HOME = CLAUDE_HOME.parent


def _agents_root() -> Path:
    """Return the .agents checkout under test, failing closed on a bad override."""
    configured = os.environ.get("AGENTS_ROOT")
    if not configured:
        return HOME / ".agents"
    root = Path(configured).expanduser()
    if not root.is_absolute():
        raise RuntimeError("AGENTS_ROOT must be an absolute path")
    if not (root / "AGENTS.md").is_file():
        raise RuntimeError(f"AGENTS_ROOT is not an .agents checkout: {root}")
    return root


AGENTS = _agents_root()
MILESTONE_WORKFLOW_SKILLS = (
    "milestone-dispatch",
    "topics",
    "codebase-design",
    "orca-cli",
    "strategy-review",
    "audit-pr-topics",
    "wayfinder",
)
NATIVE_SHARED_SKILLS = (
    "audit-pr-topics",
    "milestone-dispatch",
    "strategy-review",
    "topics",
)


class AgentContractTests(unittest.TestCase):
    def test_agents_checkout_override_is_absolute_and_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / ".agents-worktree"
            root.mkdir()
            (root / "AGENTS.md").write_text(
                "# Agent Skill Workspace\n", encoding="utf-8"
            )
            with mock.patch.dict(os.environ, {"AGENTS_ROOT": str(root)}):
                self.assertEqual(_agents_root(), root)

        with mock.patch.dict(os.environ, {"AGENTS_ROOT": "relative/.agents"}):
            with self.assertRaisesRegex(RuntimeError, "absolute"):
                _agents_root()

    def test_agents_checkout_override_never_falls_back_silently(self) -> None:
        missing = Path("/tmp/definitely-not-an-agents-checkout")
        with mock.patch.dict(os.environ, {"AGENTS_ROOT": str(missing)}):
            with self.assertRaisesRegex(RuntimeError, str(missing)):
                _agents_root()

    def test_agents_checkout_defaults_to_the_home_checkout(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_agents_root(), HOME / ".agents")

    def test_main_fast_lane_contract_matches_both_runtimes(self) -> None:
        codex = (HOME / ".codex/AGENTS.md").read_text(encoding="utf-8")
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")

        for document in (codex, claude):
            self.assertIn("primary checkout", document)
            self.assertIn("task-owned paths clean", document)
            self.assertIn("one local task-scoped commit", document)

    def test_claude_mirrors_the_crg_change_batch_contract(self) -> None:
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertIn("enqueue one `agent:change-batch`", claude)
        self.assertIn("Subagents do not enqueue or write graph state", claude)
        self.assertIn("Claude auto-memory is contextual cache", claude)

    def test_setup_reconciles_native_links_and_documents_the_seven_stage_updater(
        self,
    ) -> None:
        setup = (CLAUDE_HOME / "setup.sh").read_text(encoding="utf-8")
        readme = (CLAUDE_HOME / "README.md").read_text(encoding="utf-8")

        self.assertIn("reconcile_matt_manifest.py --check --runtime", setup)
        self.assertNotIn("reconcile_matt_manifest.py --write --runtime", setup)
        self.assertIn("git -C ~/.claude show :settings.json", setup)
        self.assertIn(".agents/skills/ship/SKILL.md", setup)
        self.assertNotIn(".agents/skills/graph-", setup)
        self.assertIn("Seven-stage refresh", readme)
        self.assertIn("safely creates missing native links", readme)
        self.assertIn("does not install or restore canonical skills", readme)

    def test_milestone_workflow_targets_exist_and_setup_verifies_them(self) -> None:
        setup = (CLAUDE_HOME / "setup.sh").read_text(encoding="utf-8")

        for name in MILESTONE_WORKFLOW_SKILLS:
            target = AGENTS / f"skills/{name}/SKILL.md"
            self.assertTrue(target.is_file(), f"missing workflow skill: {target}")
            self.assertIn(f".agents/skills/{name}/SKILL.md", setup)

    def test_native_shared_skills_are_discoverable_by_claude(self) -> None:
        setup = (CLAUDE_HOME / "setup.sh").read_text(encoding="utf-8")

        for name in NATIVE_SHARED_SKILLS:
            link = CLAUDE_HOME / "skills" / name
            target = AGENTS / "skills" / name
            self.assertTrue(link.is_symlink(), f"native skill is not linked: {link}")
            self.assertEqual(link.resolve(), target.resolve())
            self.assertTrue((link / "SKILL.md").is_file())
            self.assertIn(f'  "{name}"', setup)

    def test_cross_surface_skill_pointer_resolves_source_and_authority(self) -> None:
        agents = (AGENTS / "AGENTS.md").read_text(encoding="utf-8")
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")

        for document in (agents, claude):
            self.assertIn(
                "from a user message, repository instruction, or skill body",
                document,
            )
            self.assertIn("installed skill", document)
            self.assertIn("Report the missing capability", document)

        self.assertIn("`skills/<name>/SKILL.md`", agents)
        self.assertIn("non-user reference", agents)
        self.assertIn("`~/.agents/skills/<name>/SKILL.md`", claude)
        self.assertIn("requires a user request", claude)
        self.assertIn("`allow_implicit_invocation: false`", claude)
        self.assertIn("`disable-model-invocation: true`", claude)

    def test_graph_engineering_is_absent_from_active_routes(self) -> None:
        active_documents = (
            (HOME / ".codex/AGENTS.md").read_text(encoding="utf-8"),
            (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8"),
            (AGENTS / "AGENTS.md").read_text(encoding="utf-8"),
            (CLAUDE_HOME / "commands/ship.md").read_text(encoding="utf-8"),
            (CLAUDE_HOME / "README.md").read_text(encoding="utf-8"),
            (CLAUDE_HOME / "setup.sh").read_text(encoding="utf-8"),
        )

        for document in active_documents:
            self.assertNotIn("graph-deliver", document)
            self.assertNotIn("GRAPH-ENGINEERING.md", document)

        self.assertEqual(list((CLAUDE_HOME / "skills").glob("graph-*")), [])


if __name__ == "__main__":
    unittest.main()
