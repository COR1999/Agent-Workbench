# 01 — GitHub Archaeology

**Account:** `COR1999` (Cian, Dublin, cianorourke.com), joined 2019-04-02, 39 public repos + private.
**Analysis date:** 2026-08-19.
**Method:** full `git log` / `gh pr list` / `gh issue list` over the live repos, plus source-level scans. Ten repos cloned and read. `hotsauce-mama` read locally at depth.

---

## 1. What was analysed

| Repo | Visibility | Primary lang | Commits | PRs | Issues | Depth |
|---|---|---|---|---|---|---|
| **hotsauce-mama** | private | TypeScript | 474 | 156 | 100 | **Deep** — full history, all PR/issue titles, source, CI, CLAUDE.md |
| **senus-board-report** | public | Python + TS | 179 | ~67 | — | **Deep** — full history, source, AGENTS.md, docs |
| kitchenapp | public | TypeScript | 16 | 0 | — | Source scan |
| invoiceToSheet | public | TypeScript | 1 | 0 | — | Source scan |
| fitnessTracker | public | TypeScript | 52 | 0 | — | Source scan |
| ai-app (portfolio) | public | TypeScript | ~12 | 0 | — | Source scan |
| achara-dublin-website | public | TypeScript | 5 | 0 | — | Source scan |
| pierogalsWeb | public | TypeScript | 6 | 0 | — | Source scan |
| quadWeb | public | TypeScript | 3 | 0 | — | Source scan |
| loginApplication | public | TypeScript | 9 | 0 | — | Source scan |
| foodGen | public | Python + TS | 10 | 0 | — | Source scan |
| gscWeb | public | TypeScript | 10 | 0 | — | Metadata only |
| boutique_ado_v1 | private | HTML/Python | 100+ | 0 | — | Commit log only (2020 Django bootcamp) |
| covid_case, WikiMusic, Spotify-api-website, Vinyl-ORourke, CS50-Website, WeatherApp, … | mixed | HTML/JS/Python | small | 0 | — | Metadata only (2019–2020) |
| Forks (NativeScript, dyad, simple-icons, sdg_hub, first-contributions) | — | — | — | — | — | Excluded — no authored work |

**[FACT]** Two repos contain the overwhelming majority of your real engineering signal: `hotsauce-mama` and `senus-board-report`. Everything else is either pre-2021 learning work or a fast single-purpose build. I weighted the analysis accordingly, per your instruction.

---

## 2. The three eras

### Era 1 — Bootcamp / learning (2019-04 → 2021)

**[FACT]** `CS50-Website`, `Vinyl-ORourke`, `Spotify-api-website`, `WikiMusic`, `boutique_ado_v1`, `full-stack-hello-django`, `covid_case`. Stack: HTML/CSS/Bootstrap/jQuery, Flask, Django, MongoDB.

Commit messages from `boutique_ado_v1`:

```
finished stripe videos but cant get the webhook to work on stripes end
 cant get webhooks to work
 added loading overlay
aprofiles -updated webhook handler to handle profiles correctly
```

**[FACT]** Single branch, direct to main, no PRs, no tests, no CI. Messages record *what was attempted*, not what was decided.

### Era 2 — Fast solo Next.js builds (2025-07 → 2025-11)

**[FACT]** `ai-app`, `kitchenapp`, `fitnessTracker`, `achara-dublin-website`, `quadWeb`, `gscWeb`, `pierogalsWeb`, `invoiceToSheet`, `loginApplication`. A near-identical stack every time: **Next.js App Router + TypeScript (`strict: true`) + Tailwind + Vercel**.

**[FACT]** 3–52 commits each, single branch, direct to main, no PRs, **zero test files in 7 of 9**, informal messages with typos:

```
added funcationality for hand written invoice and filter option for invoice
tidyed uo rerouting and added useAuth.ts hook
refactored alot of code for reuseablity and restyles the page
 centralised css props and elimated css duplicate
```

**[FACT]** Several are real client or commercial pitches: `achara-dublin-website` ("Modern restaurant website for Achara Dublin"), `quadWeb` ("basic website to show to customer"), `pierogalsWeb`, `gscWeb`.

### Era 3 — Agent-assisted professional engineering (2026-06 → present)

**[FACT]** `senus-board-report` (2026-07-02 → 07-09) and `hotsauce-mama` (2026-07-14 → 07-24, still open).

The change is not gradual. It is a step function.

| Dimension | Era 2 | Era 3 (hotsauce-mama) |
|---|---|---|
| Branching | direct to main | `feature/*` → `main-dev` → `main`, enforced by CI |
| PRs | 0 | 156, 154 merged |
| Issues | 0 | 100, with a 21-label taxonomy |
| Tests | 0–1 files | 60+ unit/integration + 5 Playwright e2e |
| CI | none | lint, typecheck, test, build, e2e on real prod build, Lighthouse, RLS assertion |
| Commit bodies | 0 lines | 3,280 lines over 461 commits (~7 lines/commit) |
| Project memory | README | 49KB `CLAUDE.md` with incident history |

**[FACT]** `hotsauce-mama` produced 474 commits, 156 PRs and 100 issues in **10 calendar days** (2026-07-14 → 2026-07-24). Peak: 112 commits on 2026-07-17.

**[INFERENCE]** This velocity is only reachable with heavy agent assistance, and your history reads as someone who worked out — fast, and largely alone — how to keep quality from collapsing under that velocity. Most of the recurring problems in report 03 are *consequences of that velocity*, not of inexperience.

