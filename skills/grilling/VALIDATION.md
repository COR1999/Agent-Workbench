# grilling — field validation

**Evidence class: field, not corpus.** Measured 2026-08-24 by
`scripts/skill-usage-scan.py` across 78 sessions in every local agent store.

## Firings: 3

| Classification | Count |
|---|---|
| task (routed from ordinary work) | 2 |
| primed-session (workbench named earlier in that session) | 1 |

One firing came from `/grill-me` — an alias, not the skill's own name. That case
is worth recording because it broke the measurement before it informed it: the
first version of the scanner scored it as an *unnamed* firing, since the alias
differs from the skill name, and would have inflated the exact number the trial
depends on. An alias map now catches it.

## This skill is deliberately exempt from the trial

`docs/ROADMAP.md` places `grilling` in the **human-invoked by design** category,
with `agentic-vocabulary` and `handoff`. The reasoning: its trigger is the human's
own uncertainty about a plan, which a model cannot detect from the outside.
Scoring it on unprompted firing would measure reachability, not value.

This follows the precedent in Matt Pocock's skills repository, where the
equivalent entry point carries `disable-model-invocation: true` — the author's
explicit judgement that this kind of interview should not be model-triggered.

## Outcome: no signature, by design

The skill never builds anything. It has no artifact, so the outcome test reports
`no-signature` rather than scoring it zero — a skill that writes nothing by design
cannot be judged by looking for what it wrote.

One firing carries a `pushback?` flag. That is a heuristic on the following
message and is not a confirmed rejection.

## What this does not validate

- **Whether the questions were any good.** The skill's value is entirely in
  question quality, and nothing mechanical can see it.
- **The human-in-the-loop guarantee** — never answering its own questions — is
  locked as an invariant in `tests/skill-invariants.sh`, which checks the
  instruction is present in `SKILL.md`. That is not evidence of compliance.
- **Whether decisions surfaced by a grilling actually held.** The session that
  produced `docs/ROADMAP.md` is the obvious test case and its decisions are
  recorded there, but no follow-up has checked which of them survived contact
  with the work.
