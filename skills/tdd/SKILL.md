---
name: tdd
description: >
  Use when writing code test-first, or when asked to "use TDD", "write a failing
  test first", "red-green", or add well-tested behaviour. A methodology reference:
  it defines HOW the loop runs and the decisions hidden in "just use TDD"; the
  implementation workflow executes. Triggers on "TDD", "test first", "write the
  test first", "red green refactor".
---

# tdd

Defines the test-first loop and the judgement inside it. This skill decides *how*
to work; the surrounding implementation does the work.

## Is this even a TDD job? (ask first)

TDD fits behaviour with a knowable expected output at a stable seam. It fits
poorly for pure exploration, throwaway spikes, config, or UI look-and-feel. If it
doesn't fit, say so and don't force it.

## The loop

```
choose ONE behaviour
  → agree the test seam (where to observe the system)
  → write ONE failing test
  → confirm it fails for the RIGHT reason (not a typo/import error)
  → write the minimum code to pass
  → confirm green
  → next behaviour
```

## The decisions "use TDD" hides

- **Behaviour, not implementation.** Test observable behaviour at a seam a
  refactor wouldn't break. A test that asserts internals is a refactor tax.
- **One test at a time.** Not a batch. One red, one green, then move.
- **Independently-known expected value.** The assertion's expected value must be
  known without running the code under test — otherwise you're testing that the
  code does what the code does.
- **Right-reason red.** A test that fails because it didn't compile hasn't proven
  anything. See it fail for the reason you intend.
- **Mocks at boundaries only.** Mock true externals (network, clock, payment), not
  the thing under test. Concentrate mocks where untrusted/slow reality enters.

## Guardrails

- **Never write implementation before a failing test** for the behaviour.
- **Never skip the red step** or assert an expected value you can't independently
  justify.
- This skill is methodology, not the whole build: hand execution back to the
  implementation workflow.
