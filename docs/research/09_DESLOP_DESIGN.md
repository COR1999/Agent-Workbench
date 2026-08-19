# 09 — Deslop Design

The full specification. Not implemented — this is the design for your review.

---

## Why the reference deslop is dangerous here

The cursor/plugins `deslop` skill has four focus areas. Measured against your codebase:

| Reference focus area | Verdict for your repos |
|---|---|
| "Extra comments that are unnecessary or inconsistent with local style" | **Right instruction, catastrophic if applied naively.** Your comments are ~10% of lines and carry provenance, incident history, consequence reasoning and issue cross-references. A model told to "remove unnecessary comments" will delete `// Pinned rather than "latest" -- resolving "latest" makes this action call GitHub's release API on every run, which hit a rate limit and failed CI outright (2026-07-17)`. That comment is the only record of why that line exists. |
| "Defensive checks or try/catch blocks that are abnormal for trusted code paths" | **Actively harmful as written.** Report 03 Problem 1 is your #1 recurring bug class and it is *caused by* insufficient failure handling, not excessive. You have 31 `try` blocks in 24,856 lines — you are already at the floor. Telling a model to remove defensive code here moves you toward the bug, not away. |
| "Casts to `any` used only to bypass type issues" | **Dead clause.** Zero `any` in 24,856 lines. It will never fire. |
| "Deeply nested code that should be simplified with early returns" | **Valid but rare.** You already write guard clauses. Keep it; expect few hits. |

**[INFERENCE]** Two of four are wrong for you, one is dead, one is fine. Copying it unchanged would produce a skill that is at best inert and at worst deletes your best documentation and your error handling. This is exactly why you asked for archaeology first.

---

## What slop actually looks like in your code

**[FACT]** Measured across ten repos (report 03 Problem 10). Slop is concentrated in fast, unreviewed work — `invoiceToSheet`, `kitchenapp`, `fitnessTracker` — and near-absent in `hotsauce-mama` and `senus-board-report`. Every pattern below is a real hunk from your own repositories.

### S1 — Comments that restate the next line

```ts
// invoiceToSheet/middleware.ts
// Add security headers
// Prevent clickjacking
// Prevent MIME type sniffing
// Enable XSS protection
// Referrer policy
```

Also: `// Basic validation`, `// Validate file type`, `// Process PDF`, `// Save all sample invoices`, `// Load existing invoices on component mount`, `// Update local state`.

### S2 — Banner comments and tutorial voice

```ts
// fitnessTracker/constants.ts
/**
 * APPLICATION CONSTANTS
 * Centralized location for all app configuration values
 * This prevents "magic numbers" scattered throughout the code
 */
```

The third line explains a general software-engineering concept to a reader who is already looking at a constants file. That's an assistant talking to a student, not a developer talking to a future maintainer.

### S3 — Commented-out generator scaffold

```ts
// fitnessTracker/my-app/playwright.config.ts — ~15 lines
// {
//   name: 'Mobile Chrome',
//   use: { ...devices['Pixel 5'] },
// },
// {
//   name: 'Mobile Safari',
//   use: { ...devices['iPhone 12'] },
// },
```

### S4 — Uniform catch-log-return-generic

```ts
// invoiceToSheet — repeated at 6+ routes verbatim in shape
} catch (error) {
  console.error('Export error:', error);
  return NextResponse.json({ success: false, message: 'Failed to export data' }, { status: 500 });
}
```

**This is the highest-value detection in the whole skill**, because it is simultaneously slop *and* the origin of your #1 production bug class. See "the failure-visibility clause" below.

### S5 — Aspirational prose where a decision belongs

```ts
// invoiceToSheet/src/lib/email.ts
// Mock email service for demonstration
// In production, you'd use a service like SendGrid, Mailgun, or AWS SES
```

Speculation about a future that isn't in the codebase, addressed to nobody.

### S6 — Untyped deserialisation

```ts
// kitchenapp — 14 occurrences, one root cause
const migrated = parsed.map((invoice: any) => ({ ... }))
```

Not "lazy `any`" — an unvalidated trust boundary. Flag it as a boundary problem, hand it to `boundary-validation`, don't just delete the annotation.

### S7 — Patterns you never write, appearing in a diff

**[FACT]** Report 04 §13 established that your recent code contains no barrel `index.ts` files, no TypeScript classes, no arrow-function components, no global-state libraries, no inline hex/HSL, no inline user-facing strings, no inline magic numbers, and no commented-out code. **Any of these appearing in a diff is slop by definition for you** — not because they're bad in the abstract, but because they're inconsistent with every file around them. This is the cheapest and most reliable detection in the skill.

