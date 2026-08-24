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

### Current answer, measured 2026-08-24

**The library is reached in roughly one situation in ten where it applies.**
`scripts/build-replay-set.py`: 102 applicable situations across 61 train
sessions, 6 taken — 94% missed. Holdout agrees at 87%. The rate holds between 81%
and 94% across every attribution window tried, so it is not an artefact of a
constant someone chose.

That is the number that answers the claim. Everything else below is how it was
arrived at, including the two wrong answers on the way.

### The same question, answered three times, twice wrongly

| Answer | Method | Why it was wrong |
|---|---|---|
| "0 of 9 skills have ever fired" | one session's recollection, written into a memory file | Looked at one store. 17 of 24 firings were in OpenCode, never read. |
| "8 of 9 have fired; the thesis holds" | counting firings across all stores | Right count, wrong denominator. Firing *at all* was never the question. |
| **"~90% of applicable situations are missed"** | labelled replay set: applicable-from-outcome vs actually-fired | Stands until something falsifies it. |

Each correction made the picture worse, and each came from measuring something
the previous method could not see. `lessons/agent-sessions-live-in-multiple-stores`
predicted the first failure and the tally walked into it anyway.

The counting figures — 24 firings over 77 sessions, 8 of 9 skills — are still
true. They are simply not evidence for the claim, which is what the third method
established.

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
| `explain-and-open-pr` | 5 | 1 | 4 artifact, 1 pushback | **KEEP** — best outcome record |
| `capture-lesson` | 7 | 1 | 2 artifact, 2 none, 1 pushback | **KEEP** |
| `sweep-the-class` | 3 | **0** | no signature | **TUNE** — only ever fires when pointed at |
| `deslop` | 2 | **0** | 1 pushback | **TUNE** — batch only, and pushed back on |
| `design-handbook` | 1 | 0 | no artifact | **THIN** — one firing, nothing produced |
| `tdd` | 0 | 0 | 0 of 3 chances | **TUNE or CUT** — a judgement, not a calculation |
| `grilling`, `agentic-vocabulary`, `handoff` | 4 | 1 | — | **Exempt** — human-invoked by design |

**Corrected 2026-08-24.** The task-routed column first read 5 for
`explain-and-open-pr` and 3 for `capture-lesson`. The human pointed out that in
OpenCode he had usually asked for the workbench at the start of a session, and the
classifier only looked at the message immediately before a firing — so a session
opened with "use agent workbench methods" scored every later firing as routed from
ordinary work. Context is now evaluated across the whole session up to the firing.

Read the column as a **lower bound**: session-level priming over-attributes in the
other direction, since one mention taints every later firing in that session. The
truth for `explain-and-open-pr` is between 1 and 5.

**The finding that survives both corrections:** `sweep-the-class` and `deslop`
have never once been routed from ordinary work. Every firing came from the human
naming the library or approving a list. They are not being reached by their
descriptions; they are being reached by the human remembering they exist. That is
precisely the failure this project exists to detect, and it is invisible in the
raw firing counts — both look healthy at 3 and 2 firings.

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

## The replay set — testing the thesis without waiting for new sessions

`scripts/build-replay-set.py` turns past sessions into labelled examples. Every
session already ran an experiment: it has a prompt, and it has an observable
outcome. If a session ended with a lesson file added, `capture-lesson` was
applicable to it — whether or not it fired.

**Applicability is a different question from artifact**, and separating them is
what let the two skills with no output at all get labels:

- **artifact** (scanner) — did the skill produce its own file? Evidence it worked.
- **applicable** (replay builder) — was this the *kind* of situation the skill
  exists for? `sweep-the-class` never edits, but a session whose commits describe
  a fix is objectively one where "did I fix the instance or the class?" was worth
  asking. `deslop` applies to any generated diff before commit, so a session that
  edited and committed qualifies.

Both labels come from what the session **did**, never from an opinion about it.

### Build (2026-08-24): 83 labelled sessions

| Skill | Applicable | Fired | Missed |
|---|---|---|---|
| `sweep-the-class` | 58 | 2 | **97%** |
| `deslop` | 15 | 0 | **100%** |
| `explain-and-open-pr` | 15 | 2 | 87% |
| `capture-lesson` | 9 | 1 | 89% |
| `tdd` | 3 | 0 | 100% |
| `handoff` | 2 | 1 | 50% |
| **Overall** | **102** | **6** | **94%** |

(train split; holdout: 41 applicable situations, 88% missed — the same picture, so
this is not an artefact of the split)

**Report the rate, never the count.** The corpus size depends on an arbitrary
constant — how long after a session ends its commits still count as its own — and
that constant moves the counts by 4x:

