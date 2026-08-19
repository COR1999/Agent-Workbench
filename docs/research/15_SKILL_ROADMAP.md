# 15 — Skill Roadmap

---

## Top 5 — if you build only five

| # | Skill | Why this one |
|---|---|---|
| 1 | **sweep-the-class** | Addresses six of the ten recurring problems with one capability. You have documented, in your own tracker, three cases where a fix was declared complete and wasn't (#192, #250, #131), one of which reached a customer (#249). No external library has it. |
| 2 | **failure-visibility-review** | Your #1 recurring bug class: 11 references, two projects, two languages. Directly caused a live revenue bug. Also nonexistent in every library I read. |
| 3 | **capture-lesson** | The only skill that makes the others compound, and the fix for the largest gap found (report 08 — nine lessons trapped in one project, zero global config). Cheapest thing with the longest half-life. |
| 4 | **deslop** | You asked for it, and it's genuinely warranted — but it needs the redesign in report 09, not the reference version. Its real value is preventive: keeping agent output at the standard you already hold, on the fast client work where you skip review. |
| 5 | **verify-for-real** | Changes what "done" means. Your environment structurally cannot verify parts of your stack (no Docker, Windows-only build bugs, `next dev` ≠ production), so an agent will otherwise confidently report success it can't back. |

**Why not `audit-to-issues` in the top 5:** it has the highest single-invocation payoff in your entire history, but it's the most complex skill in the set (complexity 4/5) and you run it a handful of times per project. Build it sixth, once the cheap ones are proving themselves.

---

## Top 15 — ranked

| Rank | Skill | Tier | Provenance |
|---|---|---|---|
| 1 | sweep-the-class | 1 | ORIGINAL |
| 2 | failure-visibility-review | 1 | ORIGINAL |
| 3 | capture-lesson | 1 | ADAPTED (poteto `encode-lessons-in-structure`) |
| 4 | deslop | 1 | ADAPTED (cursor `deslop`) |
| 5 | verify-for-real | 1 | ADAPTED (poteto `prove-it-works`, cursor `verify-this`) |
| 6 | audit-to-issues | 1 | ADAPTED (your own scalability review + cursor `thermo-nuclear`) |
| 7 | record-work | 2 | ORIGINAL (your `ai-usage/*.md`) |
| 8 | boundary-validation | 2 | INSPIRED (poteto `boundary-discipline`) |
| 9 | extract-duplication | 2 | COMBINED (Fowler smells + your rule-of-three) |
| 10 | project-onboarding | 2 | INSPIRED (mattpocock `wayfinder`, steipete `project-structure`) |
| 11 | design-system-recon | 2 | INSPIRED |
| 12 | nextjs-render-boundary | 2 | ORIGINAL |
| 13 | third-party-integration | 2 | ORIGINAL |
| 14 | ui-design-exploration | 3 | INSPIRED (poteto `exhaust-the-design-space`, steipete `frontend-design`) |
| 15 | fix-ci | 3 | ADOPTED as-is (cursor) |

**Tier 3 beyond 15:** `concurrency-correctness-review`, `a11y-sweep`, `prose-deslop`, `debug-from-production-signal`, `dependency-upgrade`.
**Tier 4 experimental:** `propose-skill-change`, `visual-qa`.

---

## The six Tier 1 skills in detail

### 1. sweep-the-class

- **What:** After a defect is identified or fixed, characterise its shape, find every other instance, produce a complete inventory with a fix/defer decision per site.
- **Why:** Report 03 Problem 2. Ten references, three self-documented incomplete fixes.
- **Projects:** hotsauce-mama (primary), senus-board-report.
- **Triggers:** "where else", "same class as", "sweep", or automatically recommended by `deslop` and `verify-for-real` before declaring a fix done.
- **Inputs:** the fix just made (diff or description); the codebase.
- **Outputs:** an inventory table — file, line, matches-shape?, fix now / defer / not applicable. **No edits.**
- **Dependencies:** none. Prose-links to `extract-duplication` when the sweep finds duplication rather than defects.
- **Guardrails:** never edit as part of the sweep; report only. Never widen the shape until it matches everything. State the search performed so you can judge whether it was thorough.
- **Validation:** the inventory names a concrete search (grep pattern, symbol, call site) and every listed site has a decision.
- **Cross-project value:** maximum — language- and framework-agnostic.
- **Expected leverage:** collapses the #121→#192→#223→PR#219→PR#239 pattern from six artefacts to one.

### 2. failure-visibility-review

