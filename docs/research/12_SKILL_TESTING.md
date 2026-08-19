# 12 — Skill Testing

You said this becomes critical once the system can modify its own skills. Agreed — and that's the reason to build it now, cheaply, rather than later, properly.

---

## Three things that are all called "testing"

They have different costs and different value. Conflating them is why most skill libraries have none.

| Level | Question | Cost | Determinism |
|---|---|---|---|
| **1. Validation** | Is this file well-formed? | Trivial | Fully deterministic |
| **2. Behavioural fixtures** | Does the skill make the right call on a known case? | Moderate | Model in the loop — non-deterministic |
| **3. Outcome evaluation** | Is the codebase better after using it? | High | Requires real work over time |

**[FACT]** Of the four external libraries, only steipete ships a `validate-skills` script. **None of the 158 external skills ships behavioural fixtures.** You would be doing something none of them do.

**[RECOMMENDATION]** Build level 1 now (an afternoon). Build level 2 for `deslop` only, because it's the one skill where a false positive destroys information. Defer level 3 until the loops layer exists — it's the natural output of `record-work` accumulating.

---

## Level 1 — Validation

A script, run in CI on every push.

```
scripts/validate-skills.sh
```

Checks:

1. Every `skills/*/*/SKILL.md` has valid YAML frontmatter
2. `name` exists, is kebab-case, and matches the directory name
3. `name` is **globally unique across all folders** (they flatten into one install directory — see report 11)
4. `description` exists and is 15–60 words
5. The body has the required sections: Purpose, When to use, Procedure, Guardrails, Output
6. `provenance` is one of `original` / `adapted from …` / `inspired by …` / `combined from …`
7. Every skill in a promoted folder appears in `README.md` and in `which-skill`
8. No skill in `in-progress/` or `deprecated/` appears in either
9. The generated registry matches the committed one

**[INFERENCE]** Checks 7 and 8 are the ones that actually prevent decay. They're the mechanical enforcement of mattpocock's *"a router that lies"* rule, and they're the reason his 35-skill library hasn't rotted.

This is also `encode-lessons-in-structure` applied to your own repository, which is a good self-consistency check on the whole design.

---

## Level 2 — Behavioural fixtures

### The shape

```
skills/change/deslop/tests/
  should-flag/
    restating-comments/
      input/middleware.ts
      expected.md
  should-not-flag/
    provenance-comment/
      input/format.ts
      expected.md
  ambiguous/
    catch-that-hides-failure/
      input/reports.ts
      expected.md
```

`expected.md` is short:

```markdown
verdict: leave
reasoning: The comment names issue #250 and states a consequence the code
cannot state. Deleting it removes the only record of why this throws.
must-not-remove:
  - "A genuine query failure must not look like"
```

### Your unfair advantage

**[FACT]** You own a labelled corpus of both classes, drawn from real work:

**Slop, from your own repos:** `invoiceToSheet/middleware.ts` (comments restating headers), `invoiceToSheet` API routes (uniform catch-log-generic, 6+ sites), `fitnessTracker/constants.ts` (banner + tutorial comments), `fitnessTracker/playwright.config.ts` (~15 lines of commented-out scaffold), `invoiceToSheet/src/lib/email.ts` (aspirational prose), `kitchenapp` hooks (`(invoice: any)` at a JSON boundary).

