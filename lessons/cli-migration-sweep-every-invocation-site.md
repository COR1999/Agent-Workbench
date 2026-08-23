---
applies-to: [node, github-actions]
discovered: 2026-08
status: active
---

# A CLI migration is done only when every invocation site is swept

Renaming or replacing a deprecated command — a `lint` script, a framework CLI
subcommand — in `package.json` looks complete, but the manifest script is often
not the one that actually runs. CI workflows, Dockerfiles, Makefiles, and docs
frequently invoke the tool directly, so editing only the npm script leaves the
real failure surface untouched and armed for the next upgrade — while the diff
reads as a finished fix.

**Cost:** a deprecated-command fix applied to `package.json` while the CI
workflow still called the old command directly. The CI step stayed broken and
the edit gave false confidence that the migration was resolved; the failure was
rediscovered only on the next framework upgrade.

**Instead:** after any command rename or deprecation fix, `grep -r` the old
command string across the whole repo — package scripts, `.github/workflows`,
Dockerfiles, Makefiles, docs — and confirm zero live call sites remain. Assume
the manifest script is *not* the one CI runs until you have checked. This is
`sweep-the-class` applied to a migration: fix the class of call sites, not the
first instance you found.

**Strongest rung available:** a CI grep-guard that fails the build if the
deprecated command string appears in any tracked file — it mechanically prevents
the regression the manual sweep catches by hand.
