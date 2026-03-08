---
name: ai-agents
description: AI and agent development expertise covering LangChain, LangGraph, multi-agent systems, context engineering, evaluation, memory, and BDI patterns. Use when building AI agents, LLM pipelines, RAG systems, or any AI/agent workflow.
allowed-tools: Read
---

# AI & Agent Skills Index

This skill is a router. When activated, identify the relevant sub-skill(s) below and load them via the `Read` tool using the path provided. Do **not** invent guidance from memory — always read the sub-skill file first.

## How to Load a Sub-Skill

```
Read ~/.claude/skills/ai-agents/<skill-name>/SKILL.md
```

---

## Sub-Skill Index

### Framework & Architecture

| Sub-Skill | When to Use | Path |
|---|---|---|
| `framework-selection` | Choosing between LangChain, LangGraph, raw SDK, CrewAI, etc. | `~/.claude/skills/ai-agents/framework-selection/SKILL.md` |
| `langchain-fundamentals` | Building chains, prompts, output parsers, basic LangChain patterns | `~/.claude/skills/ai-agents/langchain-fundamentals/SKILL.md` |
| `langchain-middleware` | LCEL, runnables, callbacks, middleware in LangChain | `~/.claude/skills/ai-agents/langchain-middleware/SKILL.md` |
| `langchain-dependencies` | Managing LangChain package versions and dependency conflicts | `~/.claude/skills/ai-agents/langchain-dependencies/SKILL.md` |
| `langchain-rag` | RAG pipelines, retrievers, vector stores in LangChain | `~/.claude/skills/ai-agents/langchain-rag/SKILL.md` |

### LangGraph

| Sub-Skill | When to Use | Path |
|---|---|---|
| `langgraph-fundamentals` | Graphs, nodes, edges, state, basic LangGraph patterns | `~/.claude/skills/ai-agents/langgraph-fundamentals/SKILL.md` |
| `langgraph-persistence` | Checkpointers, memory, state persistence across runs | `~/.claude/skills/ai-agents/langgraph-persistence/SKILL.md` |
| `langgraph-human-in-the-loop` | Interrupts, approval flows, human review nodes | `~/.claude/skills/ai-agents/langgraph-human-in-the-loop/SKILL.md` |

### Agent Patterns & Design

| Sub-Skill | When to Use | Path |
|---|---|---|
| `multi-agent-patterns` | Supervisor, swarm, hierarchical, parallel agent architectures | `~/.claude/skills/ai-agents/multi-agent-patterns/SKILL.md` |
| `chat-agent-best-practices` | Conversational agents, turn management, dialogue design | `~/.claude/skills/ai-agents/chat-agent-best-practices/SKILL.md` |
| `hosted-agents` | Deploying agents to cloud, hosted LLM services | `~/.claude/skills/ai-agents/hosted-agents/SKILL.md` |
| `bdi-mental-states` | BDI (Belief-Desire-Intention) agent modeling | `~/.claude/skills/ai-agents/bdi-mental-states/SKILL.md` |
| `tool-design` | Designing tools/functions for agent use, MCP tool naming | `~/.claude/skills/ai-agents/tool-design/SKILL.md` |
| `project-development` | End-to-end AI project structure, dev workflow | `~/.claude/skills/ai-agents/project-development/SKILL.md` |

### Context Engineering

| Sub-Skill | When to Use | Path |
|---|---|---|
| `context-fundamentals` | Core concepts: context window, token budget, attention | `~/.claude/skills/ai-agents/context-fundamentals/SKILL.md` |
| `context-optimization` | Strategies to reduce token usage without losing fidelity | `~/.claude/skills/ai-agents/context-optimization/SKILL.md` |
| `context-compression` | Summarization, pruning, compressing context | `~/.claude/skills/ai-agents/context-compression/SKILL.md` |
| `context-degradation` | Diagnosing context rot, lost-in-the-middle, quality drops | `~/.claude/skills/ai-agents/context-degradation/SKILL.md` |
| `filesystem-context` | Using filesystem as external context / memory for agents | `~/.claude/skills/ai-agents/filesystem-context/SKILL.md` |

### Memory & Evaluation

| Sub-Skill | When to Use | Path |
|---|---|---|
| `memory-systems` | Short/long-term memory, vector memory, episodic memory | `~/.claude/skills/ai-agents/memory-systems/SKILL.md` |
| `evaluation` | General LLM/agent eval patterns, metrics, test harnesses | `~/.claude/skills/ai-agents/evaluation/SKILL.md` |
| `advanced-evaluation` | Advanced eval techniques: pairwise, LLM-as-judge, custom scorers | `~/.claude/skills/ai-agents/advanced-evaluation/SKILL.md` |

---

## Quick-Load Examples

**Working on a LangGraph agent with checkpointing:**
```
Read ~/.claude/skills/ai-agents/langgraph-fundamentals/SKILL.md
Read ~/.claude/skills/ai-agents/langgraph-persistence/SKILL.md
```

**Building a RAG pipeline and want to evaluate it:**
```
Read ~/.claude/skills/ai-agents/langchain-rag/SKILL.md
Read ~/.claude/skills/ai-agents/evaluation/SKILL.md
```

**Debugging context quality issues:**
```
Read ~/.claude/skills/ai-agents/context-degradation/SKILL.md
Read ~/.claude/skills/ai-agents/context-optimization/SKILL.md
```
