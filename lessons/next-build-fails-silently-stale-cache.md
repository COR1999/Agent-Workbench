---
applies-to: [nextjs]
discovered: 2026-08
status: active
---

# `next build` can exit 1 with empty output when `.next` is corrupted

A build interrupted mid-run (killed shell, timeout, crash) can leave a
`.next` directory that makes every subsequent build fail — sometimes
silently, exiting 1 after only the banner lines, with no error text in stdout
or stderr. Nothing points at the cache; the instinct is to re-read config,
dependency versions, or the code that changed, none of which is wrong.

**Cost:** A full diagnosis cycle spent on lint/ESLint configuration that was
innocent, because the failure produced zero diagnostics to reason from.

**Instead:** When `next build` fails without a usable error message — or dies
at a different stage each run — delete `.next` and rebuild before changing any
configuration. If the failure is not reproducible from clean state, it never
was a configuration problem.

**Strongest rung available:** none, this is judgement. CI runners start from
clean checkouts and so rarely hit it; local and long-lived worktree machines
are where the reflex matters.