| Window | Labelled | Applicable | Missed | Miss rate |
|---|---|---|---|---|
| 0h | 21 | 58 | 47 | 81% |
| 1h | 37 | 87 | 76 | 87% |
| **2h (default)** | **83** | **143** | **132** | **92%** |
| 6h | 94 | 174 | 162 | 93% |
| 24h | 99 | 185 | 173 | 94% |

The counts quadruple. The rate moves 13 points and never drops below 81%. Any
absolute number in this document is a function of that constant; the rate is the
finding.

**So: the library is missed in roughly nine of every ten situations where it
applies, under every window tried, in both train and holdout.** That is the state
of the thesis. It is not "8 of 9 skills have fired" and never was.

**The `sweep-the-class` row was suspected of inflation, tested, and survived.**
Its label was "a commit subject mentions a fix", broad enough that a typo fix in a
README would count. It was sharpened to require that the fix touched a *source*
file which has at least two siblings of the same kind in its directory — the
precondition for a class to exist elsewhere at all, which is the only situation
the skill claims to serve.

That removed 2 sessions out of 83. Train stayed at 58 applicable, holdout went
22 → 20, and the rate did not move. The row is real: nearly every fix in these
repositories touched source code sitting alongside plausible siblings.

A negative result, reported because it is one — the sharpening was expected to cut
that row down and did not.

### Guards, because this loop can lie to you

1. **Labels come from outcomes, never opinions.**
2. **Fixed 70/30 train/holdout split**, hashed on session id so it cannot drift.
   Tune on train only; a gain that does not reproduce in holdout is overfitting to
   history.
3. **The metric is fixed before tuning:** of the applicable-and-did-not-fire
   examples in holdout, how many would the new description catch. Changing the
   metric after seeing results is how this kind of loop deceives.
4. **Sharper, never broader.** A trigger broad enough to catch every example is
   worthless — it fires on everything else too.
5. **A model must not both rewrite the trigger and judge whether the result
   improved.** That converges on self-agreement. The judgement step needs either
   the objective label or a human.

### The corpus, and what it still cannot do

83 labelled sessions, 22 in holdout — enough to tune against and to check the
result on data that was not tuned on. It grows with real work.

What it still cannot do: judge whether a *rewritten* description would have caught
a missed example. That requires a model, and guard 5 forbids the model that wrote
the description from also scoring it. The material is prepared — every missed
example carries its prompt in the output file — but the judging step needs either
a fresh evaluator or the human.

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

- ~~Rename `pas` / `personal-agent-system` → Agent-Workbench (#3).~~ **Done
  2026-08-23.** The marker is now `workbench`; both scripts still recognise the
  old `pas` markers when stripping, so an adopted project migrates in place on
  the next run instead of gaining a duplicate block.
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

- ~~The 15-entry revisit for AND-matching never happened.~~ **Done 2026-08-24**,
  as `scripts/lesson-audit.py` rather than as a one-off opinion. Findings at 22
  lessons:

  - **4 lessons (18%) were unreachable** — they named values (`diagnostics`,
    `env-vars`, `multi-agent`, `opencode`) that `adopt.sh` could not detect, so
    they could never inline into any project however apt. Nothing reported this;
    adopt.sh simply skipped them silently. Now 0: detection was added for
    `opencode` and `multi-agent`, and `diagnostics`/`env-vars` were dropped from
    the two lessons using them, being topics rather than detectable conditions.
  - **The closed vocabulary was not closed.** Those four values were in use by
    lessons but absent from the template's table. The audit reads the detectable
    set out of `adopt.sh` itself, so this class of drift is now mechanical to
    find.
  - **`postgres` and `webhooks` were declared but undetected** (#19, #35) —
    the same silent failure. Detection added, asserted in both directions.

  **The answer to the revisit itself:** AND-matching still works for
  project-scoped lessons, and is structurally inert for **6 of 22 (27%)** whose
  `applies-to` contains only machine-level values (`windows`, `macos`,
  `opencode`, `multi-agent`). A value describing the machine is true of every
  project on it, so there is no project-level term left to narrow on — those
  lessons inline everywhere. One adopted project now matches 22 of 22.

  That is not an argument against AND. It is an argument that a machine-only
  lesson is a **machine rule wearing a lesson's frontmatter**, and belongs in the
  `AGENTS.md` rules block that `install.sh` loads once per machine. Left as a
  decision rather than actioned, because it moves the boundary between the three
  knowledge kinds and that boundary is the project's core claim.
- **`preflight-public.sh` runs in CI only** (deliberate). CI on a pull request
  blocks the merge, but the branch push is already public — this narrows the
  window, it does not close it.
- **"A session" needs a definition the scanner can apply.** A transcript scan sees
  files and turns; where one session ends is a line someone has to draw before the
  count means anything.