---

## What must never be touched

**[FACT]** Real comments from `hotsauce-mama` that a naive deslop would delete:

```ts
/** Inverse of eurCentsToEuroString — was duplicated across edit-price-form.tsx,
    edit-shipping-zone-rate-form.tsx, and admin-shipping-zones.ts before being
    centralized here. */
```
→ **Provenance.** Records why a shared helper exists and what it replaced.

```ts
// A genuine query failure must not look like "no stockists nearby" (#250)
// — this backs the public /find-us page, so a silent failure could read
// to a customer as "not sold anywhere" rather than a real outage.
```
→ **Consequence.** Explains why the non-obvious `throw` is correct.

```yaml
# Pinned rather than "latest" -- resolving "latest" makes this action call
# GitHub's release API on every run, which hit a rate limit and failed CI
# outright (2026-07-17) for a reason completely unrelated to the PR.
```
→ **Incident history.** The only record of why the version is pinned.

```ts
// eslint-disable-next-line @next/next/no-img-element -- Meta's official pixel
// fallback requires a plain <img>, not next/image (no optimization applies to
// a 1x1 tracking pixel).
```
→ **Suppression justification.** Removing it makes the suppression look arbitrary.

**The discriminator, stated once:**

> A comment earns its place if it says something the code cannot say: where this came from, what broke here before, what the obvious alternative costs, or why a suppression is legitimate. A comment that says what the code already says is slop.

That single sentence is more useful to a model than any list of banned phrases.

---

## The skill

### Purpose

Review the changes introduced on the current branch, relative to its base, and remove AI-generated slop — output that is inconsistent with the surrounding code's own conventions. Behaviour-preserving, minimal, local.

### Trigger

- You say "deslop", "clean this up", "review the diff for slop"
- Automatically recommended before opening a PR (a suggestion, not a hook)
- Model-invokable, because the cost of a false positive is bounded by the guardrails below

### Inputs

