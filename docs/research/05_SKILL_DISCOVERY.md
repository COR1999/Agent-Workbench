# 05 — Skill Discovery

Every candidate, scored against your evidence. Scores are 1–5. **Complexity is a cost** — high complexity lowers priority.

**Leverage** = (Frequency + Importance + Reuse + Failure-prevention + Time-saved + Quality) − Complexity. Max 29.

---

## Master table

| Skill | Freq | Imp | Reuse | Fail-prev | Time | Qual | Cplx | Ext | **Lev** | Class |
|---|---|---|---|---|---|---|---|---|---|---|
| **sweep-the-class** | 5 | 5 | 5 | 5 | 4 | 5 | 2 | 2 | **27** | CORE |
| **failure-visibility-review** | 5 | 5 | 5 | 5 | 3 | 5 | 2 | 1 | **26** | CORE |
| **capture-lesson** | 5 | 5 | 5 | 4 | 3 | 4 | 2 | 4 | **24** | CORE |
| **deslop** (calibrated) | 4 | 4 | 5 | 3 | 4 | 5 | 2 | 5 | **23** | CORE |
| **audit-to-issues** | 3 | 5 | 5 | 5 | 5 | 5 | 4 | 3 | **24** | CORE |
| **boundary-validation** | 4 | 5 | 5 | 5 | 3 | 4 | 3 | 3 | **23** | HIGH |
| **extract-duplication** | 5 | 3 | 5 | 2 | 4 | 4 | 2 | 4 | **21** | HIGH |
| **verify-for-real** | 5 | 4 | 5 | 4 | 2 | 4 | 2 | 3 | **22** | HIGH |
| **record-work** | 5 | 4 | 5 | 2 | 3 | 3 | 1 | 3 | **21** | HIGH |
| **nextjs-render-boundary** | 3 | 5 | 4 | 5 | 3 | 4 | 3 | 2 | **21** | HIGH |
| **project-onboarding** | 4 | 4 | 5 | 2 | 5 | 3 | 2 | 5 | **21** | HIGH |
| **third-party-integration** | 3 | 4 | 5 | 4 | 4 | 3 | 3 | 1 | **20** | HIGH |
| **design-system-recon** | 4 | 4 | 5 | 2 | 4 | 4 | 2 | 3 | **21** | HIGH |
| **ui-design-exploration** | 3 | 5 | 5 | 1 | 4 | 5 | 4 | 4 | **19** | SPECIALIZED |
| **concurrency-correctness** | 2 | 5 | 3 | 5 | 2 | 4 | 4 | 1 | **17** | SPECIALIZED |
| **a11y-sweep** | 3 | 3 | 5 | 3 | 3 | 4 | 2 | 4 | **19** | SPECIALIZED |
| **debug-from-production-signal** | 3 | 4 | 4 | 3 | 4 | 3 | 3 | 2 | **18** | SPECIALIZED |
| **prose-deslop** | 4 | 2 | 5 | 1 | 3 | 3 | 1 | 5 | **17** | SPECIALIZED |
| **dependency-upgrade** | 2 | 3 | 5 | 4 | 3 | 3 | 2 | 3 | **18** | SPECIALIZED |
| **propose-skill-change** (reflect) | 1 | 4 | 5 | 2 | 2 | 3 | 4 | 4 | **13** | EXPERIMENTAL |
| **visual-qa** (screenshot diff) | 2 | 3 | 4 | 3 | 3 | 3 | 5 | 3 | **13** | EXPERIMENTAL |
| ~~typescript-quality / no-any~~ | 1 | 1 | 3 | 1 | 1 | 1 | 2 | 5 | **6** | **REJECT** |
| ~~generic refactoring~~ | — | — | — | — | — | — | — | — | — | **REJECT** |
| ~~git-workflow / new-branch-and-pr~~ | 5 | 2 | 4 | 1 | 1 | 1 | 1 | 4 | **13** | **REJECT — script** |
| ~~run-tests / typecheck~~ | 5 | 3 | 5 | 2 | 1 | 1 | 1 | 4 | **16** | **REJECT — npm script** |
| ~~deployment~~ | 1 | 3 | 3 | 2 | 1 | 1 | 2 | 3 | **9** | **REJECT — docs** |
| ~~add-product / add-journal-post~~ | 5 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | **11** | **REJECT — runbook** |

