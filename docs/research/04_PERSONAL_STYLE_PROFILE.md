# 04 — Personal Style Profile

Your implicit conventions, measured. This profile has one job: stop a global skill from imposing a style you don't hold, and give `deslop` something concrete to calibrate against.

Everything is tagged **[OBSERVED]** (counted in your code), **[INFERRED]** (my reading), or **[RECOMMENDED]** (my proposal, not your current practice).

---

## 1. Files and naming

**[OBSERVED]**

- **Files:** `kebab-case.tsx` / `kebab-case.ts`, universally. `checkout-order-summary.tsx`, `use-local-storage-state.ts`, `admin-aggregate-rpcs.integration.test.ts`. No `PascalCase.tsx` files anywhere in `hotsauce-mama`.
  - Exception: `senus-board-report`'s frontend and the Era-2 repos use `PascalCase.tsx` for components (`ProjectCard.tsx`, `Dashboard.tsx`). **Per-project, internally consistent.**
- **Exports:** `export function ComponentName()` — 74 occurrences. `export const X = () =>` — **0**. You do not use arrow-function components.
- **Default exports** only where a framework requires them (Next.js `page.tsx`, `layout.tsx`, `route.ts`).
- **Tests:** colocated, `x.test.ts` beside `x.ts`. Integration tests get an explicit `.integration.test.ts` infix. Playwright specs live in a top-level `e2e/` with `.spec.ts`.
- **Hooks:** `use-thing.ts` in `src/lib/hooks/`, exporting `useThing`.
- **Branches:** `type/kebab-problem-description`, where the description names the *problem*, not the change.

**[INFERRED]** File naming is a project-level convention you set once and follow exactly, not a global preference. A global skill must read the local convention rather than assume kebab-case.

---

## 2. Directory architecture

**[OBSERVED]** `hotsauce-mama`, which is your most considered layout:

```
src/
  app/           routes only — page.tsx, layout.tsx, route.ts, error.tsx
    actions/     Server Actions, one file per domain (checkout.ts, admin-orders.ts)
    admin/       route group with its own (dashboard) layout
    api/
  components/
    ui/          shadcn primitives — untouched, never edited
    forms/       every form component
    layout/  home/  products/  journal/  brand/  shared/
  content/       ALL copy and data: ui-text.ts, images.ts, products/, journal/
  lib/           domain logic, grouped by concern
    admin/ analytics/ cart/ commerce/ consent/ hooks/ instagram/
    inventory/ monitoring/ orders/ stripe/ supabase/
    + flat single-concern modules: validation.ts, format.ts, rate-limit.ts, csv.ts
  types/         shared types + generated supabase.ts
```

**[OBSERVED]** The same shape appears in `senus-board-report` (`lib/` for shared logic and pure functions, `components/dashboard/` for the feature, `lib/hooks/` for data fetching) and, in miniature, in every Era-2 repo (`components/`, `constants/`, `hooks/`, `lib/`).

**[OBSERVED]** Backend equivalent, `senus/backend`: `app/{api/routes, core, models, schemas, services}` — and when a file grew, you split it into a package rather than growing it: *"split `documents.py` router into a package by concern"*, *"split `financial_metrics_extractor.py` into a mixin package"*.

**[INFERRED]** Your consistent architectural instinct is **separate by concern, and keep the composition layer thin**. From your own AGENTS.md: *"Data-shaping … is delegated to pure functions in `lib/` rather than done inline here."* This is stable enough across projects to encode.

---

## 3. Component size and shape

**[OBSERVED]**

- Largest real source file in `hotsauce-mama` is 252 lines (`validation.ts`). Largest component is 242 (`orders-bulk-actions-bar.tsx`). The only bigger files are generated (`supabase.ts`, 823) or a data table (`ui-text.ts`, 811).
- Median source file is well under 150 lines.
- Big forms are split into named field-group components: `checkout-form.tsx` + `checkout-address-fields.tsx`, `checkout-contact-fields.tsx`, `checkout-fulfillment-field.tsx`, `checkout-marketing-consent-field.tsx`, `checkout-pickup-location-field.tsx`, `checkout-order-summary.tsx`. PR #146 explicitly *"split checkout-form"*.
- Server Components by default; `"use client"` appears only where interaction demands it.

