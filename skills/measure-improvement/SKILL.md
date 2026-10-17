---
name: measure-improvement
description: >
  Use BEFORE claiming that a change made something faster, smaller, cheaper or
  more reliable, and whenever a PR says "improves performance" or "fixes a
  scaling problem". Explains how to measure correctly (same harness before and
  after, real code path, real permissions, more than one scale, repeated runs,
  a correctness check beside every speed number, and honest limits), keeps the
  raw output as evidence, and turns the numbers into a before/after image for
  the PR. Triggers on "measure", "benchmark", "prove it's faster", "before and
  after numbers", "performance PR", "did that fix it", "show the improvement".
  Not for visual UI changes (use the mockup skill) and not for one-off timing
  of something nobody will ask you to defend.
---

# measure-improvement

A number is evidence only if someone else could repeat it and get the same
answer. This skill is the procedure for getting a number you can defend, and for
showing it in a PR as a picture plus the raw output behind the picture.

**The rule behind everything: never report a number you did not run.** If you
could not measure something, the PR says "not measured" and why. A PR with an
honest gap is better than one with a confident guess.

## 0. State the claim first

Write one sentence before touching anything: *"Reading one tenant's report
takes X ms at N tenants; after the change it takes Y."* It names the **metric**
(time, rows, bytes, requests, memory), the **operation** (the exact query,
endpoint or page), and the **scale** it matters at. If you cannot write the
sentence, you do not yet know what you are measuring.

## 1. Measure the real thing

- **The real code path.** The actual query text, the actual view, the actual
  migration, not a simplified copy. If you must simplify (no database available),
  say so on the picture. A simplified model is for finding the problem; the real
  schema is for proving the fix.
- **The same permissions as production.** Run as the role the app uses (for
  example `authenticated` with row-level security on), not as a superuser. In the
  session that taught this skill, the same per-tenant report took 430 ms in a
  model without security checks, and 82 seconds on the real schema with them (100
  tenants; 316 seconds at 400). Skipping this would have under-reported the
  problem by 200x, and sent the fix after the wrong cost (indexes, which barely
  moved the real number).
