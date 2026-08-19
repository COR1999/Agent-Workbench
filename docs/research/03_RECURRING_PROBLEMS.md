# 03 — Recurring Problems

Ranked by evidence weight, with root-cause analysis. This is the report that should drive the skill library.

---

## The TypeScript premise does not hold

You asked me to investigate unnecessary `any`, unsafe casts, ignored TS errors and weak types, and said you care strongly about this.

**[FACT]** Measured across ten repositories:

- `hotsauce-mama`: **0** occurrences of `any` in 24,856 lines. One `@ts-expect-error`, in a test, annotated: *"deliberately sending a malformed/incomplete address, as a direct Server Action call could"*.
- `senus-board-report` frontend: **0** occurrences in 9,389 lines. Zero suppressions.
- 6 of the remaining 8 TS repos: **0**.
- `invoiceToSheet`: 1.
- `kitchenapp`: 14 — all of one kind (below).
- `strict: true` in every `tsconfig.json` inspected.
- 8 ESLint suppressions in `hotsauce-mama`, of which 5 are `react-hooks/exhaustive-deps` and one carries a full justification: *"Meta's official pixel fallback requires a plain `<img>`, not next/image (no optimization applies to a 1x1 tracking pixel)"*.

**[FACT]** All 14 `kitchenapp` `any`s share one root cause — deserialising `localStorage` JSON:

```ts
const migrated = parsed.map((invoice: any) => ({ ... }))
setInvoices(parsed.map((invoice: any) => ({ ... })))
```

Root cause, per your section 8 framing: **data crossing a trust boundary with no runtime schema**. Not laziness, not a missing type — `JSON.parse` legitimately returns `any`, and there was nothing to narrow it against.

**[FACT]** You already fixed this class structurally in your next serious project: `src/lib/validation.ts` (252 lines of Zod, the 3rd most-edited file in `hotsauce-mama`) plus generated `src/types/supabase.ts`.

### [RECOMMENDATION] Do not build a TypeScript-quality or no-`any` skill

The problem you asked about is measurably absent from your code and you have already solved its root cause. A `typescript-quality` skill would spend its life reporting "no findings", which is the fastest way to teach yourself to stop invoking skills.

What *is* worth keeping is the narrow, generalisable form of the real root cause — **untrusted data entering the type system without validation** — which shows up in your history as boundary problems, not `any` problems (§4 below). That belongs in a `boundary-validation` skill, at Tier 2, not Tier 1.

I'd also drop the `any` clause from the deslop skill entirely for your repos. See report 09.

---

## Problem 1 — Silent failure: a real error rendered as a legitimate empty result

**Rank: #1. Highest evidence density in the entire corpus. Two projects, two languages.**

**[FACT]** Evidence:

| Ref | Title |
|---|---|
| Issue #180 | Admin orders queries never check Supabase's error — a failed query looks identical to "no orders match" |
| Issue #250 | Silently swallowed Supabase query/RPC errors across admin + storefront reads (**same class as #180/#249**) |
| PR #249 | Fix Jungle Sauce showing different availability on listing vs. detail page |
| PR #252 | Surface silently-swallowed Supabase errors across **10 read paths** |
| PR #245 | …and silent admin-orders query errors (#180) |
| PR #253 | content-loader resilience |
| Issue #234 | Rate limiter fails open with no visibility into how often |
| Issue #190 | Resend send failures are never checked anywhere — forms report success even when the email silently failed |
| senus | "Fix fabricated-zero metrics shadowing real dashboard data (#40)" |
| senus | "Add adaptive KPI selection so a missing metric falls back, never renders empty (#61)" |
| senus | "Fix five dashboard bugs found live: fallback insights, KPI color, N/A copy…" |

**[FACT]** The clearest single instance, from PR #249's commit body:

> Found live: `getCommerceProductBySlug`'s `get_product_with_stock` RPC had never actually been pushed to either database (a missing `supabase db push`, not a code bug) — the call failed, but since only `data` was read and `error` was ignored, a real failure looked identical to "no commerce row exists yet", silently rendering Jungle Sauce as Coming Soon and hiding Add to Cart for an actually-available, in-stock product. Meanwhile `/products` (a different query path) correctly showed it as Available Now — same product, two different, contradictory answers, depending entirely on which page's silently-swallowed-or-not error path a visitor hit.

