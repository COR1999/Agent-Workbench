---
name: handoff
description: >
  Use to pass in-flight work between sessions when context is getting long, a
  session is ending, or a subtask boundary is reached — and to resume from a
  handoff at the start of a fresh session. Writes/reads a short tactical handoff
  (goal, done, remaining, blocker, files, next action) so a near-empty session
  can continue without carrying the old conversation. Triggers on "hand off",
  "wrap up this session", "running low on context", "resume where I left off",
  "continue the work", "pick this back up".
---

# handoff

Passes the baton between two sessions working the **same effort**, so no single
context has to hold the whole thing. It carries *tactical, in-flight* state only
— the strategic picture lives in the wayfinding map and git (see
`docs/CONTEXT-LOOP.md`). A handoff is disposable: delete it when the subtask lands.

Two modes. The trigger tells you which.

## WRITE — before a session ends or resets

Reset at a **boundary** (subtask done, decision resolved, spec handed off), not at
a guessed context percentage — boundaries are detectable, percentages aren't. Keep
each session to one coherent unit.

Write the handoff to **the effort's ticket as a comment** if it has one (keeps it
with the durable issue-memory); otherwise to `HANDOFF.md` at the repo root. Use
exactly this shape — every field earns its place, and **Next action is the one
that matters most**:

```markdown
## Handoff — <effort name> — <date>

**Goal:** <what this effort/subtask is trying to accomplish, one or two lines>

**Done:** <what's complete, with evidence — commit hashes, passing checks>

**Remaining:** <what's left, shortest-first>

**Last decision:** <the most recent choice made and why, or "none this session">

**Blockers / errors:** <current failures, or "none">

**Files in flight:** <paths being edited, and their state>

**Checks run:** <typecheck/tests/etc. run this session and their result>

**Next action:** <the single smallest useful next step — concrete enough to start
cold: a file:line, an exact command, a named function. If you can't state it
concretely, you haven't finished thinking; do that before ending.>

**Pointers:** map issue, branch/commit, relevant lessons.
```

Then end. Don't keep working past the handoff — that's the degraded context the
reset exists to avoid.

## READ — at the start of a fresh session

1. Read the handoff (the ticket comment, or `HANDOFF.md`).
2. Read the **map** for the strategic picture, and inspect **git state** (status,
   recent log) to confirm reality matches the handoff — trust the repo over the
   note if they disagree, and say so.
3. Do the **Next action**, then the rest of Remaining, one unit at a time.
4. When the subtask lands: record any durable decision on the map/ticket, capture
   any portable lesson (`capture-lesson`), and **delete the handoff** (it's spent).

## Guardrails

- **Tactical only.** Anything durable (a decision, a portable lesson) goes to the
  map or `lessons/`, not the handoff. The handoff dies with the subtask.
- **Concrete Next action or it failed.** A vague handoff is slower than not
  resetting at all.
- **Reset on boundaries, not percentages.** The agent can't reliably self-measure
  context; a completed unit is a signal it can.
- **Don't let handoffs accumulate.** One live handoff per effort; delete on
  completion. A pile of stale handoffs is noise, not memory.
