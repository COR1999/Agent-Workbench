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

**Second failure mode — the wrapper's implicit defaults are an invocation site
too.** Replacing a wrapper command with the underlying tool also drops whatever
the wrapper configured implicitly. A framework's lint wrapper typically layers
default ignore paths and file selection over the raw linter; swap in the bare
linter and those defaults vanish silently. In one case the migrated command then
linted the framework's *build-output* directory and reported hundreds of errors
the wrapper had always excluded. CI can hide this: if lint runs before the build
step, the generated directory does not exist yet, so CI stays green while the
command is broken on any machine that has already built. Treat the deprecated
tool's implicit behaviour — ignore paths, default globs, env defaults — as a call
site of its own: reproduce it explicitly (e.g. an `ignores` block) when you move
to the underlying tool, and verify the new command against a fully-built tree,
not just a clean checkout.

**Strongest rung available:** a CI grep-guard that fails the build if the
deprecated command string appears in any tracked file — it mechanically prevents
the regression the manual sweep catches by hand.