---

## 3. Technologies actually observed

**[FACT]** Ranked by evidence weight, not by your portfolio's self-description.

**Core, in every recent project:**

- TypeScript, `strict: true` in every `tsconfig.json` checked (9/9)
- Next.js App Router (14 → 16), React 18 → 19
- Tailwind CSS v3, pinned deliberately
- shadcn/ui + Radix primitives, pinned to `shadcn@2.10.0` with a written reason
- Vercel

**Load-bearing in hotsauce-mama:**

- Supabase (Postgres + Auth + **Row Level Security**), 29 hand-written SQL migrations including PL/pgSQL functions using `for update skip locked`
- Stripe (checkout sessions, webhooks, refunds, promotion codes)
- Resend (transactional + audience email)
- Zod (`src/lib/validation.ts`, 252 lines, 3rd most-changed file)
- Vitest + React Testing Library, Playwright, Lighthouse CI, Sentry
- GA4 + Meta Pixel, `vanilla-cookieconsent`

**Load-bearing in senus-board-report:**

- FastAPI + SQLAlchemy + Pydantic, pytest (25 test modules)
- Google Gemini (text + vision), PyMuPDF
- Recharts
- Railway (backend) + Vercel (frontend)

**[FACT]** Present but dormant: Django, Flask, MongoDB, jQuery, Bootstrap — all pre-2021. Firebase appears once (`loginApplication`, 2025-11).

**[INFERENCE]** Your real surface area for skill design is **Next.js App Router + TypeScript + Postgres-with-RLS + third-party API integration + Vercel**. Python/FastAPI is a genuine but secondary track. Everything else is CV breadth, not working context.

---

## 4. What the PR corpus says you spend time on

**[FACT]** 156 PRs in `hotsauce-mama`, classified by branch prefix:

| Prefix | Count | Share |
|---|---|---|
| `fix/` | 50 | 32% |
| `feature/` + `feat/` | 38 | 24% |
| `main-dev` (release merges) | 26 | 17% |
| `refactor/` | 8 | 5% |
| `chore/` | 6 | 4% |
| `ci/` | 5 | 3% |
| `docs/` | 5 | 3% |
| `security/` | 3 | 2% |
| `perf/` | 3 | 2% |
| `seo/` + `content/` | 6 | 4% |
| `test/` + `e2e/` | 3 | 2% |
| `hotfix/`, `audit/`, `polish/` | 3 | 2% |

**[FACT]** Excluding release merges, **fixes outnumber features 50 to 38** — in a project that was ten days old.

**[INFERENCE]** You are not primarily building features. You are primarily finding and closing gaps in features you already built. This is the single most important input to the library design: your highest-value skills are review, audit and sweep skills, not scaffolding skills.

---

## 5. What the issue corpus says

**[FACT]** 100 issues, label distribution:

| Label | Count |
|---|---|
| technical-debt | 36 |
| code-task | 33 |
| bug | 14 |
| before-launch | 11 |
| security | 10 |
| business-decision | 9 |
| performance | 9 |
| database | 7 |
| enhancement | 6 |
| reliability | 5 |
| scalability | 5 |
| accessibility | 5 |
| monitoring / architecture / postal-api / caching / seo / ux / documentation / question / good-first-issue | 1–3 each |

**[FACT]** 24 issues remain open; 9 of those are `business-decision` and blocked on a human, not on code (VAT number, courier pricing, hosting plan, label art choice).

**[INFERENCE]** You use GitHub Issues as a *findings ledger*, not a request queue. Most issues are self-filed from audits. This is unusual and it is a strength — it means a machine-readable record of your recurring problems already exists, which is what made report 03 possible.

---

## 6. Change hot-spots

**[FACT]** Most-modified files across `main` in `hotsauce-mama`:

| Changes | File | What it is |
|---|---|---|
| 43 | `src/content/ui-text.ts` | Centralised UI copy (811 lines) |
| 40 | `CLAUDE.md` | Project memory |
| 20 | `src/lib/validation.ts` | Zod schemas |
| 16 | `package.json` | |
| 15 | `src/app/products/[slug]/page.tsx` | |
| 14 | `src/app/actions/checkout.ts` | |
| 14 | `.github/workflows/ci.yml` | |
| 13 | `src/types/supabase.ts` | Generated DB types |
| 13 | `src/lib/stripe/webhook-handlers.ts` | |
| 13 | `README.md` | Runbooks |

**[FACT]** The two most-edited files in the entire project are a **string table** and a **memory document**. Neither is application logic.

**[INFERENCE]** Two of your highest-frequency activities are threading copy through a centralised content layer, and maintaining written project memory. Both are currently entirely manual.

---

## 7. Confidence

| Claim | Confidence | Basis |
|---|---|---|
| Next.js + TS + Tailwind is your working stack | **Very high** | 9/9 recent repos |
| Fix-work dominates feature-work | **Very high** | 50 vs 38 PRs, counted |
| You run structured audits that produce filed issues | **Very high** | scalability review doc → issues #221–#238 |
| `any` is not a problem in your code | **Very high** | 0 in 24,856 LOC + 0 in 9,389 LOC, scanned |
| Silent failure is your #1 recurring bug class | **High** | 5 PRs, 4 issues, 2 projects, 2 languages |
| The 2026 velocity is agent-assisted | **Medium-high** | inferred from cadence and commit prose, not directly observed |
| Era-2 repos represent "unreviewed" rather than "less skilled" work | **Medium** | inference from the era-3 contrast |
