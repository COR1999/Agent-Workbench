---
name: grilling
description: >
  Use BEFORE implementation to stress-test a plan, spec, idea, or decision and
  surface the assumptions and choices hidden inside it. An interview primitive: it
  interrogates, it does not build. Triggers on "grill this", "poke holes in this
  plan", "what am I assuming", "interview me about this", "stress-test the spec",
  "is this plan solid".
---

# grilling

Exposes the decisions buried in a proposal so they're made explicitly, by a human,
before code is written. Its purpose is not to implement anything.

```
plan / idea / spec
  → grilling
  → explicit decisions
  → shared understanding
  → implementation
```

## Method — model the subject as a design tree

Break the subject into the decisions it contains, and each decision into its
options:

```
Build authentication
├── mechanism: sessions | JWT | OAuth
├── identity provider: internal | third-party
└── session storage: cookie | token | db
```

Walk the tree. At each node, ask the human which branch and **why**, and surface
the branches they hadn't considered. The tree is the map of what's undecided.

## The interview

- Go **breadth-first**: surface the whole space of open decisions before going deep
  on any one, so nothing important stays invisible.
- Ask about the **highest-leverage / hardest-to-reverse** decisions first
  (architecture, data shape, boundaries) — not cosmetics.
- Prefer questions whose answer is a **decision**, not trivia.
- Feed each answer back: "so you've chosen X, which rules out Y — correct?"
- Stop when the tree has no unresolved branch that would change the build.

## Guardrails

- **Human-in-the-loop. Never answer your own questions.** A grilling that invents
  the human's answers has failed — the point is *their* decisions, surfaced.
- **Interrogate, don't implement.** Output is explicit decisions and remaining open
  questions, not code. Hand those to implementation (or to a wayfinding map for a
  large effort).
- Don't grill trivial or already-decided work; match the depth to the risk.
