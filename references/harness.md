# Harness Diagnostic Reference

Read this when a hook or permission blocks an operation, or before changing `settings.json`, hooks,
or permission rules. The environment is the source of truth; this file does not cache active values.

## Diagnose

1. Read the matching entry in `~/.claude/settings.json`. Record the event, matcher, command, and the
   applicable `deny`, `ask`, or `allow` rule.
2. Read the exact hook or script registered there. Do not infer behavior from its filename, this
   reference, or an old log.
3. Reproduce the smallest safe input when the source alone does not settle the result.
4. Report the deciding rule or source line, the observed decision, and the permitted alternative.

## Stable boundaries

- Settings and registered hook source define current enforcement. `CLAUDE.md` defines desired agent
  behavior but cannot override a runtime denial.
- Repository instructions define schema and migration workflow. The user-level write guard protects
  sensitive files; it does not select one database workflow for every repository.
- Diagnose first. Change settings or hooks only when the user requested that configuration change.
- Preserve fail-closed protection for secrets, force pushes, irreversible work loss, and machine
  reconfiguration. Pair a denial with a safe alternative when one exists.

Diagnosis is complete when the observed decision is tied to the current setting or source line and
the next permitted action is explicit.
