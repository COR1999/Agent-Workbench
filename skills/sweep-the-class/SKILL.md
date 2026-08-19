---
name: sweep-the-class
description: >
  Use right after making or reviewing a fix, before declaring it done, to check
  whether the same defect exists elsewhere. Answers "did I fix the instance or
  the class?". Produces an inventory of sibling instances and an explicit
  coverage statement. NEVER edits code. Triggers on "where else", "same class
  as", "sweep", "did I get them all", or any fix that could plausibly recur.
---

# sweep-the-class

## What this is

A fix closes one call site. The defect often lives at many. This skill takes a
just-made fix, characterises the *class* of defect behind it, searches for
siblings, and reports what shares the class and what was searched. It is the
answer to a specific, repeated failure: closing an issue that wasn't actually
closed because the fix landed at one site and the class survived at nine.

**It never edits.** The output is an inventory and a coverage statement. Nothing
else. That constraint is not incidental — it is what stops a "sweep" turning into
an unreviewed mass change. Fixing the siblings is a separate, deliberate act the
human takes after reading the inventory.

## The fundamental question

> Did I fix the instance, or did I fix the class?

## When to run

- Immediately after a fix, before declaring it done.
- When you catch yourself thinking "there are probably others."
- When an issue reads like it has siblings ("the X page is slow" — what about the
  other five pages built the same way?).
- Chained: any fix-type or cleanup skill should recommend running this before it
  reports completion.

## Input

- The fix just made — a diff, a commit, or a plain description of what was wrong
  and what changed.
- Optionally the issue that prompted it.

## Procedure

### Step 1 — Characterise the shape. Produce BOTH halves or stop.

A class of defect has two parts, and you need both:

1. **Mechanical signature** — a concrete, *runnable* search. A grep pattern, a
   symbol name, an API call, an import, a call shape. Something that returns a
   file-and-line list when you run it. If you cannot write one, go to Step 1a.
2. **Semantic condition** — what makes a mechanical match a *real* instance
   rather than a lookalike. The rule a human applies to each hit to decide
   same-class vs not.

Write both down explicitly before searching. Example, from a real case:

- Mechanical: files that destructure `{ data, error }` from a Supabase call.
- Semantic: …where `error` is never read before `data` is used, **and** the
  caller cannot otherwise distinguish a failed query from an empty result.

### Step 1a — If there is no mechanical signature, STOP.

Some defects are purely semantic — a subtle ordering bug, a lock-plus-limit
interaction, a race. There is no grep that finds them. **Do not fall back to
reading the whole repository.** That is unbounded, it is where scope explosion
comes from, and it produces low-confidence noise.

Instead, report exactly this and stop:

> This defect's shape is semantic and has no searchable mechanical signature. A
> sweep cannot find its siblings mechanically. A targeted human review of
> [named files / subsystem, if you can scope it] would be needed; I have not
> performed one. Not swept.

An honest stop is a valid, complete outcome. It is better than a confident wrong
answer.

### Step 2 — Declare the search scope before searching.

State where you will look and why, and what you are excluding. Default scope is
the directory of the original defect plus its siblings at the same architectural
layer — not the whole repo by default. Widen only with a stated reason.

### Step 3 — Run the mechanical signature. Collect candidates.

Two traps, both found the hard way in this skill's own validation:

- **Do not scope with a `**` glob pathspec.** `git grep -- 'src/lib/**/*.ts'`
  silently matches *zero* files directly under `src/lib/` — the `**` requires an
  intermediate directory, and it fails without erroring. Scope with a plain
  directory (`-- src/lib`, recursive by default) and confirm your candidate count
  includes top-level files.
- **If one signature doesn't cleanly separate real instances from lookalikes, the
  shape is probably two shapes.** A class like "unbounded read" has more than one
  mechanical form (fetch-all-then-aggregate; fetch-all-then-return). Re-derive per
  the guardrail below — do not paper over it by loosening one pattern until it
  catches both, which also catches everything else.

### Step 4 — Apply the semantic condition to every candidate.

Each candidate gets exactly one verdict, and every verdict is recorded with a
reason:

| Verdict | Meaning |
|---|---|
| **same-class** | Genuinely the same defect. Recommend fix or defer. |
| **similar-not-same** | Matches mechanically, differs semantically. State the distinguishing fact. |
| **false-positive** | Matched the pattern, not actually relevant. State why. |

Recording the exclusions is not busywork — it is what stops the next sweep
re-examining the same candidates, and what makes a null result trustworthy.

## Guardrails

- **Never edits. Ever.** Output is an inventory. This is the primary
  anti-scope-explosion constraint.
- **Never widen the signature until it matches everything.** If the pattern
  stops discriminating, the shape was wrong — say so and re-derive it. A signature
  that matches half the repo is not a signature.
- **Never sweep outside the declared scope silently.** Widening is allowed;
  widening without saying so is not.
- **Systemic escape hatch.** If same-class sites exceed ~20, stop enumerating and
  report: "This is systemic, not a set of instances — it wants a structural fix
  or an audit, not a sweep." That is a different kind of finding and belongs in
  an issue, not an inventory.
- **State what was searched, always** — including what was excluded and why. "No
  siblings found" is only meaningful alongside "searched 42 files under src/lib
  for pattern X." A bare "none found" is indistinguishable from having done
  nothing.

## Output format

```
CLASS:   <one sentence naming the defect class>
PATTERN: <the mechanical signature, concretely — the actual grep/symbol>
         <the semantic condition applied to each hit>
SCOPE:   <where searched> — <N files>. Excluded: <where not, and why>.

FOUND: <N> candidates → <a> same-class, <b> similar-not-same, <c> false-positive.

SAME-CLASS (<a>)
  path:line   <symbol/context>        <fix now | defer, reason>
  ...

SIMILAR, NOT SAME (<b>)
  path:line   <the distinguishing fact>

FALSE POSITIVE (<c>)
  path:line   <why it matched but doesn't count>

COVERAGE: <N> of <N> files in scope searched with pattern <X>.
          Not searched: <what, and why it was out of scope>.
```

## Validation

A sweep is well-formed when:

1. Every listed site has a verdict and a reason.
2. The search is stated concretely enough to be re-run by someone else.
3. The coverage line names what was *not* searched.
4. Zero files were modified.

## Note

This skill earns its place because the alternative has a track record: fixes
declared complete that weren't, because the class outlived the instance. The
cost of running it is a few minutes of reading. The cost of not running it has
been a customer-visible bug.
