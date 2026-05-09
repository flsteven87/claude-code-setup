# Codex CLI Troubleshooting & Prompt Structure

## Tool selection priority

```
1. codex CLI via Bash       (preferred — most reliable)
2. mcp__codex__codex         (try if CLI unavailable)
3. codex:codex-rescue agent  (LAST RESORT — this is Claude, label clearly)
```

## CLI invocation pattern

```bash
cd /tmp && codex exec \
  --skip-git-repo-check \
  --sandbox read-only \
  '<prompt>' 2>&1 | tail -200
```

Why these flags:
- `--skip-git-repo-check`: avoid CWD-related friction
- `--sandbox read-only`: review-only, no risk of unintended writes
- `2>&1 | tail -200`: filter loader noise (skill loader errors at top), keep the actual response

Override model if needed: `-c 'model="gpt-5.5"'`. Use `model="<your-target>"` per `~/.codex/config.toml`.

## Common errors

### "The 'gpt-X.X' model requires a newer version of Codex"

Root cause: installed CLI is older than what the OpenAI API gate expects for this model.

```bash
codex --version                       # what's installed
npm view @openai/codex version        # what's actually latest on npm
npm install -g @openai/codex@latest   # upgrade
codex --version                       # confirm
```

Then retry. The Claude Code bundled MCP wrapper is often even more stale than the user's installed CLI — that's why Bash CLI takes priority.

### "The 'gpt-X.X' model is not supported when using Codex with a ChatGPT account"

Different from the version error. This means the model is not available to your account tier.

```bash
python3 -c "import json; d=json.load(open('/Users/<you>/.codex/models_cache.json')); print([m['slug'] for m in d['models']])"
```

Pick a slug from this list. If the desired model is missing, a CLI upgrade may make it appear (the cache is server-fetched and depends on CLI version capabilities).

### "TokenRefreshFailed: Failed to parse server response"

Usually harmless — comes from one MCP failing to refresh, doesn't block the main Codex response. Ignore.

### "failed to stat skills entry … (symlink): No such file or directory"

Broken symlinks under `~/.codex/skills/`. Codex tries to load Claude-Code skills via symlink and fails. Either:
- Re-link to the current plugin path (e.g., `~/.claude/plugins/cache/superpowers-marketplace/superpowers/<version>/skills/<name>`)
- Delete broken symlinks (Codex skills are usable without them)

Find broken symlinks:

```bash
find ~/.codex/skills -maxdepth 1 -type l ! -exec test -e {} \; -print
```

## Prompt structure for second-opinion review

Aim for 400-600 words. Structure:

```
You are an independent senior <DOMAIN> reviewer. ~500 words. Be blunt — push back, do not validate.

CONTEXT: <stack, system, scale, constraints>. <Origin: incident / audit / migration>.
Already-shipped fixes: <commit SHAs + 1-line descriptions>.

I consolidated <N> tickets into <M> PRs:

PR1 NEX-XXX (<priority change>): <60-word summary of scope>. Argued ships first because <reason>.
PR2 NEX-YYY (<priority>): <60-word summary>.
PR3 NEX-ZZZ (<priority>): <60-word summary>.

Block chain: NEX-XXX → NEX-YYY → NEX-ZZZ.

Dropped from original: <list with reasons>.

QUESTIONS:
Q1. Anything OBVIOUSLY WRONG before we hand to the implementing agent? (Push back; I want gaps, not validation.)
Q2. Is <specific architectural pattern> the right shape, or code smell to refactor toward <alternative>?
Q3. Is <specific parameter / threshold> right for our context, or do I need <different shape>?
Q4. Best-practice anchors I missed?

Cite <DOMAIN>/SRE/GitOps refs.
```

### Why this structure works

- **Context first**: Codex needs the same picture you have to make calls
- **State your plan as bullets, not prose**: Easy for the model to identify each item to challenge
- **Bias-fighting framing** ("push back, do not validate"): Without this, the model defaults to agreement
- **Specific questions, not "what do you think"**: Forces concrete answers
- **"Cite refs"**: Forces grounded answers (SRE Workbook, official docs, etc.) rather than handwaving

## What good Codex push-back looks like

From origin session, Codex (gpt-5.5) returned:

```
"Stop calling PR1 'GitOps' unless Git is the actual source of deployed truth and a pull-based reconciler applies it."

"Your `kubectl diff -k` 'exit 0 gate' is mislabeled. kubectl diff returns 0 for no differences and 1 when differences exist. So as a pre-deploy gate, it fails on the exact case you want: an intended change."

"`pg_stat_activity_count > 70` is fake rigor unless it is derived from `max_connections`, reserved headroom, pool budgets, and pod count. Absolute numbers without budget math are theater."
```

Note the shape: blunt assertion + concrete reason + suggested fix. **If Codex returns soft validation ("looks reasonable"), the prompt was too gentle — re-prompt with stronger framing.**

## Multi-round consultation

After first round, if Codex caught architectural-level issues (re-ordering, renaming concepts, dropping sub-tasks), do a second round:

```
Round 2 prompt:
"After your push-back, I made these changes: <delta from round 1>. 
Anything ELSE I missed, or any of your round-1 critiques that I patched wrong?"
```

One round is usually enough. Two rounds for high-stakes architectural decisions. Three rounds suggests the original plan needs to be thrown out, not patched.

## Codex prompt anti-patterns

- ❌ "What do you think of this plan?" — too open, gets validation
- ❌ Listing all 47 sub-tasks — Codex can't deeply engage with that volume
- ❌ Asking yes/no questions — collapses nuance to a coin flip
- ❌ Pre-supposing the answer ("Wouldn't this be better as X?") — primes confirmation
- ❌ Skipping the "be blunt" framing — Codex will be polite by default
