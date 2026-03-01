#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
PreCompact hook: backup transcript before compaction.

Saves a copy of the current session transcript to ~/.claude/backups/
so critical context is preserved even after compaction.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path.home() / ".claude" / "backups"
MAX_BACKUPS = 20


def main():
    try:
        data = json.load(sys.stdin)
        session_id = data.get("session_id", "unknown")
        transcript_path = data.get("transcript_path")

        if not transcript_path or not Path(transcript_path).exists():
            sys.exit(0)

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_compact_{timestamp}_{session_id[:8]}.jsonl"
        backup_path = BACKUP_DIR / backup_name

        shutil.copy2(transcript_path, backup_path)

        # Prune old backups, keep latest MAX_BACKUPS
        backups = sorted(
            BACKUP_DIR.glob("pre_compact_*.jsonl"),
            key=lambda p: p.stat().st_mtime,
        )
        for old in backups[:-MAX_BACKUPS]:
            old.unlink()

        print(json.dumps({"feedback": f"Transcript backed up: {backup_name}"}))

    except Exception:
        # Never block compaction due to backup failure
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
