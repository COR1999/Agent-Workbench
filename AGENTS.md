# Agent rules

Hard rules only. Always true, no conditions, no procedure. Anything that needs an
"if" is a lesson (`lessons/`), not a rule. Anything true in only one repo belongs
in that repo's own `AGENTS.md`.

## Environment

This machine is Windows 11 with Git Bash.

- **Git Bash rewrites POSIX-looking arguments into Windows paths** before handing
  them to native executables. `--title '/admin/customers is slow'` arrives as
  `C:/Program Files/Git/admin/customers is slow`. This has already corrupted a
  real GitHub issue title. Prefix with `MSYS_NO_PATHCONV=1`, or use PowerShell,
  for any command whose arguments contain a leading slash.
- **There is no Docker on this machine.** Anything requiring a container, a local
  Postgres, or `supabase start` runs in CI only. Never report such a step as
  verified locally.

## Verification

- **Never report as verified anything you did not execute.** State what was run,
  what was assumed, and what this environment structurally cannot check. A
  partial verification reported honestly is useful; a claimed one is not.
- **"No issues found" is not an acceptable result on its own.** Report what was
  searched, where, and with what pattern. A null result must be distinguishable
  from having done nothing.

## Work records

- **Commit bodies carry the experience record.** For anything non-trivial, state:
  how it was found, the root cause, the mechanism chosen and why, and how it was
  verified. Cross-reference related issues by number. Do not reduce a fix to a
  one-line subject — the body is the only durable account of why the code is the
  way it is.

## Lessons

- **When something surprises you or costs you time, and the cause was not
  specific to this repository, write a lesson before moving on.** Use
  `templates/lesson.md`. If it can only be described using project-specific
  detail, it is project context — leave it in the project.

## Judgement

- **Encode lessons in structure, not prose, when a structure is available.**
  If you find yourself writing the same instruction twice, ask whether it can be
  a CI check, a lint rule, a pinned version, a regression test, or a type that
  makes the mistake unrepresentable. Pick the strongest rung the situation
  allows. Prose is the fallback, not the default.
- **Concentrate guards at boundaries; trust internals.** Validate where untrusted
  data enters the system — public endpoints, webhooks, deserialisation, env vars,
  URL params. Do not scatter defensive checks through code that only ever
  receives already-validated values.
