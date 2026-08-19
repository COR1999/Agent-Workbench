# 10 — Skill Format

You proposed a frontmatter block with `name`, `description`, `triggers`, `category`, `scope`, `inputs`, `outputs`, and asked me to challenge it. Here's the challenge.

---

## What the field is actually for

Frontmatter has exactly one consumer that matters: **the harness's skill loader**. It reads `name` and `description` to decide whether to surface the skill. Everything else in a frontmatter block is read by nobody unless you write software to read it.

So the test for every field is: *does something act on this?* If not, it is a comment with extra syntax, and it will drift.

---

## What the four reference libraries actually ship

**[FACT]** I read the frontmatter of all 158 external skills. The convergence is striking:

| Field | cursor (82) | poteto (69) | mattpocock (35) | steipete (56) |
|---|---|---|---|---|
| `name` | all | all | all | all |
| `description` | all | all | all | all |
| `disable-model-invocation` | some | ~24 (all principles) | ~15 | rare |
| `argument-hint` | rare | rare | a few | rare |
| `license` | — | — | — | one |
| `metadata` | — | — | — | a few (tool requirements) |
| `triggers` / `category` / `scope` / `inputs` / `outputs` / `version` / `dependencies` | **none** | **none** | **none** | **none** |

**[FACT]** Not one of 158 skills carries a `triggers`, `category`, `inputs`, `outputs`, `version` or `dependencies` field. These are four independently-designed libraries, including one from the vendor that defines the format.

**[INFERENCE]** That's not an oversight. Those fields all duplicate something that already exists somewhere better: triggers duplicate the description, category duplicates the folder, inputs/outputs duplicate the body, version duplicates git, dependencies duplicate a sentence of prose.

---

## Recommended format

```markdown
---
name: sweep-the-class
description: After identifying or fixing a defect, find every other place the same defect shape exists. Use when a fix is about to be declared done, when a bug is filed that smells like it has siblings, or when the user says "where else", "sweep", or "same class as".
---

# Purpose

One paragraph. What this does and what problem it solves.

# When to use / when not to use

Two short lists. The "not" list matters more — it's what stops the skill firing wrongly.

# Inputs

What it needs and where to get it.

# Procedure

Numbered steps.

# Guardrails

Hard constraints. What it must never do.

# Output

The shape of the result, with an example.

# Validation

How you know it worked.
```

**Two frontmatter fields. That's it.** Plus these, only when they apply:

- `disable-model-invocation: true` — for skills only you should trigger (`audit-to-issues`, `ui-design-exploration`). **Real and enforced by the harness.**
- `argument-hint: "<base-ref>"` — for skills that take an argument.
- `provenance:` — one line. You asked for this in section 38 and it's cheap:
  ```yaml
  provenance: adapted from cursor/plugins cursor-team-kit/deslop
  ```
  One string, not a nested object. `original` / `adapted from X` / `inspired by X` / `combined from X + Y`.

---

## Fields I recommend against, and why

| Field | Why not |
|---|---|
| `triggers:` | Duplicates `description`. The harness routes on the description string; a `triggers` list is invisible to it. Two places to update, one of which does nothing. **Put the triggers in the description as a "Use when…" clause** — that's what all four libraries do and it's what actually gets read. |
| `category:` | The folder is the category (`skills/find/sweep-the-class/`). A field that restates the path will drift from the path. |
| `scope:` | Undefined semantics. Nothing consumes it. |
| `inputs:` / `outputs:` | A YAML list can't express "the diff against the merge-base, or `main-dev` if it exists, else `main`". The body can. Keep them as body sections. |
| `version:` | Git owns this. A hand-maintained `version:` field is wrong the moment you edit and forget. |
| `dependencies:` | This is the one worth arguing about, because you raised dependency hell in section 22 — and the answer is that the field *causes* the hell it's meant to manage. If `deslop` declares `requires: git-diff`, either nothing enforces it (dead field) or something does (hard failure when uninstalled). A sentence in the body — *"If you haven't read this project's design tokens, run `design-system-recon` first"* — degrades gracefully to a no-op. |
| `tags:`, `author:`, `license:` | Personal repo, single author, one LICENSE at the root. |

---

## The description is the entire routing surface

**[RECOMMENDATION]** Because `description` is doing all the work, it needs a deliberate shape. The best examples in the corpus follow one:

> **[What it does]. Use when [concrete situations, including phrases the user actually says].**

Compare:

