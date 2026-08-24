# handoff — field validation

**Evidence class: field, not corpus.** Measured 2026-08-24 by
`scripts/skill-usage-scan.py` across 78 sessions in every local agent store.

## The honest headline: one data point

| Firings | Artifact | Applicable (train) | Missed |
|---|---|---|---|
| 1 | 1 | 2 | 1 |

The single firing produced a handoff file within the window, and of the two
sessions where a handoff artifact appeared, one had the skill fire. Both figures
are real and neither is evidence of anything. **A 100% success rate on one
observation and a 50% take rate on two is not a measurement; it is an anecdote
with a percentage sign attached.**

It is recorded here rather than left blank because "we have one data point" and
"we have no idea" are different states, and the difference matters when deciding
whether to cut a skill.

## Why so few opportunities

The trigger is a context boundary — a session ending, context running long, a
subtask finishing. Two things follow:

- The situation genuinely is rarer than "you fixed a bug" or "you wrote code".
  A low count is expected and is not by itself evidence of a routing failure.
- The one firing was classified `primed-session`: the workbench had been named
  earlier in that session. So there is no evidence yet of autonomous routing, and
  no evidence against it either.

`docs/ROADMAP.md` places `handoff` in the **human-invoked by design** category,
exempt from the KEEP/TUNE/CUT ranking, on the grounds that its real trigger is the
human's judgement that a session should end. This data neither supports nor
contradicts that; it is consistent with it.

## What this does not validate

- **Whether a handoff is any good.** The artifact test asks whether a file
  appeared. Whether the next session could actually resume from it — the skill's
  entire purpose — is unmeasured. The skill's own documentation names this as the
  bottleneck: "a vague handoff makes the next session slower than continuing would
  have been."
- **The resume path.** Only the write path has ever been observed. Reading a
  handoff into a fresh session has no recorded instance at all.
- **The comparison the design rests on** — multi-session work versus one long
  session — remains unrun. It is listed as outstanding in `docs/CONTEXT-LOOP.md`
  and this changes nothing about that.
