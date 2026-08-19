# 07 — Personal Skill Tree

Derived from evidence, not from the hypothesis in your section 18.

---

## First: why your proposed tree doesn't fit

Your starting hypothesis was organised by **technology** (TypeScript / React / Next.js) and by **generic activity** (Debugging / Testing / Refactoring). Both axes fail against the evidence:

- **Technology is a constant, not a dimension.** Every recent project is Next.js + TypeScript + Tailwind. A `typescript/` folder and a `nextjs/` folder would contain skills that apply to 100% of your work, which makes them useless for routing — the folder carries no information.
- **Generic activity doesn't match where your time goes.** "Debugging → TypeScript / React / Browser" implies you spend your time chasing type errors and DOM bugs. Report 01 says you spend it on silent failures, incomplete sweeps, cache boundaries, missing bounds, and races. Those don't decompose along technology lines — the silent-failure class appears identically in TypeScript/Supabase and in Python/Gemini.

The organising axis that actually fits your history is **what stage of work the skill serves**, because your PR corpus is overwhelmingly organised that way: find the problem → fix it correctly → prove it → remember it.

---

## The tree

```
PERSONAL SKILL LIBRARY
│
├── FIND ─────────────── locate defects and gaps, deliberately
│   ├── sweep-the-class ................ where else does this defect shape live?      [CORE]
│   ├── audit-to-issues ................ whole-system review on one axis → filed issues [CORE]
│   ├── failure-visibility-review ...... where can a failure look like an empty result? [CORE]
│   ├── extract-duplication ............ where has the same shape reached three copies? [HIGH]
│   ├── debug-from-production-signal ... start from Sentry/Lighthouse/live report      [SPEC]
│   └── a11y-sweep ..................... sweep-the-class with an a11y checklist        [SPEC]
│
├── CHANGE ───────────── make the change well
│   ├── deslop ......................... strip AI slop from the branch diff            [CORE]
│   ├── boundary-validation ............ untrusted input: parse, bound, allow-list     [HIGH]
│   ├── nextjs-render-boundary ......... render mode, caching, per-request leakage     [HIGH]
│   ├── third-party-integration ........ external scripts/APIs: the four constraints   [HIGH]
│   └── concurrency-correctness ........ check-then-act, idempotency, locks            [SPEC]
│
├── DESIGN ───────────── decide what it should look like before building it
│   ├── design-system-recon ............ read tokens, components, copy, brief first    [HIGH]
│   ├── ui-design-exploration .......... 2-4 real HTML directions, then choose         [SPEC]
│   └── (visual-qa) .................... deferred, complexity too high for now         [EXP]
│
├── PROVE ────────────── establish that it actually works
│   ├── verify-for-real ................ executed vs assumed vs unverifiable           [HIGH]
│   └── fix-ci ......................... drive PR checks to green                      [ADOPT]
│
├── REMEMBER ─────────── stop knowledge escaping
│   ├── capture-lesson ................. incident → the strongest artefact that fits   [CORE]
│   ├── record-work .................... per-branch work record                        [HIGH]
│   └── project-onboarding ............. build the working model of an unfamiliar repo [HIGH]
│
├── WRITE ────────────── prose you publish
│   └── prose-deslop ................... strip AI tells, keep your voice               [SPEC]
│
└── META ─────────────── the library maintaining itself
    └── propose-skill-change ........... observe → propose → test → approve            [EXP]
```

**Twenty entries. Five are CORE. That is the whole library for phase one.**

---

## Why these five stages

**[INFERENCE]** Each stage maps to something structurally present in your history:

| Stage | Evidence it exists as a distinct mode |
|---|---|
| FIND | 50 `fix/` PRs, 100 filed issues, a 98KB audit document, PRs literally named `audit/engineering-review` |
| CHANGE | 38 `feature/` + 8 `refactor/` PRs |
| DESIGN | Written design briefs with named references, `docs/dashboard-review.md`, a dedicated redesign branch, HTML proposal documents on your Desktop |
| PROVE | Three test layers, Lighthouse CI, Playwright-against-production-build, JWT-decoding in CI to prove role claims |
| REMEMBER | 49KB `CLAUDE.md`, 35 `ai-usage/*.md`, 3,280 lines of commit body, `AGENTS.md` + `@AGENTS.md` pointer |

