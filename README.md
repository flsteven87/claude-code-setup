# Claude Code Setup

My personal [Claude Code](https://claude.ai/code) configuration — a layered context architecture, a
fail-closed permission defense, and an end-to-end ship pipeline (`/ship`).

> **Security notice:** this repo contains hooks that **auto-execute shell commands** when Claude Code
> runs. Read the current `permissions.defaultMode` and hook registrations from `settings.json`, then
> review every referenced file under `hooks/` and `bin/` before using this setup.

## Two architectures

### 1. Context — progressive disclosure

The agent should carry the smallest set of rules that still prevents mistakes. Three tiers, loaded at
different times:

```
CLAUDE.md              always in context   — behavioral policy for every session
   │
   ├── rules/          path-triggered      — frontend.md on **/*.ts|tsx|jsx,
   │                                         naming-conventions.md on **/*.ts|tsx|jsx|py
   │
   └── references/     read-on-demand      — pulled only when CLAUDE.md points at them:
                                             codex-delegation.md   before dispatching Codex or
                                                                   routing a fan-out
                                             harness.md            hooks, permissions, invocation
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
│ first match wins.  │   │   (Bash) blind force → │   │   (PermissionRequest)  │
│                    │   │   lease, rm → trash,   │   │   known native tools  │
│ A deny is a hard   │   │   pip → uv             │   │   + screened Bash     │
│ fail — unreachable │   │ pre_write_guard.py     │   │   unknown → runtime   │
│ even for hooks, so │   │   (file writes) .env,  │   │                        │
│ nothing downstream │   │   *.pem, *.key, .ssh   │   │ Completion evidence   │
│ can grant it back. │   │ workflow_route_guard   │   │   owned by the task   │
│                    │   │   .py (Workflow)       │   │   and delivery gates  │
└────────────────────┘   └────────────────────────┘   └────────────────────────┘
```

The gates suggest reversible alternatives where available. The task still needs authority for
the action, including the profile's confirmation for deleting work not proven merged. Unknown
tools defer to runtime permission handling. Bash screening covers common command forms; it does
not interpret arbitrary programs or replace the task's authorization boundary.

## What's tracked

```
~/.claude/
├── CLAUDE.md                    # Behavioral policy — loaded every session
├── settings.json                # Permissions, hooks, enabled plugins, status line
├── setup.sh                     # Idempotent bootstrap (deps, chmod, gate check, plugin list)
├── statusline-command.sh        # Status bar: cwd, model, context %, rate limits
│
├── rules/                       # Path-triggered standards
│   ├── frontend.md              #   **/*.ts|tsx|jsx — React Compiler, TanStack Query, UI language
│   └── naming-conventions.md    #   **/*.ts|tsx|jsx|py
│
├── references/                  # Read-on-demand (see context architecture above)
│   ├── codex-delegation.md
│   └── harness.md
│
├── hooks/                       # Hook implementations; settings.json selects the active set
├── agents/                      # Custom subagents
├── bin/                         # Maintenance scripts
├── commands/ship.md             # Thin /ship adapter to the shared canonical contract
├── skills/                      # Local skills + shared skill links + Matt manifest
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

Install the plugins this machine needs, then use `enabledPlugins` in `settings.json` as the current
enabled-state source:

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

### 4. Verify

Launch `claude`, then run `/permissions` and `/hooks` in an interactive terminal session to confirm
rules and hooks loaded.

## Hooks

| Hook | Event | Purpose |
|---|---|---|
| `pre_bash_guard.py` | PreToolUse (Bash) | The single Bash gate; tokenizes argv rather than glob-matching. **Denies with an alternative** so none of these costs a prompt: blind force pushes → `--force-with-lease` (`--force`, `--mirror`, `-uf` bundles, `+refspec`, `git -c … push --force`; the lease forms pass, and each repository's branch protection decides which branches accept them); `rm` / `rmdir` / `find -delete` / `xargs rm` → `trash`; `pip` → `uv`. Exempt: `git rm`, paths under `/tmp`, and heredoc bodies (a script that merely *mentions* `rm` is data, not a deletion) |
| `pre_write_guard.py` | PreToolUse (Write/Edit/MultiEdit) | **Hard-denies** writes to `.env*`, `*.pem`, `*.key`, SSH/AWS/GnuPG private material, `secrets.*`, and `credentials` / `credentials.<ext>` (note: not suffixed variants like `credentials_backup`) |
| `workflow_route_guard.py` | PreToolUse (Workflow) | Blocks `Workflow({name: …})` so worker agents can't silently inherit the top-tier session model. Use `scriptPath` into `workflows/` instead |
| `auto-format.sh` | PostToolUse (Edit/Write/MultiEdit) | `ruff format` + `ruff check --fix` on `.py`; `prettier --write` on TS/JS/CSS |
| `auto_approve_safe.py` | PermissionRequest | Preserves known native-tool automation and the existing Bash checks for uncommitted-work loss or machine reconfiguration. Unknown tools and MCP requests defer to runtime permissions; configured provider grants still apply. Logs to `logs/auto_approve.log` |
| `codex-reconcile-phantoms.sh` | UserPromptSubmit | Reconciles stale/orphaned Codex jobs before each turn |
| *(inline)* | Stop | macOS notification, then truncates `hook-approvals.log` / `logs/auto_approve.log` to the last 2000 lines once either passes 5 MB |

## Permissions

`settings.json` is the source of truth for the current default mode and permission lists. The stable layering is:

- **deny** — `rm -rf /`, `mkfs`, `dd if=`, `git reset --hard`, and `git commit --amend`.

  > Force pushes have no deny rules. Globs cannot tell `--force` from `--force-with-lease`, so any
  > pattern that blocks the blind form also blocks the safe one. `pre_bash_guard.py` parses argv
  > instead: it lets the lease forms through and redirects blind forms to them. Which branches
  > accept a force push at all is each repository's branch protection.
- **ask** — `git checkout -- *`, `git checkout .`, `git restore *`. Deliberately short: these three
  discard **uncommitted** changes, the one thing the reflog cannot bring back. Everything reversible
  was removed from the prompt path in 2026-07 (`git rebase`, `kill -9`, `chmod`, `launchctl`, …), and
  deletions moved to `pre_bash_guard.py`, which redirects them to `trash` instead of asking.
- **allow** — read/write/search tools, the safe `git` verbs, `uv` / `pnpm` / `npm` / `gh` / `cargo` /
  `go`, and the MCP servers this setup relies on.

## Skills

Local skills live under `skills/`; the self-hosted Matt manifest loads its selected upstream skills
from the marketplace clone.

| Skill | Use when |
|---|---|
| `next-move` | Pick the single next engineering move from code + Linear + git + the `MEMORY.md` checkpoint |
| `latest` | Rebuild `MEMORY.md` from current truth (git + Linear + CHANGELOG) and refocus it on the session |
| `catchup` | Fast evidence-based context rebuild after a reset |
| `handoff` | End-of-session continuity capture into `MEMORY.md` |
| `rehydrate` | Forced deep re-read after `/compact` or a long pause, with an endgame best-practice check |
| `narrate` | One-page visual brief of one topic — BLUF → one diagram → key-nodes table → gaps |
| `reverse-thinking` | Pre-build review of a plan / spec — distill the end state, back-derive preconditions, check the plan against them rather than against its own framing |
| `git-converge-main` | Converge owned branches / worktrees / stashes / PRs into a clean main — script-backed audit → plan → apply |
| `humanizer` | Strip signs of AI-generated writing from text |
| `milestone-dispatch` | Reconcile one program and choose or hand off its next coherent implementation milestone |
| `topics` | Compare workstreams by business outcome and recommend the next unit of attention |
| `audit-pr-topics` | Group a contributor's pull requests into topics and assess intent, risk, and remaining work |
| `strategy-review` | Turn a topic, delivery episode, or incident into an evidence-backed product and engineering strategy |

> `humanizer` is vendored from [blader/humanizer](https://github.com/blader/humanizer) v2.9.1 —
> update by re-cloning, never by hand-editing.

### Shared with Codex

Shared behavior uses one canonical contract or two runtime-specific adapters with the same explicit
completion criteria:

- `ship` is canonical at `~/.agents/skills/ship/SKILL.md`; Claude `/ship` and Codex `$ship` are thin
  adapters that run only on the user's request to ship, typed or in prose.
- Claude and Codex `handoff` both write the primary checkout's root `MEMORY.md` and refuse to
  overwrite a different active checkpoint.
- Script-backed shared skills resolve helpers from their declared canonical directory. Compare
  behavior and completion criteria; do not claim byte identity when runtime syntax differs.
- `milestone-dispatch`, `topics`, `audit-pr-topics`, and `strategy-review` remain canonical under
  `~/.agents/skills/` and appear natively in Claude through ignored directory symlinks.

`setup.sh` verifies required shared targets and safely creates missing native links without replacing
an existing path. It does not install or restore canonical skills; restore `~/.agents/skills` before
running setup on a new machine.

### Self-hosted mattpocock-skills

`skills/mattpocock-skills/` is **not** a plugin install. It is a self-contained runtime generated
from Matt Pocock's marketplace clone:

```
skills/mattpocock-skills/
├── .claude-plugin/plugin.json   # tracked — lists the selected skills to expose
└── skills/                      # ignored — generated copy of the selected upstream skills
```

Why self-host rather than `plugin install`:

- **`handoff` is excluded.** `/handoff` belongs to the local `MEMORY.md` skill, and a same-named
  plugin skill would shadow it.
- **Disabling the upstream plugin is not enough** — a same-named installed plugin makes the
  skills-directory scan skip this manifest. The upstream plugin must be *uninstalled*.

The marketplace clone is the sole upstream source. `scripts/reconcile_matt_manifest.py` is the sole
writer for the manifest and generated runtime; it stages and validates a complete copy before
replacing the previous runtime. Updating: `claude plugin marketplace update mattpocock`, then
`uv run python ~/.claude/scripts/reconcile_matt_manifest.py --write --runtime`. The daily updater
performs both steps while preserving the local handoff exclusion.

## Agents

Two custom subagents live under `agents/`: `code-reviewer` and `security-reviewer`, both read-only
fallbacks for when Codex cannot reach the evidence. Exploration and planning use the built-in
`Explore` and `Plan` agents. Read `references/codex-delegation.md` and the current runtime
configuration before dispatch; the README does not cache model aliases, cost ratios, or worker counts.

## Slash commands

| Command | What it does |
|---|---|
| `/ship` | Thin adapter to the shared reviewed-commit delivery contract: push/PR gates, merge, established deployment, observation, and exact task-local cleanup. |

Everything else comes from the skills layer or a plugin — spec / ticket / implement / debug / TDD /
review flows are delivered by `mattpocock-skills:*`.

## Maintenance scripts

| Script | What it does |
|---|---|
| `bin/update-all.sh` | Seven-stage refresh: Claude CLI → plugin marketplaces → Matt manifest → plugins → Codex CLI → `uv` tools → symlinks `bin/*` into `~/.local/bin`. Does **not** refresh vendored or shared skills |
| `bin/codex-hygiene` | Recovery for a wedged Codex plugin: kills matching companion/app-server processes and clears job state. Probes every job's pid first and **refuses (exit 1) while any job is genuinely alive**, because killing the shared app-server would take live jobs with it. `--dry-run` to preview, `--force` to sweep anyway |
| `bin/codex-reconcile-phantoms.sh` | The selective version, and the one wired as the `UserPromptSubmit` hook: probes each job's pid, marks only the dead ones failed (never deletes), touches no processes. Safe to run while other windows are live |

## What CLAUDE.md enforces

`CLAUDE.md` is behavioral policy written for frontier models: goals, boundaries, and completion
criteria, with the method left to the model. The harness system prompt already covers delivery
discipline, message shape, and autonomy, so the file carries only what it does not:

- **Authority** — a change request authorizes the whole local loop through the commit; a short list
  of irreversible actions is confirmed at the point of action; `/ship` owns delivery on request
- **Scope** — deliver at the intended scope, report nearby bugs as follow-ups, commit tests only
  where the task or the repository asks
- **Simplicity** — simplest shape first; every mechanism names the failure it prevents and leaves
  when that failure stops recurring; single path
- **Verification** — done means observed, including looking at rendered UI; no added verification
  ritual
- **Delegation** — delegate only large independent tracks; Codex as independent reviewer for
  material-risk changes; event-driven supervision
- **Communication** — zh-tw replies, business consequence before mechanism, one-screen final
  message, a bounded 淨變化 / 在哪看 / 沒包含 block, no system internals in product copy
- **Memory and Git** — `MEMORY.md` as the shared checkpoint corrected in place, append-only history

## Customization

1. **CLAUDE.md** — replace with your own policy (heavily preference-specific)
2. **rules/** — swap for your stack
3. **references/** — your own on-demand deep dives; point at them from `CLAUDE.md`
4. **hooks/pre_bash_guard.py** — adjust what the Bash gate redirects or denies
5. **settings.json** — permission rules, hooks, plugins
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
since every one is gated on `ORCA_AGENT_HOOK_*` variables that exist only inside an Orca pane.

This used to rest on remembering to stage by explicit pathspec, and a single `git add -A` was enough
to sweep the blocks in — which is how they reached the public repo twice on 2026-08-07. The rule is
now enforced instead of documented:

```bash
git update-index --skip-worktree settings.json    # set once; survives in .git/index
```

With that bit set, Git ignores worktree edits to `settings.json`, so `git add -A` cannot stage the
Orca blocks and `git status` stops reporting the file as modified. To change the *tracked* settings
deliberately:

```bash
git update-index --no-skip-worktree settings.json   # unlock
# edit, stage the portable content, commit
git update-index --skip-worktree settings.json      # re-lock
```

To stage a portable version without touching the live file — the usual case, since the worktree copy
must keep the Orca blocks for Orca to work:

```bash
jq '.hooks |= (with_entries(.value |= map(select(
     ([.hooks[]?.command // ""] | map(test("orca/agent-hooks")) | any) | not)))
   | with_entries(select(.value | length > 0)))' settings.json > /tmp/portable.json
git update-index --no-skip-worktree settings.json
git update-index --cacheinfo 100644,"$(git hash-object -w --stdin < /tmp/portable.json)",settings.json
git commit -m '...' && git update-index --skip-worktree settings.json
```

## License

[MIT](LICENSE)
