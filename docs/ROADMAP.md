# Roadmap — what this project is proving, and how

The current decision record. Written 2026-08-23 from a grilling session. This is
the **single store** for these decisions: the map issue (#7) indexes and links
here, it does not restate them (see `docs/WAYFINDING.md` — the map is an index).

A session working in this repo should read this before starting, and update it
when a decision here changes.

## The claim under test

Skills must get picked up **without the human naming them**. If a skill only ever
fires because someone typed its name, the library is a command palette, not a
carried capability — and it has not earned the machinery around it.

Evidence so far: 2 skills validated retrospectively; **0 of 9 fired via natural
request** across a multi-hour real session. That number is the baseline this
roadmap exists to move.

## Portability constraint

This must work in **Claude Code, OpenCode, Cursor / Windsurf / Copilot, and any
tool that reads `AGENTS.md`.**

- Lessons and rules are the portable floor — they are plain markdown in
  `AGENTS.md` and work anywhere.
- Skills work wherever the tool supports them.
- **No mechanism may depend on a Claude-only feature.** This rules out hooks as
  the measurement path.

## Two categories of skill

Following the precedent that some interviews cannot be model-triggered, skills
split in two:

| Category | Skills | In the trial? |
|---|---|---|
| **Model-invocable** | `sweep-the-class`, `deslop`, `capture-lesson`, `explain-and-open-pr`, `tdd`, `design-handbook` | Yes — these must fire on their own |
| **Human-invoked by design** | `grilling`, `agentic-vocabulary`, `handoff` | **Exempt.** Their trigger is the human's own uncertainty, which a model cannot detect. Scoring them on unprompted firing measures reachability, not value. |

## Measurement

- **One script scans the session transcripts** every tool already writes to disk.
  Not a hook (Claude-only), not a counter file the model appends to (self-report,
  and it can only record firings — never the denominator).
- Start from `lessons/agent-sessions-live-in-multiple-stores.md`: enumerate every
  backend's store first. Reading one store and concluding zero is the exact
  failure that lesson records.
- Log **raw**; in a **later pass** classify each firing twice: prompted vs
  unprompted, and kept vs redirected. Both are needed — see the metric hazard below.
- **The denominator is a session.**

## Lesson evidence

A lesson never "fires" — it is inert text pasted into a project's `AGENTS.md`, so
nothing observable happens when it works. The rule in `AGENTS.md` ("name the
lesson when it changes what you do") is what makes lesson usage countable.

Citations come back into this repository. The recurring cost — every citation is
also a sanitization decision — is accepted deliberately.

## The metric hazard, and the guard on it

If the score is "unprompted firings", the winning move for any skill is a
broader trigger — which raises its number while making it fire when it should
not. The metric would reward exactly the behaviour that makes the library
worse. Surfaced by asking whether "audit this repo" should trigger `grilling`:
it should not (an audit examines what exists; grilling interrogates what has
not been decided), and a trigger broad enough to catch it would be a
false positive dressed up as a win.

**The score is fired-and-KEPT, not fired.** The classification pass records,
for every firing, whether the skill was kept or immediately redirected. A
rejected firing subtracts. Broadening a trigger then costs rather than pays.
At 35 sessions the volume is small enough to classify by reading, which is why
this works without the scanner having to guess.

**Rewrite constraint (expires when the rewrite is done):** descriptions may be
made *sharper*, never *broader*. No new trigger verb enters a description
unless a real session was missed because it was absent.

## The trial (#12)

1. Rewrite the descriptions of the **six model-invocable** skills. Leave the three
   human-invoked ones alone.
2. Then count from zero.
3. Judge at **35 sessions**.
4. Rank the six by **kept** unprompted firings and **cut the bottom third**.

The trade accepted: rewriting six descriptions at once gives no per-change
attribution. The question being answered is "does anything route at all", against
a known 0/9 baseline — not "which wording worked".

## Scope

**Now**

- Rename `pas` / `personal-agent-system` → Agent-Workbench (#3). It gets harder
  with every project adopted; today is the cheapest it will ever be.
- Skill evolution (#40) promoted from future to live — it *is* the rewrite
  experiment.

**Closed as won't-build-yet** (reopenable, nothing lost)

- Dreaming (#41), model/task routing (#42). Both were "future" with no build
  trigger; an issue with no trigger is a wish, not a plan.

**Not built until the trial resolves.** If skills do not route themselves, every
layer built on top of them is a castle on sand.

## Audience

Open source, **fork-friendly only**. MIT and a clear README. No plugin packaging,
no cross-platform test matrix, no support burden. Others may take it and improve
it; they are owed nothing.

## Known open questions

- **The 15-entry revisit for AND-matching never happened.** The ledger is at 21
  lessons. The rule that a lesson applies only when *every* `applies-to` value is
  detected has not been re-tested at this size.
- **`preflight-public.sh` runs in CI only** (deliberate). CI on a pull request
  blocks the merge, but the branch push is already public — this narrows the
  window, it does not close it.
- **"A session" needs a definition the scanner can apply.** A transcript scan sees
  files and turns; where one session ends is a line someone has to draw before the
  count means anything.
