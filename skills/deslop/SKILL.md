---
name: deslop
description: >
  YOU HAVE JUST WRITTEN OR GENERATED A BLOCK OF CODE and are about to commit it —
  run this over your own diff first. It strips the noise a model adds: comments
  that restate the code, tutorial-voice asides, commented-out scaffold, lazy
  `any`, inline values the project has a home for — WITHOUT touching legitimate
  engineering. Diff-scoped, never removes information, safety, or intent. Not a
  linter, not a bug finder. The moment is the trigger: your own generated diff,
  before it is committed. Also triggers on "deslop", "clean up this AI code",
  "remove the slop".
---

# deslop

## What this is

A filter for the noise language models add to otherwise-fine code. It operates
**only on the changed lines of an AI-generated or AI-assisted diff**, and it
removes a line only when doing so loses nothing. It is not a code reviewer, not a
refactorer, not a bug finder. When it meets something that isn't slop — a real
error-handling gap, an `any` at a trust boundary — it **hands off and reports;
it does not fix.**

This skill is deliberately narrow because the codebases it runs against are
already clean. Its comments carry provenance and incident history; its defensive
code prevents a real, recurring production bug (a failure that looks like an
empty result). A generic "clean-code" pass would delete exactly those. So the
question this skill asks is not "is this good code" but:

> Would this line exist, in this file, if a careful author familiar with the
> surrounding code had written it?

That is answerable from the file itself, and it does not import an outside
ideology over the local conventions.

## The three gates

A line is removed or rewritten **only if all three gates pass.** If any gate
fails, leave it.

```
G1 — SCOPE        Is it in the diff against the base?
                  Untouched code is out of scope, however bad.

G2 — CONSISTENCY  Is it inconsistent with THIS file's own conventions,
                  inferred from the file plus 2–3 sibling files?
                  The local file beats any global preference, always.

G3 — LOSSLESS     Does removing it lose INFORMATION, SAFETY, or INTENT?
                  If yes → do not remove. Report instead.
```

G3 is the whole adaptation. Expand it every time:

- **INFORMATION** — anything a reader can't recover from the code: where this came
  from, what broke here before, what the obvious alternative costs, why a
  suppression is legitimate. Never remove a comment containing an issue reference,
  a date, a file path, or the words *found*, *incident*, *instead*, *because*,
  *was duplicated*, *deliberately*, *otherwise*.
- **SAFETY** — anything that makes a failure visible or undoes a partial write.
  See the failure-visibility clause below. This user's #1 production bug is a
  swallowed failure; removing error handling here is not cleanup, it is a
  regression.
- **INTENT** — a recorded deliberate choice: a justified suppression, a pinned
  version, a load-bearing generic (`unknown[]`), a null-safe config guard that
  exists so tests run unconfigured, a validation bound.

## The failure-visibility clause

On meeting a `catch`, a swallowed error, or a generic failure return, ask first:
**can the caller distinguish failure from an empty or successful result?**

- **No** → this is not slop, it is the #1 bug class. **Do not remove.** Report it
  and recommend making failure visible.
- **Yes, and the block only adds a `console.error`** → this is catch-log noise.
  Propose replacing it with the local pattern (throw on read paths; a
  discriminated result on write paths). **Replace, never silently delete.**
- **Wraps an external call after a state-changing write** → load-bearing
  compensation. **Never touch.**

## What deslop removes — the pattern catalogue

Ordered by confidence. Each must still clear all three gates.

1. **Patterns this codebase never writes, appearing in the diff** — barrel files,
   TS classes where functions are the norm, arrow-function components in a
   function-declaration file, inline hex where a token file exists, inline
   user-facing strings where a content file exists, inline magic numbers,
   commented-out code, **and lazy `any`** (`x: any`, `as any` to silence the
   compiler). *Highest confidence: inconsistency is definitional.* This is how
   `any` is handled — caught by G2 because these repos have zero of it, not by a
   dedicated rule. The one `any` that survives G2 is `any` at a trust boundary
   (JSON.parse, deserialization), which G3 protects as information about an
   unvalidated input and routes to the human — see `tests/ambiguous.md#2`.
2. **Comments that restate the next line** — `// Add security headers` above
   `headers.set(...)`; `// Create a new workbook` above `new Workbook()`.
3. **Banner / tutorial-voice comments** — `/* APPLICATION CONSTANTS ... prevents
   magic numbers */`.
4. **Commented-out scaffold** — generator leftovers, disabled config blocks.
5. **Catch-log-return-generic** — via the failure-visibility clause, so this is a
   *replacement*, not a deletion.
6. **Aspirational prose** — `// In production, you'd use SendGrid/Mailgun/...`.
7. **Inline strings / colours / numbers** the project has a home for.
8. **Nesting a guard clause would flatten** — rare in these repos.

## What deslop does NOT do

- **No dedicated `any` clause.** There is none in this skill, by design, not
  disabled — deleted. `any` is not treated as a special problem: lazy `any` is
  caught by G2 like any other off-convention pattern (these repos measure zero
  `any` across 34k+ lines), and trust-boundary `any` is protected by G3 and handed
  to the human because its fix is *validation*, not a type edit (see
  `tests/ambiguous.md#2`). The reason the standalone clause is gone is that it
  would only ever fire on the boundary case — the one case where auto-editing is
  wrong.
- No behaviour change, no signature/API change, no renames, no file moves.
- No architectural change, no re-abstraction, no cross-file consolidation.
- Never imposes a style the surrounding files don't already demonstrate.
- **When uncertain, leave it and say so.**

## Procedure

1. Get the diff against the base. Only changed lines are in scope (G1).
2. Read the changed file(s) and 2–3 siblings to learn local conventions (G2).
3. For each candidate line: run G2, then G3 (with the failure-visibility clause).
   Removable only if both pass.
4. Apply removals/rewrites. Behaviour must not change.
5. Run the project's typecheck and tests. Report if they fail.
6. Emit the two-section report.

## Output format

```
Deslopped <n> hunks across <m> files. <one line: what kinds were removed>.
Typecheck and tests pass.

Left alone (flagged, not changed):
- path:line — <what it is> — <why it's not slop / what to do instead>
```

The second section is mandatory and is what makes the skill trustable unattended.
A run that flags two things and changes nothing is a valid, useful run.

## Self-check before reporting done

- `git diff` contains only deletions and comment rewrites — no logic changes.
- No removed line matches the G3 never-remove keyword guard. (Grep the diff for
  the keyword list; if any hit, you removed something you shouldn't have.)
- Typecheck and tests pass, or the failure is reported.

## Validation

Gated on the fixture corpus in `tests/`:

- `should-not-flag.md` (22 real hunks): **100%. A single false positive blocks
  release.** Non-negotiable.
- `should-flag.md` (10 real hunks): ~80% acceptable.
- `ambiguous.md` (4 hunks): must **flag and hand off**, must **not** auto-fix.

Run the corpus before trusting the skill on a real diff.
