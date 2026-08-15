from __future__ import annotations

import unittest
from pathlib import Path


CLAUDE_HOME = Path(__file__).parents[1]
HOME = CLAUDE_HOME.parent


class AgentContractTests(unittest.TestCase):
    def test_graph_maintainers_share_one_canonical_reference(self) -> None:
        report = HOME / ".agents/GRAPH-ENGINEERING.md"
        codex = (HOME / ".codex/AGENTS.md").read_text(encoding="utf-8")
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")
        skill_workspace = (HOME / ".agents/AGENTS.md").read_text(encoding="utf-8")

        self.assertTrue(report.is_file())
        report_text = report.read_text(encoding="utf-8")
        self.assertIn("Maintainer reference", report_text)
        self.assertIn("Routine delivery agents", report_text)
        self.assertIn("Truth hierarchy", report_text)
        self.assertIn("Model and harness governance", report_text)
        self.assertIn("Protocol for changing this setup", report_text)
        for document in (codex, claude):
            self.assertIn("~/.agents/GRAPH-ENGINEERING.md", document)
            self.assertIn("Routine", document)
        self.assertIn("GRAPH-ENGINEERING.md", skill_workspace)

    def test_matt_orca_flow_has_one_human_delivery_entry(self) -> None:
        codex = (HOME / ".codex/AGENTS.md").read_text(encoding="utf-8")
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertIn("$graph-deliver", codex)
        self.assertIn("/graph-deliver", claude)
        for document in (codex, claude):
            self.assertIn("atomic Graph skills own", document)
            self.assertIn("implementation, review, the final gate", document)
            self.assertIn("resident", document)
            self.assertIn("`dispatched` receipt", document)
            self.assertIn("main agent stops supervising", document)

    def test_main_fast_lane_contract_matches_both_runtimes(self) -> None:
        codex = (HOME / ".codex/AGENTS.md").read_text(encoding="utf-8")
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")

        for document in (codex, claude):
            self.assertIn("### Main Fast Lane", document)
            self.assertIn("primary checkout", document)
            self.assertIn("task-owned paths clean", document)
            self.assertIn("one local task-scoped commit", document)
            self.assertIn("Review, diagnosis, and planning remain read-only", document)

    def test_explicit_fugu_invocation_policy_matches_each_runtime(self) -> None:
        for name in ("fugu-advisor", "fugu-worker"):
            canonical_policy = (
                HOME / f".agents/skills/{name}/agents/openai.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", canonical_policy)

            skill = (CLAUDE_HOME / f"skills/{name}/SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("disable-model-invocation: true", skill)

    def test_ticket_reviewers_are_leaf_tasks_with_an_immutable_head(self) -> None:
        run = (HOME / ".agents/skills/graph-run/SKILL.md").read_text(
            encoding="utf-8"
        )
        integrate = (HOME / ".agents/skills/graph-integrate/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Pin a clean `integration_head`", run)
        self.assertIn("fresh read-only routes", integrate)
        self.assertIn("same immutable head", integrate)
        self.assertIn("Do not edit, commit, run the full gate", integrate)

    def test_graph_reviewers_receive_a_holdout_input_set(self) -> None:
        review = (HOME / ".agents/skills/code-review/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Give each reviewer only its axis prompt", review)
        self.assertIn("Never pass writer rationale", review)
        self.assertIn("fresh Claude Code `opus`", review)
        self.assertIn("fresh Grok `grok-4.6`", review)

        standards = review.split("**Standards reviewer prompt**")[1].split(
            "**Spec reviewer prompt**"
        )[0]
        spec = review.split("**Spec reviewer prompt**")[1].split("### 5")[0]

        self.assertIn("commit list", standards)
        self.assertIn("Withhold the commit list", spec)
        self.assertNotIn("and commit list", spec)

    def test_review_axes_own_their_reviewer_lifecycle(self) -> None:
        review = (HOME / ".agents/skills/code-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        run = (HOME / ".agents/skills/graph-run/SKILL.md").read_text(
            encoding="utf-8"
        )
        report = (HOME / ".agents/GRAPH-ENGINEERING.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Pin `HEAD` before launching and hold it frozen", review)
        self.assertIn("voids that axis", review)
        self.assertIn("still equals its pinned head", review)
        self.assertIn("the Spec axis receives the sealed acceptance itself", review)
        self.assertIn("told the reviewer to treat as complete is writer rationale", review)
        self.assertIn("owns its reviewer from launch to teardown", review)
        self.assertIn("Block on the runtime's own wait", review)
        self.assertIn("rather than to an interval you choose", review)
        self.assertIn("checkpoint, not a state transition", review)
        self.assertIn("answers liveness and\n   nothing else", review)
        self.assertIn("Once it has exited, drain its output by cursor", review)
        self.assertIn("Release the handle last", review)
        self.assertIn("dies before its verdict, exits non-zero, or loses its handle", review)
        self.assertIn("no reviewer outlives the axis that launched it", run)
        self.assertIn("no reviewer outlives its axis", report)

        ticket = (HOME / ".agents/skills/graph-ticket/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Fix commits land after both axes have reported", ticket)
        self.assertIn(
            "`HEAD` did not move between an axis launching and that axis reporting", report
        )
        self.assertIn(
            "received the sealed acceptance itself, not a writer-composed retelling", report
        )

        integrate = (HOME / ".agents/skills/graph-integrate/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("each axis under `$code-review`'s reviewer lifecycle", integrate)
        self.assertIn("fails anywhere in\nthat lifecycle is `blocked-external`", integrate)

    def test_dispatch_completes_on_observed_owner_start(self) -> None:
        dispatch = (HOME / ".agents/skills/graph-dispatch/SKILL.md").read_text(
            encoding="utf-8"
        )
        report = (HOME / ".agents/GRAPH-ENGINEERING.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "owner that started, not on keystrokes that were sent", dispatch
        )
        self.assertIn("resubmit once", dispatch)
        self.assertIn("no `dispatched` value", dispatch)
        self.assertIn("observes that the owner's first turn started", report)
        self.assertIn("placement gate, not supervision", report)

    def test_delivery_gate_and_yolo_contracts_are_explicit(self) -> None:
        execute = (HOME / ".agents/skills/graph-run/SKILL.md").read_text(
            encoding="utf-8"
        )
        implement = (HOME / ".agents/skills/graph-ticket/SKILL.md").read_text(
            encoding="utf-8"
        )
        ship = (HOME / ".agents/skills/ship/SKILL.md").read_text(encoding="utf-8")
        helper = (
            HOME
            / ".agents/skills/graph-dispatch/scripts/delivery_manifest.py"
        ).read_text(encoding="utf-8")

        self.assertIn("full relevant gate once on the final reviewed head", execute)
        self.assertIn("`full_gate=deferred-to-delivery`", implement)
        self.assertIn("Under `$graph-run`", ship)
        self.assertIn('CURRENT_PERMISSION_MODE = "yolo"', helper)
        self.assertIn('YOLO_FLAG = "--dangerously-bypass-approvals-and-sandbox"', helper)
        self.assertIn("def approval_brief", helper)
        self.assertIn("def compare_substrate", helper)
        self.assertIn("def role_envelope", helper)
        self.assertIn("def resident_handoff_envelope", helper)
        self.assertIn("def verify_delivery_coverage", helper)
        self.assertIn('DELIVERY_CLAIM_SCHEMA = "graph-delivery-claim"', helper)
        self.assertIn("# 核准交付", helper)
        dispatch = (
            HOME / ".agents/skills/graph-dispatch/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("four-point `approval` card", dispatch)
        self.assertIn("one delivery ID may claim exactly one Run", dispatch)
        self.assertIn("business approval content must use Traditional Chinese", helper)

    def test_graph_dispatch_hands_ownership_to_a_direct_capable_resident(self) -> None:
        dispatch = (HOME / ".agents/skills/graph-dispatch/SKILL.md").read_text(
            encoding="utf-8"
        )
        run = (HOME / ".agents/skills/graph-run/SKILL.md").read_text(
            encoding="utf-8"
        )
        helper = (
            HOME / ".agents/skills/graph-dispatch/scripts/delivery_manifest.py"
        ).read_text(encoding="utf-8")
        deliver = (HOME / ".agents/skills/graph-deliver/SKILL.md").read_text(
            encoding="utf-8"
        )
        ship = (HOME / ".agents/skills/ship/SKILL.md").read_text(encoding="utf-8")

        self.assertIn("## Full handoff", dispatch)
        self.assertIn("Do not create its Run, Task, or Dispatch", dispatch)
        self.assertIn("stop supervising", dispatch)
        self.assertIn("`Topic · Ticket/Issue` display name", dispatch)
        self.assertIn("def worktree_display_name", helper)
        self.assertIn("There is always one writer slot", run)
        self.assertIn("direct ownership means zero active writer Dispatches", run)
        self.assertIn("delegation\nmeans exactly one", run)
        self.assertIn("exact delegate", run)
        self.assertIn("wait for TUI idle", run)
        self.assertIn("worker-start --terminal", run)
        self.assertIn("owner\n`shell_command`", dispatch)
        self.assertIn("dispatcher has no lifecycle role", run)
        self.assertIn("delivered-worktree-retained", run)
        self.assertIn("Follow sealed `delivery_mode`", run)
        self.assertNotIn("Without a delivery flag", run)
        self.assertIn("render the finalizer envelope", run)
        self.assertIn("No separate\nfinalizer worker or ticket receipt is created", run)
        self.assertIn("return the `dispatched` handoff confirmation once", deliver)
        self.assertIn("intermediate human pause inside this one delivery cycle", deliver)
        self.assertIn("human-requested `$git-converge-main` pass", ship)
        self.assertIn("schema `ship-local-finalization`", ship)
        self.assertIn("does not rewrite the already-terminal Graph outcome", ship)

        ticket = (HOME / ".agents/skills/graph-ticket/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("this ticket clearly owns it", ticket)

    def test_claude_mirrors_the_crg_change_batch_contract(self) -> None:
        claude = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertIn("enqueue one `agent:change-batch`", claude)
        self.assertIn("Subagents do not enqueue or write graph state", claude)
        self.assertIn("Claude auto-memory is contextual cache", claude)

    def test_setup_is_verify_only_and_documents_the_seven_stage_updater(self) -> None:
        setup = (CLAUDE_HOME / "setup.sh").read_text(encoding="utf-8")
        readme = (CLAUDE_HOME / "README.md").read_text(encoding="utf-8")

        self.assertIn("reconcile_matt_manifest.py --check --runtime", setup)
        self.assertNotIn("reconcile_matt_manifest.py --write --runtime", setup)
        self.assertIn("git -C ~/.claude show :settings.json", setup)
        self.assertIn(".agents/skills/ship/SKILL.md", setup)
        self.assertIn(".agents/skills/graph-deliver/SKILL.md", setup)
        self.assertIn(".agents/skills/graph-run/SKILL.md", setup)
        self.assertIn("Seven-stage refresh", readme)
        self.assertIn("does not install or restore them", readme)


if __name__ == "__main__":
    unittest.main()
