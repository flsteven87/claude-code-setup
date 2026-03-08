---
name: claude-prompt-engineering-guide
description: "Comprehensive Claude prompt engineering reference covering Opus 4.6/Sonnet 4.6/Haiku 4.5, system vs user prompts, Anthropic's official prompt structure, advanced techniques (CoT, adaptive thinking, tool use), MCP integration, and production prompt patterns. Use when designing system prompts, optimizing prompt performance, or learning Claude-specific prompt engineering."
---

# Claude Professional Prompt Engineering Guide

Comprehensive reference for Claude Opus 4.6, Sonnet 4.6 & Haiku 4.5 prompt engineering.

## When to Use

- Designing or optimizing system prompts for Claude models
- Understanding Claude-specific prompt patterns (adaptive thinking, effort parameter)
- Learning Anthropic's official prompt structure and best practices
- Integrating prompts with MCP tools and Skills
- Comparing prompt strategies across Claude model tiers

## Quick Reference

### Anthropic's 10-Component Framework

1. **Context** — Background information and domain knowledge
2. **Goal** — Clear objective statement
3. **Constraints** — Boundaries and limitations
4. **Examples** — 3-5 few-shot demonstrations in `<examples>` tags
5. **Format** — Desired output structure
6. **Tone** — Voice and style guidelines
7. **Contingencies** — Edge case handling
8. **References** — External sources or documentation
9. **Thinking** — Reasoning strategy (CoT, adaptive)
10. **Output** — Final deliverable specification

### Key Claude 4.x Patterns

- **XML structuring**: Use `<instructions>`, `<context>`, `<examples>` tags for clear sections
- **Positive instructions**: "Write in prose" beats "Don't use markdown"
- **Adaptive thinking**: Let Claude decide reasoning depth based on complexity
- **Effort parameter**: Control depth without prompt changes (GA in 4.6)
- **No prefill**: Assistant turn prefilling removed in Claude 4.6 — use system prompt instructions instead

### Model Selection Guide

| Model | Best For | Context | Strengths |
|-------|----------|---------|-----------|
| Opus 4.6 | Complex reasoning, coding agents | 200K | Deepest analysis, sustained coherence |
| Sonnet 4.6 | Balanced speed + quality | 200K | Best cost/performance ratio |
| Haiku 4.5 | Fast tasks, classification | 200K | Lowest latency, highest throughput |

## Full Reference

For detailed coverage of all topics, read `references/Claude-Prompt-Guide.md`:
- Architecture deep-dive and attention mechanics
- System prompt vs user prompt strategies
- Advanced techniques (CoT, tool use prompting, structured output)
- MCP, Skills & Superpowers integration
- Production prompt patterns and examples
- Memory Bank reference

For skill file authoring best practices, read `references/skills-guide.md`.
