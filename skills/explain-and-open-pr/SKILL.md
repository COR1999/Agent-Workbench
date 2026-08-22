---
name: explain-and-open-pr
description: >
  Use to turn finished changes or a found-and-fixed problem into a GitHub PR with
  a plain-English explanation, instead of letting changes pile up uncommitted.
  Isolates the change onto a clean branch (leaving unrelated work untouched),
  writes a work-record commit and a digestible PR body. Triggers on "open a PR",
  "create a pr", "raise a pull request", "PR this", "don't let this stack up",
  "put this up for review".
---

# explain-and-open-pr

Turns a change into a reviewable PR whose description a non-technical reader can
follow, without sweeping in the human's other uncommitted work.

## Procedure

1. **Isolate.** Never PR a mixed working tree. Create a branch off the base
   (`main-dev`/`main`) and bring in **only** the relevant files. When the working
   tree also holds unrelated uncommitted work, use a **git worktree** off the base
   and apply a patch of just those files there — the human's tree stays untouched.
   Confirm those files have no other divergence from the base first.
2. **Commit with a work record.** Body states: how it was found, root cause, the
   mechanism chosen and why, and how it was verified. Not a one-line subject. End
   the message with a **`Model:` trailer** naming the model that authored it —
   `Model: <Provider> <Model> (<model-id>)` (see AGENTS.md "Work records").
3. **PR body leads in plain English.** First section is **"In plain English"**:
   what it fixes, why it matters, what does *not* change — digestible, non-technical.
   Then the technical detail below. Foot the PR body with the same **`Model:`**
   line, so the reviewer can see which model produced the change.
4. **Verify before claiming.** Run the project's typecheck/tests; state what ran,
   what passed, and what the environment structurally couldn't check. Never claim
   a verification you didn't execute.
5. Open the PR against the integration branch; clean up the worktree.

## Guardrails

- **Isolate first — never sweep in unrelated changes.** The worktree keeps the
  human's tree safe.
- **Plain-English section is mandatory** and comes first.
- On Windows/Git Bash, pass `gh` a body file by a real path (its `/tmp` isn't the
  Windows temp); prefix leading-slash args with `MSYS_NO_PATHCONV=1`.

## TODO
Attaching images (design before/after, screenshots) to PRs needs an image-hosting
approach decided (Agent-Workbench capability, not per-project). Leave until a skill
that produces images (design-handbook, #4) needs it.
