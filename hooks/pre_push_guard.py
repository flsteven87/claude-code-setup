#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Compatibility shim — this hook was renamed to pre_bash_guard.py on 2026-07-27.

A Claude Code session reads settings.json at startup and holds it, so sessions
that were already running still invoke this path. Deleting the file broke every
live session's Bash calls until this shim went back.

Delete once no session started before 2026-07-27 is still running.
"""

import runpy
import sys
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("pre_bash_guard.py")), run_name="__main__")
