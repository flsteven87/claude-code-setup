# Anti-Pattern Examples Codex Catches

These are concrete instances from real audits where Codex push-back exposed gaps that self-review missed. The *shape* generalizes — the specific examples are SRE-flavored because that's where the origin session lived.

The point of this file is to **prime your audit thinking** with the categories of mistakes Codex consistently catches. Reading these before drafting the Codex prompt helps you anticipate weak spots and ask sharper questions.

## Category 1: Misnamed concepts

Calling something X when it isn't really X. Naming drives expectations and review effort downstream.

**Example (origin session)**: "GitOps idempotency" PR title. Codex: "Stop calling this GitOps unless Git is the actual source of deployed truth and a pull-based reconciler applies it." OpenGitOps requires declarative + versioned + pull + continuous reconciliation. CI-driven push deploys are not GitOps even if they're idempotent.

**General shape**: Borrowing prestige from a well-defined term to label a partial implementation. Triggers wrong expectations from reviewers.

**How to catch in audit**: For every named concept in the plan, ask "does this strictly match the term's definition, or am I borrowing the prestige?"

## Category 2: Tool semantic misuse

Using a tool's exit code, return value, or behavior in a way that contradicts its documented semantics.

**Example (origin session)**: `kubectl diff -k` proposed as a "zero-diff CI gate" with exit-0 expectation. Codex: "kubectl diff returns 1 on differences, 0 on none — exit 1 is the normal case for an intended change. As a release gate, this fails on the case you actually want."

**General shape**: Building a check around a tool's exit code without consulting the tool's docs. Plausible-sounding reasoning that survives self-review because it sounds right.

**How to catch in audit**: For every tool's exit code or return value used as a gate, **read the man page or doc**. Don't infer from past usage.

## Category 3: Hardcoded thresholds (theater)

Picking a magic number for an alert threshold without deriving it from system constants.

**Example (origin session)**: `pg_stat_activity_count > 70` for a PG capacity alert. Codex: "Absolute numbers without budget math are theater. Should be derived from `max_connections`, reserved headroom, pool budgets, pod count."

**General shape**: A round number that sounds reasonable but has no math behind it. The threshold drifts away from reality the moment any of the underlying constants changes.

**How to catch in audit**: For every threshold (>, <, ratio), ask "what formula derives this from system constants?" If the answer is "no formula, I picked it because it seemed right", refuse.

## Category 4: Log-text matching alerts

Matching alert rules on free-text log content rather than structured event metadata.

**Example (origin session)**: `logger == "api.core.agents.streaming" AND level == ERROR` proposed as a Sentry rule. Codex: "Log-text alerts rot. Should be backed by stable structured event taxonomy."

**General shape**: Pattern-matching on log strings that any developer can change without understanding the alert depends on them. The rule silently breaks the next time the log line is reworded.

**How to catch in audit**: For every alert rule keyed on log content, ask "what stable structured event would replace this?" Refactor toward emitting tagged events at the source; alert on tag.

## Category 5: Single-window vs multi-window burn rate

Page rules built on a single time window over an SLO error rate.

**Example (origin session)**: 14×/5min single-window burn rate over 99.9%/30d 5xx SLO. Codex: "Google's SRE Workbook does NOT recommend single-window for 99.9%. Standard is multi-window multi-burn-rate: page on (1h+5m at 14.4×) AND (6h+30m at 6×); ticket on (3d+6h at 1×). Plus min-event guard for traffic variance."

**General shape**: Picking the simplest signal because it's easier to reason about, when the literature has documented better-behaved primitives. SRE Workbook ch.5 is the load-bearing reference here.

**How to catch in audit**: For any threshold-based alert proposal, ask "is there a multi-window or burn-rate equivalent that handles noise / reset / low-traffic better?" The Workbook usually has the answer.

## Category 6: Wrong-layer probe

Synthetic or readiness probe targeting a layer that doesn't reflect user-visible behavior.

**Example (origin session)**: `/health/ready` Blackbox probe as the user-path synthetic. Codex: "/health/ready is a routing signal, not a user transaction. Add a real user-path synthetic (POST /chat/* with auth token)."

**General shape**: Probing the side of the system that's easy to probe rather than the side that reflects user experience. Shipping success metric is "probe succeeds" while users still see failures.

**How to catch in audit**: For every probe, ask "what's the smallest user-visible path this exercises?" If the probe doesn't traverse it, it's a routing canary, not a user-experience signal.

## Category 7: Image tags vs digests

Pinning container images by tag (even SHA-tagged) rather than digest.

**Example (origin session)**: Plan said "pin image SHA tag in IaC". Codex: "Even SHA tags are mutable in registries. Only image DIGEST (`@sha256:...`) is immutable. Pinning by tag was always a half-fix."

**General shape**: Confusing apparent immutability (a SHA-shaped tag) with actual immutability (a content-addressable digest). The tag can be retagged in the registry without notice.

**How to catch in audit**: For every image reference in deploy manifests, check it's `image: foo@sha256:...` not `image: foo:sha-abc123`.

## Category 8: Resource-boundary violation

Logic that should live at one layer (resource ownership, validation) leaks into a higher layer (business logic, request handling).

**Example (origin session)**: `PoolLoopMismatchError` raised inside `session.py` (request layer) when the cross-loop invariant belongs to the pool factory itself. Codex: "If session code is now where loop ownership is enforced, that's a smell. Pool factory should own loop identity, pool wrapper rejects cross-loop use, session layer just consumes the contract."

**General shape**: A guard / invariant placed where the violation is *detected*, not where the resource is *owned*. Future refactors that touch the wrong layer will accidentally remove or weaken the guard.

**How to catch in audit**: For every guard / invariant, ask "what resource owns this invariant? Is the guard placed at that resource's boundary, or scattered into consumers?"

## Category 9: Exception-time logging vs metrics

Treating one-time error logs as observability for ongoing system health.

**Example (origin session)**: Plan said "log `pool.get_stats()` when PoolTimeout catches". Codex: "Exception-time logging is not observability. Promote to first-class Prometheus metrics (`chat_pool_acquire_latency_seconds`, `chat_pool_waiters`, `chat_pool_in_use`)."

**General shape**: Designing observability around the moment of failure rather than continuous health signal. You see a snapshot at exception time but can't see the slow degradation that led to it.

**How to catch in audit**: For every "log X when error" proposal, ask "should X be a continuous metric scraped every Ns?"

## Category 10: Sequencing inversion

Putting alert / observability before correctness fixes, so alerts fire on noisy/wrong signals.

**Example (origin session)**: Initial block chain was NEX-570 → NEX-569 (alerts) → NEX-567 (readiness probe + DB error class). Codex: "Don't operationalize a noisy or semantically wrong signal. Fix readiness semantics and DB failure classification first, then wire the pager."

**General shape**: Shipping observability on top of code that doesn't yet emit clean signals. Alerts will fire on false positives / wrong classes, generating noise that erodes the on-call's trust.

**How to catch in audit**: For every "alert / dashboard / monitor" PR, ask "are the signals it consumes already correct, or am I shipping observability on top of broken semantics?"

---

## Using this file

Before drafting the Codex prompt:

1. Read this file
2. For each category, mentally check: "Is the plan I'm about to propose vulnerable to this category?"
3. If yes, **bake the worry into the Codex prompt** as a specific question. Example: "Q3: Is `> 70` derived from any budget math, or is it theater?"

Then Codex's job is to confirm or push back on YOUR worry, not start from zero.

This is more efficient than asking Codex to find every issue from scratch. You're using the categories as a priming index.
