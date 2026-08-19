# 11 — Skill Routing

---

## How routing actually works today

**[FACT]** In Claude Code, Codex and Cursor, skills are surfaced to the model as a list of `name` + `description` pairs. The full SKILL.md is loaded only when the skill is invoked. This is already progressive disclosure, and it is already implemented by the harness.

**[INFERENCE]** That has a consequence worth stating plainly: **you do not need to build a routing system.** Your section 21 diagram (request → intent → skill index → candidates → relevance → load) is a description of what the harness does when it reads descriptions. Building a parallel index would mean maintaining a second source of truth that the harness ignores.

What you *do* need to build is the thing routing quality actually depends on: **descriptions that are distinguishable from each other**.

---

## The real constraint: description budget

**[FACT]** Every skill's description sits in context for every request, whether used or not. steipete has 56 skills and a dedicated `skill-cleaner` skill whose description reads *"skill audit: live budget, usage, duplicates, compact descriptions"* — he treats it as a scarce resource that needs periodic auditing.

**[INFERENCE]** At 15–20 skills you have comfortable room. At 50+ you'd need steipete's discipline. This is a concrete, mechanical argument for your own "30 excellent skills, not 500 mediocre ones" instinct: the cost of a mediocre skill isn't that it's mediocre, it's that it **taxes every other skill's chance of being found**.

---

## The three routing failures at your scale

### 1. Overlap between neighbouring skills

Your highest-risk collisions:

| Pair | Why they collide | Fix |
|---|---|---|
| `deslop` vs `code-review` | Both "review the diff" | Deslop's description must say *"not a bug finder, not a code reviewer"* |
| `sweep-the-class` vs `audit-to-issues` | Both "find more instances" | Sweep starts from **one known defect**; audit starts from **an axis and no known defect** |
| `failure-visibility-review` vs `deslop` | Both touch `catch` blocks | Deslop hands off to it; say so in both descriptions |
| `design-system-recon` vs `project-onboarding` | Both "read the project first" | Recon is UI-scoped and always precedes design work; onboarding is whole-repo and once per repo |
| `extract-duplication` vs `sweep-the-class` | Both find repeated shapes | Extraction finds repeated *working code*; sweep finds repeated *defects* |

**[RECOMMENDATION]** Every description that has a neighbour gets an explicit contrast clause. This is the single highest-value routing investment, it costs one sentence each, and it's the thing that breaks first as the library grows.

### 2. Silence — the skill exists and never fires

**[INFERENCE]** The biggest risk for the FIND skills, because their trigger moments are ones you don't currently notice. Nothing in your workflow says "a fix was just made, so sweep." That's precisely why the gap exists.

Two mitigations:

- **Put the moment in the description**, not just the topic: *"Use when a fix is about to be declared done"* is a routable moment. *"Finds similar defects"* is not.
- **Chain from a skill that does fire.** `deslop` and `verify-for-real` both run near the end of a change and both should recommend `sweep-the-class` in their output. A skill that recommends another skill is the cheapest routing mechanism there is, and it doesn't consume description budget.

### 3. Wrong-time firing

`audit-to-issues` running mid-feature would be actively disruptive — it's a multi-hour operation that files a dozen issues. **Mark it `disable-model-invocation: true`.** Same for `ui-design-exploration` (produces artefacts you must look at) and `capture-lesson` (writes to the shared library).

---

## The router skill

**[RECOMMENDATION]** Adopt mattpocock's `ask-matt` pattern — one user-invoked skill that maps the library and the flows between skills.

```markdown
---
name: which-skill
description: Ask which skill fits your situation. A router over this library.
disable-model-invocation: true
---

## By what you're doing

**Something's broken and I fixed it** → `sweep-the-class` (always), then
`verify-for-real`, then `capture-lesson` if it taught you something durable.

**I want to know what's wrong with this codebase** → `audit-to-issues`,
scoped to one axis (scalability / security / a11y / data integrity).

**About to open a PR** → `deslop`, then `verify-for-real`.

**Starting UI work** → `design-system-recon`, then `ui-design-exploration`
if the direction isn't settled.

**New repo, or one I haven't touched in months** → `project-onboarding`.

**Something surprised me** → `capture-lesson`.

## By symptom

| Symptom | Skill |
|---|---|
| "It shows no results but I think the query failed" | `failure-visibility-review` |
| "This page isn't updating after an admin change" | `nextjs-render-boundary` |
| "The pixel/analytics/webhook isn't firing" | `third-party-integration` |
| "This looks like the same bug as last week" | `sweep-the-class` |
| "This is the third time I've written this" | `extract-duplication` |
| "Can someone actually call this with bad input?" | `boundary-validation` |
```

**[FACT]** mattpocock's maintenance rule for this file is the important part: *"a new skill it never mentions, or a stale one it still routes to, is a router that lies."* Add or rename a skill, update the router in the same commit.

---

## Why not a registry file

You proposed `registry/skills.yml`. **I'd argue against it.**

The filesystem already is the registry — `find skills -name SKILL.md` is the complete, always-correct list. A YAML registry is a second source of truth that can disagree with the first, and when it disagrees the harness believes the filesystem while you believe the YAML.

**[RECOMMENDATION]** If you want a registry artefact (for a README table, or a future installer), **generate it**:

```bash
scripts/generate-registry.sh   # filesystem -> registry.json + README table
```

and have CI fail if the generated output differs from what's committed. Then it can't drift. That's the `encode-lessons-in-structure` ladder applied to your own repo: a generated-and-verified artefact beats a hand-maintained one.

---

## Routing across harnesses

**[FACT]** You use at least Claude Code and Codex (both appear in your portfolio's AI Tools list, and `~/.codex/` exists on your machine).

**[RECOMMENDATION]** Install to both, from one source:

```bash
# scripts/link-skills.sh — adapted from mattpocock/skills
for DEST in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  for src in skills/*/*/; do
    ln -sfn "$PWD/$src" "$DEST/$(basename "$src")"
  done
done
```

Two consequences to plan for:

1. **Skill names must be globally unique across all folders**, since they flatten into one directory. `find/sweep-the-class` and `change/deslop` both land as `~/.claude/skills/sweep-the-class` and `~/.claude/skills/deslop`.
2. **Symlinks on Windows** need Developer Mode enabled or an elevated shell. Git Bash `ln -s` falls back to a copy otherwise, which silently breaks the "`git pull` updates everything" property. **Test this early** — it's the kind of Windows-specific trap that report 08 says keeps biting you. If symlinks prove unreliable, fall back to a `sync-skills` script that copies and is re-run after each pull, and say so explicitly rather than assuming.

---

## Summary

| Question | Answer |
|---|---|
| Do I need to build a router? | **No.** The harness routes on descriptions. |
| What determines routing quality? | Description precision, and contrast clauses between neighbours. |
| How do skills I'd never think to invoke get invoked? | Chaining — skills that do fire recommend the ones that don't. |
| How do I stop expensive skills firing wrongly? | `disable-model-invocation: true`. |
| Do I need a registry file? | **No.** Generate it from the filesystem, or skip it. |
| What's the scaling limit? | Description budget. Fine to ~30. Audit beyond that. |
| How do I stay portable? | One symlink script, two destinations, globally unique names. |
