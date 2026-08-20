---
name: capture-lesson
description: >
  Use immediately after something surprises you or costs you time, while the
  context is fresh. Prompts for what happened, applies the four-part test,
  drafts a lesson against the template, and writes it to lessons/. Triggers on
  "that's a lesson", "capture this", "I should remember this", or at the end of
  a fix that taught you something portable.
---

# capture-lesson

## What this is

Lessons evaporate. The thing you just learned, the trap you just hit, the
workaround you just found — in three days you will not remember the detail that
made it a lesson rather than a fix. This skill captures it while the context is
fresh, applies the four-part test to keep the ledger honest, and writes the file
so you don't have to.

## When to run

- Immediately after something surprises you or costs you time.
- At the end of a fix that taught you something *portable* (not project-specific).
- When you catch yourself thinking "I should remember this."
- Chained: `sweep-the-class` and `deslop` should suggest running this when they
  surface a new class of defect or a new slop pattern.

## Procedure

### Step 1 — Gather the raw material

Ask (or infer from the conversation):

1. **What happened?** The surprise, the failure, the cost.
2. **What was the cause?** The technical mechanism, not the symptom.
3. **What should be done instead?** The action a future agent takes differently.
4. **What stack or condition makes this true?** The `applies-to` values.

If any of these are unclear, ask once. Do not guess — a vague lesson is worse
than no lesson.

### Step 2 — Apply the four-part test

All four must hold. **Stop at the first failure.** Do not write a lesson that
fails the test.

1. **Did it cost something real?** Time, a bug, an outage, a revert, a re-filed
   issue. → If no: it is a preference. **Stop.**
2. **Would it be true in a different repository, given the same condition?**
   → If no: it is project context. **Stop.** Tell the human to add it to the
   project's own `AGENTS.md` instead.
3. **Is it non-obvious?** Would someone hit this and not find the answer within
   30 seconds from the code, the docs, or the error message?
   → If no: it is documentation. **Stop.**
4. **Does it change what an agent does, not just what it knows?** State the next
   line of code someone writes differently because of it. If you cannot, it
   fails.
   → If no: it is a fact. **Stop.**

Test 4 is the one that fails most often and matters most.

### Step 3 — Check for duplicates and near-matches

Grep `lessons/*.md` for the core concept. If a lesson already covers this:
- Same thing → report "already captured in `<slug>`" and **stop**.
- Related but distinct → note the relationship in the new lesson's body.

### Step 4 — Derive the slug and filename

- Slug: kebab-case, imperative or noun-phrase, ≤40 chars. Examples:
  `check-the-error-not-just-the-data`, `server-action-is-a-public-endpoint`.
- Filename: `lessons/<slug>.md`.

Check that the filename doesn't already exist.

### Step 5 — Draft the lesson

Use exactly this structure (matches `templates/lesson.md`):

```markdown
---
applies-to: [<values from the closed vocabulary>]
discovered: <YYYY-MM>
status: active
---

# <One-line claim, imperative or fact>

<Two to four sentences. What is true and why it bites. No project names, no
client names, no repo names, no issue numbers.>

**Cost:** <What it actually broke, in generic terms.>

**Instead:** <What to do.>

**Strongest rung available:** <The structural encoding that would enforce this,
or "none, this is judgement".>
```

### Step 6 — Validate applies-to against the vocabulary

Every value in `applies-to` must be in the closed vocabulary in
`templates/lesson.md`. If you need a new value, **stop** — adding one requires
adding its detection line to `scripts/adopt.sh` at the same time. Report this
and let the human decide.

### Step 7 — Write the file

Write the lesson to `lessons/<slug>.md`.

### Step 8 — Update the README

Add a row to the lessons table in `README.md`:

```markdown
| [<slug>](lessons/<slug>.md) | `<applies-to>` | <one-line claim> |
```

Keep the table sorted alphabetically by slug.

### Step 9 — Report

```
Captured: lessons/<slug>.md
Applies to: <values>
Claim: <one-line>

README.md updated. Run `git diff` to review before committing.
```

## Guardrails

- **Never write a lesson that fails the four-part test.** Report which test
  failed and stop.
- **Never invent `applies-to` values.** The vocabulary is closed. If none fit,
  the lesson may be too narrow (project context) or too broad (a rule).
- **Never include project names, client names, repo names, or issue numbers.**
  If the claim can't be stated without them, it is project context.
- **Ask rather than guess.** The human has the context; you have the template.
- **Cap check:** if `lessons/` already has ~25+ entries, remind the human to
  re-apply test 4 to every entry before adding more.

## Output

The lesson file, the README update, and a one-line summary. The human reviews
the diff and commits.
