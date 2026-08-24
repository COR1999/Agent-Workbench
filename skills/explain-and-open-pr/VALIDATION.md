# explain-and-open-pr — field validation

**Evidence class: field, not corpus.** `deslop` and `sweep-the-class` were
validated against fixture sets before release. This skill has something those did
not have at the time — a record of what happened when it actually ran, recovered
from session transcripts by `scripts/skill-usage-scan.py`. Neither class is
stronger in general. Fixtures prove behaviour on cases someone chose; field data
proves behaviour on cases nobody chose, and cannot cover what never occurred.

Measured 2026-08-24 across every local agent store, 78 sessions.

## Did it do its job when it fired? — 5 firings, 4 artifacts

| Outcome | Count | Meaning |
|---|---|---|
| artifact | **4** | a commit existed in the repository within 6h of the firing |
| pushback? | 1 | the next human message matched a correction pattern |

**4 of 5 is the best outcome record in the library.** The one flagged `pushback?`
is a heuristic on the following message, not a confirmed rejection; it is counted
against the skill anyway rather than argued away.

The artifact test is loose in one direction and stated so: any commit in the
window counts, so a commit the human made by hand is indistinguishable from one
this skill produced. On a solo repository that is acceptable. On a shared one it
would not be.

## Was it reached on its own? — between 1 and 5 of 5

| Classification | Count |
|---|---|
| task (routed from ordinary work) | 1 |
| primed-session (the workbench was named earlier in that session) | 4 |

Both numbers are bounds, not counts. `task` is a **lower** bound: it only counts
firings in sessions where the workbench was never mentioned at all. `primed-session`
is an **upper** bound on library involvement, because a single mention taints
every later firing in that session regardless of what actually prompted it. The
truth is somewhere between 1 and 5.

An earlier version of this document would have said 5. That was wrong: the
classifier looked only at the message immediately before the firing, so a session
opened with "use agent workbench methods" scored every later firing as ordinary
routing. The human caught it.

## Was it reached often enough? — no

`scripts/build-replay-set.py` labels a past session from what it produced: a
session that edited files and committed them is one where this skill was
applicable, fired or not.

| Split | Applicable | Fired | Missed |
|---|---|---|---|
| train | 15 | 2 | **87%** |
| holdout | 8 | 3 | 62% |

So: when it runs it works, and it does not run nearly often enough. It is
simultaneously the strongest skill in the library by outcome and one of the
largest gaps by volume. That combination is why "make it fire more" is justified
*here* specifically, on evidence, and is not a general aim — see the metric
hazard in `docs/ROADMAP.md`.

## What this does not validate

- **The plain-English section.** The skill's guarantee is that a non-technical
  reader can follow the PR body. Nothing here measures that; it needs a human to
  read one.
- **The isolation guarantee.** "Never sweeps in unrelated work" is the promise
  most likely to cause harm if broken, and the artifact test cannot see it — a
  commit is a commit whether or not it swept in someone's uncommitted work.
  Unvalidated, and worth a fixture.
- **Behaviour on a shared repository.** Every data point is from a solo operator.
