# design-handbook — field validation

**Evidence class: field, not corpus.** Measured 2026-08-24 by
`scripts/skill-usage-scan.py` across 78 sessions in every local agent store.

## One firing, and it produced nothing

| Firings | Artifact | Applicable (train) | Missed |
|---|---|---|---|
| 1 | **0** | 0 | 0 |

The skill fired once. No HTML file appeared in the repository within the window.
The occasioning prompt was an image attachment with a design request — squarely
the situation the skill exists for.

`docs/ROADMAP.md` classes this as **THIN**: one firing, nothing produced.

## Three readings, and the data cannot separate them

1. **The skill ran and the human abandoned the direction.** Producing nothing is
   then correct — the skill's whole point is that a direction gets approved
   *before* production code changes.
2. **The handbook was produced somewhere untracked.** The artifact test only sees
   files committed to the repository within the window. An HTML file written to a
   scratch directory, or produced and discarded, is invisible to it.
3. **The skill failed to produce its output.**

Nothing in the transcript record distinguishes these. Reading that one session
would; it has not been done.

The `missed=0` row is equally weak: it says no session produced an HTML file
without the skill firing, which on a codebase that rarely produces standalone HTML
is close to no information at all.

## What this does not validate

- **The core guarantee** — no production code changes before the human approves a
  direction — has never been observed being kept or broken.
- **The ≤3 options, one recommended** constraint is locked by
  `tests/skill-invariants.sh`, which checks the *instruction* is present. That is
  not evidence the skill obeys it.
- **Output quality.** Entirely unmeasured, and probably not measurable this way:
  whether a design handbook is any good is a human judgement, which is precisely
  why the skill hands one over instead of deciding.

One firing is an anecdote. This document exists to say that plainly rather than to
leave the file absent and let the gap look like an oversight.
