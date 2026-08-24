# Changelog

Notable changes to the workbench. Semantic versioning: **MAJOR** = a skill's
judgement or the import contract changed in a way that could alter results;
**MINOR** = a lesson or skill added; **PATCH** = a fix or clarification.

Skills install once per machine, so only one version is ever active — versions
exist for communication and rollback, not concurrent use.

## [0.7.0] — 2026-08-23

### Changed
- **BREAKING (import contract): the managed-block marker is renamed `pas` →
  `workbench`** (#3). A project's `AGENTS.md` now carries
  `<!-- workbench:start -->` / `<!-- workbench:end -->`, and the machine-wide
  `CLAUDE.md` carries `<!-- workbench-rules:start -->`. The `## Inherited from
  personal-agent-system` line becomes `## Inherited from Agent-Workbench`.

  **Nothing breaks on upgrade.** `adopt.sh`, `unadopt.sh` and `install.sh` all
  recognise the old markers when stripping, so a re-run *migrates* an existing
  block in place instead of appending a second one. Verified against fixtures
  covering: an old block plus surrounding user content, a re-run for idempotency,
  `unadopt` on a new block, and `unadopt` on a legacy-only block. Content above
  and below the block survived every path.

  The legacy handling stays until no adopted project carries the old marker.
  Removing it early would silently orphan a block and load two copies of the
  rules into every session.

### Added
- `scripts/skill-usage-scan.py` — counts skill firings across every local agent
  store (Claude-family JSONL and OpenCode's SQLite), with an artifact test for
  whether a firing helped, a miss test for opportunities not taken, and a context
  column separating task-routed firings from library-invoked ones.
- `scripts/build-replay-set.py` — turns past sessions into labelled routing
  examples with a fixed train/holdout split.
- `docs/ROADMAP.md` — the single store for the project's decisions, auto-loaded
  via `CLAUDE.md`.
- `lessons/copy-fallback-freezes-the-install` — an installer that falls back from
  symlink to copy freezes the installed content at install time.
- `AGENTS.md` rule: name the lesson slug in the work record when a lesson changes
  what you do.

### Fixed
- **Eight real repository names were present in this public tree** and are now
  genericized. `preflight-public.sh` held no repository-name patterns at all, and
  scanned the whole working directory including `.git/` and the gitignored
  `.research/` clones — so it failed on every run and was dismissed as a known
  false positive. It now scans tracked files only, exits clean, and was verified
  to still catch a planted leak.

## [0.6.2] — 2026-08-23

### Changed
- **`cli-migration-sweep-every-invocation-site` — added a second failure mode.**
  Beyond sweeping call sites, a CLI migration must reproduce the deprecated
  wrapper's *implicit* behaviour: swapping a framework lint wrapper for the raw
  linter silently drops the wrapper's default ignore paths, so the new command
  lints build output and fails — while CI can stay green because lint runs before
  the build directory exists. Surfaced by executing such a migration and hitting
  hundreds of errors from a generated directory. README row updated to match.

## [0.6.1] — 2026-08-22

### Added
- **README "Working here (for the agent)" section** — an orientation for any
  agent landing in the repo: what it's for (a carry-along toolkit, not an app),
  and the loop — use the skills, capture lessons when surprised, report evidence
  after deploying a skill so it earns/loses its place, the human-triggered
  "dreaming" evolution pass, and signing work with a `Model:` line. Makes the
  operating model explicit instead of implicit.

## [0.6.0] — 2026-08-22

### Added
- **Model provenance on every commit, PR, and issue.** A model authoring any of
  these must name itself — provider, model, and version — via a `Model:` trailer
  on commits and a matching `Model:` line at the foot of PR/issue bodies
  (`Model: <Provider> <Model> (<model-id>)`). Codified as a hard rule in
  `AGENTS.md` "Work records" and wired into the `explain-and-open-pr` procedure,
  so contributions can be traced to a specific model and weighted for trust.

## [0.5.0] — 2026-08-21

### Changed
- **Publication sanitization.** The repo is public; all client-identifying
  material is removed or genericized: private repo names, issue/PR numbers,
  brand and product names, and brand-voice guidance in `skills/*/VALIDATION.md`,
  `skills/*/tests/*.md`, and the design spec. Evidence structure, verdicts, and
  metrics are preserved. `docs/research/` (the raw archaeology reports) is no
  longer part of the public tree — its conclusions live on in the lessons,
  skills, and design spec.
- **New: `scripts/preflight-public.sh`** — greps the tree for known
  client-identifying patterns and fails with a nonzero exit if any are present.
  Run before any public push; this is the "Before publishing" checklist made
  mechanical instead of remembered.

### Fixed
- README claimed the repo was private while it was public — now states actual
  visibility and the sanitization policy.

## [0.4.0] — 2026-08-20

### Added
- Five net-new skills: **design-handbook** (#4), **explain-and-open-pr** (#5),
  **agentic-vocabulary** (#8), **tdd** (#10), **grilling** (#11). Each kept
  minimal with a trigger-first description and invariant locks in
  `tests/skill-invariants.sh`. To be exercised in production and pruned.
  Closes #4, #5, #8, #10, #11.

## [0.3.0] — 2026-08-20

### Added
- **skills/handoff** + **docs/CONTEXT-LOOP.md** — the "smart context loop"
  exploration (#9). Keep ephemeral session context small; move durable state to
  artifacts a fresh session reloads. The map + git are the strategic layer we
  already had; `handoff` adds the tactical between-session baton (goal / done /
  remaining / blocker / files / next action). Honest finding: an agent can't
  reliably self-measure context %, so resets happen on **boundaries** (a
  completed unit), not a hard-coded 40%. Deliberately NOT built: a
  context-policy runtime, adaptive thresholds, model orchestration.

## [0.2.4] — 2026-08-20

### Added
- **MIT `LICENSE`** — the repo is now formally open-source. (Closes #2.)

## [0.2.3] — 2026-08-20

### Added
- **`tests/skill-invariants.sh`** — a tiny plain-shell suite that greps each
  `SKILL.md` for its load-bearing rules (sweep-the-class "never edits" + coverage;
  deslop's information/safety/intent gate, failure-visibility clause, and *no*
  `any` gate; capture-lesson's four-part test) and fails if one is edited out.
  Our own "encode lessons in structure" rung applied to the skills themselves.
  Inspired by the bats invariant-tests in `mattpocock`/`mitoperni-squad`; kept to
  a handful of locks, no bats/build dependency. (Closes #6.)

## [0.2.2] — 2026-08-20

### Added
- Lesson **vitest-fork-timeout-windows** — vitest's default forks pool can hang
  on Windows (`Timeout waiting for worker to respond`); run with
  `--no-file-parallelism`. Captured from real work on a client design pass.

## [0.2.1] — 2026-08-20

### Changed
- **`adopt.sh` now detects monorepo stacks.** Checks `frontend/`, `backend/`,
  `web/`, `app/`, `client/`, `server/` subdirs for their own `package.json`,
  `requirements.txt`, `pyproject.toml`, `tsconfig.json`, `components.json`.
  A repo like `client-reporting` (Python backend + Next.js frontend) now
  correctly detects all 15 stack values and matches the appropriate lessons.

## [0.2.0] — 2026-08-20

### Added
- **skills/capture-lesson** — captures a lesson while the context is fresh.
  Prompts for what happened, applies the four-part test (refuses to write if it
  fails), drafts against the template, writes to `lessons/`, updates the README
  table. Use immediately after something surprises you or costs you time.

## [0.1.1] — 2026-08-20

Fixes from an independent review of the v0.1.0 build.

### Fixed
- **Machine rules now actually reach the agent.** `install.sh` previously
  installed only skills; the machine-wide rules in `AGENTS.md` (Git Bash path
  mangling, no-Docker honesty, verification/coverage rules) loaded nowhere.
  `install.sh` now also copies them into `~/.claude/CLAUDE.md` inside an
  idempotent managed block. Copied rather than `@`-imported to avoid absolute
  Windows path resolution — the fragility this repo has a lesson about.
- Added `.gitattributes` forcing `*.sh` to LF so a Windows checkout can't corrupt
  the shell scripts with CRLF line endings.
- **Added the root `CLAUDE.md` (`@AGENTS.md`)** the docs promised but that was
  missing — the workbench now eats its own dog food.
- **`skills/deslop/VALIDATION.md`: corrected the coverage accounting.** The
  mechanical-guard count was overstated as "20 of 22"; the accurate figure is
  13 mechanically guarded / 9 by judgment. Every hunk is still protected by a
  stated rule; only the accounting of *which* mechanism was wrong.
- **`adopt.sh` now matches the managed block on its stable prefix**, like
  `unadopt.sh`, so editing the marker wording between versions can no longer leave
  an old block unrecognised and append a duplicate.
- **`next-og-imageresponse-windows` version fixed** — frontmatter and body
  disagreed (`16.2.10` vs `14.2.35`); both now say `14.2.35`, the observed value.

### Changed
- `adopt.sh` detects more of the `applies-to` vocabulary (radix, vitest,
  playwright, isr, vercel, railway, fastapi, sqlalchemy, gemini, supabase-dir).
  `templates/lesson.md` now documents that the detector is a subset and that a
  lesson using an undetected value will silently not inline.
- `README.md`: added a **"Before publishing"** section. The lessons are
  client-safe, but the test fixtures and `VALIDATION.md` files quote private
  repos verbatim and must be scrubbed or excluded before any public release.
- Marked `docs/V0.1_DESIGN_SPECIFICATION.md` as a frozen historical doc and noted
  the `reports/` → `docs/research/` path move.

## [0.1.0] — 2026-08-19

First gated release. Everything below was validated against real repository
history before shipping (see each skill's `VALIDATION.md`).

### Added
- **Lessons ledger** — 6 client-safe lessons with a closed `applies-to`
  vocabulary and AND-matching. `templates/lesson.md` carries the four-part test.
- **Rules** — machine-wide `AGENTS.md`: Git Bash path mangling, no-Docker
  verification honesty, "no issues found" coverage rule, record-work reminder,
  boundary-discipline and encode-in-structure judgement notes.
- **skills/sweep-the-class** — never-edits sibling-defect finder. Validated:
  10/10 recall on a silent-error class, 2/2 on an unbounded-scan
  class. Surfaced a real same-class bug the original human fix missed.
- **skills/deslop** — three-gate AI-noise filter. `any` clause deleted by design.
  Gated at 22/22 on real should-not-flag hunks (TS + Python).
- **Import mechanism** — `scripts/install.sh` (machine skill install),
  `scripts/adopt.sh` (idempotent per-project import), `scripts/unadopt.sh`.
- **docs/research** — the 16-report archaeology and the v0.1 design spec.

### Deliberately not included
Registry, validator, generator, stage folders, `principles/`, `.agent/`,
workflow engine, dreaming loop, npm/pip packaging, CI. See
`docs/V0.1_DESIGN_SPECIFICATION.md` → "What we are deliberately not building".
