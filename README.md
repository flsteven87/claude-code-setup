# Claude Code Setup

My personal [Claude Code](https://claude.ai/code) configuration — layered permission defense, auto-formatting, and three end-to-end automation pipelines (`/implement` → `/ship` / `/merge-pr`).

> **Security notice:** this repo contains hooks that **auto-execute shell commands** when Claude Code runs. Review every file under `hooks/` before using. Never blindly clone someone else's Claude Code config without auditing it.

## Architecture

```
                              ┌────────────────────────────┐
                              │     Claude Code Runtime     │
                              └─────────────┬──────────────┘
                                            │
       ┌────────────────────────────────────┼────────────────────────────────────┐
       │                    │               │                 │                  │
┌──────▼──────┐   ┌─────────▼────────┐  ┌───▼───────────┐  ┌──▼───────────────┐
│ settings    │   │ Dippy            │  │ pre_write_    │  │ auto_approve_    │
│ .json       │   │ (PreToolUse,     │  │ guard.py      │  │ safe.py          │
│             │   │  Bash)           │  │ (PreToolUse,  │  │ (Permission-     │
│ Static      │   │                  │  │  Write/Edit)  │  │  Request)        │
│ allow/deny  │   │ Enforces uv,     │  │               │  │                  │
│ rules       │   │ blocks rm -rf,   │  │ Hard-blocks   │  │ Auto-approves    │
│             │   │ protects .env    │  │ writes to     │  │ safe ops;        │
│             │   │                  │  │ secrets       │  │ prompts on rm/   │
│             │   │                  │  │ (.env / .pem  │  │ sudo / rebase    │
│             │   │                  │  │  / .ssh / …)  │  │                  │
└─────────────┘   └──────────────────┘  └───────────────┘  └──────────────────┘
```

Four cooperating layers. Anything that slips one layer is still caught by the next.

## What's tracked

```
~/.claude/
├── CLAUDE.md                  # Development standards (4-layer architecture, naming, codex delegation, …)
├── settings.json              # Permissions, hooks, plugins, status line config
├── setup.sh                   # One-time bootstrap (Dippy install, copy config, chmod hooks)
├── statusline-command.sh      # Status bar: cwd, model, context %, rate limits
│
├── hooks/                     # 6 active hooks (see table below)
│   ├── auto-format.sh
│   ├── auto_approve_safe.py
│   ├── pre_compact.py
│   ├── pre_write_guard.py
│   ├── verify_gate.py
│   └── workflow_route_guard.py
│
├── commands/                  # 3 slash commands (heavy automation pipelines)
│   ├── implement.md           # /implement — plan-driven implementation w/ size-aware triage
│   ├── ship.md                # /ship      — main-based ship pipeline (simplify → verify → review → push)
│   └── merge-pr.md            # /merge-pr  — PR auto-pilot (review → fix → merge)
│
├── skills/                    # 16 tracked skills (see table below)
├── workflows/
│   └── deep-research.js       # Routed research workflow with per-stage models
├── rules/                     # backend.md, frontend.md, naming-conventions.md
├── references/                # prompt-engineering.md, etc.
│
└── dippy/
    └── config                 # Dippy allow/deny ruleset (copied to ~/.dippy/config by setup.sh)
```

> **Not tracked:** `plugins/` (auto-managed by Claude Code, machine-specific paths), `memory/` (auto-memory per-project), `logs/`, `projects/`, anything containing credentials.

## Quick start

### 1. Clone

```bash
# Back up existing config first
[ -d ~/.claude ] && mv ~/.claude ~/.claude.backup

git clone https://github.com/flsteven87/claude-code-setup.git ~/.claude
```

### 2. Run setup

```bash
cd ~/.claude && ./setup.sh
```

Verifies prerequisites (Claude Code CLI, `uv`), installs [Dippy](https://github.com/ldayton/Dippy), copies `dippy/config` to `~/.dippy/config`, makes hooks executable.

### 3. Install plugins

The exact plugin set this config assumes (as of 2026-07):

```bash
claude plugin install superpowers@superpowers-marketplace
claude plugin install codex@openai-codex
claude plugin install code-review@claude-plugins-official
claude plugin install typescript-lsp@claude-plugins-official
claude plugin install pyright-lsp@claude-plugins-official
claude plugin install andrej-karpathy-skills@karpathy-skills
claude plugin install impeccable@impeccable
claude plugin install ralph-loop@claude-plugins-official
```

### 4. Verify

```bash
claude
# Inside Claude Code:
/permissions    # Permission rules loaded
/hooks          # Hooks registered
```

## Hooks

| Hook | Event | Purpose |
|---|---|---|
| `dippy` | PreToolUse (Bash) | Validates every Bash command. Enforces `uv` over `pip`, blocks `rm -rf`, protects `.env*`. Exit 0 = allow, exit 2 = deny |
| `pre_write_guard.py` | PreToolUse (Write/Edit/MultiEdit) | **Hard-denies** writes to `.env*`, `*.pem`, `*.key`, SSH/AWS/GnuPG private material, `secrets.*`, `credentials*` |
| `auto-format.sh` | PostToolUse (Edit/Write/MultiEdit) | `ruff format` + `ruff check --fix` on `.py`; `prettier --write` on TS/JS/CSS |
| `auto_approve_safe.py` | PermissionRequest | Auto-approves safe ops; prompts on `rm`, `git rebase`, `git reset --hard`, `sudo`, `kill`, `shutdown`, etc. Logs to `~/.claude/logs/auto_approve.log` |
| `pre_compact.py` | PreCompact | Snapshots transcript before context compaction (keeps last 20) |
| `workflow_route_guard.py` | PreToolUse (Workflow) | Blocks unrouted named workflows so worker agents do not inherit the top-tier session model |
| `verify_gate.py` | Stop | Blocks completion while a delivery pipeline still has unobserved end-state checks |
| `osascript notify` | Stop | macOS native notification when Claude finishes a response |

`settings.json` also carries explicit deny rules for `git push --force origin main`, `git reset --hard *`, and `git commit --amend*`.

## Slash commands

| Command | What it does |
|---|---|
| `/implement` | Plan-driven implementation with size-aware triage. Codex executes; CC orchestrates. Does NOT commit (chain `/ship` after). |
| `/ship` | Solo / main-based ship pipeline. Express lane for tiny diffs; full lane = simplify (Codex) → verify → Codex review → verify-then-patch → commit → push to `origin/main` → worktree cleanup. |
| `/merge-pr` | PR auto-pilot. Review + auto-fix findings + merge open GitHub PR to main. |

Everything else (catchup, handoff, latest, brainstorming, planning, debugging, …) lives in the skills layer below or is delivered by an installed plugin.

## Skills (tracked locally)

16 skills live as real files under `skills/` — clone the repo and they work immediately, no plugin install required. Plugin-delivered skills (e.g. `superpowers:*`, `codex:*`) coexist via their own prefixed names.

| Skill | Use when |
|---|---|
| `strategic-next` | Producing the next-step strategy with extended thinking after deep project analysis |
| `latest` | Rebuilding MEMORY.md from current truth (git + Linear + CHANGELOG) and re-focusing it on what the session needs |
| `catchup` | Fast evidence-based context rebuild after a reset |
| `handoff` | End-of-session continuity capture into MEMORY.md |
| `rehydrate` | Forced deep re-read after `/compact` or long pauses, with best-practice endgame check |
| `narrate` | One-page visual brief of one topic — fixed contract: BLUF → one diagram → key-nodes table → gaps; `--full` for the deep walkthrough (replaces narrate-glance + narrate-topic) |
| `dispatch-strategy` | Dispatch waves + swim-lane visual for a ticket series against live git/Linear; board mode also picks what to close next (absorbed triage-next) |
| `reverse-thinking` | Critical pre-build review of an implementation plan / architecture spec |
| `topic-to-tickets` | Deep audit → Codex push-back → PR-shaped, dependency-ordered Linear tickets |
| `git-state-audit` | Audit + clean local + remote git state (status, branches, stash, worktrees, dangling commits) |
| `github-workflow` | Repo + workflow ops via `gh` CLI |
| `dev-review` | Time-period contribution review across NexRex repos (zh-tw narrative) |
| `daily-standup` | Ultra-short morning team update (zh-tw, 3 sections × ≤3 bullets) from yesterday's git + Linear |
| `graphify` | Build a persistent knowledge graph from a folder of files (code, docs, papers) |
| `humanizer` | Strip signs of AI-generated writing from text |
| `docs-cleanup` | Remove shipped plans/specs and re-current architecture docs against code truth |

## CLAUDE.md standards

The `CLAUDE.md` file enforces development standards across all projects:

- **4-layer architecture** — API → Service → Repository → DB
- **Python** — Pydantic V2, async discipline, `uv` tooling, ruff linting
- **Frontend** — React Compiler (no manual memo), TanStack Query key factories, useEffect cleanup
- **Naming** — strict conventions across files, classes, identifiers
- **Single Elegant Version** — no `_v2`, no legacy code, no backward-compat shims
- **Codex delegation policy** — Codex implements / reviews; Claude Code plans / synthesizes
- **Response shape** — recommendation-first, principle-filter before option menus, hard stop on milestone complete
- **Execution defaults** — built-in quality gate (Codex adversarial review before any plan/ticket finalizes), done = observed at the end state (deploys verified live, UI screenshot-matched), minimal fix first, production-data dry-run SOP
- **Stage-appropriate engineering** — pre-PMF posture: user-facing quality > automation completeness; eval/guard/dashboard infra is opt-in only
- **Communication** — zh-tw plain-language reporting that survives compaction and agent relays; completed work reported as delta (淨變化 / 在哪看 / 沒包含), never as raw diff or forwarded agent output
- **Git automation** — high automation, careful guardrails (auto-commit + auto-push for shipped work; deny rules + hooks fail-closed on destructive ops)

## Customization

To adapt for your own use:

1. **CLAUDE.md** — replace with your own standards (this is heavily project / preference specific)
2. **rules/** — swap for your stack
3. **dippy/config** — adjust Bash allow/deny
4. **settings.json** — modify permission rules, add/remove hooks
5. **commands/** — write your own pipelines
6. **skills/** — add domain-specific skills

### Credential management

Zero credentials live in this repo. Sensitive data lives outside:

| Secret | Location | Tracked? |
|---|---|---|
| MCP server tokens | Project-level `.mcp.json` or `.claude/settings.local.json` | gitignored per project |
| Auth cache | `~/.claude/mcp-needs-auth-cache.json` | gitignored |
| Auto-memory / sessions | `~/.claude/projects/<slug>/memory/`, `logs/`, `transcripts/`, etc. | gitignored (whole `projects/` tree) |

### Path portability

All hook commands use `~` for `$HOME` expansion (e.g. `~/.claude/hooks/auto-format.sh`), so tracked `settings.json` stays portable across machines.

## License

[MIT](LICENSE)
