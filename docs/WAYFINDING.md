# Wayfinding — how Agent-Workbench survives across sessions

A design note, not machinery. It records what we take from Matt Pocock's
**Wayfinder** skill, what we leave behind, and the lightweight model
Agent-Workbench uses so a chunk of work larger than one agent session doesn't lose
its place when the session ends.

Source studied: `mattpocock/skills` → `skills/engineering/wayfinder/SKILL.md`
(read 2026-08-20, cloned read-only into the gitignored `.research/`).

## The problem it solves

An AI session has a context limit. A real effort — "add a wayfinding layer",
"redesign the storefront", "make the workbench open-source" — spans many
sessions. Without durable external state, each new session re-derives what's
done, what's left, and why, from the human's memory. That's the tax this exists
to remove.

The five questions a resuming session must answer *without* the human
re-explaining everything:

1. What was I doing?
2. What is complete?
3. What remains?
4. What is blocked?
5. What was the last decision, and what's the next smallest useful action?

## What Wayfinder is

Wayfinder charts a big, foggy effort as a **map** (one issue on the tracker,
labelled `wayfinder:map`) whose **tickets** (child issues) are each a single
*decision*, sized to one session. Core ideas:

- **Plan, don't do.** Tickets resolve decisions, not build slices. The map is
  done when the way is clear and nothing's left to decide.
- **Map = index, not store.** Each decision lives in exactly one place (its
  ticket); the map gists and links, never restates.
- **Fog of war.** Only ticket what you can phrase *sharply now*. The rest sits in
  "Not yet specified" and graduates into tickets as the frontier advances.
- **Frontier.** The open, unblocked, unclaimed tickets — the edge of the known.
  One ticket per session (research excepted).
- **Refer by name.** Use issue titles in narration, never bare `#42`.

## What we adopt

| From Wayfinder | Why it fits Agent-Workbench |
|---|---|
| **The map issue** (Destination · Decisions-so-far · Not-yet-specified · Out-of-scope) | This *is* the missing cross-session state. Answers the five questions directly. |
| **Decision tickets** as child issues, one decision each | Sized to a session; the unit of durable progress. |
| **Fog-of-war discipline** | Matches our "don't build ahead of evidence" ethos exactly. |
| **Frontier / one-ticket-per-session** | The context-limit resilience the whole system is for. |
| **Refer by name** | Free, and makes narration legible. |

## What we modify

- **Plain GitHub issues + a tiny label set**, not a tracker-abstraction layer.
  GitHub has no strong native issue dependencies, so "blocked by" is a body line
  or a task-list checkbox, not a native edge.
- **No required sub-skills.** Wayfinder leans on `grilling`, `domain-modeling`,
  `prototype`, `research` sub-skills invoked via a Skill tool. We don't need them
  to start: a human and an agent talking, plus our lessons ledger for evidence,
  is enough. Add structure only if the plain version proves too loose.
- **We also *do*, not only plan.** Wayfinder is planning-by-default and hands off
  at the spec. Our back half already exists (below), so our map can carry through
  to implementation for small efforts, holding the plan/do line only for the
  genuinely large, foggy ones.

## What we reject

Everything that's Matt's *distribution* system, not the idea: the Claude plugin
packaging, `marketplace.json`, the `docs/` mirror tree, the bucket taxonomy
(`engineering/productivity/misc/…`), the multi-subagent orchestration, the
no-em-dash house rule. Copying any of it would betray our minimalism. We are
*inspired by* Wayfinder, not forking the skills system.

## What was redundant / already ours

- **Lessons ≈ recorded decisions.** A decision made while resolving a ticket, if
  portable, becomes a `capture-lesson` entry. The ledger is the evidence store
  future tickets consult.
- **GitHub-as-memory** was already the intent; Wayfinder gives it a shape.

## The Agent-Workbench model

Wayfinder covers the front half (fog → decisions → spec). Our skills already
cover the back half. Joined by the lessons ledger, the whole loop is:

```
FOGGY IDEA
  → MAP issue            destination, decisions-so-far, fog, out-of-scope
    → DECISION TICKETS    one open question per child issue, one per session
      → resolve with EVIDENCE + LESSONS       (the ledger feeds this)
      → record the DECISION back on the map
  → way clear → SPECIFICATION
    → IMPLEMENTATION       guarded by sweep-the-class + deslop
      → VALIDATION         skill gates
        → CAPTURE-LESSON   → back into the ledger, informing future maps
```

The loop closes: lessons learned while building inform the decisions of the next
effort. Nothing here is new machinery — it's a *convention* over GitHub issues
plus the skills we already have.

## The issue convention (minimal)

- **`wayfinder:map`** — the one map issue for an effort. Body: Destination /
  Decisions so far / Not yet specified / Out of scope.
- **`decision`** — a decision ticket (an open question whose resolution is a
  choice). Body: the question, sized to one session.
- **`research`** — a ticket resolved by reading/investigation (can run in
  parallel; the one type that may resolve more than one per session).
- Reuse GitHub's stock **`bug`**, **`enhancement`**, **`documentation`**,
  **`question`** for everything else. No bespoke taxonomy until evidence demands
  one.

A ticket is **blocked** if its body says `Blocked by #N` (or an unchecked
task-list item); the **frontier** is open issues with no unresolved blocker. Keep
it that simple until it hurts.

## What this deliberately does NOT do

No orchestrator, no model-switching, no dreaming loop, no autonomous ticket
resolution. The map is written and read by whoever's driving — human or agent —
and a session still resolves at most one decision. This note preserves the
*possibility* of more (a map is a clean seam for future automation) without
building any of it now.
