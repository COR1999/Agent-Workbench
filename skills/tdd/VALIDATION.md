# tdd — field validation

**Evidence class: field, not corpus.** Measured 2026-08-24 by
`scripts/skill-usage-scan.py` and `scripts/build-replay-set.py` across 78
sessions in every local agent store.

## It has never fired

| Firings | Applicable (train) | Applicable (holdout) | Taken |
|---|---|---|---|
| **0** | 3 | 1 | **0** |

Zero firings in 78 sessions. Four sessions added a new test file — the situation
the skill exists for — and it fired in none of them.

## Zero firings is not the same as "not needed", and the difference was measured

The first reading of this skill was that it should be CUT: never used in 78
sessions. That reading was wrong, and correcting it required a different
measurement — inverting the artifact test to count opportunities rather than
firings.

The second reading overcorrected. On a loose signature — any touched path
containing "test" — it showed **13** missed chances, which looked damning.
Requiring an *added* test file gives **3**. Roughly 77% of the apparent gap was an
artefact of the measurement, found by sharpening the signature before acting on
it.

So the honest position is the narrow one: **0 of 4 is a routing failure, not
absence of demand — and 4 data points cannot carry a KEEP or CUT decision.** That
is a judgement someone has to make, and `docs/ROADMAP.md` records it as a
judgement rather than dressing it as a calculation.

## What was changed as a result

The description was retuned on 2026-08-23. Every trigger it listed was a *name for
the practice* — "TDD", "test first", "red green refactor" — which a model only
matches if the human already used that vocabulary. It now leads with the
detectable situation: "YOU ARE ABOUT TO CREATE A NEW TEST FILE".

Scope was not broadened and no new trigger verb was added, per the rewrite
constraint in `docs/ROADMAP.md`.

**The losing condition is stated in advance:** if `tdd` is still at zero
task-routed firings after a fair run of real work, the description is not the
lever. It then needs a rule that fires it, or it needs cutting.

## What this does not validate

Everything about the skill's actual content. Nothing here says whether its
red-green loop is well described, whether its guidance is correct, or whether
following it produces better tests. **A skill that never fires cannot be validated
on anything except its reachability**, and that is all this document reports.
