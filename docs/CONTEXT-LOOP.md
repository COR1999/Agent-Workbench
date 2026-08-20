# The context loop — long-running work without long-running sessions

An exploration of issue #9. It records what's true, what we can build now, and
what stays deliberately unbuilt. The goal: let a workflow run for as long as it
needs while each individual agent session stays small and focused.

Grounded in Matt Pocock's Ralph writeup
(https://www.aihero.dev/why-the-anthropic-ralph-plugin-sucks, read 2026-08-20)
and in what this harness actually exposes.

## The principle (the part worth keeping)

> Keep the **ephemeral** agent context small; move **durable** state into
> artifacts a fresh session can reload.

Ralph's mechanism (a bash loop that re-invokes the agent with an empty context
each iteration, reconstructing prior work from git + a progress file) is one
expression of it. The loop isn't the point; the ephemeral/durable split is. His
"40% → dumb zone" claim is a useful heuristic, not a measured law — and notably
his own article gives *no* way to measure context usage. We treat 40% as
advisory, never as a hard-coded trigger.

## What we already have

Agent-Workbench didn't start from zero here. The durable layer largely exists:

| Layer | Lifetime | Where it lives | Already built? |
|---|---|---|---|
| **Strategic / durable** | forever | the wayfinding **map** issue, git history, `lessons/`, specs | ✅ yes |
| **Tactical / handoff** | one effort, across sessions | a per-effort handoff artifact | ⬜ the gap |
| **Ephemeral** | one session | the conversation, tool output, reasoning | discarded every reset |

The **map issue is our progress file.** It already answers "what's the goal, what's
decided, what's on the frontier, what's blocked." A fresh session reading the map
+ git + lessons reconstructs the strategic picture without the old conversation.

So the only missing piece is the **tactical** layer: the in-flight detail of the
*current* subtask that's too granular and short-lived for the map — the current
blocker, files mid-edit, checks already run this session, the exact next
micro-step. That's what a **handoff** captures.

## The handoff (the one thing we add)

A handoff is the baton between two sessions working the *same* subtask. It's
written when a session is about to end or reset, and read first by the next.
Distinct from the map: the map is strategic and permanent; a handoff is tactical
and disposable (delete it when the subtask lands). See `skills/handoff/SKILL.md`
for the structure and the write/read procedure.

The loop, adapted to what we have:

```
fresh session
  → read: map (strategic) + handoff if present (tactical) + git state
  → do ONE coherent unit of work
  → write/update the handoff (or, if the unit is done, a map decision + delete handoff)
  → end
```

Each session starts near-empty and does one unit. The *workflow* is the sequence
of sessions; no single context has to hold it all.

## Can we measure context to auto-reset? Honest finding

**Not reliably, from inside the session.** The harness surfaces a context meter to
the human, but the agent does not get a stable programmatic "% used". Proxy
signals exist and are coarse:

- injected token-budget markers (this session shows `<total_tokens>` hints),
- compaction events (the harness summarising when it runs long),
- turn count, cumulative tool-output size, repeated file reads.

None give a trustworthy live percentage. So auto-thresholding from inside the
agent is unreliable, and the article's own silence on measurement is consistent
with that.

**Therefore the reset trigger is a boundary, not a percentage.** Prefer resetting
at a **natural workflow boundary** — a subtask completed, a decision ticket
resolved (recall the wayfinding rule: *one ticket per session*), a spec handed
off. These are events the agent *can* detect precisely. The "40% smart zone" is a
reason to keep units small, not a gauge to poll. If a harness later exposes a real
utilisation signal, it slots in as an *additional* early-warning, not a
replacement for boundary-based resets.

## What we deliberately do NOT build

- **No context-policy runtime / orchestrator.** No engine polling utilisation and
  auto-spawning sessions. That's the "autonomous orchestration" this project has
  parked (Phase 11) and would be premature infrastructure.
- **No adaptive threshold system.** 40% stays advisory prose, not config.
- **No auto model-switching.** Out of scope.

The map remains a clean seam: if any of these earn their place later, they read
and write the same durable artifacts this design already uses.

## Trade-offs and limits (so we don't oversell it)

- **Reload cost.** A fresh session must re-read the map/handoff/git — real tokens
  spent rebuilding context. Worth it only when a unit of work is big enough that
  the reload is cheaper than carrying a degraded context. Tiny tasks: just finish
  them in one session.
- **Handoff quality is the bottleneck.** A vague handoff makes the next session
  slower than continuing would have been. The skill's structure exists to force
  the specifics.
- **Not all work chunks cleanly.** Some threads genuinely need continuous context;
  forcing a reset mid-thought loses more than it saves. Boundary-based resets
  respect this; percentage-based ones wouldn't.
- **Unproven at scale here.** We have not yet run a real multi-session effort
  end-to-end to compare against one long session. That comparison (issue #9 AC) is
  the next evidence to gather.

## Status against issue #9's acceptance criteria

- Measure context utilisation → **investigated**: not reliably self-measurable;
  boundary-based resets instead of %-based. Documented above.
- Configurable threshold → **advisory only**, by design; a runtime knob is deferred.
- Prototype creating a handoff → **done** (`skills/handoff`).
- Resume from a handoff → **done** (same skill, read mode).
- Durable state survives reset → **yes**: map + git + lessons + handoff.
- Compare vs one long session → **not yet**; needs a real multi-session trial.
- 40% default vs adaptive → **neither**: 40% is advisory; reset on boundaries.
- Document trade-offs → **this doc**.
- Make it reusable policy → the **handoff skill + the map convention** are the
  reusable pieces; the runtime engine stays unbuilt.