- **Representative data, at more than one size.** One size is a point; two or
  three show the *shape* (does cost follow your data or everyone's?). Pick sizes
  that map to the tiers people care about (for example 100 and 400 tenants).
  Say how the data was made and what it leaves out.
- **Use your own scratch database, and check what is behind a port first.** Before
  running a migration tool or a loader, find out what is listening and whose it is
  (`ss -ltnp`, then connect and look). In the session that taught this skill a
  migration run landed in a database the session had not created. It was empty
  and local, so nothing was lost, but nothing had verified that beforehand. Create
  a database of your own (copy a template), work only there, and drop it at the
  end. Make loader scripts refuse hosted hosts and databases not named like
  scratch ones.
- **Use the environment's own versions.** Record the database or runtime version,
  core count, and whether client and server share a machine. If your tool is a
  different version from production, say what that could change.

## 2. Same harness, before and after

- One script, run **before** the change and **after**, against the **same data**
  on the **same machine**, back to back. Never compare today's run to a number
  from last week or from a different tool.
- Keep the change out of the measuring code. The only difference between the two
  runs is the change under test.
- **Repeat, adaptively.** Up to 3 runs per measurement; report the **minimum**
  (best case, least noise) *and* the **median**, and say which the chart shows. If
  runs are long, stop repeating after about 90 seconds of total time and write the
  number of runs (`n=`) next to the result; a single 5-minute run is acceptable if
  labelled `n=1`. Let the script do this, not you by hand.
- **Discard nothing silently.** If a run is odd, keep it in the raw output and say
  why you distrust it.
- **Check for interference.** Nothing else heavy may run on the machine while you
  measure: no builds, no test suite, no leftover process from an earlier attempt.
  Killing a client does not stop its query on the server: an orphaned
  query kept a CPU core busy for over 7 minutes and overlapped the next
  measurements. Cancel it on the server (`pg_cancel_backend`), re-measure
  anything it overlapped, and set a statement timeout in the script so a
  forgotten run cannot linger.
- **Measure each change separately when you made more than one.** Apply the
  function, measure; add the indexes, measure. Otherwise you cannot say which
  change earned its place. Here that showed the indexes did nothing with security
  on and a 40x gain without it, so they were kept for the path that benefits.
- **Measure every path that reads it.** The same query behaved differently as a
  signed-in user (security checks per row) and as the service role (none). Report
  both; a fix can help one and not the other.
- Time the thing you named. Server-side execution time and end-to-end time answer
  different questions; say which one you recorded.

## 3. A speed number needs a correctness number beside it

A faster wrong answer is a regression. For every measured operation, also record
that **the result is the same**: same rows, same totals, same count, compared by
the script, not by eye. If it is not the same, that is the finding.

## 4. Record failures too

If you tried a fix that did not help, put it in the notes with its number ("adding
the column to the grouping: 2.8 s, no change"). It stops the next person trying
it, and it shows the final fix was chosen against alternatives.

## 5. Prove the test can fail

If the change comes with a test, run the test **with the fix removed** and show
that it fails. A test that cannot fail proves nothing. Say how many tests fail
and the symptom.

## 6. Keep the evidence

Save, outside the chat: the **script**, the **raw output of each run** (before and
after), the **commit** measured, and the **environment** line. Put the raw output
in the PR in a collapsed `<details>` block, and the script where a reviewer can
run it (in the repo if it is small and generally useful, otherwise attached or
linked). Every number in the picture must trace to a line in that output.

## 7. Make the picture

Use the helper scripts in this skill's `scripts/` directory.

1. Write `data.json` from the saved raw output (copy numbers, do not retype from
   memory):

   ```json
   {
     "title": "Per-tenant report read",
     "subtitle": "Real schema, row-level security on, PostgreSQL 17",
     "unit": "ms",
     "groups": [
       { "label": "100 tenants (720k rows)", "before": 3000, "after": 12 },
       { "label": "400 tenants (2.9M rows)", "before": 60000, "after": 13 }
     ],
     "method": "min of up to 3 runs, EXPLAIN ANALYZE execution time, same data before and after",
     "caveat": "one query at a time, no concurrent users; synthetic data",
     "source": "evidence/before-after.txt"
   }
   ```

2. `node ~/.claude/skills/measure-improvement/scripts/before-after-chart.mjs data.json chart.html`
   It chooses a log scale automatically when values differ by more than 50x (a
   linear bar for 12 ms next to 60,000 ms is invisible) and says so on the
   picture. It also prints the same numbers as a table, so colour is never the
   only carrier, and puts the method, the caveat and the raw-output path on the
   image itself.
3. `~/.claude/skills/measure-improvement/scripts/render-png.sh chart.html chart.png`
   (headless Chromium from the Playwright cache; set `CHROME=` if elsewhere, or
   screenshot the HTML with a browser tool).
4. **Look at the PNG.** Check the labels, the scale note and that no number is cut
   off. Do not publish a picture you have not seen.
5. Publish with the `mockup` skill's tooling (`imgup chart.png`), fetch the URL
   back and confirm it loads before claiming it works.

Rules for the picture: same units both bars; "lower is better" stated; the ratio
shown to two significant figures only (three runs do not justify more); no
truncated axis on a linear chart; synthetic or modelled data labelled as such;
no client names, real file paths with private information, or issue numbers in a
public repository.

## 8. Put it in the PR

Use the repository's PR template. Under its **Before and after** section put:

````markdown
![Before and after: <what>](<png url>)

| Measurement | Before | After | Change |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

**Method:** <one line: harness, data, runs, min or median, what was timed>
**Environment:** <database/runtime version, cores, shared machine?>
**Correctness:** <the check that results are identical, and what it covered>

<details><summary>Raw output</summary>

```
<paste the saved raw output>
```
</details>

**Not measured / limits:** <concurrency, production hardware, real data, anything else>
````

Link the issues with "Closes #N" and, for a tracking issue, "Related: #N". If the
PR claims a fix, the numbers above are what justify the word.

## What not to claim

- "N times faster in production": you measured a model or a test database.
- A result at one scale as if it held at others.
- A percentage or ratio with more precision than your runs support.
- That a hosted setting (limits, plan, version) is what you assumed, unless you
  read it from the live source this session.
- Anything about concurrency from single-query timings.

## Worked example (the session that produced this skill)

Claim: reading one tenant's season report costs time in proportion to every
tenant's data. Method: apply the real migrations to a real database, load
synthetic tenants at two sizes (100 and 400), time the real view as the
application's own database role and as the role that bypasses row-level security,
then apply the change and re-time with the same script. Result: 81.6 s to 1.1 s
(100 tenants) and 315.6 s to 1.1 s (400) with security on; 319 ms to 2.2 ms and
980 ms to 2.3 ms without. What the procedure caught: the no-security model
under-reported by 200x (section 1); a plausible fix that did nothing was recorded
(section 4); a killed client left an orphan query on the server that skewed runs
(section 2); the indexes helped one path and not the other (section 2). The
evidence image was built with `scripts/before-after-chart.mjs` from the saved
output files, looked at, and published.