---

## Detail on the candidates worth building

### 1. sweep-the-class — **CORE**

**Description.** After a defect is identified or fixed, characterise its *shape*, find every other instance of that shape in the codebase, and produce a complete inventory with a fix/defer decision per site.

**Evidence.** Report 03 Problem 2. Ten references, including three cases where you documented against yourself that a closed fix was incomplete: issue #192 (*"still do the unbounded full-table-scan closed issue #121 said was fixed"*), issue #250 (*"same class as #180/#249"*), issue #131 (*"doesn't work as intended"*). Plus PRs whose titles are literally counts of missed sites: #171 (3 admin pages), #252 (10 read paths), #206 (3 copies), #76 (3 copies), #103 (12 files).

**Projects observed.** hotsauce-mama (primary), senus-board-report (`"fix: repo-wide code quality audit"`, `"JSX dedup"`).

**Frequency 5** — implicated in at least six of the ten recurring problems. **Importance 5** — its absence produced a live customer-facing bug (#249). **Reuse 5** — language- and framework-agnostic. **Failure prevention 5.** **Complexity 2** — it's grep plus judgement; the hard part is characterising the shape, not the search.

**External support 2** — nothing in cursor/poteto/mattpocock/steipete does this. `blast-radius` (poteto) is adjacent but asks "what does my change affect", not "where else does this defect live". This is close to an original skill.

**Confidence: very high.**

---

### 2. failure-visibility-review — **CORE**

**Description.** Sweep a diff, module or route for places where a failure is representable as a success or an absence. Apply the local remedy: throw on read paths, return a discriminated result on write paths, and make sure monitoring sees it.

**Evidence.** Report 03 Problem 1. Eleven references across two projects and two languages. Issues #180, #190, #234, #250; PRs #245, #249, #252, #253; senus #40, #55, #61.

**Frequency 5, Importance 5, Reuse 5, Failure prevention 5.** **Complexity 2** — the detection pattern is concrete: destructured `error` never read, `?? []` on a nullable result, `except: pass`, `catch { return genericFailure }`, `.ok` unchecked.

**External support 1** — I found nothing equivalent in any of the four libraries. Original.

**Confidence: very high.**

---

### 3. capture-lesson — **CORE**

**Description.** Turn an incident, correction or discovery into the *right artefact at the right strength*: a CI check, a lint rule, a pinned version, a regression test, a rule in AGENTS.md, a project-memory note, or a portable lesson in the central library. Explicitly prefers structural mechanisms over prose.

**Evidence.** Report 02 §3. You already do this — six documented instances of an incident becoming a mechanism (Playwright suite, `guard-main-base.yml`, the RLS CI assertion, pinned `setup-cli`, trace upload on failure, concurrency cancellation). And at least one where you stopped at prose that nothing enforces (`shadcn@latest`). `CLAUDE.md` is 49KB and is the 2nd most-edited file in the repo — the practice is real and heavy.

**Why CORE despite low direct failure prevention.** This is the skill that makes every other skill improve over time, and it is the concrete seed of the dreaming layer you want later. Building it now costs little and makes the rest of the system compound.

**External support 4** — poteto's `principle-encode-lessons-in-structure` is an excellent, directly adaptable statement of the principle; cursor's `continual-learning` is the mechanism for the AGENTS.md half.

**Confidence: high.**

---

### 4. deslop (calibrated) — **CORE**

**Description.** Review the branch diff against its base for AI-generated slop, calibrated against the local file's own conventions. Full spec in report 09.

**Evidence.** Report 03 Problem 10 — measured slop signatures concentrated in `invoiceToSheet` (11 narrating comments, 35 `console.log`, 23 uniform catches), `kitchenapp`, `fitnessTracker`. Near-zero in `hotsauce-mama` and `senus`.

**Honest note.** Your two flagship projects are already clean, so deslop's value there is *preventive* — it keeps agent output at the standard you already hold. Its value is highest on the fast client work (Era 2), which is exactly the work where you currently skip review. Frequency 4 rather than 5 for that reason.

**External support 5** — cursor's `deslop` is the direct source; poteto's `unslop` and `no-comments` are adjacent. But see report 09: the reference version needs two of its four focus areas changed for your codebase, not copied.

**Confidence: high (on need). Medium (on the reference implementation's fitness).**

---

### 5. audit-to-issues — **CORE**

**Description.** Run a bounded whole-system review along a named axis (scalability, security, a11y, data integrity), tracing real request paths with file and line evidence, and emit filed GitHub issues in your existing format with labels, severity, evidence, suggested fix, acceptance criteria and effort.

**Evidence.** Report 02 §2. `hotsauce-mama-scalability-review.md` — 98KB, 15 sections, 16 pre-written issues, which became issues #221–#238 and drove PRs #219, #239, #240, #243. Plus PRs #125, #127, #145, and senus's `#66` repo-wide audit and pre-submission audit.

**Time saved 5, Quality 5, Failure prevention 5.** **Complexity 4** — this is the most complex skill in the set. It needs a scoped axis, a real traversal strategy, an evidence standard and an output format. It's also the one with the largest demonstrated payoff in your own history.

**Frequency 3** — you run it a handful of times per project, not daily. That's fine; leverage per invocation is enormous.

**External support 3** — cursor's `thermo-nuclear-code-quality-review` and steipete's `github-deep-review` are structurally similar; neither emits filed issues.

**Confidence: very high on value. Medium on getting the scope right first try.**

---

### 6. boundary-validation — HIGH

**Description.** For any point where untrusted data enters — Server Actions, route handlers, webhooks, `JSON.parse`, `localStorage`, env vars, third-party API responses, URL params — verify it is parsed into a validated shape with bounds, format and cardinality constraints, and that redirects/hosts are allow-listed.

**Evidence.** Report 03 Problem 4 — nine references (#194, #196, #197, #202, #203, #204, #114, #115, #188). Your own `CLAUDE.md` section *"Server Action conventions — two mistakes already made once"*. Also absorbs the real root cause of the `kitchenapp` `any` cluster.

**This is where your TypeScript concern actually belongs.** Not a no-`any` rule; a trust-boundary discipline.

**Confidence: very high.**

---

### 7. extract-duplication — HIGH

**Description.** Find repeated logic/shape at or above your rule-of-three threshold, propose the extraction with the local convention (custom hook in `lib/hooks/`, shared module in `lib/`, constant in `constants.ts`, string in `ui-text.ts`), and write the provenance comment recording the call sites replaced.

**Evidence.** Report 02 §5 — the single most common refactor in every project and every era. PRs #70–#77 (seven consecutive), #103, #206, #207, #208, plus commits in pierogalsWeb, fitnessTracker, kitchenapp, loginApplication, senus.

**Failure prevention only 2** — duplication rarely causes outages for you. But time saved and quality are high, frequency is maximal, and complexity is low.

**Confidence: very high.**

---

### 8. verify-for-real — HIGH

**Description.** Before claiming work is done, produce an explicit verification statement: what was actually executed, what was assumed, what this environment structurally cannot check (no Docker, Windows-only build bugs, `next dev` ≠ production), and what the production-parity check would be.

**Evidence.** Report 03 Problem 7 — seven references, including the CSP production outage, the CI env-scoping breakage, senus's CI-only failures, and multiple CI comments in your own hand admitting *"not independently re-verified against a real run"*.

**Confidence: high.**

---

### 9. record-work — HIGH

**Description.** Produce a per-branch work record in your existing shape: *Context* → *What was investigated first* (including rejected approaches and why) → *What was built* → *Why nothing else was needed*.

**Evidence.** You have already written **35 of these** — `senus-board-report/frontend/docs/ai-usage/*.md`. They contain rejected alternatives with exact error messages, infrastructure trade-offs, and notes on where you were consulted before a path was chosen. Nothing in `hotsauce-mama` carries the practice forward; there the equivalent content lives scattered in commit bodies.

**Complexity 1.** This is the cheapest skill in the set and it is the substrate the dreaming layer will need. Build it early even though its immediate payoff is modest.

**Confidence: very high** — you invented it; it just isn't portable.

---

### 10. nextjs-render-boundary — HIGH

**Description.** For a given route: determine its actual render mode, identify what forces it dynamic, check whether that's intended, verify cache/revalidate strategy against the data's mutability, and flag any per-request value (nonce, cookie, header) that can leak into cached output.

**Evidence.** Report 03 Problem 3 — eleven references including your only production outage (#137), your only revert (#153), and a code comment that asserted the opposite of reality (#193).

**Confidence: high.**

---

### 11. project-onboarding — HIGH

**Description.** On entering an unfamiliar repo, build the working model: stack and versions, render/data-flow architecture, the content/token/config layers, the test layers and what each is allowed to assume, the git workflow, and the settled decisions not to re-litigate.

**Evidence.** Indirect but strong. Your `CLAUDE.md` opens *"Read this file first in every new session on this repo"* and exists specifically so that *"a new session can pick this up without re-deriving the architecture discussion that produced it."* You have 39 repos and are actively adding client projects. Every external library has an equivalent (mattpocock `wayfinder`, steipete `project-structure`, cursor `figure-it-out`).

**Confidence: medium-high** — the need is inferred from your documentation behaviour rather than directly observed as a failure.

---

### 12. third-party-integration — HIGH

**Description.** A checklist-driven integration review for external scripts and APIs: SPA route-change handling, CSP/allow-list implications including fallback delivery paths, consent gating vs hydration, event idempotency, failure-response checking, timeouts, and quota/rate-limit behaviour.

**Evidence.** Report 03 Problem 6 — seven Meta Pixel PRs. Plus Instagram Graph API (#132, #135 — a token bootstrapped via a workaround with unverified expiry), Gemini quota resilience (senus, three separate PRs), Resend error checking (#214), Stripe timeouts (#230).

**Confidence: high.**

---

### 13. design-system-recon — HIGH

**Description.** Before any UI work: locate and read the token source, the component inventory, the copy layer, the written design brief and its references, and the local patterns for empty/loading/error states. Report what exists so new UI extends rather than duplicates.

**Evidence.** Report 04 §7 and §10. `globals.css` `:root` as sole colour source; `ui-text.ts`; `images.ts`; senus AGENTS.md's full component inventory ending *"Extend these existing components/utilities rather than replacing them"*; hotsauce's *"no component should ever hardcode a hex/HSL value"*. Your #1 and #3 most-edited files are content/config layers, so any UI generation that ignores them produces immediate rework.

**Confidence: high.** This is the dependency that makes `ui-design-exploration` viable.

---

### 14. ui-design-exploration — SPECIALIZED

**Description.** Given a UI request, generate 2–4 genuinely distinct directions as standalone HTML previews using the project's real tokens, let you choose, then iterate — implementation only after selection.

**Evidence.** This is the weakest-evidenced of the high-scoring skills, and I want to be explicit about that. It is mostly **your stated goal** (sections 27–28), not something I observed you doing. What I *did* observe: written design briefs with named references, `docs/dashboard-review.md` as a standalone design review that drove a resequencing, a deliberate dashboard redesign branch, and a large HTML-artefact habit outside repos (`executive-summary.html`, `technical-architecture-proposal.html`, `multi-tenant-architecture-proposal.html`, `senus-interview-study-guide.html` on your Desktop — you clearly already think in standalone HTML documents).

**Complexity 4.** Real risk of becoming a junk-drawer mega-skill. See report 08 for the decomposition I'd recommend.

**Confidence: medium.** High confidence you want it; medium confidence about the right shape.

---

### 15. a11y-sweep — SPECIALIZED

**Evidence.** Seven single-instance PRs (#44, #95, #96, #98, #104, #159, #205), of which three are the same defect shape in different components. **This is `sweep-the-class` with an a11y checklist attached**, so build it only after `sweep-the-class` exists, and build it thin.

---

### 16. debug-from-production-signal — SPECIALIZED

**Description.** Start from a real signal (Sentry event, live user report, Lighthouse regression, CI failure) and drive to a reproduction, then a root cause, then a regression test.

**Evidence.** "Found live:" opens several of your commit bodies (#248, #249). PR #169 was a live production JS error. PR #240 added the error tracking that makes this possible; before that you had none (#229).

**Confidence: medium** — the capability is real but you've only had production signal for a few weeks, so the frequency evidence is thin.

---

### 17. prose-deslop — SPECIALIZED

**Description.** Strip AI tells from prose you're about to publish — READMEs, PR bodies, issue text, audit documents, client-facing HTML.

**Evidence.** You produce a great deal of prose (98KB audit doc, 49KB CLAUDE.md, 35 work records, client proposals as HTML/PDF on your Desktop). Frequency is genuinely high. **But** importance is 2 because your prose is already good and distinctive.

**Critical adaptation:** poteto's `unslop` bans em dashes outright. You use them constantly and they're part of your voice. Adopting it unmodified would fight you. See report 06.

---

### 18. dependency-upgrade — SPECIALIZED

**Evidence.** PR #110 (Next 14→16, React 18→19, ESLint 8→9), PR #251 (3 high-severity CVEs), issues #80, #92, #113, #186, plus `overrides` for `sharp`/`postcss`. Real, recurring, but a handful of times per project.

---

## Explicit rejections

| Candidate | Why rejected |
|---|---|
| **typescript-quality / no-`any`** | **Zero `any` in 34,000+ lines of your serious work.** A skill that never fires trains you to stop invoking skills. The real root cause lives in `boundary-validation`. |
| **generic "refactoring"** | Too broad to route to and too broad to guardrail. Decomposes into `extract-duplication`, `sweep-the-class`, and the rest. |
| **generic "testing"** | Your test strategy is deliberate and layered (report 04 §9). A generic testing skill would fight it. Test-writing belongs *inside* the fix skills as a required output. |
| **generic "debugging"** | Same. Decomposes into `debug-from-production-signal` and `verify-for-real`. |
| **git-workflow / new-branch-and-pr** | Deterministic. This is a shell script plus a rule, not a skill. |
| **run tests / typecheck / lint** | Already `npm run test:ci` / `typecheck` / `lint`. A skill wrapping an npm script is pure overhead. |
| **deployment / environment config** | Your README and `.env.example` already document this per project. Documentation, not a skill. |
| **add a product / add a journal post** | A project runbook that already exists in your README. Explicitly project-local, zero cross-project reuse. |
| **"Fix Next.js authentication"** | Your own section 17 rejects this correctly. It's a composition of `boundary-validation` + `nextjs-render-boundary` + `verify-for-real`. |
| **UI/visual regression diffing** | Real value, but complexity 5 for you (Windows, no Docker, screenshot-baseline flakiness) and Lighthouse CI already guards the score axis. Revisit later. |

---

## Where the leverage actually concentrates

**[INFERENCE]** Six of the ten recurring problems in report 03 reduce to the same meta-problem: *a defect of known shape exists in several places and gets found one at a time.* One skill addresses all six. If you build only one thing, build `sweep-the-class`.
