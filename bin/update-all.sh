#!/usr/bin/env bash
# Refresh user skills and supported plugins. General tool/runtime maintenance has its own owner.
set -euo pipefail

if [[ $# -eq 0 ]]; then
  set -- --commit
fi
exec uv run --no-project --with pyyaml python \
  "$HOME/.agents/scripts/update_external_skills.py" --plugins "$@"