**[INFERRED]** Your ceiling is roughly 250 lines before you split, and you split along *domain* seams (address, contact, fulfilment), not arbitrary line counts.

---

## 4. Comments — the most important section for deslop

**[OBSERVED]** ~2,463 comment lines against 24,856 total in `hotsauce-mama` — around 10%, which is high. But of a very particular kind.

Your comments do four jobs, and essentially only these four:

**(a) Provenance — where this came from and what it replaced**
```ts
/** Inverse of eurCentsToEuroString — was duplicated across edit-price-form.tsx,
    edit-shipping-zone-rate-form.tsx, and admin-shipping-zones.ts before being
    centralized here. */
```

**(b) Incident history — what went wrong here before**
```yaml
# Pinned rather than "latest" -- resolving "latest" makes this action call
# GitHub's release API on every run, which hit a rate limit and failed CI
# outright (2026-07-17) for a reason completely unrelated to the PR being
# tested. A pinned version skips that lookup entirely.
```

**(c) Consequence — why the obvious alternative is wrong**
```ts
// A genuine query failure must not look like "no stockists nearby" (#250)
// — this backs the public /find-us page, so a silent failure could read
// to a customer as "not sold anywhere" rather than a real outage.
```

**(d) Suppression justification**
```ts
// eslint-disable-next-line @next/next/no-img-element -- Meta's official pixel
// fallback requires a plain <img>, not next/image (no optimization applies to
// a 1x1 tracking pixel).
```

**[OBSERVED]** What is essentially absent from `hotsauce-mama` and `senus`: comments restating the next line. Only 5 narrating-comment matches in 24,856 lines.

**[OBSERVED]** What slop looks like in *your* code, from Era-2 repos:

- Section labels restating code — `// Add security headers`, `// Prevent clickjacking`, `// Validate file type`, `// Process PDF`
- Banner headers — `/** APPLICATION CONSTANTS / Centralized location for all app configuration values */`
- Tutorial voice explaining a general concept — `// This prevents "magic numbers" scattered throughout the code`
- Commented-out generator scaffold left in place (~15 lines in `playwright.config.ts`)
- Aspirational TODO-in-prose — `// Mock email service for demonstration / In production, you'd use a service like SendGrid, Mailgun, or AWS SES`

**[INFERRED]** The discriminator is sharp and mechanically usable: **a comment that says something the code cannot say is yours; a comment that says what the code already says is slop.** Provenance, incidents, consequences and justifications are all in the first category. This is the single most important calibration input for `deslop`, and a generic "remove unnecessary comments" instruction would delete your best documentation.

**[OBSERVED]** Style detail: you frequently use `--` and `—` inside comments as an aside separator, and reference issue numbers inline (`(#250)`, `see issue #155`). Both are load-bearing.

---

## 5. Error handling

**[OBSERVED]**

- 31 `try` blocks in 24,856 lines. Deliberate, not reflexive.
- `try/catch` is used specifically for **compensating actions**, not for logging: wrap an external call that follows a state-changing write, and undo the write on failure (`cancelPendingOrderAndReleaseStock`).
- Read paths **throw** on a genuine query error rather than returning empty — the fix pattern established across PRs #245/#249/#252:
  ```ts
  if (error) {
    throw new Error(`Failed to load stockists: ${error.message}`);
  }
  ```
- Writes return a discriminated `ActionResult`, surfaced through one shared function:
  ```ts
  export function toastResult(result: ActionResult) {
    (result.success ? toast.success : toast.error)(result.message);
  }
  ```
- Null-safety at config boundaries is a deliberate pattern: `isSupabaseConfigured()` guards, so unit tests can run without a database.

