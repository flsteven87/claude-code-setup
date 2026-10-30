#!/usr/bin/env bash
# Refresh user skills and supported plugins. General tool/runtime maintenance has its own owner.
set -euo pipefail

mode_selected=false
for arg in "$@"; do
  if [[ "$arg" == --check || "$arg" == --commit ]]; then mode_selected=true; fi
done
if [[ "$mode_selected" == false ]]; then set -- --commit "$@"; fi
exec uv run --no-project --with pyyaml python \
  "$HOME/.agents/scripts/update_external_skills.py" --plugins "$@"
