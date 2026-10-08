import importlib.util
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "checkpoint", Path(__file__).resolve().parents[1] / "scripts/read_maintenance_checkpoint.py"
)
checkpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checkpoint)


class MaintenanceCheckpointTests(unittest.TestCase):
    def test_latest_daily_retains_all_later_followups(self):
        current = "## 2026-10-08T09:11:13+08:00 daily development-tool update\n- current\n"
        followup = "\n## Follow-up 2026-10-08 — recovery\n- still open\n"
        history = "Old scheduler description\n## 2026-10-07T09:45:32+08:00 daily development-tool update\n- old\n"
        self.assertEqual(checkpoint.latest_checkpoint(history + current + followup), current + followup)

    def test_recovery_heading_is_not_a_new_daily_checkpoint(self):
        text = "## 2026-10-08 daily development-tool update\n- unresolved\n\n## 2026-10-08T12:00:00+08:00 update recovery\n- fixed\n"
        self.assertEqual(checkpoint.latest_checkpoint(text), text)

    def test_missing_daily_heading_fails_instead_of_loading_history(self):
        with self.assertRaises(ValueError):
            checkpoint.latest_checkpoint("## Setup\nNo daily checkpoint yet.\n")


if __name__ == "__main__":
    unittest.main()