**[INFERRED]** Your rule, stated as you'd state it: *never let a failure be indistinguishable from an empty or successful result, and never leave a partial write behind.* This is a genuine, hard-won principle and it should be a **rule in AGENTS.md**, not a skill.

---

## 6. TypeScript

**[OBSERVED]**

- `strict: true` everywhere. Zero `any` in your two serious projects. 59 uses of `unknown`.
- Explicit return types on exported functions (`function formatEurCents(cents: number): string`).
- Generics used with real constraints: `useServerAction<TArgs extends unknown[]>`.
- Discriminated unions for results (`ActionResult`), and a shared `src/types/` directory.
- Database types generated, not hand-written (`src/types/supabase.ts`).
- Runtime validation via Zod, kept in one place (`src/lib/validation.ts`), and deliberately *separate* schemas for form shape versus action input.
- Domain values kept in their base unit and converted at the edges (`price_eur_cents`, `formatEurCents`, `euroStringToEurCents`).

**[INFERRED]** You treat the type system as a design tool, not a formality, and you already distinguish "compile-time shape" from "runtime trust". There is nothing for a TypeScript-hygiene skill to add.

---

## 7. Content, copy and configuration

**[OBSERVED]** The strongest single convention in your work:

- **No user-facing string is written inline.** `src/content/ui-text.ts` is 811 lines and the most-modified file in the repo (43 changes). PR #208 exists purely to fix strings that bypassed it.
- **No colour is written inline.** `globals.css` `:root` is the sole source; `tailwind.config.ts` maps it. Your rule: *"no component should ever hardcode a hex/HSL value."*
- **No image path is written inline.** `src/content/images.ts` maps every slot, with per-slot `isPlaceholder` tracking.
- **No magic number is written inline.** `src/lib/constants.ts`; `pierogalsWeb` has a commit literally titled "extract magic numbers to constants".
- Adding a product or journal post is a content-file operation with no component changes — stated in `CLAUDE.md` as *"the load-bearing pattern of the whole site"*.

**[INFERRED]** This is your most distinctive architectural signature, it's consistent across projects and eras, and any skill that generates UI must respect it or it will produce code you immediately have to refactor.

---

## 8. Git and GitHub

**[OBSERVED]**

- `feature/* → main-dev → main`, never direct to main, enforced by CI.
- One PR per problem; commit messages within a branch are logically scoped, not one giant commit (stated explicitly in `CLAUDE.md`).
- Subject lines: sentence case, imperative, no strict Conventional Commits — `Add`, `Fix`, `Extract`, `Document`, `Wire`, `Move`, `Make`. A minority use `feat(admin):` / `fix(e2e):`. **Mixed, and you seem comfortable with that.**
- Commit bodies are post-mortems: how found → root cause → mechanism → verification → cross-references.
- Issues are a findings ledger with a 21-label taxonomy, closed by PR title (`closes #250`).

**[INFERRED]** Your commit-body standard is genuinely unusual and worth preserving explicitly, because an agent's default is a one-line subject and no body.

---

## 9. Testing

**[OBSERVED]** Three named layers with different jobs (unit with Supabase deliberately unconfigured; integration against real Postgres in CI; e2e against a real production build with real Stripe/email). Tests are written as the durable artefact of a specific incident, or for the revenue path, rather than to hit coverage.

**[INFERRED]** Your implicit test-selection rule is: *test what has already broken, and test what takes money.* I would encode that as a rule rather than replace it.

---

## 10. UI and design

**[OBSERVED]**

- shadcn/ui New York + Radix, pinned to `shadcn@2.10.0`; `components/ui/` is never hand-edited.
- Tailwind utility classes inline; `tailwind-merge` + `clsx` + `class-variance-authority` for variants; `prettier-plugin-tailwindcss` for class ordering.
- Design briefs are written down with named external references before building.
- Strong, repeated opinions about honest empty states: omit rather than render empty, don't draw a trend from two points, render nothing when the data isn't disclosed.
- Accessibility treated as correctness, not polish — a11y issues carry the `accessibility` label alongside `bug`.
- Motion respects `prefers-reduced-motion` globally.

