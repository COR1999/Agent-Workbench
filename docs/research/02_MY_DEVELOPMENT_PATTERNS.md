# 02 — My Development Patterns

How you actually work, derived from history rather than from what you'd say about yourself.

---

## 1. The unit of work is a narrow, named branch with one PR

**[FACT]** Every one of the 156 PRs in `hotsauce-mama` is scoped to one named concern. Median change size is small; the largest non-release PRs are deliberate infrastructure drops. Branch prefixes are a genuine taxonomy, not decoration: `fix/`, `feature/`, `feat/`, `refactor/`, `chore/`, `ci/`, `docs/`, `security/`, `perf/`, `seo/`, `content/`, `test/`, `e2e/`, `hotfix/`, `audit/`, `polish/`.

**[FACT]** Branch names describe the *problem*, not the change: `fix/reserve-stock-concurrency-false-rejection`, `fix/swallowed-supabase-errors`, `fix/checkout-duplicate-product-stock-corruption`.

**[FACT]** The release path is a three-tier train, documented in `CLAUDE.md` and enforced by `.github/workflows/guard-main-base.yml`:

```
feature/* → main-dev → main
```

**[INFERENCE]** You think in *problem units*, not change units. A skill that operates on "the current branch versus its base" fits your workflow natively. A skill that operates on "the whole codebase" does not, except in the audit mode below.

---

## 2. You work in two modes, and they are very different

### Mode A — Narrow fix loop

Read issue → branch → one focused change → tests → PR → merge to `main-dev`. Fast, small, high volume. 50 of 156 PRs.

### Mode B — Whole-system audit

**[FACT]** Evidence for a recurring, deliberate audit mode:

- `hotsauce-mama-scalability-review.md` on your Desktop — 98KB, 15 sections, ranked top-20 risk list, load simulation, production readiness scores, **and 16 pre-written GitHub issues in full issue format** (Title / Labels / Priority / Severity / Description / Evidence / Impact / Suggested Fix / Acceptance Criteria / Estimated Effort). Issues #221–#238 in the repo are the filed output.
- PR #125 `fix/production-readiness-audit` (+1162/−54, 38 files)
- PR #127 `fix/audit-followup`
- PR #145 `audit/engineering-review`
- PR #239 "scalability review follow-through"
- `senus-board-report`: "fix: repo-wide code quality audit (bugs, a11y/layout, lint) (#66)", "fix: final pre-submission audit — doc accuracy, test isolation, JSX dedup"

**[FACT]** Your own stated standard, from that review's opening: *"This is not a generic code review. Every finding below traces a real request path through actual files in this repo (paths and line numbers included)."*

**[INFERENCE]** The audit → filed-issues → fix-PR pipeline is the highest-value pattern in your entire history, and it is entirely ad-hoc. It has no name, no template, and no repeatable trigger. Formalising it is the single clearest win available.

---

## 3. You encode lessons in structure, not just in prose

**[FACT]** Repeated instances of turning a one-off failure into a permanent mechanism:

