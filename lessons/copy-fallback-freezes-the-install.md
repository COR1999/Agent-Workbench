---
applies-to: [windows, multi-agent]
discovered: 2026-08
status: active
---

# An installer that falls back from symlink to copy freezes the thing it installed

Install scripts that link a source directory into a tool's config directory
commonly fall back to copying when the OS refuses the symlink — on Windows,
whenever the process lacks symlink privilege. The fallback succeeds, so the
install reports success, the directory exists, the files are present, and the
tool keeps working. What is silently lost is every subsequent edit to the source:
the installed copy is a snapshot taken at install time, and nothing ever tells
you it has gone stale.

**Cost:** three days of edits to an installed instruction library reached no
session at all. The staleness was invisible — the directory listing looked
correct and every consumer behaved normally — and was found only by grepping the
*installed* file for a string added to the *source*. An experiment about to be
run on the edited content would have measured the old content and produced a
confident, wrong result.

**Instead:**

- After installing, verify the installed artifact by *content*, not existence:
  grep the installed file for a string you know is only in the current source.
- Treat "the directory is there" as no evidence at all — the same class of error
  as [[node-modules-without-bin-is-broken]].
- If the installer can copy, assume it did. Re-run it after every source change
  rather than after every pull, and check which mode it chose from its output.
- When several tools read the same installed directory, one stale copy affects
  all of them at once; verifying one is verifying all only if they share a path.

**Strongest rung available:** have the installer write the source commit hash
beside the installed copy, and have the consumer (or a check script) compare it
against the source's current hash — turning silent staleness into a visible
mismatch. Failing that, a verify step in the installer that greps the installed
file for a sentinel from the source and exits nonzero when it is absent.
