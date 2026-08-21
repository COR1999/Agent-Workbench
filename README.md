# Agent-Workbench

Portable engineering knowledge and agent capabilities — a small, evidence-based
skill library an AI coding agent can carry from project to project. Designed from
an archaeology of real repositories (`docs/research/`), not from generic
best-practice lists.

**Scope:** a lessons ledger and nine skills (see the Skills table below).
Deliberately small. See `docs/V0.1_DESIGN_SPECIFICATION.md`
for what is intentionally *not* here and why.

**License:** [MIT](LICENSE).

> The import tooling (`adopt.sh`, installed blocks) uses the internal marker
> prefix `pas` / "personal-agent-system" — the project's original name. Renaming
> that throughout is tracked as an issue; it touches already-adopted projects, so
> it's a deliberate future pass, not a blind find-replace.

> **This repo is private, and not yet safe to publish.** The *lessons* are
> client-safe by design (generic claims, no client names). But the skill test
> fixtures (`skills/*/tests/*.md`) and the `VALIDATION.md` files quote real
> private repositories by name, verbatim source, business logic, and issue/PR
> numbers — that is what makes them trustworthy as validation, and what makes
> them unpublishable as-is. Before any public release, scrub or exclude
> `skills/*/tests/` and `skills/*/VALIDATION.md`. See "Before publishing" below.

## Layout

```
AGENTS.md          hard rules — always true, no conditions
CLAUDE.md          @AGENTS.md
VERSION            the workbench version, stamped into projects on import
CHANGELOG.md       what changed between versions
lessons/           conditional knowledge — true when applies-to matches
templates/         lesson.md, project-AGENTS.md
skills/            nine skills (each SKILL.md; validated ones + VALIDATION.md)
scripts/
  install.sh       machine setup: install skills into the harness skills dirs
  adopt.sh         per-project import (idempotent)
  unadopt.sh       remove the import from a project
docs/
  V0.1_DESIGN_SPECIFICATION.md   the design this was built to
  research/                       the 16-report archaeology it came from
```

## Versioning

- **Semver tags** (`v0.1.0`), not date tags. Skills install once per machine, so
  only one version is ever active — you will never run two projects against
  different workbench versions at once. Versions therefore exist to *communicate
  change and enable rollback*, which semver does and dates don't: a MAJOR bump
  says "a skill's judgement or the import contract changed," a MINOR says "content
  added." See `CHANGELOG.md`.
- **Main branch only.** Solo operator, gated steps — the gates are the safety, not
  branches. Releases are tags on `main`. A `dev` branch would be ceremony.
- **Pinning is zero-cost.** Every project records the version it imported from in
  one line — `## Inherited from personal-agent-system (v0.1.0, imported …)` —
  written by `adopt.sh`. Lessons additionally carry their own `(slug, date)`
  markers. Together these make a future staleness check a `grep`, not a rewrite.

## Tests

```
bash tests/skill-invariants.sh
```

Locks each skill's load-bearing rules so they can't be silently edited out of a
`SKILL.md`. Exit 0 = all held. No build step, no dependencies.

## Working across sessions

Development that spans more than one AI session is tracked as durable memory on
GitHub Issues, not in any one session's context. Start here:

- **[Agent-Workbench development map](../../issues/7)** (`wayfinder:map`) — what's
  done, what's on the frontier, what's blocked, the last decisions. Read it first
  when resuming.
- **[docs/WAYFINDING.md](docs/WAYFINDING.md)** — the model: map + decision
  tickets + fog-of-war, inspired by Matt Pocock's Wayfinder.

## The three-way split

Everything here is one of three things, and keeping them apart is the whole
mechanism of portability:

| | Scope | Where it lives |
|---|---|---|
| **Rule** | Always true, no condition | `AGENTS.md` |
| **Lesson** | True when `applies-to` matches | `lessons/*.md` |
| **Project context** | True only in one repo | that repo's `AGENTS.md` |

