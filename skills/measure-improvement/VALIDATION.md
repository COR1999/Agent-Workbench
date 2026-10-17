# measure-improvement — validation

**Evidence class: one firing, by the session that wrote it. Not independent.** The
skill was distilled from a single real change and then used on that same change's
pull request. That shows the procedure is usable and that it catches things; it does
not show the skill routes from its description in a fresh session, or that another
agent following it produces the same quality. Do not read its presence in the
library as proof of either.

## The firing it was written from

A performance fix to a per-tenant report query in a multi-tenant web application:
the read cost grew with every tenant's data, not just the caller's. The procedure
(real schema, real database role, two data sizes, one script run before and after,
a correctness comparison, a published before/after chart and the raw output in the
pull request) ran end to end. What it caught that a quicker approach would have missed:

| Caught | By which rule |
|---|---|
| A model without row-level security reported 430 ms; the real schema with it took 82 s (200x) | measure as the application's own role, on the real schema |
| Indexes alone did nothing (80.7 s vs 81.6 s); the real fix was a different query shape | measure each change separately; record what did not work |
| The same index helped one code path (no security checks) 40x and the other not at all | measure every path that reads it |
| A client killed mid-run left its query running on the server for 7+ minutes, overlapping later runs | check for interference; cancel on the server; set a statement timeout |
| A migration tool had been pointed at a database the session had not created | check what is behind a port, use a scratch database |
| Three deliberate breakages of the new function were each caught by a different test | prove the test can fail |

## What was executed when the scripts were written

| Script | What ran | Result |
|---|---|---|
| `scripts/before-after-chart.mjs` | dummy data, then the real measured numbers (two charts); the output was opened and read | log scale chosen automatically; ratios shown to two significant figures; method, caveat and raw-output path printed on the image; three layout defects (cut-off footer, "10.0" tick labels, dead space above the chart) found by looking and fixed |
| `scripts/render-png.sh` | headless Chromium from the Playwright cache, with and without ImageMagick trimming | produced the PNGs that were published |

Not run: the scripts on a machine without Chromium (it prints a message and exits 1);
the chart script's error paths beyond a missing required field; any automated test of
the chart output beyond reading it.

## What would count as evidence

- Fired from "prove it's faster" or "show the improvement" with no skill named:
  **routed**, not primed.
- The pull request has a before/after image whose every number appears in the raw
  output attached to it, a correctness check, and a "not measured" line.
- A reviewer who was not the author could reproduce at least one number from the
  attached script.
- The agent did not report a figure from a model or an earlier tool as if it were
  measured on the real thing.

Record each firing here with its outcome. After about ten firings, keep, sharpen or cut.
