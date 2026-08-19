# Changelog

Notable changes to the workbench. Semantic versioning: **MAJOR** = a skill's
judgement or the import contract changed in a way that could alter results;
**MINOR** = a lesson or skill added; **PATCH** = a fix or clarification.

Skills install once per machine, so only one version is ever active — versions
exist for communication and rollback, not concurrent use.

## [Unreleased]

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