If it needs an "if", it is a lesson. If it names a project, it is project
context and does not belong here.

## Lessons

| Lesson | Applies to | Claim |
|---|---|---|
| [check-the-error-not-just-the-data](lessons/check-the-error-not-just-the-data.md) | `supabase` | Read the `error`, or a failure looks identical to an empty result |
| [server-action-is-a-public-endpoint](lessons/server-action-is-a-public-endpoint.md) | `server-actions` | A Server Action is a public POST endpoint; re-validate on the server |
| [compensate-after-external-call](lessons/compensate-after-external-call.md) | `stripe` | An external call after a state-changing write needs a compensating path |
| [next-dev-is-not-production](lessons/next-dev-is-not-production.md) | `nextjs` | `next dev` does not replicate static/ISR caching |
| [next-og-imageresponse-windows](lessons/next-og-imageresponse-windows.md) | `nextjs`, `windows` | ~~`next/og`'s `ImageResponse` breaks `next build` on Windows~~ superseded 2026-08: no longer reproduces on Next 15 |
| [layout-metadata-leaks-to-all-pages](lessons/layout-metadata-leaks-to-all-pages.md) | `nextjs-app-router` | `canonical`/`og:url` in the root layout become every page's canonical; set them per page |
| [stacked-pr-base-deletion-cascade](lessons/stacked-pr-base-deletion-cascade.md) | `github-actions` | Deleting a stacked PR's base branch auto-closes every PR above it and they can't be reopened |
| [shadcn-pin-tailwind-v3](lessons/shadcn-pin-tailwind-v3.md) | `shadcn`, `tailwind-v3` | Pin the shadcn CLI; `@latest` emits Tailwind-v4-only CSS |
| [vitest-fork-timeout-windows](lessons/vitest-fork-timeout-windows.md) | `vitest`, `windows` | vitest's forks pool can hang on Windows; use `--no-file-parallelism` |

Writing a new one: `templates/lesson.md`. It carries the four-part test and the
closed `applies-to` vocabulary. Apply the test honestly — the ledger is worth
having only while every entry changes what an agent does.

## Skills

| Skill | Use it | Guarantee |
|---|---|---|
| [sweep-the-class](skills/sweep-the-class/SKILL.md) | After a fix, before calling it done — find sibling instances of the same defect | Never edits; reports an inventory + coverage. Retrospectively validated (10/10 and 2/2 on real history). |
| [deslop](skills/deslop/SKILL.md) | On an AI-generated diff, before committing — strip model noise | Diff-scoped; never removes information, safety, or intent. Gated at 22/22 on real should-not-flag hunks. |
| [capture-lesson](skills/capture-lesson/SKILL.md) | Immediately after something surprises you or costs you time | Applies the four-part test; writes to `lessons/` + updates README. Refuses to write a lesson that fails the test. |
| [handoff](skills/handoff/SKILL.md) | When context is getting long / a session is ending / resuming a fresh session | Writes/reads a tactical handoff so a near-empty session continues without the old conversation. See [docs/CONTEXT-LOOP.md](docs/CONTEXT-LOOP.md). |
| [design-handbook](skills/design-handbook/SKILL.md) | "design/redesign this", "show me what it could look like" | A browsable HTML handbook to approve BEFORE any production code changes. |
| [explain-and-open-pr](skills/explain-and-open-pr/SKILL.md) | "open a PR", "don't let this stack up" | Isolates the change on a clean branch; commits a work record; PR body leads in plain English. |
| [tdd](skills/tdd/SKILL.md) | "use TDD", "write the test first" | The red-green loop and the decisions "use TDD" hides. Methodology, not the whole build. |
| [grilling](skills/grilling/SKILL.md) | Before implementation — "grill this plan", "what am I assuming" | Interviews a plan/spec as a design tree to surface hidden decisions. Interrogates, never builds. |
| [agentic-vocabulary](skills/agentic-vocabulary/SKILL.md) | When an agentic term is unfamiliar/overloaded | Reference glossary — look a term up instead of inventing its meaning. |

