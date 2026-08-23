# Agent-Workbench

Portable engineering knowledge and agent capabilities — a small, evidence-based
skill library an AI coding agent can carry from project to project. Designed from
an archaeology of real repositories — its conclusions are distilled in
`docs/V0.1_DESIGN_SPECIFICATION.md` — not from generic best-practice lists.

**Scope:** a lessons ledger and three skills (`sweep-the-class`, `deslop`,
`capture-lesson`). Deliberately small. See `docs/V0.1_DESIGN_SPECIFICATION.md`
for what is intentionally *not* here and why.

**License:** [MIT](LICENSE).

> **This repo is public and sanitized for publication.** The *lessons* are
> client-safe by design (generic claims, no client names). The skill test
> fixtures (`skills/*/tests/*.md`) and `VALIDATION.md` files still quote real
> repository history — that is what makes them trustworthy as validation — but
> every source is anonymized or genericized: no client names, brands, or private
> issue/PR numbers. `scripts/preflight-public.sh` enforces this mechanically.
> See "Sanitization policy" below.

## Working here (for the agent)

If you are an AI agent operating in this repo, this is what it is *for* and how
its loop works — read this before defaulting to your own habits.

**Purpose.** This is a *carry-along toolkit*, not an app to build. Its value is
that you reuse its skills and lessons across projects instead of re-deriving them
every session. When a task matches a skill, use the skill.

**1 — Use the skills.** `skills/` holds packaged, evidence-tested procedures (each
with a `SKILL.md` and a `VALIDATION.md`). They trigger from their descriptions or
by name; consult the matching one before improvising. A skill encodes a decision
that was already litigated against real repositories — don't relitigate it blind.

**2 — Keep learning (lessons).** When something surprises you or costs you time
and the cause is *portable* (not specific to the project you're in), capture it
with the `capture-lesson` skill into `lessons/`. The library only stays sharp if
real friction feeds back into it. A lesson is conditional knowledge (true when its
`applies-to` matches); a rule in `AGENTS.md` is unconditional.

**3 — Report evidence when deployed.** After using a skill on real work, record
whether it earned its place — where it fired, whether it helped, where it missed.
This evidence is what promotes, sharpens, or *cuts* a skill: one that never pulls
its weight is removed, not kept out of politeness. `docs/WAYFINDING.md` is the
cross-session state this feeds.

**4 — Dreaming (evolution).** Periodically the accumulated lessons and evidence
are mined for patterns that should become a new skill, a CI check, or a cut. This
is currently a deliberate, human-triggered pass — treat it as the intended
direction, not a running automated loop (see `docs/CONTEXT-LOOP.md`).

**5 — Sign your work.** Every commit, PR, and issue you author carries a `Model:`
line naming you — provider, model, version (see `AGENTS.md` "Work records"). This
is how a contribution is traced to a specific model and weighted for trust.

## Layout

```
AGENTS.md          hard rules — always true, no conditions
CLAUDE.md          @AGENTS.md
VERSION            the workbench version, stamped into projects on import
CHANGELOG.md       what changed between versions
lessons/           conditional knowledge — true when applies-to matches
templates/         lesson.md, project-AGENTS.md
skills/            sweep-the-class, deslop (each SKILL.md + VALIDATION.md)
scripts/
  install.sh       machine setup: install skills into the harness skills dirs
  adopt.sh         per-project import (idempotent)
  unadopt.sh       remove the import from a project
docs/
  V0.1_DESIGN_SPECIFICATION.md   the design this was built to
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
| [backslash-escape-slop-breaks-tsx](lessons/backslash-escape-slop-breaks-tsx.md) | `react`, `typescript` | AI-generated TSX can contain literal `\``, `\${` escapes that break compilation; regex-strip before hand-editing |
| [check-lastexitcode-not-stderr](lessons/check-lastexitcode-not-stderr.md) | `windows` | PowerShell surfaces native-command stderr as error text; a mutating command can print scary output and still succeed |
| [check-the-error-not-just-the-data](lessons/check-the-error-not-just-the-data.md) | `supabase` | Read the `error`, or a failure looks identical to an empty result |
| [server-action-is-a-public-endpoint](lessons/server-action-is-a-public-endpoint.md) | `server-actions` | A Server Action is a public POST endpoint; re-validate on the server |
| [compensate-after-external-call](lessons/compensate-after-external-call.md) | `stripe` | An external call after a state-changing write needs a compensating path |
| [next-build-fails-silently-stale-cache](lessons/next-build-fails-silently-stale-cache.md) | `nextjs` | `next build` exiting 1 with no error text usually means corrupted `.next`; clear it before touching config |
| [next-dev-is-not-production](lessons/next-dev-is-not-production.md) | `nextjs` | `next dev` does not replicate static/ISR caching |
| [next-og-imageresponse-windows](lessons/next-og-imageresponse-windows.md) | `nextjs`, `windows` | `next/og`'s `ImageResponse` breaks `next build` on Windows |
| [node-modules-without-bin-is-broken](lessons/node-modules-without-bin-is-broken.md) | `node`, `windows` | `node_modules` present ≠ toolchain works; check `.bin` shims after any interrupted install |
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

## Sanitization policy

This repo is public. The rules that keep it publishable:

1. **No client-identifying material anywhere.** No client names, brand names,
   product names, or private-repo issue/PR numbers. Evidence is cited against
   anonymized sources ("a known fix set in `client-commerce`", "a tracking
   issue") — the structure, verdicts, and metrics stay, the identity goes.
2. **Raw archaeology reports are not in the public tree.** Their conclusions
   live on in the design spec, the lessons, and each skill's `VALIDATION.md`.
3. **Run `scripts/preflight-public.sh` before any push.** It greps the tree for
   known identifying patterns and exits nonzero if any appear. If this repo ever
   gains collaborators, wire it into CI rather than relying on memory.
4. **New evidence follows the same rule at write time.** When a lesson or
   validation doc is captured from client work, genericize it then — not in a
   future scrub pass.

The import tooling (`adopt.sh`, installed blocks) uses the internal marker
prefix `pas` / "personal-agent-system" — the project's original name. Renaming
that throughout is tracked as an issue; it touches already-adopted projects, so
it's a deliberate future pass, not a blind find-replace.