**[INFERENCE]** The stage names also make routing natural in conversation. "Where else is this broken" → FIND. "Is this actually done" → PROVE. "Don't lose this" → REMEMBER. Technology names give the router nothing to work with; verbs do.

---

## Directory layout

**[RECOMMENDATION]** Mirror the tree, with mattpocock-style promotion buckets:

```
skills/
  find/
    sweep-the-class/SKILL.md
    audit-to-issues/SKILL.md
    failure-visibility-review/SKILL.md
    extract-duplication/SKILL.md
  change/
    deslop/SKILL.md
    boundary-validation/SKILL.md
    nextjs-render-boundary/SKILL.md
    third-party-integration/SKILL.md
  design/
    design-system-recon/SKILL.md
    ui-design-exploration/SKILL.md
  prove/
    verify-for-real/SKILL.md
  remember/
    capture-lesson/SKILL.md
    record-work/SKILL.md
    project-onboarding/SKILL.md
  write/
    prose-deslop/SKILL.md
  in-progress/          not installed, not routed, public on purpose
  deprecated/           kept for history, never installed
principles/
  encode-lessons-in-structure.md
  boundary-discipline.md
  exhaust-the-design-space.md
  make-operations-idempotent.md
```

**Note:** skill directory names are globally unique regardless of folder, because the installer symlinks them flat into `~/.claude/skills/`. The folders are for *your* navigation and for the README, not for the harness. That's a real constraint, not a preference — plan names accordingly.

---

## Skill dependencies

You asked for REQUIRED / OPTIONAL / RECOMMENDED. My recommendation is to **not encode dependencies in metadata at all** — see report 10 for why. But the real relationships, for your own understanding and for the router, are:

```
sweep-the-class
  └── used by → a11y-sweep, failure-visibility-review, extract-duplication

audit-to-issues
  └── produces → issues, which feed → sweep-the-class, boundary-validation, …

design-system-recon
  └── required before → ui-design-exploration
  └── recommended before → any UI generation

capture-lesson
  └── consumes → output of verify-for-real, debug-from-production-signal, deslop
  └── feeds → propose-skill-change (later)

project-onboarding
  └── recommended before → everything, in an unfamiliar repo

deslop
  └── needs → the local style profile (report 04 §14) and a git base ref
```

**[RECOMMENDATION]** Express these as one sentence of prose inside each SKILL.md ("Run `design-system-recon` first if you haven't read this project's tokens"), not as a `dependencies:` field. A prose link degrades gracefully when the other skill isn't installed. A metadata field either silently does nothing or hard-fails — which is the dependency hell you flagged in section 22.

---

## Three things deliberately absent from this tree

**No `github/` branch.** Your git workflow is a three-line convention plus a CI guard that already exists. Branch/PR/conflict/release skills solve team problems (reviewers, long-lived branches, contested merges) that your history shows you don't have — 154 of 156 PRs self-merged, zero merge-conflict incidents.

**No `testing/` branch.** Not because testing doesn't matter — your test architecture is one of the best things in your repos — but because "write a test" is not a standalone request in your history. It is always the *artefact of something else*: an incident (`csp-static-cache.spec.ts`), a coverage gap found in audit (#91 → PR #105), or a fix that needs a regression guard. So the regression test belongs as a **required output** inside the FIND and CHANGE skills, not as a skill you invoke.

**No `infrastructure/` branch.** One `fix-ci` adopted wholesale. Deployment and environment config are documented per-project in your READMEs and `.env.example`, which is the right home for them.

---

## The tree over time

**[INFERENCE]** Where it should grow, and where it should not:

- **FIND** will grow. Every new recurring defect class you discover adds a sweep. This is healthy — each addition is backed by an incident.
- **CHANGE** should stay small and stack-specific. If you move off Next.js, three of its five entries retire cleanly.
- **REMEMBER** should stay at three. If it grows, the growth belongs in the workflow layer, not here.
- **META** is where the future dreaming layer attaches. One experimental entry now; do not build it out.

The failure mode to watch for is FIND and CHANGE blurring — a "review the diff for X" skill and a "do X correctly" skill collapsing into one. Keep them separate: FIND skills produce **inventories and decisions**, CHANGE skills produce **edits**. That distinction is also what keeps guardrails enforceable.
