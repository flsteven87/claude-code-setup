---
name: learned
description: Create, update, or retrieve project-specific micro-skills and hard-won learnings from past sessions. Use when you discover a reusable pattern, a gotcha worth capturing, a project-specific convention, or when asked to "remember this" or "save this pattern".
allowed-tools: Read, Write, Glob
---

# Learned — Micro-Skill Manager

This skill manages a collection of project-specific micro-skills built from real session experience. Each micro-skill is a tiny, atomic, reusable piece of guidance that captures what would otherwise be lost between sessions.

## When to Activate

- User says "記住這個", "save this pattern", "下次也這樣做"
- You discover a project-specific gotcha or non-obvious behavior
- You find a repeating pattern that isn't yet in CLAUDE.md
- User asks to retrieve or list captured learnings
- A task is repeatedly done the same way across sessions

## Actions

### 1. Create a New Micro-Skill

Use `~/.claude/skills/learned/SKILL_TEMPLATE.md` as the base.

Save to: `~/.claude/skills/learned/<slug>.md`  
Naming: short, lowercase, kebab-case (e.g. `supabase-auth-gotcha.md`, `tanstack-invalidation-pattern.md`)

Fill all template sections with **specific, actionable** content. Avoid vague generalities.

### 2. List Existing Micro-Skills

```
Glob ~/.claude/skills/learned/*.md
```

Exclude `SKILL.md` and `SKILL_TEMPLATE.md`.

### 3. Retrieve a Micro-Skill

```
Read ~/.claude/skills/learned/<slug>.md
```

### 4. Update a Micro-Skill

Read → edit the relevant section → Write back. Preserve structure.

### 5. Retire a Micro-Skill

When a pattern is superseded or no longer applies, update `status: deprecated` in the frontmatter rather than deleting. Add `replaced_by:` if applicable.

## Quality Standards

Each micro-skill must be:
- **Atomic** — one concept, one pattern
- **Actionable** — steps are concrete and repeatable  
- **Scoped** — clearly states when it applies AND when it doesn't
- **Current** — reflects the latest codebase reality

Never create micro-skills that duplicate content already in CLAUDE.md or project rules.
