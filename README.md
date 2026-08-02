# Claude Code Setup

My personal [Claude Code](https://claude.ai/code) configuration — a layered context architecture, a
fail-closed permission defense, and an end-to-end ship pipeline (`/ship`).

> **Security notice:** this repo contains hooks that **auto-execute shell commands** when Claude Code
> runs, and `permissions.defaultMode` is `acceptEdits`. Review every file under `hooks/` and `bin/`
> before using. Never blindly clone someone else's Claude Code config without auditing it.

## Two architectures

### 1. Context — progressive disclosure

The agent should carry the smallest set of rules that still prevents mistakes. Three tiers, loaded at
different times:

```
CLAUDE.md              always in context   — behavioral policy for every session (~170 lines)
   │
   ├── rules/          path-triggered      — backend.md on **/*.py, frontend.md on
   │                                         **/*.ts|tsx|jsx, naming-conventions.md always
   │
   └── references/     read-on-demand      — pulled only when CLAUDE.md points at them:
                                             codex-delegation.md   before dispatching Codex
                                             model-routing.md      before a workflow / agent fan-out
                                             prompt-engineering.md before writing a prompt
                                             harness.md            hooks & permissions debugging
                                             autonomous-loops.md   unattended runs
```

The test for adding a line to `CLAUDE.md`: *would removing it cause a mistake?* If the agent would
already do it from the repo, the filesystem, or its system prompt, it gets cut — or demoted a tier.

### 2. Safety — fail-closed layers

```
                        ┌─────────────────────────┐
                        │   Claude Code Runtime   │
                        └────────────┬────────────┘
                                     │
      ┌──────────────────────────────┼──────────────────────────────┐
      │                              │                              │
┌─────▼──────────────┐   ┌───────────▼────────────┐   ┌─────────────▼──────────┐
│ settings.json      │   │ PreToolUse gates       │   │ Exit gates             │
│                    │   │                        │   │                        │
│ deny → ask → allow │   │ pre_bash_guard.py      │   │ auto_approve_safe.py   │
│ first match wins.  │   │   (Bash) force push →  │   │   (PermissionRequest)  │
│                    │   │   user, rm → trash,    │   │   auto-OKs everything  │
│ A deny is a hard   │   │   pip → uv             │   │   except uncommitted-  │
│ fail — unreachable │   │ pre_write_guard.py     │   │   work destroyers      │
│ even for hooks, so │   │   (file writes) .env,  │   │                        │
│ nothing downstream │   │   *.pem, *.key, .ssh   │   │ verify_gate.py (Stop)  │
│ can grant it back. │   │ workflow_route_guard   │   │   blocks "done" while  │
│                    │   │   .py (Workflow)       │   │   end state unobserved │
└────────────────────┘   └────────────────────────┘   └────────────────────────┘
```

The gates prefer **redirecting to a reversible alternative over stopping to ask**: a
deletion is denied with "use `trash`" rather than prompted, because a recoverable
deletion needs no confirmation. What survives as a prompt is the short list that
destroys work nothing can restore.

Anything that slips one layer is still caught by the next.

## What's tracked

```
~/.claude/
├── CLAUDE.md                    # Behavioral policy — loaded every session
├── settings.json                # Permissions, hooks, enabled plugins, status line
├── setup.sh                     # Idempotent bootstrap (deps, chmod, gate check, plugin list)
├── statusline-command.sh        # Status bar: cwd, model, context %, rate limits
│
├── rules/                       # Path-triggered standards
│   ├── backend.md               #   **/*.py   — 4-layer architecture, Pydantic V2, async, uv, ruff
│   ├── frontend.md              #   **/*.ts|tsx|jsx — React Compiler, TanStack Query, effects
│   └── naming-conventions.md    #   always
│
├── references/                  # Read-on-demand (see context architecture above)
│   ├── codex-delegation.md
│   ├── model-routing.md
│   ├── prompt-engineering.md
│   ├── harness.md
│   └── autonomous-loops.md
│
├── hooks/                       # 7 active hooks + 1 rename shim (see table below)
├── agents/                      # 4 routed subagents (see table below)
├── bin/                         # 3 maintenance scripts (one is a live hook)
├── commands/ship.md             # /ship — the only local slash command
├── skills/                      # 12 local skills + the mattpocock self-host manifest
└── workflows/deep-research.js   # Routed research workflow with per-stage models
```

> **Not tracked:** `plugins/` (auto-managed, machine-specific paths), `projects/` (per-project
> auto-memory, sessions, transcripts), `logs/`, `backups/`, `*.log`, `.credentials.json`,
> `mcp-needs-auth-cache.json`, `secrets/`. The full list is in [`.gitignore`](.gitignore) — it names
> specific paths rather than pattern-matching every possible secret, so audit before adding files.

## Quick start

### 1. Clone

```bash
[ -d ~/.claude ] && mv ~/.claude ~/.claude.backup
git clone https://github.com/flsteven87/claude-code-setup.git ~/.claude
```

### 2. Run setup

```bash
cd ~/.claude && ./setup.sh
```

Verifies prerequisites (Claude Code CLI, `uv`, `trash`), makes `hooks/*.sh` + `bin/*` executable
(Python hooks run through `uv run`, so they need no exec bit), and fails the run if
`pre_bash_guard.py` does not deny a test deletion — an open Bash gate must not pass setup silently.
It then **prints** the plugin and marketplace commands for steps 3–4; plugin installation is
interactive, so `setup.sh` never runs it for you.

### 3. Install plugins

Six plugins, matching `enabledPlugins` in `settings.json`:

```bash
claude plugin install codex@openai-codex
claude plugin install code-review@claude-plugins-official
claude plugin install typescript-lsp@claude-plugins-official
claude plugin install pyright-lsp@claude-plugins-official
claude plugin install ralph-loop@claude-plugins-official
claude plugin install andrej-karpathy-skills@karpathy-skills
```

> **Do not `plugin install mattpocock-skills@mattpocock`** — those skills are self-hosted instead.
> See [Self-hosted mattpocock-skills](#self-hosted-mattpocock-skills) below.

### 4. Optional native dependency

`settings.json` wires [TempoTerm](https://tempoterm.com) status hooks on eight lifecycle events
(`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`,
`Notification`, `Stop`, `SessionEnd` — every event except `PreCompact`). Without
`/Applications/TempoTerm.app` these fail harmlessly but noisily — install TempoTerm, or strip the
`tempo-term` entries from `settings.json`.

### 5. Verify

Launch `claude`, then run `/permissions` and `/hooks` in an interactive terminal session to confirm
rules and hooks loaded.

## Hooks

| Hook | Event | Purpose |
|---|---|---|
| `pre_bash_guard.py` | PreToolUse (Bash) | The single Bash gate; tokenizes argv rather than glob-matching. **Denies with an alternative** so none of these costs a prompt: force pushes → hand to the user (`--force`, `--force-with-lease`, `--mirror`, `-uf` bundles, `+refspec`, `git -c … push --force`); `rm` / `rmdir` / `find -delete` / `xargs rm` → `trash`; `pip` → `uv`. Exempt: `git rm`, paths under `/tmp`, and heredoc bodies (a script that merely *mentions* `rm` is data, not a deletion) |
| `pre_write_guard.py` | PreToolUse (Write/Edit/MultiEdit) | **Hard-denies** writes to `.env*`, `*.pem`, `*.key`, SSH/AWS/GnuPG private material, `secrets.*`, and `credentials` / `credentials.<ext>` (note: not suffixed variants like `credentials_backup`) |
| `workflow_route_guard.py` | PreToolUse (Workflow) | Blocks `Workflow({name: …})` so worker agents can't silently inherit the top-tier session model. Use `scriptPath` into `workflows/` instead |
| `auto-format.sh` | PostToolUse (Edit/Write/MultiEdit) | `ruff format` + `ruff check --fix` on `.py`; `prettier --write` on TS/JS/CSS |
| `auto_approve_safe.py` | PermissionRequest | Auto-approves everything except commands that destroy **uncommitted** work (`git reset --hard`, `git restore`, `git checkout --`) or reconfigure the machine (`sudo`, `csrutil`, `spctl`, `shutdown`, `reboot`, device writes). Logs to `logs/auto_approve.log` |
| `pre_compact.py` | PreCompact | Snapshots the transcript before context compaction (keeps last 20) |
| `verify_gate.py` | Stop | Blocks completion while a delivery pipeline still has unobserved end-state checks (armed by `/ship` stage 6.5) |
| `codex-reconcile-phantoms.sh` | UserPromptSubmit | Reconciles stale/orphaned Codex jobs before each turn |
| *(inline)* | Stop | macOS notification, then truncates `hook-approvals.log` / `logs/auto_approve.log` to the last 2000 lines once either passes 5 MB |

## Permissions

`settings.json` runs `defaultMode: auto` with three explicit lists:

- **deny** (22 rules) — `rm -rf /`, `mkfs`, `dd if=`, `git reset --hard`, `git commit --amend`, and
  every force-push spelling a glob can express: `--force` / `-f` in any position, bare `git push -f`,
  `--force-with-lease`, `--mirror`, short-option bundles, and `+refspec`.

  > Permission rules are globs with no awareness of Git's argument grammar, so they cannot express
  > "a force flag anywhere in this push" on their own — `git -c … push --force` slips past any
  > pattern short enough to be safe. That is what `pre_bash_guard.py` is for: the deny list is the
  > strongest layer (a hard fail no hook can grant back), and the hook parses argv to close what
  > globs structurally cannot reach. Neither layer is load-bearing alone.
- **ask** — `git checkout -- *`, `git checkout .`, `git restore *`. Deliberately short: these three
  discard **uncommitted** changes, the one thing the reflog cannot bring back. Everything reversible
  was removed from the prompt path in 2026-07 (`git rebase`, `kill -9`, `chmod`, `launchctl`, …), and
  deletions moved to `pre_bash_guard.py`, which redirects them to `trash` instead of asking.
- **allow** — read/write/search tools, the safe `git` verbs, `uv` / `pnpm` / `npm` / `gh` / `cargo` /
  `go`, and the MCP servers this setup relies on.

## Skills

12 skills live as real files under `skills/` — clone the repo and they work immediately, no plugin
install required.

| Skill | Use when |
|---|---|
| `next-move` | Pick the single next engineering move from code + Linear + git + the `MEMORY.md` checkpoint |
| `latest` | Rebuild `MEMORY.md` from current truth (git + Linear + CHANGELOG) and refocus it on the session |
| `catchup` | Fast evidence-based context rebuild after a reset |
| `handoff` | End-of-session continuity capture into `MEMORY.md` |
| `rehydrate` | Forced deep re-read after `/compact` or a long pause, with an endgame best-practice check |
| `narrate` | One-page visual brief of one topic — BLUF → one diagram → key-nodes table → gaps (`--full` for the deep walkthrough) |
| `reverse-thinking` | Pre-build review of a plan / spec — distill the end state, back-derive preconditions, check the plan against them rather than against its own framing |
| `git-converge-main` | Converge owned branches / worktrees / stashes / PRs into a clean main — script-backed audit → plan → apply |
| `docs-cleanup` | Remove shipped plans/specs and re-current architecture docs against code truth |
| `humanizer` | Strip signs of AI-generated writing from text |

> `humanizer` is vendored from [blader/humanizer](https://github.com/blader/humanizer) v2.9.1 —
> update by re-cloning, never by hand-editing.

### Shared with Codex

Four skills are mirrored from `~/.codex/skills/` so both agents do the job identically. **Codex is
the source of truth** — author there, then mirror here. Each Codex copy carries an extra
`agents/openai.yaml` (platform metadata, no Claude Code equivalent); the Claude Code copies convert
Codex's `$skill` invocation syntax to `/skill` and resolve `$skill_dir` to the skill's own directory.

| Shared skill | Claude Code copy lives in | Why it must not drift |
|---|---|---|
| `handoff` | `skills/` | Both agents checkpoint into the same repo-root `MEMORY.md`; either resumes the other's work. `SKILL.md` is byte-identical |
| `next-move` | `skills/` | One portfolio decision model across both agents |
| `git-converge-main` | `skills/` | Script-backed (`scripts/git_converge.py` + tests); divergent copies would apply different mutation rules to the same repo |
| `nexrex-weekly-engineering-report` | `nr-platform/.claude/skills/` | Script-backed (`scripts/collect_git_activity.py` + tests); the report contract *is* the deliverable |

`nexrex-weekly-engineering-report` reads that repo's `AGENTS.md` and NEX Linear team, so its Claude
Code copy is checked into `nr-platform` rather than held here — it is still Codex-mirrored, just
from a different directory. Its scripts also carry that repo's `black`/`isort` formatting, so only
`SKILL.md` is claimed byte-identical.

Check parity with:

```bash
for s in handoff next-move git-converge-main; do
  diff -q ~/.codex/skills/$s/SKILL.md ~/.claude/skills/$s/SKILL.md
done
diff -q ~/.codex/skills/nexrex-weekly-engineering-report/SKILL.md \
        ~/Desktop/NexRex/nr-platform/.claude/skills/nexrex-weekly-engineering-report/SKILL.md
```

`handoff`, `next-move`, and `nexrex-weekly-engineering-report` are byte-identical and should be
silent. Only `git-converge-main` differs — the `$`→`/` conversion plus a Claude-specific `skill_dir`
assignment.

### Self-hosted mattpocock-skills

`skills/mattpocock-skills/` is **not** a plugin install. It is a local manifest that loads Matt
Pocock's skills straight out of the marketplace clone:

```
skills/mattpocock-skills/
├── .claude-plugin/plugin.json   # tracked — pins the 21 skills to expose
└── skills -> ../../plugins/marketplaces/mattpocock/skills   # symlink into the (untracked) clone
```

Why self-host rather than `plugin install`:

- **`handoff` is excluded.** `/handoff` belongs to the local `MEMORY.md` skill, and a same-named
  plugin skill would shadow it.
- **`disable-model-invocation` is stripped** from `handoff` / `catchup` / `latest`. That flag hides a
  skill from the model's list entirely, and a subagent can never route around it.
- **Disabling the upstream plugin is not enough** — a same-named installed plugin makes the
  skills-directory scan skip this manifest. The upstream plugin must be *uninstalled*.

Updating: `claude plugin marketplace update mattpocock`. Only regenerate `plugin.json` when upstream
**adds** a skill.

## Agents

Four subagents under `agents/`, each pinned to a tier per the routing table in `CLAUDE.md` Part 3 —
worker tier drives roughly 5× the cost of orchestrator tier, so nothing inherits the session model by
accident.

| Agent | Model | Use when |
|---|---|---|
| `researcher` | `haiku` | Explore the codebase and external docs for context without polluting the main window |
| `code-reviewer` | `opus` | Quality / security / best-practice review after a change |
| `security-reviewer` | `opus` | Auth, authorization, RLS policies, API surface, sensitive-data handling |
| `test-writer` | `opus` | Generate tests following existing project conventions |

## Slash commands

| Command | What it does |
|---|---|
| `/ship` | Solo / main-based ship pipeline. Express lane for tiny diffs; full lane = simplify (Codex) → verify → Codex review → verify-then-patch → commit → push to `origin/main` → worktree cleanup |

Everything else comes from the skills layer or a plugin — spec / ticket / implement / debug / TDD /
review flows are delivered by `mattpocock-skills:*`.

## Maintenance scripts

| Script | What it does |
|---|---|
| `bin/update-all.sh` | Six-stage refresh: Claude CLI → plugin marketplaces → plugins → Codex CLI → `uv` tools → symlinks `bin/*` into `~/.local/bin`. Does **not** refresh vendored skills like `humanizer` |
| `bin/codex-hygiene` | Recovery for a wedged Codex plugin: kills matching companion/app-server processes and clears job state. Probes every job's pid first and **refuses (exit 1) while any job is genuinely alive**, because killing the shared app-server would take live jobs with it. `--dry-run` to preview, `--force` to sweep anyway |
| `bin/codex-reconcile-phantoms.sh` | The selective version, and the one wired as the `UserPromptSubmit` hook: probes each job's pid, marks only the dead ones failed (never deletes), touches no processes. Safe to run while other windows are live |

## What CLAUDE.md enforces

`CLAUDE.md` is behavioral policy — language and framework standards live in `rules/`. (The one
stack-specific rule it keeps is routing schema changes through the Supabase MCP, because that one is
enforced by a hook rather than by a linter.)

- **Single Elegant Version** — one current version of everything; no `_v2`, no legacy, no
  backward-compat shims, no patchwork repairs
- **Scope discipline** — minimal best-practice fix first; abstraction layers need an explicit go-ahead
- **Stage-appropriate engineering** — pre-PMF posture; user-facing quality beats automation
  completeness, and eval / CI-guard / dashboard infra is opt-in only
- **Execution defaults** — built-in quality gate (Codex adversarial review before any plan or spec
  finalizes), *done = observed at the end state* (deploys verified live, UI screenshot-matched),
  production-data dry-run SOP
- **Response shape** — recommendation-first; principle-filter before any option menu; decisions lead
  with the consequence and attach the mechanism one line below; hard stop on milestone complete
- **Communication** — zh-tw reporting that survives compaction and agent relays; completed work
  reported as a delta (淨變化 / 在哪看 / 沒包含), never as a raw diff or forwarded agent output
- **Delegation & routing** — Codex implements and reviews, Claude Code plans and synthesizes; every
  subagent and workflow stage is routed to a tier
- **Git automation** — high automation with careful guardrails: auto-commit and auto-push for shipped
  work, deny rules and hooks fail closed on destructive ops

## Customization

1. **CLAUDE.md** — replace with your own policy (heavily preference-specific)
2. **rules/** — swap for your stack
3. **references/** — your own on-demand deep dives; point at them from `CLAUDE.md`
4. **hooks/pre_bash_guard.py** — adjust what the Bash gate redirects or denies
5. **settings.json** — permission rules, hooks, plugins; drop the TempoTerm entries if unused
6. **agents/** + **skills/** + **commands/** — your own workers and pipelines

### Credential management

Zero credentials live in this repo.

| Secret | Location | Tracked? |
|---|---|---|
| MCP server tokens | Project-level `.mcp.json` or `.claude/settings.local.json` | gitignored per project |
| Auth cache | `~/.claude/mcp-needs-auth-cache.json` | gitignored |
| Auto-memory / sessions / transcripts | `~/.claude/projects/<slug>/` | gitignored (whole tree) |

### Path portability

All hook commands use `~` for `$HOME` expansion, so tracked `settings.json` stays portable across
machines. `setup.sh` fails the run if a hardcoded `/Users/` path appears.

That guard is why `settings.json` reads as modified on a machine running the Orca desktop app. Orca
injects ten hook blocks carrying absolute `/Users/<you>/.orca/agent-hooks/` paths, and those are
**deliberately never committed** — seeing that delta in `git status` is the expected steady state,
not something to clean up. They are an install artifact under the same rule as `plugins/`:
auto-generated plus machine-specific stays out of the repo. Committing them would buy nothing on
either side — Orca re-injects them wherever it is installed, and everywhere else each block no-ops,
since every one is gated on `ORCA_AGENT_HOOK_*` variables that exist only inside an Orca pane. Stage
by explicit pathspec, never `git add -A`.

## License

[MIT](LICENSE)