That is a customer-facing revenue bug caused by an ignored destructured `error`.

### Root cause analysis

Symptom: errors ignored. Candidate causes, tested against the evidence:

| Candidate cause | Verdict |
|---|---|
| Carelessness | **No.** It recurs in code written carefully enough to have 7-line commit post-mortems. |
| Missing knowledge of the API | **No.** You know Supabase returns `{ data, error }`; you destructure `data` from it. |
| The happy path and the failure path have identical shapes | **Yes.** `data` is `null` both when the query failed and when nothing matched. `(data ?? []).map(...)` is correct-looking code for both. |
| No type-level signal | **Yes, contributing.** `PostgrestResponse` types `data` as nullable regardless of `error`, so `strict` mode never complains. TypeScript cannot help you here. |
| No test asserts the failure path | **Yes, contributing.** PR #252's own commit notes it *"Added fresh test coverage for `getActivePickupLocations`, which had none before."* |
| Absence of monitoring at the time | **Contributing.** Error tracking only landed in PR #240 (`feat/error-tracking-monitoring`), after most of these bugs. |

**[INFERENCE]** The true root cause is a **shape collision at every I/O boundary where "failed" and "empty" are represented identically** — Supabase reads, RPC calls, Resend sends, rate-limit checks, AI extraction results, content loading. It is not specific to Supabase and not specific to TypeScript. `senus-board-report` hits the identical class in Python with Gemini extraction returning zeros.

**[RECOMMENDATION]** This deserves a dedicated Tier 1 skill — `failure-visibility-review` — that sweeps a diff or a module for every place a failure can be mistaken for absence, and that knows your two established remedies: throw and let monitoring see it (public reads), or return a distinguishable `ActionResult` (writes).

---

## Problem 2 — The incomplete sweep: fixed at one call site, missed at nine

**Rank: #2. You have documented this against yourself twice, explicitly.**

**[FACT]** Direct evidence, in your own words:

- Issue #192: *"list-customers.ts and analytics.ts **still do the unbounded full-table-scan closed issue #121 said was fixed**"*
- Issue #250: *"…(same class as #180/#249)"*
- Issue #131: *"`check_rate_limit()` PUBLIC-revoke fix (PR #127) **doesn't work as intended**"*
- PR #171: *"Add missing `requireAdmin()` check on **3 admin pages**"*
- PR #252: *"Surface silently-swallowed Supabase errors across **10 read paths**"*
- PR #206: *"Centralize the email sign-off into brand.ts instead of **3 duplicated copies**"*
- PR #76: *"Centralize euro↔cents conversion, remove **3 duplicated copies**"*
- PR #77: *"Derive cart subtotal/itemCount in CartProvider instead of **3 call sites**"*
- PR #103: *"Extract a shared PageContainer component"* — issue #87 says *"same max-w/padding string repeated in **12 files**"*
- Issue #223 → #121 → #192: the same unbounded-query finding filed three times across two audits

**[FACT]** The `unbounded query` thread alone: #121 (filed) → closed → #192 (still broken) → #223 (filed again by the scalability review) → PR #219 → PR #239 ("follow-through").

### Root cause analysis

| Candidate cause | Verdict |
|---|---|
| Bad memory | No — you cross-reference issue numbers precisely. |
| Scope discipline taken too far | **Partially.** Your `senus` AGENTS.md rule 1 says *"Work in feature-branch scope only. Don't redesign architecture or implement unrelated features."* A same-class sibling in another file reads as "unrelated". |
| No mechanical step between "fix" and "done" | **Primary.** Nothing in your workflow asks "where else does this exact shape appear?" The audits catch it later, at 10× the cost. |
| Agents optimise for the reported instance | **Primary.** An agent given "fix #180" fixes #180. It has no instruction to generalise, and generalising unasked is normally the wrong default. |