| Incident | Structural response |
|---|---|
| CSP nonce shipped broken to production despite passing every `next dev` check (#137, #153) | Playwright e2e suite running against a real `next build && next start`, plus `e2e/csp-static-cache.spec.ts` as the named regression test |
| A PR merged straight to `main`, bypassing `main-dev` (#107, #112) | `.github/workflows/guard-main-base.yml` fails any PR to `main` not headed by `main-dev` |
| Default DB grants make RLS the only backstop for future tables (#119) | CI step queries `pg_class.relrowsecurity` and fails the build if any public table lacks RLS |
| `supabase/setup-cli@latest` hit GitHub's release-API rate limit and failed CI for unrelated reasons (2026-07-17) | Version pinned to `2.109.1`, with the reason in a comment |
| Playwright traces lost on ephemeral runners while debugging a flaky spec (2026-07-22) | `upload-artifact` step gated on `if: failure()` |
| CI minutes burning on superseded runs | `concurrency` group with `cancel-in-progress`, `paths-ignore` for docs |

**[FACT]** Counter-example — where you stopped at prose: `shadcn@latest` generates Tailwind-v4-only CSS incompatible with your v3 setup. The mitigation is a paragraph in `CLAUDE.md`. Nothing enforces it.

**[INFERENCE]** You already practise `encode-lessons-in-structure` (which is a named principle in the poteto/cursor libraries) at a high level, but inconsistently and without a trigger. You do it when the failure was painful. You don't do it when the failure was merely noticed.

---

## 4. Your commits are post-mortems

**[FACT]** 3,280 lines of commit body across 461 commits. A representative example, in full:

> **Fix hydration mismatch: consent state now uses useSyncExternalStore**
>
> Found live: on any repeat visit with marketing consent already granted, MetaPixel's `<noscript>` was flagged as a client-only addition React couldn't reconcile against the server HTML, tearing down and re-rendering that whole subtree. Root cause: ConsentProvider's old useState+useEffect only guarantees the SSR value and the client's *first* render start in sync (both false) — it does nothing to stop a descendant's hydration, if deferred behind a Suspense boundary, from running after CookieConsent.run() has already resolved for an already-consented visitor…
>
> useSyncExternalStore's getServerSnapshot is the mechanism React documents specifically for this… Confirmed via a Playwright repro (grant marketing consent, reload, watch for the mismatch) before and after this change.

**[FACT]** The consistent shape is: **how it was found → root cause → mechanism chosen and why → how it was verified → cross-reference to related issues**. PR #248's follow-up commit even documents a bug the fix itself introduced and then fixed.

**[FACT]** Cross-referencing is systematic. Issue #250: *"Silently swallowed Supabase query/RPC errors across admin + storefront reads (same class as #180/#249)"*. Issue #192: *"list-customers.ts and analytics.ts still do the unbounded full-table-scan closed issue #121 said was fixed"*.

**[INFERENCE]** You are already generating the "experience" records that your future dreaming layer would need. They are just scattered across commit bodies, PR titles, issue text and a 49KB CLAUDE.md, in four different shapes, in one repo.

---

## 5. You centralise aggressively, and you do it reactively

**[FACT]** Centralisation is the single most common refactor across your entire history, in every era:

| Project | Evidence |
|---|---|
| hotsauce-mama | PRs #70–#77: seven consecutive `refactor/` PRs extracting `useServerAction`, `useFormAction`, `useSubscribeForm`, `useSelection`, `useLocalStorageState`, euro↔cents conversion, cart derived values |
| hotsauce-mama | `src/content/ui-text.ts` (811 lines) — all UI copy; `src/lib/constants.ts`; `src/content/images.ts`; `globals.css` `:root` as the single colour source |
| hotsauce-mama | PR #103 "Extract a shared PageContainer component" (same max-w/padding string in 12 files) |
| hotsauce-mama | PR #206 "Centralize the email sign-off into brand.ts instead of 3 duplicated copies" |
| senus-board-report | "refactor: split documents.py router into a package by concern", "split metrics.py", "split financial_metrics_extractor.py into a mixin package" |
| senus-board-report | `use-async-data.ts` as "the shared loading/error/data/refetch primitive underneath all of them" |
| pierogalsWeb | "Refactor Hero section and extract magic numbers to constants" |
| fitnessTracker | "moved logic from stat overview into useStats.ts" |
| kitchenapp | "centralised css props and elimated css duplicate" |
| loginApplication | "created useAuthform hook", "added useAuth.ts hook" |

**[FACT]** The extraction almost always happens *after* 3+ copies exist, and the commit or comment records the count. `src/lib/format.ts`:

```ts
/** Inverse of eurCentsToEuroString — was duplicated across edit-price-form.tsx,
    edit-shipping-zone-rate-form.tsx, and admin-shipping-zones.ts before being
    centralized here. */
```

**[INFERENCE]** You have a well-calibrated, consistent instinct here — "rule of three, then extract, and record where it came from". You do not over-abstract; I found no speculative generality in the recent repos. The cost is that duplication accumulates until you happen to notice it. That is a detection problem, not a judgement problem, which makes it automatable.

---

## 6. You verify against reality, not against the dev server

**[FACT]** Explicit, repeated preference for real-environment verification:

- Playwright runs against `next build && next start`, deliberately, because `next dev` "doesn't replicate ISR/static-page caching"
- Lighthouse CI runs against the same real production server across 6 specific routes, with thresholds set from "real measured scores minus buffer, not round numbers picked blind"
- `e2e/admin-login.spec.ts` sends a **real magic-link email** and reads it back from the local mail catcher
- `e2e/checkout-flow.spec.ts` creates a **real Stripe test-mode session**
- CI decodes the Supabase JWT payloads to *prove* which role each key carries rather than trusting the field names
- Integration tests run against a real disposable Postgres in CI

**[FACT]** And the honest counterweight, from your own CI comments: *"not independently re-verified against a real run (no Docker on the machine this was written on either)"*.

**[INFERENCE]** You hold a high verification bar but your local machine can't meet it — no Docker, Windows-specific bugs — so verification is displaced into CI, which makes your feedback loop slow and makes "I verified this" ambiguous. See report 03 §7.

---

## 7. How you use TypeScript

**[FACT]** Measured, not assumed:

| Repo | LOC (TS/TSX) | `any` | `@ts-ignore` / `@ts-expect-error` | `strict` |
|---|---|---|---|---|
| hotsauce-mama | 24,856 | **0** | 1 (justified, in a test) | true |
| senus-board-report (frontend) | 9,389 | **0** | 0 | true |
| achara-dublin-website | 2,110 | 0 | 0 | true |
| pierogalsWeb | 1,668 | 0 | 0 | true |
| ai-app | 2,293 | 0 | 2 | true |
| loginApplication | 644 | 0 | 0 | true |
| quadWeb | 1,013 | 0 | 0 | true |
| fitnessTracker | 1,320 | 0 | 0 | true |
| invoiceToSheet | 2,068 | 1 | 0 | true |
| kitchenapp | 7,276 | **14** | 0 | (n/a) |

**[FACT]** `unknown` appears 59 times in `hotsauce-mama` — you reach for it deliberately. Generic constraints are written properly: `useServerAction<TArgs extends unknown[]>`.

**[FACT]** All 14 `any`s in `kitchenapp` have one root cause — deserialising untyped JSON:

```ts
const migrated = parsed.map((invoice: any) => ({ … }))
setInvoices(parsed.map((invoice: any) => ({ … })))
```

**[FACT]** In `hotsauce-mama` the same class of problem is solved correctly: `src/lib/validation.ts` (252 lines of Zod, 3rd most-changed file), plus generated `src/types/supabase.ts`.

**[INFERENCE]** You do not have an `any` habit. You had an untyped-deserialisation-boundary problem in one 2025 project, and you have already solved it structurally in your 2026 work. See report 03 §1 for what this means for the skill library.

---

## 8. How you handle errors

**[FACT]** 31 `try` blocks across 24,856 lines in `hotsauce-mama` — sparse and deliberate. Your `CLAUDE.md` documents the rule you derived:

> Any external API call (Stripe, Resend, etc.) that happens *after* a state-changing DB write must have its failure path clean that write up. … When writing a Server Action that reserves/commits something before calling out to a third-party API, ask "what undoes this if the external call fails?" before considering it done.

**[FACT]** The result pattern is uniform and centralised — `ActionResult` + `toastResult` + `useServerAction`, six lines total for the entire success/error branch:

```ts
export function toastResult(result: ActionResult) {
  (result.success ? toast.success : toast.error)(result.message);
}
```

**[FACT]** The counter-pattern, from `invoiceToSheet` (2025), repeated at every route:

```ts
} catch (error) {
  console.error('Export error:', error);
  return NextResponse.json({ success: false, message: 'Failed to export data' }, …);
}
```

**[INFERENCE]** Your mature error philosophy is: *a failure must be distinguishable from an empty result, and a partial write must be undone*. Your immature pattern was: *catch everything, log it, return a generic message*. Report 03 shows that the immature pattern is exactly the root of your most expensive recurring bug class.

---

## 9. How you test

**[FACT]** Test files sit next to source (`storefront.ts` / `storefront.test.ts`), not in a mirrored `__tests__` tree — except in `senus-board-report`'s frontend, which does use `__tests__/`. Both conventions are internally consistent per project.

**[FACT]** Three distinct layers in `hotsauce-mama`, each with a stated job:

- `*.test.ts` — unit/component, Vitest + RTL, run with Supabase deliberately *unconfigured* to exercise null-safe fallbacks
- `*.integration.test.ts` — real disposable Postgres, concurrency and RLS
- `e2e/*.spec.ts` — real production build, real Stripe test session, real magic-link email

**[FACT]** Tests are frequently added *as the regression artefact of a specific incident*: `e2e/csp-static-cache.spec.ts`, PR #158 "unit tests for the three untested admin CRUD Server Actions", PR #105 "component test coverage for the add-to-cart and checkout forms — the core revenue path".

**[FACT]** 7 of 9 Era-2 repos have **zero** tests.

**[INFERENCE]** You test what has hurt you or what is revenue-critical. That is a defensible strategy and I would not try to replace it with a coverage target. But it means the decision "does this need a test" is made ad hoc every time, and in fast projects the answer defaults to no.

---

## 10. How you build UI

**[FACT]** A consistent architecture across all recent projects:

- One source of truth for design tokens — `globals.css` `:root`, mapped through `tailwind.config.ts` to shadcn semantic slots. Your rule: *"no component should ever hardcode a hex/HSL value."*
- shadcn/ui + Radix primitives, `components/ui/` untouched, project components layered above
- A written design brief with named references. `senus`'s AGENTS.md: *"Bloomberg terminal meets Stripe dashboard meets climate analytics platform"*, references "Stripe Dashboard, Linear, Vercel, Bloomberg Terminal (simplified), McKinsey executive decks". `hotsauce-mama`'s CLAUDE.md: *"premium, warm, story-led editorial food brand (think Aesop, Flamingo Estate, Fishwife) — not novelty hot-sauce branding. No flames, skulls, or 'EXTREME HEAT' language anywhere, including in code comments, placeholder copy, or component names."*
- All user-facing copy in a content layer (`ui-text.ts`, `brand.ts`, `constants/`), never inline

**[FACT]** You write repeatable UI runbooks. From `CLAUDE.md`, verbatim heading: *"Repeatable swap-in checklist (run this whenever new/updated label art arrives)"* — five numbered steps.

**[FACT]** `docs/dashboard-review.md` in `senus-board-report` is a standalone UX/architecture review that drove a dashboard resequencing.

**[FACT]** Adaptive-empty-state rules are explicit and recur: *"a category with nothing real to show is omitted, never rendered empty"*, *"renders nothing when the selected period's filing doesn't disclose a full cost breakdown"*, *"a 1-2-dot 'trend' communicates nothing real, so it isn't drawn as one"*.

**[INFERENCE]** You have a real, articulable design practice — brief-first, token-driven, reference-anchored, with strong opinions about honest empty states. The gap is that this practice is re-derived from scratch in each project's AGENTS.md, and there's no step where you compare visual options before committing to code.

---

## 11. How you document

**[FACT]** Four distinct document types, used consistently:

| Type | Example | Purpose |
|---|---|---|
| Agent context | `CLAUDE.md` (49KB), `frontend/AGENTS.md` | Architecture, decisions, incidents, "don't repeat this" |
| Human runbook | `README.md` — "How to add a new product", "How to swap placeholder images for real photography", "Going live: switching from Stripe test mode to real payments", "Manual QA checklist (pre-launch)" | Operating the thing |
| Work record | `frontend/docs/ai-usage/*.md` — **35 files**, one per feature branch | What was investigated, what was built, why |
| Design/architecture review | `docs/dashboard-review.md`, `docs/architecture.md`, `hotsauce-mama-scalability-review.md` | Deliberate whole-system analysis |

**[FACT]** `frontend/CLAUDE.md` in `senus-board-report` contains exactly one line: `@AGENTS.md`. You already solved cross-harness portability.

**[FACT]** The `ai-usage/*.md` files have a stable shape: *Context* → *What was investigated first* → *What was built* → *Why X was not needed*. One of them documents a rejected approach (local Tesseract OCR) with the exact error, the infrastructure cost of proceeding, and the fact that you were consulted before a path was chosen.

**[INFERENCE]** This is the most under-recognised asset in your history. Those 35 files are an *experience corpus* in your own voice, already written, already structured. They are the natural training substrate for the later dreaming layer, and the natural template for a `record-work` skill. They exist in exactly one repo and nothing carries them forward.

---

## 12. Environment constraints that shape everything

**[FACT]** You work on Windows 11 with Git Bash.

- **No Docker locally.** Your CI comments say so twice: *"Runners have Docker + plenty of disk (unlike the machine this was first built on)"*, *"no Docker on the machine this was written on either"*. Integration tests, local Supabase and RLS checks therefore cannot run on your machine.
- **Windows-only library bugs.** `CLAUDE.md`: *"Do not use `next/og`'s `ImageResponse` … as of Next.js 14.2.35 it hit a Windows-only bug in its bundled default font loader (`TypeError: Invalid URL` inside `@vercel/og`) that broke `next build` locally on Windows, even though it built fine in CI/Vercel (Linux)."*
- **Git Bash path mangling.** Issue #223's own title in your repo reads: *"C:/Program Files/Git/admin/customers and get_customer_summaries() are fully unbounded"*. The intended string was `/admin/customers`. Git Bash's MSYS path conversion rewrote a POSIX-looking argument into a Windows path, and it got committed to a GitHub issue title.

**[INFERENCE]** Every external skill library you named assumes macOS or Linux (steipete's is deeply macOS-specific — Xcode, Instruments, Peekaboo, `remote-mac`). Portability for you means Windows-first, and the Git Bash argument-mangling trap alone is worth encoding, because it has already corrupted a real artefact.

---

## 13. Summary of the profile

**[INFERENCE]** Compressed to five sentences:

1. You build Next.js + TypeScript + Postgres product software, at very high agent-assisted velocity, mostly alone.
2. Most of your effort goes into *finding and closing gaps in work already shipped*, via narrow fix branches and periodic whole-system audits.
3. You are unusually good at writing down why — in commits, in CLAUDE.md, in per-branch work records — and unusually inconsistent about turning that writing into a mechanism.
4. Your quality instincts (no `any`, centralise on the third copy, verify against real builds, honest empty states) are already better than any generic rule set would impose.
5. Your bottleneck is not knowledge. It is that knowledge is trapped per-project and gaps are found by luck rather than by sweep.