```yaml
# Weak — states the topic, not the trigger
description: Remove AI-generated code slop and clean up code style

# Strong — the model can decide from this alone
description: Review the branch diff against its base and remove AI-generated slop
  inconsistent with the surrounding code's own conventions. Use before opening a PR,
  or when the user says "deslop", "clean this up", or "review the diff for slop".
  Not a refactoring tool and not a bug finder.
```

mattpocock's `code-review` description is 60 words and names the two axes, the parallelism, and four trigger phrases. steipete's are compressed to a single dense line (`"GitHub deep review: bugs, PRs, best fix, stale-or-real, read code first."`) — terser, but he has 56 skills competing for description budget and has a `skill-cleaner` skill specifically to audit it.

**[RECOMMENDATION]** For 15–20 skills you have room. Aim for 25–50 words. Include a negative clause where the skill is easily confused with a neighbour — `deslop` vs `code-review`, `sweep-the-class` vs `audit-to-issues` — because collisions between similar descriptions are the main routing failure at your scale.

---

## Directory shape

```
skills/find/sweep-the-class/
  SKILL.md              required
  reference/            optional — loaded only when the procedure says to
    shape-patterns.md
  tests/                optional
    should-flag/
    should-not-flag/
  scripts/              optional — deterministic helpers
    find-siblings.sh
```

**Progressive disclosure:** the harness loads `name` + `description` for every skill always, and the SKILL.md body only when invoked. So the real budget question is **description length across the whole library** — that's what's always in context. Anything long (checklists, pattern catalogues, examples) goes in `reference/` and is read on demand by an explicit instruction in the procedure.

**[RECOMMENDATION]** Keep SKILL.md under ~200 lines. `deslop`'s S1–S7 catalogue and its never-delete list should live in `reference/slop-patterns.md`, with the SKILL.md saying "read `reference/slop-patterns.md` before classifying".

---

## What the minimum metadata actually needs to support

You asked me to determine this per concern:

| Concern | Mechanism | Metadata needed |
|---|---|---|
| **Discovery** (does it exist) | `README.md` + the router skill | none — generated from the filesystem |
| **Routing** (should I use it now) | `description` | `name`, `description` |
| **Progressive disclosure** | Directory structure + explicit reads in the procedure | none |
| **Execution** | The SKILL.md body | none |
| **Validation** | `tests/` + a validator script | none — conventions, not fields |
| **Versioning** | Git | none — see report 14 |
| **Evolution** | `capture-lesson` + git history | none |
| **User-only invocation** | `disable-model-invocation: true` | that one field |
| **Provenance** | `provenance:` | one string |

**Total: two required fields, three optional.** Everything else you proposed is served better by the filesystem, by git, or by the body.

---

## Rules, principles, skills, scripts — the distinction

You asked for this in section 16. The test I'd use:

| Type | Test | Lives in | Your examples |
|---|---|---|---|
| **RULE** | Always true. No procedure. Violating it is always wrong. | `AGENTS.md` | Never commit directly to `main`. Never commit secrets. A failure must never be indistinguishable from an empty result. Never claim verified what you couldn't execute. |
| **PRINCIPLE** | A judgement heuristic. Applies sometimes. No steps. | `principles/*.md`, `disable-model-invocation: true` | Encode lessons in structure. Concentrate guards at boundaries. Exhaust the design space before committing. |
| **SKILL** | A repeatable procedure with judgement in it. Has steps, guardrails and an output. | `skills/<stage>/<name>/SKILL.md` | `deslop`, `sweep-the-class`, `audit-to-issues` |
| **SCRIPT** | Deterministic. Same input, same output. No judgement. | `scripts/` | Link skills into `~/.claude/skills`, validate frontmatter, create branch + PR |
| **WORKFLOW** | An ordered sequence of skills toward an objective. | Later phase. Not now. | Feature development; design exploration |
| **PROJECT MEMORY** | A fact about one project. | Project `AGENTS.md` / `docs/` | Why this project uses Supabase; the Jungle Sauce label swap-in checklist |
| **LESSON** | A fact that generalises past one project. | Central `lessons/` (report 08) | `next/og` breaks on Windows; Git Bash mangles POSIX arguments |

**[RECOMMENDATION]** The failure mode you're most at risk of is turning rules into skills. "Don't use `any` as a lazy escape hatch" is a rule, and a weak one for you since you never do it. "Find every other place this defect shape exists" is a skill because it has steps and produces an artefact. When in doubt: *if it has no procedure, it isn't a skill.*
