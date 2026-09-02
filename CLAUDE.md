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
- **Harness behavior:** when a hook or permission blocks work, or before editing settings, hooks, or
  skill invocation, read `~/.claude/references/harness.md`.
- **Autonomous loops:** before starting unattended or batch agent work, read
  `~/.claude/references/autonomous-loops.md`.

## Scope And Authorization

- Inspect applicable instructions, source, constraints, and existing patterns before non-trivial
  work.
- For answer, review, diagnosis, or planning requests, inspect and report without changing state.
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

## Product Priority

- **Outcome gate:** before selecting, planning, or expanding change work, name the affected user or
  business operation, current problem, observable outcome, and why it matters now. A direct technical
  request, approved spec, or ticket may supply the outcome without an invented user story.
- **Working behavior is the baseline.** Preserve user-visible behavior outside the accepted outcome;
  this protects behavior, not the implementation behind it, and **Single-path** still governs code
  paths.
- When choosing among candidates, address material security, privacy, data-integrity, reliability,
  and irreversible risk, user-facing defects, and committed features before internal improvement.
  Technical work earns scope only when directly requested or when concrete evidence shows it unlocks
  the outcome, removes repeated operating cost, or reduces a named material risk.
- Deliver the smallest reversible slice with observable value now. Keep speculative refactoring, deep
  optimization, and adjacent cleanup outside the active task. If broader technical work or the scope
  changes, state the evidence and reapply the outcome gate before proceeding.

## Complexity Discipline

- **Evidence gate:** start with the simplest direct or linear shape that satisfies the observable
  outcome and named risks. Reuse repository mechanisms; keep deterministic work in code and contracts,
  and use model judgment for interpretation, routing under ambiguity, synthesis, or recovery.
- Treat each added agent, workflow layer, retry, fallback, memory layer, or abstraction as a
  hypothesis. Before retaining it, name the concrete failure, invariant, or operating cost it
  addresses; show why the simpler baseline is insufficient; and name the smallest check or
  representative evaluation that distinguishes them.
- **State earns its keep** by enforcing named transition invariants that are material to correctness.
  Match its states, persistence, recovery, and observability to those invariants.
- **Identity earns its keep** by providing immutable content identity to a named consumer. Keep a Git
  SHA local to the review, delivery, caching, or resume workflow whose correctness depends on it.
- Scale proof to the blast radius: a focused check can justify a bounded local design; durable or
  production agentic systems require representative evals and runtime evidence. Retain complexity
  only while its evidence holds, and stop at the verified outcome.

## Engineering

- **Single-path:** maintain one current implementation. Add compatibility or fallback behavior only
  for an explicit product or migration requirement, with a defined removal condition.
- **Done means observed.** A deploy, migration, scheduled job, feature toggle, or UI change is complete
  only after its relevant end state has been verified.
- Before finalizing a plan, spec, or ticket batch with material architecture, authorization, data, or
  release risk, read the Codex delegation reference and obtain an independent end-state check.
- For production-data changes: dry-run, report findings, obtain explicit approval, back up, execute,
  and verify. Each transition must be observable before the next begins.
- Create documentation files or start development servers only when the user requests them.
- Verify fast-moving facts online and use exact dates when the user says "latest" or gives a relative
  date.

## Frontend Design Routing

- Use `impeccable` as the sole default owner for frontend design, redesign, and UI/UX refinement.
- Owl is installed but dormant by default. Switch to `owl-design` only when the human explicitly names
  Owl in natural language or invokes `/owl-design`; that selection replaces Impeccable for the task.
- Keep one creative owner per task. A proposed staged workflow or state model must pass the Complexity
  Discipline evidence gate.
- Frontend-related skills retained only through a system or broader bundle exception may provide
  narrow engineering or audit evidence, but never own the design.
- For a clean A/B comparison, start a fresh agent session after switching. If both variants will write
  code, use separate Orca worktrees with one writer each.

## Communication

- Reply in Traditional Chinese when the user writes Chinese. Write code, comments, commits, and
  repository documentation in professional English unless the repository establishes another
  convention. Translate upstream or agent output; do not relay it raw.
- Use short direct sentences, one term per concept, and define non-obvious terms on first use.
  Reuse repository `CONTEXT.md` vocabulary when present. When a repository uses `MEMORY.md`, its
  primary checkout root file is session truth; Claude auto-memory is contextual cache and must be
  verified before use. `Active Workstreams` contains only authorized, owned work with a currently
  executable next step; park every other state under a non-active heading. Keep durable decisions in
  their owning issue, spec, ADR, or source file.
- **Recommendation-first:** lead with the best supported call. Present options only when the user
  must own a genuine value tradeoff.
- **Consequence-first:** a human-facing answer establishes what a material technical fact changes,
  states it with its evidence, and stands alone for a reader who did not watch the work. The active
  output style carries the detailed presentation; this line holds when none is active. An
  unestablished consequence is reportable; an invented one never is.
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
  irreversible migration. When repository instructions require a dedicated worktree, a clean
  task-local worktree based on the resolved default branch satisfies this placement condition; all
  other entry conditions remain.
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
- A slash token in ordinary prose is a request, not an authorization, and the runtime never expands
  it. When it names a model-visible skill, confirm the bounded target in one question, then invoke
  that skill. Several tokens in one instruction run in the order and under the conditions written.
  When the tool layer refuses the skill or the runtime owns the command (`/ship`, plugin commands,
  built-ins), do the already-authorized adjacent work, then name the canonical command for the user
  to run standalone. Never emulate a refused skill from its `SKILL.md` or a child skill. `/artifacts`
  asks for a published Artifact; produce one instead of naming the command.
- Use `/mattpocock-skills:grill-with-docs`, `/mattpocock-skills:to-spec`, and
  `/mattpocock-skills:to-tickets` only when the human requests those discovery or planning
  artifacts. They do not gate a direct implementation request.
- The local `/handoff` updates the primary checkout's root `MEMORY.md` and stops rather than overwrite
  another active checkpoint. Request a portable handoff document for another directory or person.

## Tooling

- In Python projects, use the repository's `uv` environment: `uv run`, `uv add`, and `uv run pytest`.
- When a code question spans many files rather than one — architecture, dependency, impact, ownership,
  cross-file flow, or broad review — answer it through `use-code-review-graph` before reading files.
  That skill owns when the graph wins, the freshness gate, and the call budget. Skip it for one file,
  one symbol, or anything a targeted grep already answers.
- Graph consumers are read-only; only `crg-lifecycle` and `crg-safe-refresh` may write graph state.
- After the root agent completes one tracked-file change batch, enqueue one `agent:change-batch`
  event. Subagents do not enqueue or write graph state.
- Run the smallest relevant check early and the full relevant gate before handoff when feasible.
  Report what was validated, what was not run, and residual risk.
