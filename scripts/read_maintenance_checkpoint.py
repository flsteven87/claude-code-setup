#!/usr/bin/env python3
"""Read the latest daily checkpoint and subsequent follow-ups without changing history."""

import re
import sys
from pathlib import Path


DAILY_HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2}\S* daily development-tool update\s*$", re.MULTILINE)


def latest_checkpoint(text: str) -> str:
    headings = list(DAILY_HEADING.finditer(text))
    if not headings:
        raise ValueError("No daily update checkpoint found; inspect the memory format before proceeding.")
    return text[headings[-1].start():]


def main() -> int:
    primary = Path.home() / ".claude/automations/daily-dev-update/memory.md"
    mirror = Path.home() / ".codex/automations/automation/memory.md"
    source = primary if primary.exists() else mirror
    try:
        checkpoint = latest_checkpoint(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"Source: {source.relative_to(Path.home())}", file=sys.stderr)
    sys.stdout.write(checkpoint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