- **What:** Sweep a diff, module or route for places where a failure is representable as an empty or successful result.
- **Why:** Report 03 Problem 1.
- **Triggers:** "why is this empty", "silent failure", after any data-layer change, chained from `deslop`.
- **Inputs:** a diff or a module path.
- **Outputs:** a list of sites where failure is indistinguishable from absence, each with the local remedy (throw on read paths, `ActionResult` on write paths) and whether monitoring would see it.
- **Detection patterns:** destructured `error` never read; `?? []` on a nullable result; `catch { return genericFailure }`; `except: pass`; unchecked `.ok`/`.error` on an SDK response; a fallback value that's indistinguishable from real data.
- **Guardrails:** never delete error handling; only make failure distinguishable. Flag, propose, don't silently rewrite control flow.
- **Validation:** every finding names what the user would incorrectly conclude.

### 3. capture-lesson

- **What:** Turn an incident, correction or discovery into the right artefact at the right strength.
- **Why:** Report 08. You do this reactively and inconsistently.
- **Triggers:** "remember this", "that surprised me", after `verify-for-real` finds a gap, after a revert, after any "found the hard way" moment.
- **Inputs:** the incident; what was tried; what the cost was.
- **Outputs:** exactly one of — a CI check, a lint rule, a pinned version, a regression test, a rule in `AGENTS.md`, a project decision record, or a portable `lessons/` entry. Plus a stated reason for choosing that rung.
- **The rung ladder** (strongest first, from poteto): unrepresentable state → lint/CI failure → canonical helper → runtime check → prose rule → note.
- **Guardrails:** **dry-run by default** — show the artefact and require confirmation before writing to the central library. Never file the same lesson twice; check `lessons/` first. Always date-stamp and record the version context.
- **Validation:** the chosen rung is the strongest one available, and the reason is stated.

### 4. deslop

Full specification in report 09. Key deltas from the reference: the failure-visibility clause (never delete error handling), the earn-its-place comment discriminator, the "patterns you never write" detection, and a dead `any` clause removed.

### 5. verify-for-real

- **What:** Before claiming done, state what was executed, what was assumed, what this environment structurally cannot check, and what the production-parity check would be.
- **Why:** Report 03 Problem 7.
- **Outputs:**
  ```
  Executed:     npm run typecheck, npm run test:ci (44 passed)
  Not executed: integration tests (need Docker — unavailable on this machine)
  Assumed:      the RPC exists in production (not verified; last `supabase db push` unknown)
  Prod parity:  cache behaviour needs `next build && next start`; `next dev` won't show it
  Verdict:      PARTIALLY VERIFIED
  ```
- **Guardrails:** never report VERIFIED for something inferred. Always name the specific blocker, not "couldn't test".
- **[FACT] grounding:** PR #249's root cause was an RPC that had never been pushed to either database. This skill's "assumed" line is exactly where that would have surfaced.

### 6. audit-to-issues

- **What:** Bounded whole-system review along one named axis, tracing real request paths with file:line evidence, emitting filed GitHub issues in your existing format.
- **Why:** Report 02 §2. Highest single-invocation payoff in your history.
- **Triggers:** user-invoked only (`disable-model-invocation: true`).
- **Inputs:** the axis (scalability / security / a11y / data integrity / reliability); scope; label vocabulary.
- **Outputs:** a review document plus draft issues with Title / Labels / Priority / Severity / Description / Evidence (file:line) / Impact / Suggested Fix / Acceptance Criteria / Effort. **Dry-run by default** — show drafts before filing.
- **Guardrails:** one axis per run. Every finding traces a real path with file and line. Say "not proven" when the trail is weak (steipete's standard, and yours). Never file without confirmation.

---

## Build order

**Phase 1 — foundation (start here)**
1. Repo skeleton + `AGENTS.md` (rules only, incl. the four Windows rules from report 13)
2. `scripts/link-skills.sh` — **and verify Windows symlinks work on day one**
3. `scripts/validate-skills.sh` + CI
4. `lessons/` seeded with the nine already identified in report 08

That's a day, and item 4 alone captures value you currently lose on every new project.

**Phase 2 — the two originals**
5. `sweep-the-class`
6. `failure-visibility-review`

Both are pure procedure, no fixtures needed, and both address problems you can test against real history — run them retrospectively on `hotsauce-mama` at the commit before #250 and see whether they find the ten read paths.

**Phase 3 — deslop, properly**
7. `deslop` + the fixture set from report 12, `should-not-flag` written first

**Phase 4 — memory and proof**
8. `capture-lesson`, `record-work`, `verify-for-real`

**Phase 5 — the expensive one**
9. `audit-to-issues`

**Then stop and use it for a month** before adding Tier 2. The whole argument of report 05 is that leverage concentrates in a handful of skills; adding more before these have proven themselves is how you get a junk drawer.

---

## What not to build

Restating for the record: no workflow engine, no dreaming system, no database, no CLI framework, no registry file, no profile YAML tree, no version pinning, no `.agent/` directory, no `typescript-quality` skill, no git/PR/merge-conflict skills, no generic testing/debugging/refactoring skills.
