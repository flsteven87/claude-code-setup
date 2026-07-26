# Harness Reference — Hooks & Permissions

> Moved out of CLAUDE.md 2026-07-25. These are **facts about the environment**, not instructions —
> hooks fire deterministically whether or not this file is in context. Read it when debugging why an
> action was blocked, when editing `settings.json`, or when adding a hook.
> The behavioral implications that actually change what Claude does stay in CLAUDE.md.

## Active hooks

Hooks live in `~/.claude/hooks/` and `~/.claude/bin/`.

| Hook | Event | What it does |
| --- | --- | --- |
| `auto-format.sh` | PostToolUse (Write/Edit/MultiEdit) | `uv run ruff format` + `ruff check --fix` on `.py`. Prettier on TS/JS/CSS is opportunistic — `npx --no` silently skips it unless the project has prettier installed. |
| `pre_write_guard.py` | PreToolUse (Write/Edit/MultiEdit) | **Denies** writes to `.env*`, `*.pem`, `*.key`, SSH private keys, `.ssh/`, `.aws/`, `.gnupg/`, `secrets.*`, `credentials*`, and `*.sql` under any `migrations/` directory. |
| `pre_push_guard.py` | PreToolUse (Bash) | **Denies** every `git push` carrying a force flag, by tokenizing argv rather than glob-matching: `--force`, `--force-with-lease`, `--mirror`, short-option bundles (`-uf`, `-fu`), `+refspec`, `git -c … push --force`, and force pushes hidden after `&&` / `;`. `--force-if-includes` alone is not a force and passes. |
| `workflow_route_guard.py` | PreToolUse (Workflow) | **Denies** `Workflow({name: ...})` launches — named/built-in workflows ship with no model routing. |
| `verify_gate.py` | Stop | Deterministic done=observed gate. Pipelines arm it (`uv run ~/.claude/hooks/verify_gate.py arm "<task>" "<check>"`); the turn cannot end until the end state is observed and `… clear` is run. Cwd-scoped, 6h TTL, platform force-ends after 8 consecutive blocks. |
| `auto_approve_safe.py` | PermissionRequest | Auto-approves everything except a word-boundary-regex dangerous list (`rm`, `sudo`, `git rebase`, `git reset --hard`, force pushes, discard-forms of `git checkout`/`git restore`, `kill`, macOS system-config commands); matches fall through to a manual prompt. It only sees what `settings.json` rules didn't already decide — `allow`ed commands never reach it, and `deny`/`ask` rules win over its output. |
| `pre_compact.py` | PreCompact | Context preservation before auto-compact. |
| `codex-reconcile-phantoms.sh` | UserPromptSubmit | Reconciles stale/dead Codex-inline job state before every prompt; warns if a live job exists in cwd. |
| `dippy` | PreToolUse (Bash) | External rule engine (config: `~/.claude/dippy/config`). **Denies** `pip`/`pip3` (enforces `uv add`) and the literal `rm -rf` prefix, plus sensitive-path protection. Writes `~/.claude/hook-approvals.log` on every Bash call. |
| Stop hook | Stop | macOS notification (`osascript`) + Glass sound; rotates `hook-approvals.log` and `logs/auto_approve.log` at >5MB. |
| TempoTerm status hooks | many | `--status-hook` calls that drive the terminal status indicator. No model context cost. |

## Permission rules (`settings.json`)

Evaluated **deny → ask → allow, first match wins** — an `ask` rule beats a broader `allow`.

- **deny** (hard-fail, unreachable even for hooks): force pushes in every spelling a glob can express (`--force`, `-f` in any position, `--force-with-lease`, `--mirror`, `-uf` bundles, `+refspec`), `git reset --hard *`, `git commit --amend*`, `git rebase -i *`, `git clean -f*`, catastrophic `rm -rf` targets, `mkfs`, `dd if=*`
  - Globs cannot parse Git's argument grammar, so `git -c … push --force` and similar reach `pre_push_guard.py` instead — that hook is what makes "no force push, ever" actually total
- **ask** (always prompts): `rm -rf *`, `git checkout -- *`, `git checkout .`, `git restore *` — the technical backing for Scope Discipline's "never discard files you didn't modify"
- Non-interactive `git rebase` forms are NOT denied — they fall through to `auto_approve_safe.py`'s prompt instead (different layer, same outcome)
- `defaultMode: acceptEdits`

## Other environment facts

- **Active worktrees break repo-walking CLIs** (e.g. `shopify app dev`) — they abort on duplicate
  configs inside `.claude/worktrees/<active>/`. Run such CLIs outside the worktree session.

## Why this matters in practice

Anthropic's own guidance: *a rule written in CLAUDE.md is a request; a `PreToolUse` hook is enforcement.*
When a rule must hold every time, add a hook rather than a prompt instruction.
