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
- **Do not trust a document's claim about a mutable precondition — verify it
  against the live source.** A README that says "this repo is private", a config
  that says a flag is off, a comment that says a step ran: each can silently
  drift from reality while still reading as authoritative. Before acting on such
  a precondition, check the thing itself (`gh repo view --json visibility`, the
  actual flag, the actual run), not the document that asserts it. A good
  checklist guarded by a stale precondition still fails.
- **An empty delegated result is a failure of delegation, not a null finding.**
  When a subagent or a delegated task returns no content, treat the delegation
  itself as having failed — investigate or redo the work with direct tools. Never
  carry it forward as "searched, found nothing": that is the same lie as a claimed
  verification.
- **An edit that succeeded is not an edit that matched.** Fuzzy matching can apply
  an `old_string` containing lines that are not present verbatim in the file. Read
  back the touched region after any edit whose match you did not verify —
  especially one that surprised you by succeeding — before building on it.

## Public tree

- **This repository is public and built from private client work. Genericize
  client-identifying material at the moment you write it — never defer to a
  later scrub pass.** Client, brand, and repository names, private issue/PR
  numbers, and real file paths must not enter the tree in raw form; deferring
  means the identifier ships. `scripts/preflight-public.sh` is the boundary
  backstop, not a licence to write dirty and clean up later. When it catches a
  new class of identifier, add its pattern there so the next catch is mechanical.

## Work records

- **Commit bodies carry the experience record.** For anything non-trivial, state:
  how it was found, the root cause, the mechanism chosen and why, and how it was
  verified. Cross-reference related issues by number. Do not reduce a fix to a
  one-line subject — the body is the only durable account of why the code is the
  way it is.
- **Every commit, PR, and issue a model authors must name the model that wrote
  it — provider, model, and version — so contributions can be traced to a
  specific model and compared for reliability over time.** Add a `Model:` trailer
  to commit messages (last line, after the work-record body), and a matching
  `Model:` line at the foot of every PR and issue body. Format:
  `Model: <Provider> <Model> (<model-id>)`, e.g.
  `Model: Anthropic Claude Opus 4.8 (claude-opus-4-8)`. Name the actual model
  doing the work, never a placeholder or a default; a human-authored change
  carries no such line. This is provenance, not attribution theatre — it exists
  so the human can weight trust by which model produced the work.

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
