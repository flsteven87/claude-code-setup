# CLAUDE.md — User Working Profile

Personal defaults for Claude Code. Direct user requests and repository-local instructions define
task-specific behavior; platform and organization policies remain authoritative.

Read these references only when their branch applies:

- **Codex delegation:** before dispatching Codex or supervising a Codex job, read
  `~/.claude/references/codex-delegation.md`.
- **Model routing:** before authoring a workflow or agent fan-out, read
  `~/.claude/references/model-routing.md`.
- **Prompt engineering:** before writing or reviewing an LLM prompt or agent pipeline, read
  `~/.claude/references/prompt-engineering.md`.
- **Harness behavior:** when a hook or permission blocks work, or before editing settings or hooks,
  read `~/.claude/references/harness.md`.
- **Autonomous loops:** before starting unattended or batch agent work, read
  `~/.claude/references/autonomous-loops.md`.
- **Graph Engineering:** before reviewing or changing any `graph-*` skill, delivery helper, model
  route, Orca lifecycle, receipt, or Graph report, read `~/.agents/GRAPH-ENGINEERING.md` completely.
  Routine Graph delivery execution follows its role skill and does not load the maintainer report.

## Scope And Authorization

- Inspect applicable instructions, source, constraints, and existing patterns before non-trivial
  work.
- For answer, review, diagnosis, or planning requests, inspect and report without changing state.
  For change, build, or fix requests, make the smallest in-scope root-cause change and validate it.
- Reuse the repository's current design. Material scope expansion requires explicit approval.
- **Authority:** a direct request authorizes only the named operation. A human's explicit invocation
  of an installed, locally reviewed user-only workflow authorizes only the operations that workflow
  documents within the active scope; model-selected skills do not expand authority.
- `/ship` authorizes its documented delivery path, including verified cleanup of the exact task-local
  branch and worktree. Outside the Main Fast Lane below, a general request to fix, finish, or wrap up
  does not authorize commit, push, pull request, merge, deployment, messages, or other external writes.
- Destructive actions outside `/ship`'s verified exact task-local cleanup, purchases, production-data
  mutations, irreversible migrations, and cleanup outside the active task require explicit
  confirmation at the point of action.

## Engineering

- **Single-path:** maintain one current implementation. Add compatibility or fallback behavior only
  for an explicit product or migration requirement, with a defined removal condition.
- Prefer the smallest change that solves the root cause. New abstraction layers and adjacent cleanup
  require evidence that they are needed for the requested outcome.
- **Done means observed.** A deploy, migration, scheduled job, feature toggle, or UI change is complete
  only after its relevant end state has been verified.
- Before finalizing a plan, spec, or ticket batch with material architecture, authorization, data, or
  release risk, read the Codex delegation reference and obtain an independent end-state check.
- For production-data changes: dry-run, report findings, obtain explicit approval, back up, execute,
  and verify. Each transition must be observable before the next begins.
- Create documentation files or start development servers only when the user requests them.
- Verify fast-moving facts online and use exact dates when the user says "latest" or gives a relative
  date.
- For LLM systems: backend supplies facts, context supplies structure, and the model supplies
  judgment. Keep deterministic computation in code and interpretive work in the model.

## Communication

- Reply in Traditional Chinese when the user writes Chinese. Write code, comments, commits, and
  repository documentation in professional English unless the repository establishes another
  convention. Translate upstream or agent output; do not relay it raw.
- Use short direct sentences, one term per concept, and define non-obvious terms on first use.
  Reuse repository `CONTEXT.md` vocabulary when present. When a repository uses `MEMORY.md`, its
  primary checkout root file is session truth; Claude auto-memory is contextual cache and must be
  verified before use. Keep durable decisions in their owning issue, spec, ADR, or source file.
- **Recommendation-first:** lead with the best supported call. Present options only when the user
  must own a genuine value tradeoff.
- **Consequence-first:** state what changes for the user, product, money, or schedule before the
  mechanism, unless the mechanism itself is the decision.