Each skill's `VALIDATION.md` records how it was tested against real repository
history. Install with `scripts/install.sh` (once per machine — skills need no
per-project step).

## Installing (once per machine)

```
scripts/install.sh
```

Does two machine-global things (and nothing per-project):

1. Symlinks each skill into `~/.claude/skills` and `~/.agents/skills` (copy
   fallback where symlinks aren't available). Skills are then usable everywhere.
2. Copies the machine-wide **rules** from this repo's `AGENTS.md` into
   `~/.claude/CLAUDE.md`, inside an idempotent managed block, so they load in
   every session. Without this the rules reach no agent. (Copied, not
   `@`-imported, to sidestep absolute-Windows-path resolution.)

Re-run after `git pull` to refresh both. Idempotent — safe to run repeatedly.

## Adopting into a project

```
scripts/adopt.sh /path/to/project
```

Idempotent — safe to re-run after a `git pull` of the workbench. The import
contract:

| | What happens |
|---|---|
| **Detected** | The project's stack, from `package.json` / `tsconfig.json` / source (the closed `applies-to` vocabulary). |
| **Copied into the project** | Nothing as separate files. The managed block is written *into* `AGENTS.md`: the matched lessons, the record-work reminder, and the version marker — between `<!-- pas:start -->` / `<!-- pas:end -->`. |
| **Symlinked** | Nothing per-project. Skills are machine-level (see install). |
| **Added to `AGENTS.md`** | The managed block only. Anything outside the markers is never touched. |
| **`CLAUDE.md`** | Created as `@AGENTS.md` if absent; if it exists without that line, left alone with a note. |
| **Project must already have** | A directory. Git optional. A harness with `~/.claude` or `~/.agents` optional (only skills need it; lessons and rules work from `AGENTS.md` with any agent). |

**Lessons are copied, not referenced** — a reference never goes stale but requires
someone to remember to look, and the whole problem this ledger solves is that
nobody does.

To remove: `scripts/unadopt.sh /path/to/project` strips the managed block and
leaves your own content intact.

### By hand, if you prefer no tooling

1. `cp templates/project-AGENTS.md <project>/AGENTS.md`, fill in the Stack section.
2. `echo '@AGENTS.md' > <project>/CLAUDE.md`
3. Inline the lessons whose `applies-to` values are **all** present, one line each:
   `- **<slug>** (<YYYY-MM>) — <claim>`. Only Stack and Inherited lessons are
   required; other sections fill in as the project teaches you.

## Matching rule

A lesson applies when **every** value in its `applies-to` is detected in the
project. Narrower is better: `[nextjs, windows]` is more useful than `[nextjs]`,
because a lesson that matches everything is a rule and a lesson that matches
nothing is dead weight.

## Staleness

| `status` | Meaning | Action |
|---|---|---|
| `active` | Believed current | Inline freely |
| `unverified-since <version>` | Was true; conditions may have changed | Inline; the text says to re-check |
| `superseded by <slug>` | Proven false or replaced | Never inline. **Never delete** — why it was believed, and what disproved it, is itself the lesson. |

## Before publishing

This repo is currently private. If you ever make it public:

1. **Remove or sanitize `skills/*/tests/*.md`** — they contain verbatim source
   and business logic from private repos.
2. **Remove or sanitize `skills/*/VALIDATION.md`** — they name private repos and
   real issue/PR numbers.
3. **Re-check `docs/research/`** — the archaeology reports reference private repos
   throughout; decide whether they go public or stay in a private branch.
4. The `lessons/`, `templates/`, `scripts/`, `AGENTS.md`, and `SKILL.md` files are
   already client-safe and can be published as-is.

The cleanest split, if you want a public face without losing the validation
evidence: keep a private `main` and publish a `public` branch with steps 1–3
applied. Do not try to scrub in place on the only copy — the real hunks are the
proof the skills work, and you will want them.
