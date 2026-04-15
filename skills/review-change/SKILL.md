---
name: review-change
description: Use when the user says /review-change or wants a findings-first review of current staged, unstaged, or targeted code changes.
---

# Review Change

Review code changes with a bug-finding mindset, not a change-summary mindset.

## Workflow

1. Determine scope from the current diff or the files the user named.
2. Inspect only that scope unless the user explicitly asks for broader review.
3. Prioritize correctness bugs, regressions, security risks, and missing tests.
4. Reference exact files and lines when possible.
5. Keep summary content brief after findings.

## Output

Use this structure:
- Findings ordered by severity
- Open questions or assumptions
- Brief residual risk summary

## Rules

- If there are no findings, say that explicitly.
- Do not silently fix issues unless the user asked for a review-and-fix workflow.
- Treat review comments as evidence-backed claims, not style preferences.