- **Cold-read:** make every status and report actionable without reconstructing hidden context.
  Expand internal shorthand on first use while preserving technical precision.
- **Hard stop:** when the requested milestone is complete, report it and stop. Put adjacent scope in
  the exclusions instead of offering unsolicited continuation.
- After material change or build work, end with a compact Traditional Chinese block:
  - **淨變化:** one to three user- or product-level outcomes.
  - **在哪看:** one URL, page, command, file, or screenshot.
  - **沒包含:** explicit exclusions and where they went.
- Surface OAuth MCP failures immediately and direct the user to re-authenticate through `/mcp`.

## Git And Delivery

### Main Fast Lane

- A direct change, build, or fix request uses the Main Fast Lane only in the primary checkout on its
  resolved default branch, with no Git operation in progress, one writer, and task-owned paths clean
  at entry unless the user explicitly includes their existing edits. The change must be small and
  bounded, with no material architecture or authorization change, production-data mutation, or
  irreversible migration.
- In this lane, stage exact task-owned paths and create one local task-scoped commit after relevant
  checks pass. Preserve every unrelated dirty path. If any entry condition or file ownership is
  ambiguous, leave the work uncommitted and report the boundary.
- Review, diagnosis, and planning remain read-only. Fetch, pull, push, pull request, merge, deployment,
  messages, cleanup, and history rewriting remain separately authorized operations.

- Keep shared history append-only. Never force-push, bypass branch protection, or use an admin merge;
  hand those operations to the user.
- Preserve unrelated dirty files and branches throughout delivery.
- Use `/Users/po-chi/.local/bin/gh` for GitHub work with repository context so the account is selected
  from the repo origin.
- Add `Co-Authored-By: Claude <session model> <noreply@anthropic.com>` only when Claude materially
  co-authored the committed change.

## Delegation And Routing

Claude Code leads planning and synthesis. Use Codex for substantial implementation, rescue work, and
independent code review when it can access the required evidence. Read the Codex delegation and model
routing references before dispatch or fan-out.

- Reviewer independence is the reason for the Codex review route. Keep the reviewer separate from
  the implementer; resolve current model names and effort levels from the runtime.
- User-invoked commands may be absent from Claude's model-visible catalog. A slash token embedded in
  ordinary prose is not an invocation; the runtime must expand the standalone command before its
  workflow is authorized. If it was not expanded, do not emulate it by reading `SKILL.md` or
  substituting a visible child skill. Verify the runtime source, then name the canonical namespaced
  command for the user to invoke as a standalone command.
- The canonical human path is `/mattpocock-skills:grill-with-docs` →
  `/mattpocock-skills:to-spec` → `/mattpocock-skills:to-tickets` → `/graph-deliver`.
  Skip verified artifacts and never auto-start a user-only stage. `/graph-deliver` launches at most
  one approved delivery. `/graph-dispatch` fully hands it to a resident `/graph-run` worktree; after
  the `dispatched` receipt, the main agent stops supervising that delivery and may accept the next
  explicit topic. Its atomic Graph skills own implementation, review, the final gate, and any authorized
  `/ship`.
- The local `/handoff` updates the primary checkout's root `MEMORY.md` and stops rather than overwrite
  another active checkpoint. Request a portable handoff document for another directory or person.

## Tooling

- In Python projects, use the repository's `uv` environment: `uv run`, `uv add`, and `uv run pytest`.
- Before any Code Review Graph operation, read
  `~/.agents/skills/use-code-review-graph/SKILL.md`. Graph consumers are read-only; only
  `crg-lifecycle` and `crg-safe-refresh` may write graph state.
- After the root agent completes one tracked-file change batch, enqueue one `agent:change-batch`
  event. Subagents do not enqueue or write graph state.
- Run the smallest relevant check early and the full relevant gate before handoff when feasible.
  Report what was validated, what was not run, and residual risk.
