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
        self.assertIn("Pin a clean `integration_head`", run)
        self.assertIn("finalizer envelope's", run)
        self.assertIn("`review_command` synchronously", run)
        self.assertIn("full sealed delivery range", run)
        self.assertIn("bind the same delivery ID and manifest digest", run)
        self.assertIn("`coverage-invalid`", run)

    def test_graph_reviewers_receive_a_holdout_input_set(self) -> None:
        review = (HOME / ".agents/skills/code-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        helper = (
            HOME
            / ".agents/skills/graph-dispatch/scripts/delivery_manifest.py"
        ).read_text(encoding="utf-8")

        self.assertIn("builds both inputs from the sealed manifest and Git", review)
        self.assertIn("withhold commit subjects and writer\nrationale", review)
        self.assertIn('f"## Commit list', helper)
        self.assertIn("These criteria are the complete approved set", helper)
        self.assertIn("commit messages and ", helper)
        self.assertIn("writer rationale are withheld", helper)

    def test_graph_reviews_use_one_evidence_lock(self) -> None:
        review = (HOME / ".agents/skills/code-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        run = (HOME / ".agents/skills/graph-run/SKILL.md").read_text(
            encoding="utf-8"
        )
        report = (HOME / ".agents/GRAPH-ENGINEERING.md").read_text(
            encoding="utf-8"
        )
        helper = (
            HOME
            / ".agents/skills/graph-dispatch/scripts/delivery_manifest.py"
        ).read_text(encoding="utf-8")

        self.assertIn("Execute the envelope's `review_command` synchronously", review)
        self.assertIn("This single call is the **review lock**", review)
        self.assertIn("supplied only by the writer is not review evidence", review)
        self.assertIn("def run_review_gate", helper)
        self.assertIn("ThreadPoolExecutor(max_workers=2)", helper)
        # Claude honors `--tools ""`; Grok's allow-list form leaks, so only the
        # Standards axis may record that intention.
        self.assertIn('"--tools",\n            ""', helper)
        self.assertIn("Grok's `--tools` is an allow-list of built-ins", helper)
        self.assertIn('REVIEW_GATE_SCHEMA = "graph-review-gate/v3"', helper)
        self.assertIn('REVIEW_RECEIPT_SCHEMA = "graph-ticket-review/v4"', helper)
        # A reviewer that never saw the evidence has not judged it, and one verdict per
        # exact range is what keeps a rerun from buying a second opinion.
        self.assertIn('"insufficient-input"', helper)
        self.assertIn("another review gate already holds this Run", helper)
        self.assertIn("every review lock is terminal with durable evidence", run)
        self.assertIn("One blocking helper call launches both", report)

        ticket = (HOME / ".agents/skills/graph-ticket/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("execute the envelope's `review_command` synchronously", ticket)
        self.assertIn("rejects writer-authored review claims", ticket)
        self.assertIn("The helper built the Spec input directly", report)

        run = (HOME / ".agents/skills/graph-run/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Preserve both axes' finding sets", run)
        self.assertIn("re-hashable evidence at the current head", run)
        self.assertIn("is `blocked-external`", run)

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
        self.assertIn('YOLO_PERMISSION_MODE = "yolo"', helper)
        self.assertIn('GATED_PERMISSION_MODE = "approval-required"', helper)
        self.assertIn("def permission_mode_for", helper)
        self.assertIn("def satisfiability_report", helper)
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
        self.assertIn("`approval` card verbatim", dispatch)
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
        self.assertIn("No separate finalizer worker or ticket receipt is created", run)
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
