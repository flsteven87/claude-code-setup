# Autonomous Loops Reference

Read this before starting unattended or repeated agent work. Inspect the current plugin state and
command help first; an installed but disabled loop is unavailable.

## Admission gate

Use a loop only when the task is mechanical, its success criterion is machine-checkable, each
iteration can leave recoverable state, and a finite bound exists. Keep design, product judgment,
production debugging, and ambiguous work attended.

## Operating contract

1. Verify the selected runtime is enabled and supports both an iteration bound and an observable
   completion condition. Do not start an unbounded loop.
2. Externalize the objective, current item, last verification result, and blockers in a compact state
   file. Git and durable artifacts remain authoritative.
3. Run attended until the same prompt and verifier complete representative work reliably.
4. After three failed attempts on the same item, mark it pending for a human and continue only with
   independent items.
5. Stop at the configured bound. Report completed items, unresolved items, final verification, and
   the single next human decision.

For recurring work that must run while the machine or session is unavailable, use only a currently
supported scheduler whose persistence and authority boundary have been verified.

The loop is complete when it reaches the machine-checkable success condition or the finite bound and
leaves a recoverable state plus an explicit unresolved list.
