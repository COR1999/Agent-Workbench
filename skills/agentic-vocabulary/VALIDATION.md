# agentic-vocabulary — field validation

**Evidence class: field, not corpus.** Measured 2026-08-24 by
`scripts/skill-usage-scan.py` across 78 sessions in every local agent store.

## Firings: 1

Classified `primed-session` — the workbench had been named earlier in that
session — so there is no recorded instance of it being reached from ordinary work.
There is also no recorded instance of it being reached and rejected.

Outcome: `no-signature`. It is a lookup; it writes nothing, so the artifact test
reports that rather than scoring it zero.

## Exempt from the trial, and the most at risk anyway

`docs/ROADMAP.md` places this in the **human-invoked by design** category. Its
trigger is a specific and unobservable event: the model encountering a term whose
meaning it is uncertain about. A model that *thinks* it knows what "skill" or
"harness" means will not look it up, and nothing external can tell the difference
between correct confidence and misplaced confidence.

That makes it structurally the hardest skill in the library to validate, and it is
already flagged as the most at-risk entry in the KEEP/TUNE/CUT trial (#12).

## The honest position

A reference work is used when someone is unsure, and being unsure is private. One
firing in 78 sessions is consistent with:

- the skill being unnecessary because the terms are already understood,
- the skill being necessary and never reached because uncertainty is not
  self-detected,
- the terms rarely coming up.

**No measurement available here distinguishes these, and none is likely to.** If
this skill is ever cut, it should be cut on the judgement that a glossary does not
earn a slot in the library — not on a firing count that was never going to be
meaningful.

## What this does not validate

Whether any definition in it is correct or useful. That needs a reader, not a
counter.
