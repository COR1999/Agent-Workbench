# capture-lesson — field validation

**Evidence class: field, not corpus.** Recovered from session transcripts by
`scripts/skill-usage-scan.py`, measured 2026-08-24 across 78 sessions in every
local agent store.

## Did it do its job when it fired? — 7 firings, and the ambiguity matters

| Outcome | Count | Meaning |
|---|---|---|
| artifact | 3 | a file was added under `lessons/` within 6h |
| no-artifact | 2 | no lesson file appeared |
| repo-unavailable | 1 | the repository is no longer on disk; unmeasurable |
| pushback? | 1 | the next human message matched a correction pattern |

**The two `no-artifact` rows are not necessarily failures, and this is the single
most important caveat in this document.** The skill's stated guarantee is that it
*refuses* to write a lesson failing the four-part test. A firing that produces no
file may be the skill working exactly as specified — declining, correctly.

The artifact test cannot tell a refusal from a failure. Only reading the two
sessions can, and that has not been done. Until it is, "3 of 7 produced a lesson"
should not be read as "4 of 7 failed".

This is a limit of the measurement, not a hedge: any skill whose correct behaviour
is sometimes to do nothing is invisible to an output-based test.

## Was it reached on its own? — between 1 and 7 of 7

| Classification | Count |
|---|---|
| task (routed from ordinary work) | 1 |
| primed-session (the workbench was named earlier in that session) | 6 |

Bounds, not counts — `task` is a lower bound and `primed-session` an upper bound
on library involvement, because one mention of the workbench taints every later
firing in that session. See `docs/ROADMAP.md`.

Worth noting against the low end: the prompts that occasioned firings include
"why stop", "can u finnish this" and "Do all". None names a skill.

## Was it reached often enough? — better than most, still not often

A session that added a file under `lessons/` is one where this skill was
applicable, fired or not (`scripts/build-replay-set.py`).

| Split | Applicable | Fired | Missed |
|---|---|---|---|
| train | 9 | 1 | 89% |
| holdout | 3 | 1 | 67% |

Against the whole library's 94% train miss rate this is mid-pack, and by the
scanner's own opportunity measure it takes 58% of its chances — the second-best
figure recorded. Both are true; they count slightly different things (sessions
versus firings), which is why both are shown.

## What this does not validate

- **The four-part test itself.** Whether the test correctly separates a lesson
  from a preference is the skill's core judgement, and nothing here measures it.
  It would need a fixture set of candidate lessons with known verdicts — the
  approach `deslop` used, and the obvious next piece of work.
- **Lesson quality.** The artifact test asks only whether a file appeared. A
  worthless lesson and a good one are identical to it.
- **The refusal path**, as above — unmeasured, and structurally unmeasurable this
  way.
