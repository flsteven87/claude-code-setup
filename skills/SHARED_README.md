# Shared Skills SSOT

Updated: 2026-04-09

This directory is the personal shared skill catalog for cross-agent use.

Consumers:
- `/Users/po-chi/.claude/skills`
- `/Users/po-chi/.codex/skills`

Operational rules:
- Add or edit shared personal skills here first.
- Run `/Users/po-chi/.codex/bin/sync-shared-skills.sh` after any rename,
  addition, or deletion so Claude and Codex mirrors stay clean.
- Keep each skill self-contained with a resolvable `SKILL.md`.
- Do not leave stale symlinks here; this directory is the source of truth.
