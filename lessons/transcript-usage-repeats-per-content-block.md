---
applies-to: [python, multi-agent]
discovered: 2026-10
status: active
---

# Agent transcripts repeat one API response's usage across several events: dedupe before summing

A coding agent's transcript stores a single API response as several events, one per
content block, and each carries the same `usage` block. Streamed responses add a
wrinkle: the earlier events can hold a partial `output_tokens` that grows to its final
value in the last. Summing the usage fields over events counts one response once per
block.

**Cost:** In a real store, 6,970 usage events came from 2,859 distinct responses, so a
naive sum overstated tokens and spend by about 2.4x. It was caught only because the
usage was counted per distinct request id before any design was settled; a total built
on the naive sum would have looked plausible, since nothing about it is internally
inconsistent.

**Instead:** Key on the request id (falling back to the message id), keep the
field-wise maximum of each numeric usage field (the last streamed event equals it), and
count a response once. Then cross-check the computed total against any total the tool
itself records, which here agreed to within 0.4%.

**Strongest rung available:** a test with a fixture that stores one response across
three events with growing partial output, asserting it prices once at the final value
(done, in `tests/spend-scan.sh`).