**[INFERENCE]** This is your highest-leverage gap. Every instance is cheap to prevent (one grep at fix time) and expensive to discover (a full audit, a re-filed issue, a second PR, and in #249's case a live customer-facing bug). It costs you PRs, issues, and credibility with yourself — three of your issues exist solely because a previous fix was declared complete and wasn't.

**[RECOMMENDATION]** `sweep-the-class` — Tier 1, and I'd argue the single most valuable skill in the whole library. Given a fix just made, characterise the *shape* of the defect, search the codebase for every other instance, and report a complete inventory with a fix/defer decision per site. Its output is a checklist, not automatic edits.

---

## Problem 3 — Render-boundary and caching mismatches in the Next.js App Router

**Rank: #3. Caused your only production outage and your only revert.**

**[FACT]** Evidence:

| Ref | Title |
|---|---|
| PR #35 | Storefront product page not updating after admin activate/price change |
| PR #54 | Admin analytics/customers pages not updating after order status change |
| PR #137 | **URGENT**: CSP blocking Next.js's own hydration scripts (broke admin login site-wide) |
| PR #153 | **Revert** CSP nonce — broke production via a static/ISR caching mismatch |
| PR #218 | Make /products, /products/[slug], /find-us genuinely static/ISR instead of fully dynamic |
| Issue #193 | Public storefront pages are fully dynamic/uncached, **with a code comment incorrectly claiming find-us is static** |
| Issue #221 | Storefront listing and detail pages hit the database twice per view with zero caching |
| Issue #226 | No cache/CDN layer exists anywhere in front of commerce database reads |
| Issue #155 | Properly scope a strict CSP nonce to dynamic routes only (not static/ISR pages) |
| PR #247 | Scope strict CSP nonce to /admin/* + /api/admin/* only |
| PR #248 | Fix real hydration mismatch around consent-gated MetaPixel rendering |

**[FACT]** Your own summary of the incident, from `CLAUDE.md`:

> added after a CSP nonce shipped broken to production despite passing every `next dev`-based check … Playwright drives an actual `next build && next start` server, which `next dev` doesn't replicate for caching-dependent bugs.

### Root cause analysis

Three distinct sub-causes, all real:

1. **`next dev` is not the runtime.** Static/ISR caching, per-request nonces and hydration timing behave differently in a production build. Your dev loop could not observe the failure mode. **Structurally fixed** — Playwright against a real build.
2. **A route's render mode is implicit and easy to change accidentally.** Reading a cookie or a header anywhere in a tree silently makes the whole route dynamic. Issue #193 records a code comment asserting the opposite of reality — the author believed the route was static.
3. **Per-request values and cached output are fundamentally incompatible**, and nothing in the framework or the type system says so. A CSP nonce baked into a cached page is served to every subsequent visitor. This is what forced the revert.

**[INFERENCE]** Sub-cause 1 is solved. Sub-causes 2 and 3 are not, and they're not solvable by a rule ("use ISR") because the correct answer is per-route. What's needed is an *analysis* capability: given a route, determine its actual render mode, what forces it, whether that's intended, and whether anything per-request leaks into cached output.

**[RECOMMENDATION]** `nextjs-render-boundary` — Tier 2. Not a "Next.js everything" skill; strictly render mode, cache/revalidation, and per-request-value leakage.

---

## Problem 4 — Missing input bounds and validation, found after shipping

**[FACT]** Evidence — an entire cluster of PRs, all filed after the feature was live:

| Ref | Title |
|---|---|
| PR #202 / #197 | Validate stockist `url` as a real URL (rendered as a raw href on the public site) |
| PR #203 / #196 | Add sanity ceilings on admin-entered prices and shipping rates |
| PR #204 / #194 | Cap contact/wholesale field lengths — *unbounded text interpolated straight into email subject lines* |
| PR #209 / #179 | Admin order search breaks silently when a name or email contains a parenthesis |
| PR #210 / #188 | Duplicate `productId` entries in a checkout cart corrupt stock-batch accounting — **exploitable for free product** |
| PR #208 / #183 | Carrier field has no max length |
| PR #125 | Open redirect in admin magic-link callback via unvalidated `next` param (#114) |
| PR #125 | Redirect URLs built from unvalidated client `Host` headers (#115) |
| CLAUDE.md | *"A client-side Zod schema (react-hook-form + zodResolver) is not server-side validation."* |

**[FACT]** Your `CLAUDE.md` heading for this is: **"Server Action conventions — two mistakes already made once, don't repeat them"**, found *"during a security review (2026-07-17) of `startCheckout`, which had both of these at once."*

### Root cause analysis

**[INFERENCE]** The root cause is that a Server Action is a **public POST endpoint that looks like a function call**. Everything about the ergonomics — you import it, you call it with typed arguments, TypeScript checks the call — implies a trusted internal boundary. It isn't one. The form's Zod schema sits on the wrong side. The type signature is a compile-time fiction from the attacker's perspective.

Secondary cause: bounds are invisible by omission. Nothing prompts "what's the maximum length of this field?" — the field simply works.

**[RECOMMENDATION]** `boundary-validation` — Tier 2. Covers the whole class: Server Action re-validation, field bounds/format/uniqueness, redirect/host allow-listing, and untrusted deserialisation (which is where the `kitchenapp` `any`s came from). This is the correct, evidence-derived home for your TypeScript concern.

---

## Problem 5 — Check-then-act races and non-idempotent handlers

**[FACT]** Evidence:

| Ref | Title |
|---|---|
| Issue #81 / PR #101 | Stripe webhook handler is not idempotent — duplicate order emails on event redelivery |
| Issue #122 / PR #149 | Narrow crash-window can orphan a stock reservation with nothing to release it |
| Issue #188 / PR #210 | Duplicate productId corrupts stock-batch accounting |
| Issue #189 / PR #211 | `reserve_stock()` wrongly rejects a real second batch under concurrent checkouts (Postgres `FOR UPDATE` + `LIMIT` interaction) |
| Issue #191 / PR #212 | Webhook payment-confirmation and low-stock dedup guards are **check-then-act, not atomic** |
| PR #66 | Checkout: server-side validation + orphaned stock cleanup on failure |
| PR #242 | Duplicate Purchase conversion event on order-confirmation refresh/revisit |
| Issue #225 | `reserve_stock()`'s row-level lock serialises concurrent purchases of a popular product |
| Migration | `20260722140000_reserve_stock_skip_locked.sql` |

**[FACT]** Your scalability review's own assessment of this area: *"Stock reservation correctness is genuinely well engineered … closes real oversell/orphan races that a naive implementation would hit under concurrency. This is above-average work for a pre-launch project and should not be re-litigated."*

### Root cause analysis

**[INFERENCE]** Not a knowledge gap — you demonstrably understand `for update skip locked` and idempotency keys. The root cause is that **correct-under-concurrency is invisible in single-threaded reading and untested by default**. `if (!alreadySent) { send() }` reads as obviously correct. It is only wrong at the moment two webhook redeliveries interleave, which no unit test produces unless someone deliberately writes one. You did eventually write them: `src/lib/orders/stock-reservation.integration.test.ts`, `admin-aggregate-rpcs.integration.test.ts` — against a real Postgres, in CI, because you can't run Docker locally.

**[RECOMMENDATION]** `concurrency-correctness-review` — Tier 3. Narrow, high-value, only relevant to a subset of your work (webhooks, inventory, payments), but that subset is the revenue path. Deliberately Tier 3 rather than Tier 1 because it applies to few files, not because it's low value.

---

## Problem 6 — Third-party script integration in the App Router

**[FACT]** Evidence — seven PRs on essentially one feature:

| Ref | Title |
|---|---|
| PR #169 | Live production bug: Meta Pixel throws `ReferenceError: fbq is not defined` |
| PR #173 / #184 | PageView never fired on client-side navigation |
| PR #213 / #187 | Track query-string-only navigation, not just pathname changes |
| PR #176 | CSP blocks Meta Pixel's form/iframe fallback delivery |
| PR #242 | Duplicate Purchase conversion event on refresh/revisit |
| PR #248 | Hydration mismatch around consent-gated MetaPixel rendering |
| Issue #185 | No regression coverage for the consent-rejected path |

**[INFERENCE]** Four independent constraints intersect on one component and no single mental model covers all of them: (1) SPA route changes don't fire the script's page-load hooks; (2) CSP must allow the script *and* its fallback delivery paths; (3) consent gating changes what renders, which collides with hydration; (4) analytics events must be idempotent per user action. Each of your seven PRs fixed one of the four and revealed another.

**[RECOMMENDATION]** `third-party-script-integration` — Tier 2. Cross-project value is real: you wired GA4 + Meta Pixel here, Instagram's Graph API here, Gemini in two projects, Stripe, Resend. The checklist generalises past pixels.

---

## Problem 7 — Local environment cannot verify what production does

**[FACT]** Evidence:

- No Docker on your machine — stated twice in CI comments. Integration tests, local Supabase, RLS checks are CI-only.
- `next/og`'s `ImageResponse` breaks `next build` on Windows only; works in CI/Vercel.
- The CSP incident: passed every `next dev` check, broke production.
- CI env-scoping breakage: *"found the hard way — see git history on `.github/workflows/ci.yml` around 2026-07-21 for the exact breakage this caused the first time"* — unit tests need Supabase *unconfigured*, e2e needs it configured, and job-wide `$GITHUB_ENV` broke that.
- senus: *"Fix two real CI-only failures caught by the new GitHub Actions workflow"*.
- Git Bash MSYS path conversion rewrote `/admin/customers` into `C:/Program Files/Git/admin/customers` **inside a committed GitHub issue title** (#223).
- Multiple CI comments admit a step was *"not independently re-verified against a real run"*.

**[INFERENCE]** Your verification bar is high but your local loop can't meet it, so "done" is ambiguous until CI runs. This makes every claim of completion probabilistic and pushes discovery late. It also means an agent working with you will confidently report success on work it could not actually verify.

**[RECOMMENDATION]** `verify-for-real` — Tier 2. Before claiming done: state what was actually executed versus assumed, what the environment could not check, and what the production-parity check would be. Plus a hard rule about POSIX-looking arguments in Git Bash (see report 13).

---

## Problem 8 — Duplication accumulating until noticed

**[FACT]** Covered in report 02 §5. Seven consecutive refactor PRs (#70–#77), plus #103 (12 files), #206 (3 copies), #207 (a duplicate unused image slot), #208 (strings bypassing `ui-text.ts`). Present in every era and every project, including one-commit ones (`pierogalsWeb`: "extract magic numbers to constants").

**[INFERENCE]** Your extraction judgement is good; your detection is manual and late. That's the automatable half.

**[RECOMMENDATION]** `extract-duplication` — Tier 2. Must respect your rule-of-three calibration and your provenance-comment convention (*"was duplicated across X, Y, Z before being centralized here"*), and must not extract on the second occurrence.

---

## Problem 9 — Accessibility fixed in single-instance micro-PRs

**[FACT]** Seven separate PRs, each fixing one thing:

| PR | Fix |
|---|---|
| #44 | Descriptive `aria-label` on homepage Learn More link |
| #95 | Accessible labels on cart/add-to-cart quantity inputs |
| #96 | Skip-to-content link |
| #98 | `prefers-reduced-motion` |
| #104 | Borderline WCAG AA contrast on footer text |
| #159 | Descriptive featured-product link text |
| #205 | Accessible names on admin sort/bulk-status dropdowns |

**[INFERENCE]** A textbook instance of Problem 2 applied to a11y. Three of these seven (unlabelled inputs, non-descriptive link text, unnamed dropdowns) are the same defect shape in different components. They were found one at a time, by Lighthouse or by eye, and fixed one at a time.

**[RECOMMENDATION]** Not its own Tier 1 skill. This is `sweep-the-class` applied to a11y plus a Lighthouse CI gate you already have. An `a11y-sweep` skill sits at Tier 3.

---

## Problem 10 — AI code slop, concentrated in fast unreviewed work

**[FACT]** Slop-signature scan across all repos (narrating comments / `console.log` / `catch` blocks):

| Repo | Narrating comments | `console.log` | `catch` |
|---|---|---|---|
| invoiceToSheet | 11 | 35 | 23 |
| kitchenapp | 10 | 21 | 25 |
| fitnessTracker | 15 | 0 | 0 |
| foodGen | 3 | 7 | 10 |
| **hotsauce-mama** | **5** | **6** | **20** |
| **senus-board-report** | **2** | **0** | **20** |
| achara / quadWeb / pierogals / loginApplication / ai-app | 0–2 | 0–1 | 0–1 |

**[FACT]** Concrete samples. `invoiceToSheet/middleware.ts`:

```ts
// Add security headers
// Prevent clickjacking
// Prevent MIME type sniffing
// Enable XSS protection
// Referrer policy
```

`fitnessTracker/constants.ts` — banner comments in a tutorial voice:

```ts
/**
 * APPLICATION CONSTANTS
 * Centralized location for all app configuration values
 * This prevents "magic numbers" scattered throughout the code
 */
```

`fitnessTracker/my-app/playwright.config.ts` — ~15 lines of commented-out generator scaffold left in place.

`invoiceToSheet` — the same block at every route:

```ts
} catch (error) {
  console.error('Export error:', error);
  return NextResponse.json({ success: false, message: 'Failed to export data' }, ...);
}
```

**[FACT]** Contrast with `hotsauce-mama`'s actual comment style, which is provenance and rationale:

```ts
/** Inverse of eurCentsToEuroString — was duplicated across edit-price-form.tsx,
    edit-shipping-zone-rate-form.tsx, and admin-shipping-zones.ts before being
    centralized here. */
```

```ts
// A genuine query failure must not look like "no stockists nearby" (#250)
// — this backs the public /find-us page, so a silent failure could read
// to a customer as "not sold anywhere" rather than a real outage.
```

### The connection that matters

**[INFERENCE]** The `invoiceToSheet` catch-and-log-and-return-generic block is *literally the same pattern* as Problem 1, your #1 production bug class. In 2025 it read as harmless boilerplate. In 2026 it cost you a customer-facing revenue bug and five PRs.

So: **deslop and failure-visibility are the same problem seen from two ends.** A deslop skill that simply deletes defensive `try/catch` — which is what the reference implementation says to do — would strip the only thing standing between you and an unhandled crash, without replacing it with a distinguishable failure. That is a net negative for you. See report 09.

---

## Ranked summary

| # | Problem | Evidence weight | Cost when it hits | Automatable? |
|---|---|---|---|---|
| 1 | Silent failure (error looks like empty) | 11 refs, 2 projects, 2 languages | Customer-facing revenue bug | **High** |
| 2 | Incomplete sweep across call sites | 10 refs, 3 self-documented recurrences | Re-filed issues, duplicate PRs, live bug | **High** |
| 3 | Render-boundary / caching mismatch | 11 refs | Production outage + a revert | Medium |
| 4 | Missing input bounds/validation | 9 refs | Exploitable stock corruption, open redirect | **High** |
| 5 | Check-then-act races / idempotency | 9 refs | Duplicate emails, oversell risk | Medium |
| 6 | Third-party script integration | 7 refs | Live JS error, lost analytics | Medium |
| 7 | Local env can't verify production | 7 refs | False "done", late discovery | Medium |
| 8 | Duplication accumulating unnoticed | 12+ refs, every era | Refactor debt, drift | **High** |
| 9 | A11y found one instance at a time | 7 refs | Slow, repeated | **High** (via #2) |
| 10 | AI slop in fast unreviewed work | measured, era-2 concentrated | Becomes problem #1 later | **High** |
| — | `any` / lazy TypeScript | **0 in 34k+ LOC** | — | N/A — not a problem |

**[INFERENCE]** Problems 1, 2, 4, 8, 9 and 10 are all fundamentally *the same meta-problem*: **defects of a known shape exist in more than one place, and you find them one at a time.** That is why `sweep-the-class` is the highest-leverage single capability in this whole design.
