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

**Baseline, measured 2026-08-23** by `scripts/skill-usage-scan.py` across every
local store: **24 skill firings over 77 sessions**, and **8 of the 9 skills have
fired at least once**. Only `tdd` has never fired.

This replaces the previous claim here, that 0 of 9 had ever fired naturally.
That claim came from one session's recollection of one store and was simply
wrong: 17 of the 24 firings are in OpenCode, which the hand-maintained tally had
never looked at. `lessons/agent-sessions-live-in-multiple-stores.md` predicted
exactly this failure, and the tally walked into it anyway — which is the case for
measuring rather than remembering, made at our own expense.

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

### Did it help?

Firing is not helping. Some skills leave their own trace in git, so the scanner
checks whether that trace appeared within a window of the firing:
`capture-lesson` should produce a file under `lessons/`, `explain-and-open-pr` a
commit, `design-handbook` an HTML file, `handoff` a handoff file, `tdd` a test.

Skills that write nothing **by design** — `sweep-the-class` never edits,
`grilling` never builds, `agentic-vocabulary` is a lookup — report
`no-signature`. They are judged by reading, and the tool says so rather than
scoring them zero.

Three limits, stated so the numbers are not over-read:

- **A refusal looks like a failure.** `capture-lesson` is *supposed* to decline
  when the four-part test fails. A firing with no lesson file may be the skill
  working exactly as specified. Only reading the row can tell.
- **Attribution is loose.** Any commit in the window counts; on a solo repo that
  is acceptable, on a shared one it would not be.
### Could it have fired and didn't?

The gap above is now partly closed by inverting the artifact test: a session where
a skill's artifact appeared but the skill never fired is an **opportunity not
taken**. Measured 2026-08-23:

Measured 2026-08-23, after the signatures were sharpened (see below):

| Skill | Fired | Missed | Took |
|---|---|---|---|
| `explain-and-open-pr` | 5 | 10 | 33% of its chances |
| `capture-lesson` | 6 | 5 | 55% |
| `tdd` | 0 | 3 | 0% |
| `handoff` | 1 | 1 | 50% |
| `design-handbook` | 1 | 0 | 100% |

**The sharpening changed the conclusion, which is why it was done before acting.**
The first pass used loose signatures — any commit counted as a chance for
`explain-and-open-pr`, and touching any path containing "test" counted as a chance
for `tdd`. That reported 17 and 13 misses. Requiring an *added* file, and
requiring the session to have actually edited something before a commit counts,
gives 10 and 3. `tdd`'s apparent gap was 77% artefact of the measurement.

Where that leaves each:

- **`explain-and-open-pr`** — strongest by outcome (5 of 5 firings produced a
  commit) and still the largest gap (10 missed). Firing more is justified *here*,
  on evidence, not as a general aim.
- **`tdd`** — 0 of 3. Still a routing failure rather than absence of demand, but
  the case is thin. KEEP-or-CUT on 3 data points is a judgement, not a
  calculation, and should be called as one.
- **`capture-lesson`** at 55% and **`handoff`** at 50% are working acceptably.
  Pushing them higher re-creates the metric hazard above.

Still **upper bounds, not counts**. A commit made by hand inside an agent session
is indistinguishable from one the agent should have opened a PR for.

Still invisible: a miss for `sweep-the-class`, `grilling`, `deslop` or
`agentic-vocabulary`. They leave no trace whether they fire or not, so for them
this method reports nothing rather than zero.

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

## Verdicts from the first classification pass (2026-08-23)

Reading the 24 rows, rather than scoring them, exposed a distinction the counts
hid: **what occasioned the firing**. Three kinds:

- **task** — the human described ordinary work and the model chose the skill. This
  is the only kind that supports the thesis.