---

## 11. Dependencies

**[OBSERVED]**

- Small, deliberate dependency set. In `hotsauce-mama`, 30 runtime deps, almost all either Radix primitives or a named service SDK.
- You pin when a "latest" bit you, and you write down why (`shadcn@2.10.0`, `supabase/setup-cli@2.109.1`, `eslint-config-next` exact).
- You use `overrides` to patch transitive CVEs (`sharp`, `postcss`) rather than waiting upstream.
- You upgrade majors deliberately and in one PR with a stated reason (#110: Next 14→16, React 18→19, ESLint 8→9, "fixing high-severity CVEs").
- You explicitly reject options and record why: `next-mdx-remote/rsc` *"not `@next/mdx`, not Contentlayer"*; no `next/og` `ImageResponse`.

**[INFERRED]** Recording the rejected alternative is a habit worth making explicit in the library — it's the thing that stops a future session re-litigating a settled decision.

---

## 12. Prose style

**[OBSERVED]** In READMEs, CLAUDE.md, commit bodies and audit documents:

- Long-form, dense, technical. Full paragraphs, not bullet soup.
- Heavy em-dash use for asides. Frequent parenthetical qualification.
- Explicit uncertainty markers — *"not independently re-verified against a real run"*, *"treat it as provisional if it's ever load-bearing"*, *"not re-verified against 16.2.10"*.
- Time-stamped incidents — *"found the hard way (2026-07-22)"*, *"as of 2026-08-06"*.
- Cross-references to git history as the source of truth — *"see git history around 2026-07-23 for why"*.
- Second-person imperative when writing rules for a future session — *"don't repeat them"*, *"do not run `npx shadcn@latest`"*.

**[INFERRED]** You write for a future reader who has forgotten everything, which is exactly the right instinct for agent context. Note that poteto's `unslop` skill bans em dashes outright — adopting it unmodified would fight your natural voice for no benefit.

---

## 13. What you do *not* do

**[OBSERVED]** Absences are as informative as presences. In your recent work I found no:

- `any` or type suppressions used for convenience
- speculative abstraction or unused generality
- deep nesting (early returns and guard clauses are the norm)
- barrel `index.ts` re-export files
- classes in TypeScript (functions and hooks only)
- global state libraries (Context + hooks only; no Redux/Zustand/Jotai)
- ORM in the TS stack (Supabase client + hand-written SQL migrations and RPCs)
- inline user-facing strings, colours, or magic numbers
- commented-out code in the serious projects

**[INFERRED]** Skills should be built assuming these absences hold, and `deslop` should treat their *appearance* in a diff as the signal — a barrel file, a class, an inline hex, a Zustand store or a commented-out block appearing in your codebase is slop by definition, because you never write them.

---

## 14. [RECOMMENDED] The style profile as a machine-readable artefact

**[RECOMMENDATION]** Rather than a `profiles/*.yml` tree (report 14 argues against that), keep this as **one short markdown file per project**, generated once and edited by hand — `.agent/style.md` or a section in `AGENTS.md`. It needs to answer only what a global skill can't guess:

```markdown
## Local style (for deslop and code-gen)

- Files: kebab-case. Components: `export function`, never arrow consts.
- Comments earn their place by saying what code can't: provenance, incidents,
  consequences, suppression justifications. Delete anything that restates code.
- User-facing strings -> src/content/ui-text.ts. Colours -> globals.css :root.
  Numbers -> src/lib/constants.ts. Never inline.
- try/catch is for compensating a partial write, not for logging.
  Read failures throw. Write failures return ActionResult.
- Extract on the third copy, and record the three call sites in the doc comment.
- Never: barrel files, classes, arrow-function components, global state libs.
```

That is roughly the whole profile, it fits in an agent's context for free, and it's the input a project-calibrated `deslop` actually needs.