**Not slop, from your own repos:** `hotsauce-mama/src/lib/format.ts` (provenance comment naming three call sites), `.github/workflows/ci.yml` (the `setup-cli` pin incident note), `src/lib/locations.ts` (the #250 consequence comment), `src/components/shared/meta-pixel.tsx` (justified suppression), `src/app/actions/checkout.ts` (compensating try/catch), `src/lib/hooks/use-server-action.ts` (deliberate `unknown[]` generic), `isSupabaseConfigured()` guards.

**[INFERENCE]** This makes your fixture set *evidence-grounded rather than invented*, which is the same standard you hold your own audits to. No general-purpose library can do this — they'd have to make examples up.

### How to run it

There's no way around a model in the loop; the skill's output is judgement, not a value. But you can make it cheap and repeatable:

```bash
scripts/eval-skill.sh deslop
```

For each fixture: copy `input/` to a scratch git repo, commit as base, apply nothing, invoke the skill against the base, capture the diff and summary, then compare against `expected.md` — mechanically for `must-not-remove` strings, and by a second model call for the verdict.

**[RECOMMENDATION]** Make the `must-not-remove` check purely mechanical (grep the resulting file for each string). That gives you a deterministic, zero-cost regression guard on the failure mode that matters most, without needing a judge model at all. The judge only adjudicates the softer verdicts.

### The pass bar

| Set | Bar | Why |
|---|---|---|
| `should-not-flag` | **100%** | A false positive deletes information that can't be recovered and destroys your trust in the skill. Non-negotiable. |
| `should-flag` | ~80% | A miss just means slop survives one round. Cheap. |
| `ambiguous` | Must flag **and** must not auto-fix | Tests the hand-off behaviour, which is where the failure-visibility clause lives |

**[INFERENCE]** The asymmetry is the whole point. Most testing frameworks weight false positives and false negatives equally. For a skill that edits your code, they are not remotely equal.

---

## Level 3 — Outcome evaluation

Deferred, but worth knowing what it looks like so you don't build something that blocks it.

**The question:** did using the skill make things better? For `sweep-the-class`, the honest metric is *"how many issues were filed after 2026-09 that say 'same class as #X'"* — you want that number to go to zero.

**[FACT]** You already generate this data. Issues #192, #250 and #131 are, in effect, negative evaluations of previous fixes, written by you, in your own tracker.

**[RECOMMENDATION]** Don't build measurement infrastructure. Instead make `record-work` capture one field that makes later measurement possible:

```markdown
skills-used: sweep-the-class, verify-for-real
```

That single line, accumulated over months, is the dataset. If a defect class recurs after a sweep ran, you have the evidence. If it recurs where no sweep ran, that's a routing failure, not a skill failure — and you can tell the difference. Without the field you can't.

---

## Testing skills that write to the world

`capture-lesson` writes to the central `lessons/` directory. `audit-to-issues` files GitHub issues. These are outward-facing and irreversible in a way `deslop` isn't.

**[RECOMMENDATION]** Both need a **dry-run mode as the default**: produce the artefact, show it, and require confirmation before writing or filing. This mirrors poteto's `reflect`, which is explicit about it:

> Before applying any Accepted edit, present the synthesizer's full output to the user and wait for explicit approval. Skill changes affect every future agent in the org; do not auto-apply.

Your history supports this. PR #153 was a **revert** of a change that passed every check you had. The lesson you drew was to add a verification layer — but the more general lesson is that confident-and-wrong happens, and the cheap mitigation is a confirmation step on anything hard to undo.

---

## When the system can modify its own skills

You asked for this to be designed, not built. The gate should be:

```
propose  →  fixtures added first  →  fixtures pass on the OLD skill?
                                       ├─ yes → the change is unnecessary, reject
                                       └─ no  → apply change → all fixtures pass?
                                                  ├─ no  → reject
                                                  └─ yes → human approves → merge
```

**[INFERENCE]** The critical constraint is the second one: **a proposed skill change must arrive with a fixture that the current skill fails**. Without it, "improvements" are unfalsifiable and the skill accretes text forever — which is the observed failure mode of every self-editing prompt system. This is the same standard you already apply to your own bug fixes: `e2e/csp-static-cache.spec.ts` exists because the incident happened, and it fails against the pre-fix code.

That single rule is most of the governance your section 37 asks for, and it costs nothing to write down now.

---

## What to build, in order

1. `scripts/validate-skills.sh` + CI — **do this with the first skill**, not after ten
2. `deslop` fixtures, `should-not-flag` set first — the seven real hunks listed above
3. Mechanical `must-not-remove` checking — deterministic, no model needed
4. `skills-used:` field in `record-work` — one line, enables everything later
5. Dry-run defaults on `capture-lesson` and `audit-to-issues`
6. Everything else: later, and only if the library gets big enough to need it
