# Changelog

Notable changes to the workbench. Semantic versioning: **MAJOR** = a skill's
judgement or the import contract changed in a way that could alter results;
**MINOR** = a lesson or skill added; **PATCH** = a fix or clarification.

Skills install once per machine, so only one version is ever active — versions
exist for communication and rollback, not concurrent use.

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
  10/10 recall on the PR #252 silent-error class, 2/2 on the #192 unbounded-scan
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
