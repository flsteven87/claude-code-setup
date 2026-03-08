# Prompt Engineering Standards

> Referenced from CLAUDE.md. These principles apply when writing or optimizing LLM prompts in the codebase.

## Core Philosophy: Principle-Driven, Not Case-Specific

LLM prompts should teach **how to think**, not **what to output**. A principle-driven prompt generalizes across scenarios; a case-specific prompt breaks the moment conditions shift.

| ❌ Case-Specific (Brittle) | ✅ Principle-Driven (Adaptive) |
|---|---|
| "If product has no reviews, suggest collecting reviews" | "Identify the attribute with the largest gap vs. benchmark, then recommend the highest-leverage action to close it" |
| "For shoes, check size. For electronics, check warranty" | "Evaluate whether category-relevant attributes are present based on the product type" |
| "If score < 60, say 'needs improvement'. If > 80, say 'good'" | "Assess quality relative to the scoring threshold and explain the primary factor driving the score" |
| "Return JSON with fields: title, description, score" | "Return a structured response containing: the subject identifier, your qualitative assessment, and the quantitative metric" |

## Rules

### 1. Teach Reasoning, Not Templates

- ❌ Enumerate every possible case → LLM follows list mechanically, misses unlisted cases
- ✅ State the evaluation principle → LLM applies it to any case, including novel ones

### 2. Describe Intent, Not Just Format

- ❌ "Return a JSON object with `action` and `reason` fields"
- ✅ "Recommend the single most impactful action and explain why it matters more than alternatives"
- The format instruction can follow, but the intent must come first

### 3. Use Constraints, Not Exhaustive Rules

- ❌ "Do not mention reviews if there are < 5 reviews. Do not suggest price changes if price is within 10% of average..."
- ✅ "Only recommend actions the merchant can realistically execute. Skip suggestions that require data not available in the input"
- Constraints define boundaries; exhaustive rules create gaps

### 4. Separate Deterministic from Interpretive

- ❌ Asking the LLM to do math, counting, or lookup (it will hallucinate)
- ✅ Do deterministic work in code, pass results to LLM for interpretation
- Pattern: code formats + calculates → LLM interprets + narrates

### 5. Provide Calibration, Not Scripts

- ❌ "High quality = 5 stars. Medium = 3 stars. Low = 1 star"
- ✅ "High quality means it would satisfy a discerning buyer without additional research. Calibrate against best-in-class competitors in the same category"
- Calibration anchors the LLM's judgment; scripts remove its judgment

### 6. One Prompt, One Cognitive Task

- ❌ Single prompt that reads context, analyzes gaps, synthesizes actions, and formats output
- ✅ Pipeline: Read → Diagnose → Synthesize (each prompt does one thing well)
- Complex multi-step reasoning degrades quality; decompose into focused stages

### 7. Make Skipping Explicit

- ❌ Hoping the LLM will skip irrelevant sections silently
- ✅ "If [condition], skip this section entirely and proceed to [next step]"
- LLMs tend to fill space; explicit skip instructions prevent noise

## Anti-Patterns

| Pattern | Why It Fails |
|---------|-------------|
| Long example lists | LLM mimics examples instead of understanding principle |
| Role-playing without task clarity | "You are a senior analyst" adds fluff, not precision |
| Nested conditionals in natural language | LLM loses track; use code for branching logic |
| Repeating the same instruction in different words | Adds noise, signals uncertainty, wastes tokens |
| "Be thorough and comprehensive" | Produces padding; specify what thoroughness means |

## Review Checklist

When reviewing prompts in the codebase:

- [ ] Could a new scenario break this prompt? (→ needs principle, not case list)
- [ ] Is the LLM being asked to do something deterministic? (→ move to code)
- [ ] Does the prompt say what to think about, or just what format to return?
- [ ] Are there > 3 conditional branches? (→ decompose or move branching to code)
- [ ] Would removing 30% of the text lose any actual instruction? (→ trim)