| Input | Source | Required |
|---|---|---|
| Base ref | Explicit argument, else `main-dev` if it exists, else `main`, else the tracking branch's upstream | Yes |
| The diff | `git diff <base>...HEAD` (three-dot: merge-base, so unrelated base movement isn't reviewed) | Yes |
| Surrounding context | Full contents of each changed file, not just the hunks | Yes |
| Local style profile | `.agent/style.md` or the style section of `AGENTS.md`, if present | Optional |
| Sibling files | 2–3 nearby files of the same kind, for convention inference | Yes |

### Procedure

1. **Resolve and validate the base.** `git rev-parse` it. Empty or unresolvable diff → stop and say so. Do not silently review the working tree.
2. **Read the local conventions before judging anything.** For each changed file, read the whole file and 2–3 siblings. Establish: comment density and kind, error-handling shape, naming, export style, where strings/colours/numbers live. If `.agent/style.md` exists, it overrides inference.
3. **Classify each added hunk** against the S1–S7 catalogue plus the "inconsistent with this file's own conventions" catch-all.
4. **Apply the failure-visibility clause** (below) before proposing any edit to error handling.
5. **Decide per finding: remove, rewrite, or leave.** Default is leave. See guardrails.
6. **Apply only high-confidence edits.** Anything uncertain becomes a note in the summary, not an edit.
7. **Verify behaviour is unchanged** — `npm run typecheck` and `npm run test:ci`, or the project's equivalents. Report if they fail.
8. **Summarise in 1–3 sentences**, plus a short list of what was left alone and why, when that list is non-empty.

### The failure-visibility clause

**This clause is the most important adaptation in the whole skill and has no equivalent in the reference implementation.**

When a `try/catch`, a swallowed error, or a generic failure return is found:

- **Never delete it outright.**
- Ask first: *if this path fails, can the caller or the user tell the difference between failure and an empty/successful result?*
  - **No** → this is not slop, it is Problem 1. Do not remove it. Report it and recommend `failure-visibility-review`.
  - **Yes, and the catch adds nothing but a `console.error`** → it is slop. Propose replacing it with the local pattern (throw on read paths, `ActionResult` on write paths), not with deletion.
- If the `try/catch` wraps an external call that follows a state-changing write, **it is load-bearing** — your `CLAUDE.md` documents exactly this. Never touch it.

### Focus areas

Ordered by expected hit rate in your code:

1. Patterns you never write, appearing in the diff (S7) — highest confidence
2. Comments restating code (S1), banner/tutorial comments (S2)
3. Commented-out code (S3)
4. Uniform catch-log-return-generic (S4) — via the failure-visibility clause
5. Inline strings / colours / magic numbers that belong in `ui-text.ts` / `globals.css` / `constants.ts`
6. Aspirational prose (S5)
7. Untyped deserialisation (S6) — flag and hand off, don't fix
8. Nesting that guard clauses would flatten
9. Duplication introduced within the diff itself (three or more copies) — flag, hand to `extract-duplication`

### Guardrails

**Hard constraints:**

- Only touch lines the diff added or changed. Untouched code is out of scope even if it's worse.
- No behaviour change. If a change could alter runtime behaviour, it isn't deslop.
- No public API changes, no signature changes, no file moves, no renames.
- No architectural change, no re-abstraction, no consolidation across files.
- Never delete a comment that names an issue number, a date, a file path, a prior incident, or a rejected alternative.
- Never delete error handling. Only ever replace it with the local pattern, and only when failure stays visible.
- Never remove a `TODO` that references an issue number. Do flag a `TODO` that references nothing.
- Never impose a style the surrounding files don't already use. The local file always wins over any global preference.
- **When uncertain, leave it and say so.**

**Explicit non-goals:** this is not a refactoring tool, a linter, a code reviewer, or a bug finder. If it starts finding bugs, that's `code-review`'s job and the finding goes in the summary, not the diff.

### Outputs

```
Deslopped 4 hunks across 3 files. Removed 6 comments restating adjacent code,
one commented-out config block, and one inline hex that belongs in globals.css.
Typecheck and tests pass.

Left alone (flagged, not changed):
- src/lib/reports.ts:42 — catch swallows a failed query and returns []. This is
  a silent-failure risk, not slop. Recommend failure-visibility-review.
- src/lib/import.ts:18 — `(row: any)` on a JSON.parse boundary. Recommend
  boundary-validation rather than deleting the annotation.
```

Two sections, always: what changed, and what was deliberately not changed. The second section is what makes the skill trustworthy enough to run unsupervised.

---

## Global deslop + project style profile

You asked whether deslop should be global-plus-profile. **Yes, but the profile should be small and mostly optional.**

**[RECOMMENDATION]** Three tiers, in precedence order:

1. **The local file wins.** Convention is inferred from the file being edited and its siblings. This handles 90% of cases with no configuration, and it's why the same skill works on `hotsauce-mama` (kebab-case, `export function`) and `senus/frontend` (PascalCase components) without either project declaring anything.
2. **The project profile overrides inference**, when present — `.agent/style.md` or a section in `AGENTS.md`. Roughly 15 lines (report 04 §14). It exists to state things inference gets wrong or can't see: "comments about incidents are load-bearing here", "all copy goes to `ui-text.ts`", "never use `next/og` ImageResponse".
3. **The global skill supplies the judgement**, never the style. The S1–S7 catalogue, the earn-its-place discriminator, the failure-visibility clause, the guardrails.

The failure mode to avoid is the profile becoming a second codebase. If `.agent/style.md` exceeds about 30 lines, the excess belongs in `AGENTS.md` as project context, not in a deslop profile.

---

## Failure modes

| Failure mode | Likelihood | Mitigation |
|---|---|---|
| **Deletes a provenance or incident comment** | **High** — this is the primary risk | The earn-its-place discriminator; the never-delete list (issue numbers, dates, paths, incidents, rejected alternatives); fixtures drawn from real `hotsauce-mama` comments |
| **Deletes error handling and creates a silent failure** | **High** | The failure-visibility clause; never-delete-only-replace rule; fixtures from `invoiceToSheet` vs `hotsauce-mama` |
| Scope creep into refactoring | Medium | Diff-only constraint; explicit non-goals; behaviour-preservation rule |
| Imposes an external style (e.g. banning em dashes) | Medium | Local file wins; global supplies judgement not style |
| Fires on an empty or wrong diff | Medium | Base resolution and validation in step 1 |
| Finds nothing and feels useless on clean repos | **High on `hotsauce-mama`** | Expected and correct. Reporting "no slop found" on a clean branch is a pass, not a failure. Say so in the summary. |
| Silently breaks the build | Low | Mandatory typecheck + test run in step 7 |

---

## Validation — how you know it worked

1. `git diff` after the skill runs contains only deletions and comment rewrites, no logic changes
2. `npm run typecheck` and `npm run test:ci` pass
3. No removed line contains an issue reference, a date, a file path, or the words "found", "incident", "instead", "because", "was duplicated"
4. The summary is 1–3 sentences and names a count
5. The "left alone" section exists whenever anything was flagged

Checks 1 and 3 are mechanical and worth writing as a script the skill runs on itself.

---

## Testing strategy

**[RECOMMENDATION]** Your fixtures should come from your own repositories, not from synthetic examples. This is a genuine advantage you have that a general library doesn't: you own a labelled corpus of both classes.

```
skills/change/deslop/tests/
  should-flag/
    restating-comments/          # invoiceToSheet/middleware.ts, verbatim
    banner-tutorial-comments/    # fitnessTracker/constants.ts
    commented-out-scaffold/      # fitnessTracker playwright.config.ts
    catch-log-generic/           # invoiceToSheet API routes
    aspirational-prose/          # invoiceToSheet/src/lib/email.ts
    inline-hex/                  # synthetic — you have no real examples
    barrel-file/                 # synthetic
  should-not-flag/
    provenance-comment/          # src/lib/format.ts euroStringToEurCents
    incident-comment/            # .github/workflows/ci.yml setup-cli pin
    consequence-comment/         # src/lib/locations.ts #250 comment
    justified-suppression/       # meta-pixel.tsx no-img-element
    compensating-try-catch/      # src/app/actions/checkout.ts
    deliberate-unknown/          # useServerAction<TArgs extends unknown[]>
    null-safe-config-guard/      # isSupabaseConfigured()
  ambiguous/
    catch-that-hides-failure/    # should FLAG but not DELETE — hand off
    untyped-json-parse/          # should FLAG but not FIX — hand off
```

Each fixture is a small directory containing the file, a `expected.md` stating the correct verdict (`remove` / `rewrite` / `leave` / `flag-and-hand-off`) and one sentence of reasoning.

**The bar to pass:** 100% on `should-not-flag`. A false positive here is worse than any number of false negatives, because it destroys information that cannot be recovered and it destroys your trust in the skill. False negatives just mean slop survives one more round.

**How to run it:** for each fixture, invoke the skill on a scratch copy and compare the verdict to `expected.md`. This is a judgement evaluation, not a unit test — it needs a model in the loop. Report 12 covers the mechanics.

---

## Worked examples

**Should remove:**
```diff
- // Add security headers
  response.headers.set("X-Frame-Options", "DENY");
- // Prevent MIME type sniffing
  response.headers.set("X-Content-Type-Options", "nosniff");
```
*Reasoning: each comment restates the line beneath it. The header names are self-describing.*

**Should leave:**
```ts
// A genuine query failure must not look like "no stockists nearby" (#250)
if (error) throw new Error(`Failed to load stockists: ${error.message}`);
```
*Reasoning: names an issue, states a consequence the code cannot state, justifies a non-obvious throw.*

**Should flag, not change:**
```ts
} catch (error) {
  console.error('Export error:', error);
  return NextResponse.json({ success: false, message: 'Failed to export data' });
}
```
*Reasoning: matches S4, but deleting it removes the only handling on the path. The correct fix is to make the failure distinguishable, which is `failure-visibility-review`'s job. Report and hand off.*

**Should rewrite, not delete:**
```diff
- const eur = `€${(cents / 100).toFixed(2)}`;
+ const eur = formatEurCents(cents);
```
*Reasoning: `src/lib/format.ts` already owns this and its doc comment records that it was centralised from three call sites. Reintroducing the fourth is inconsistent with the file's own history. Behaviour is identical.*

---

## Future improvements

Deliberately not in v1:

- **Learn from your own corrections.** When you revert one of deslop's edits, that's a labelled negative example. Feeding those back into the fixture set is the natural first use of `capture-lesson` on a skill rather than on code.
- **A mechanical pre-pass.** S3 (commented-out code) and S7 (barrel files, classes, inline hex) are detectable by grep with near-zero false positives. Running that first would cut the model's search space and make the judgement half cheaper and more focused. This is `principle-build-the-lever` applied to the skill itself.
- **Slop-density reporting over time.** If deslop finds nothing on 20 consecutive branches, the skill's job is done for that project and it should say so rather than continuing to run.
- **Bidirectional coupling with `capture-lesson`.** If deslop flags the same pattern three times in one project, that's a signal the project needs a lint rule, not a third manual cleanup.

---

## One-line summary of the adaptation

> The reference deslop tells the model to remove comments and defensive code. For your repositories, comments and error handling are the two things it must protect most carefully — and the real slop is the *uniform, thoughtless* version of both, plus anything inconsistent with conventions your own files already demonstrate.
