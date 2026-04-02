#!/usr/bin/env bash
# Launch Joi — Discord persona for Claude Code
# Usage: joi [additional claude args...]

set -euo pipefail

# Set persona marker — SessionStart hook reads this
export JOI_MODE=true

# Launch from Joi's dedicated workspace (gives her own memory)
cd ~/.claude/joi

# Start Claude Code with Discord channel
exec claude --channels plugin:discord@claude-plugins-official "$@"