- **library-invoked** — the human pointed at the workbench ("use agent workbench
  methods", "report back to agentworkbench with any new lessons"). Unprompted by
  skill *name*, but not autonomous routing.
- **batch** — "do all", accepting a list the model had already proposed.

| Skill | Firings | Task-routed | Outcome | Verdict |
|---|---|---|---|---|
| `explain-and-open-pr` | 5 | **5** | 4 artifact, 1 pushback | **KEEP** — strongest in the library |
| `capture-lesson` | 6 | 3 | 2 artifact, 2 none, 1 pushback | **KEEP** |
| `sweep-the-class` | 3 | **0** | no signature | **TUNE** — only ever fires when pointed at |
| `deslop` | 2 | **0** | 1 pushback | **TUNE** — batch only, and pushed back on |
| `design-handbook` | 1 | 1 | no artifact | **THIN** — one firing, nothing produced |
| `tdd` | 0 | 0 | 0 of 3 chances | **TUNE or CUT** — a judgement, not a calculation |
| `grilling`, `agentic-vocabulary`, `handoff` | 4 | 1 | — | **Exempt** — human-invoked by design |

**The finding that matters:** `sweep-the-class` and `deslop` have never once been
routed from ordinary work. Every firing came from the human naming the library or
approving a list. They are not being reached by the descriptions; they are being
reached by you remembering they exist. That is precisely the failure this project
exists to detect, and it is invisible in the raw firing counts — both look healthy
at 3 and 2 firings.

`explain-and-open-pr` is the counter-example that keeps the thesis alive: five
firings, all five from ordinary work, four produced a commit.

## Where the firings actually happened

Only **3 of 24 firings were inside Agent-Workbench itself**. The other 21 happened
in real project work, across four separate repositories. The library is not just
testing itself:

| Repository | Firings |
|---|---|
| a model-tracking project | 9 |
| a commerce project | 5 |
| a reporting project | 3 |
| an app project | 3 |
| Agent-Workbench (self-referential) | 3 |
| other | 1 |

Task-routed firings of workbench skills **outside** this repo: `explain-and-open-pr`
×4, `capture-lesson` ×2, `design-handbook` ×1. That is the thesis in its narrowest
honest form — the library travelled to other projects and was reached from
ordinary work there.

## The whole dataset came from a frozen copy

`scripts/install.sh` falls back from symlink to copy when the OS refuses a link.
On this machine it had copied, on 2026-08-20, and every skill edit since then
reached no session at all. Both harnesses read the same
`~/.claude/skills` directory — confirmed from OpenCode's own recorded skill paths
— so all 24 firings ran against identical, three-day-old content.

Two consequences, one bad and one good:

- The retune of three descriptions would have measured nothing. It was live only
  after `install.sh` was re-run and verified by grepping the *installed* file for
  a string only present in the source.
- The baseline is unusually clean *because* of the freeze: every firing in it ran
  against the same content, so it is a fair before-picture for the experiment
  below.

Captured as [`copy-fallback-freezes-the-install`](../lessons/copy-fallback-freezes-the-install.md).

## Running experiment: three descriptions retuned (started 2026-08-23)

Hypothesis: `sweep-the-class` and `deslop` never route from ordinary work because
their descriptions lead with *the human's phrasing* ("where else", "remove the
slop") and bury the model-detectable moment. `tdd` never routes because every
trigger it lists is a name for the practice rather than the situation.

Change made: in all three, the detectable moment is now first and in capitals —
"you have just fixed a bug", "you have just written a block of code and are about
to commit", "you are about to create a new test file". Scope is unchanged and no
new verb was added, per the rewrite constraint above: sharper, never broader.

Baseline to beat, at the moment of the change:

| Skill | Firings | Task-routed | Chances taken |
|---|---|---|---|
| `sweep-the-class` | 3 | 0 | not measurable |
| `deslop` | 2 | 0 | not measurable |
| `tdd` | 0 | 0 | 0 of 3 |

The test is the next scan. **Task-routed** is the number that matters — total
firings can rise from library-invoked prompts without meaning anything. If
task-routed is still zero after a fair run of real work, the description is not
the lever and the honest conclusion is that these skills need a rule that fires
them, or need cutting.

## The trial (#12)

1. Rewrite descriptions **only where the measured data shows a problem**. The
   original plan — rewrite all six — was premised on 0 of 9 firing. With 8 of 9
   firing, rewriting a description that demonstrably works risks a regression for
   no gain. `tdd` (zero firings) is the clear candidate; anything else needs a
   reason from the classification pass.
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
