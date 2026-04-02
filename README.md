# Claude Code Setup

My personal [Claude Code](https://claude.ai/code) configuration — a battle-tested setup for autonomous coding with layered security, auto-formatting, and custom workflows.

## Architecture

```
                          ┌─────────────────────────────┐
                          │     Claude Code Runtime      │
                          └──────────────┬──────────────┘
                                         │
               ┌─────────────────────────┼─────────────────────────┐
               │                         │                         │
    ┌──────────▼──────────┐   ┌──────────▼──────────┐   ┌─────────▼─────────┐
    │  Layer 1: Deny/Allow │   │  Layer 2: Dippy      │   │  Layer 3: Auto    │
    │  (settings.json)     │   │  (PreToolUse hook)    │   │  Approve Hook     │
    │                      │   │                      │   │                   │
    │  Static rules that   │   │  Command-level gate  │   │  Catches anything │
    │  Claude evaluates    │   │  that blocks/allows  │   │  that slips       │
    │  before tool calls   │   │  Bash execution      │   │  through L1 + L2  │
    └──────────────────────┘   └──────────────────────┘   └───────────────────┘
```

**Three-layer permission defense:**

1. **settings.json** — Static allow/deny rules evaluated by Claude Code natively
2. **[Dippy](https://github.com/ldayton/Dippy)** — External command validator (PreToolUse hook) that enforces `uv` over `pip`, blocks `rm -rf`, protects `.env` files
3. **auto_approve_safe.py** — PermissionRequest hook that auto-approves safe operations and prompts for dangerous ones (git force-push, sudo, kill, etc.)

## What's Included

```
~/.claude/
├── settings.json              # Permissions, hooks, plugins, status line
├── CLAUDE.md                  # Development standards (architecture, naming, linting)
├── .mcp.json                  # MCP server config (empty at user level — credentials go in project-level)
│
├── hooks/
│   ├── auto-format.sh         # PostToolUse: ruff (Python) + prettier (JS/TS) after every edit
│   ├── auto_approve_safe.py   # PermissionRequest: auto-approve safe ops, prompt for dangerous
│   ├── pre_compact.py         # PreCompact: backup transcripts before context compaction
│   └── joi-persona.sh         # SessionStart: inject Joi persona for Discord sessions
│
├── commands/                  # Custom slash commands (/autopilot, /cycle, /review-change, etc.)
├── skills/                    # Reusable skill definitions (double-check, ai-agents, prompt-engineering, etc.)
├── rules/                     # Modular coding rules (backend.md, frontend.md, naming-conventions.md)
├── references/                # Reference docs (frontend-principles.md, prompt-engineering.md)
│
├── dippy/
│   └── config                 # Dippy config reference (actual location: ~/.dippy/config)
│
├── plugins/
│   ├── installed_plugins.json # Plugin registry (superpowers, frontend-design, typescript-lsp, discord)
│   ├── known_marketplaces.json# Registered plugin marketplaces
│   └── blocklist.json         # Blocked plugins
│
├── joi/                       # Joi Discord persona (launch script + identity CLAUDE.md)
├── channels/discord/          # Discord channel access policy
└── statusline-command.sh      # Custom status bar (dir, model, context %, rate limits)
```

## Quick Start

### Prerequisites

- [Claude Code CLI](https://claude.ai/code) installed
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Dippy](https://github.com/ldayton/Dippy) (Bash command gatekeeper)

### 1. Install Dippy

Dippy is a **critical** part of this setup. It acts as a PreToolUse hook that intercepts every Bash command Claude tries to run, enforcing rules like "use `uv` instead of `pip`" and blocking destructive operations.

```bash
uv tool install dippy
```

Verify it works:

```bash
dippy --help
```

### 2. Clone this repo

```bash
git clone https://github.com/flsteven87/claude-code-setup.git ~/.claude
```

> **Already have a `~/.claude` directory?** Back it up first:
> ```bash
> mv ~/.claude ~/.claude.backup
> ```

### 3. Copy the Dippy config

The repo includes the Dippy config as a reference at `dippy/config`. Copy it to Dippy's actual config location:

```bash
mkdir -p ~/.dippy
cp ~/.claude/dippy/config ~/.dippy/config
```

### 4. Install plugins

The plugins themselves are not tracked (just the metadata). Install them:

```bash
# Launch Claude Code and it will prompt you to install missing plugins,
# or install manually:
claude plugins install superpowers@superpowers-marketplace
claude plugins install frontend-design@claude-plugins-official
claude plugins install typescript-lsp@claude-plugins-official
claude plugins install discord@claude-plugins-official
```

### 5. Verify the setup

```bash
claude
# Then inside Claude Code:
/permissions    # Check permission rules are loaded
/hooks          # Verify all 6 hooks are registered
```

## How It Works

### Permission System

The `settings.json` uses `acceptEdits` mode — file reads and edits are auto-approved, Bash commands go through the three-layer defense.

**Allow rules** (auto-approved):
- All built-in tools: Read, Edit, Write, Glob, Grep, WebSearch, WebFetch, Task, NotebookEdit
- All MCP tools: `MCP(*)`
- All git operations: `Bash(git add *)`, `Bash(git commit *)`, etc.

**Deny rules** (always blocked):
- Destructive filesystem: `rm -rf /`, `rm -rf ~`, `mkfs`, `dd`
- Destructive git: `git push --force` to main/master, `git reset --hard`

### Hooks

| Hook | Event | What It Does |
|------|-------|-------------|
| `dippy` | PreToolUse (Bash) | Validates every Bash command against allowlist. Enforces `uv` over `pip`, blocks `rm -rf`, protects `.env` files |
| `auto-format.sh` | PostToolUse (Edit/Write) | Runs `ruff format` + `ruff check --fix` on Python, `prettier --write` on JS/TS/CSS |
| `auto_approve_safe.py` | PermissionRequest | Auto-approves safe operations. Prompts for: `git rebase`, `sudo`, `rm`, `kill`, `shutdown`, etc. Logs all decisions to `~/.claude/logs/auto_approve.log` |
| `pre_compact.py` | PreCompact | Saves transcript backup before context compaction. Keeps latest 20 backups |
| `joi-persona.sh` | SessionStart | Injects Joi persona context when `JOI_MODE=true` (for Discord sessions) |
| macOS notification | Stop | Sends a native notification when Claude finishes responding |

### Dippy Deep Dive

[Dippy](https://github.com/ldayton/Dippy) is not part of Claude Code's standard toolchain — it's a standalone Python CLI that acts as a command gatekeeper. It's registered as a PreToolUse hook:

```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": "dippy",
      "timeout": 5000
    }]
  }]
}
```

When Claude Code attempts any Bash command, Dippy receives the command via stdin and:
- **Exit 0** → allow (command matches an `allow` rule)
- **Exit 2** → deny with message (command matches a `deny` rule)
- Applies **last-match-wins** rule ordering

Key rules in `~/.dippy/config`:

```bash
# Force uv ecosystem
deny pip "Use uv add instead of pip install"
allow uv

# Allow dev tooling
allow git add
allow pnpm
allow gh
allow curl

# Safety
deny rm -rf "Be more specific about what to remove, or use trash"
deny-redirect **/.env* "Never write secrets directly, ask the user to do it"
```

**Without Dippy installed**, the PreToolUse hook will fail silently (non-zero exit codes other than 2 are treated as warnings), and Claude Code falls back to the other two permission layers. The setup still works, but you lose the `pip` → `uv` enforcement and `.env` write protection.

### Custom Commands

| Command | Description |
|---------|-------------|
| `/autopilot` | Fully autonomous E2E workflow — detects work from MEMORY.md or executes a given task |
| `/cycle` | Runs N cycles of: autopilot → agent-test → designer-test |
| `/review-change` | Deep code review of recent changes |
| `/review-and-commit` | Lightweight review + commit |
| `/go` | Start implementation after confirming direction |
| `/primer` | Quick project structure overview |
| `/catchup` | Rebuild context after `/clear` |
| `/handoff` | Save state to MEMORY.md before `/clear` |
| `/housekeep` | Deep clean codebase artifacts |
| `/codebase-audit` | Full technical + business architecture audit |
| `/agent-test` | Automated QA testing per flow |
| `/designer-test` | Automated UI design review per page |
| `/roadmap` | Strategic direction updates to MEMORY.md |
| `/research-and-build` | Research best practices, then plan and build |
| `/web-interface-guidelines` | Review UI code against Vercel guidelines |

### Skills

Notable custom skills (invoked automatically by relevant tasks):

| Skill | Trigger |
|-------|---------|
| `double-check` | Deep analysis before careful implementation |
| `strategic-next` | Project-level "what's next" strategic planning |
| `ai-agents` | AI agent development (LangChain, LangGraph, multi-agent, context engineering) |
| `claude-prompt-engineering-guide` | Prompt engineering reference for Claude models |
| `commit-message` | Structured commit message generation |
| `github-workflow` | GitHub repo and workflow operations |
| `dev-review` | Developer contribution review over time periods |
| `security-review` | Security-focused code audit |
| `codebase-audit` | Full technical architecture review |
| `ui-ux-pro-max` | UI/UX design and implementation guidance |

### CLAUDE.md Standards

The `CLAUDE.md` file enforces development standards across all projects:

- **4-Layer Architecture**: API → Service → Repository → Database
- **Python**: Pydantic V2, async discipline, `uv` tooling, ruff linting
- **Frontend**: React Compiler (no manual memo), TanStack Query key factories, useEffect cleanup
- **Naming**: Strict conventions for files, classes, and identifiers
- **Single Elegant Version**: No legacy code, no `_v2` suffixes, no backward compatibility hacks

## Customization

### Adapt for your own use

1. **CLAUDE.md** — Replace with your own coding standards
2. **rules/** — Swap for your stack's conventions
3. **dippy/config** — Adjust allowed/denied commands for your workflow
4. **settings.json** — Modify permission rules, add/remove hooks
5. **commands/** — Create your own slash commands
6. **skills/** — Add domain-specific skills

### Credential management

This repo is designed to contain **zero credentials**. Sensitive data lives elsewhere:

| Secret | Location | Tracked? |
|--------|----------|----------|
| Discord bot token | `~/.claude/channels/discord/.env` | gitignored |
| MCP server tokens | Project-level `.mcp.json` or `.claude/settings.local.json` | gitignored per project |
| Auth cache | `~/.claude/mcp-needs-auth-cache.json` | gitignored |

## License

MIT
