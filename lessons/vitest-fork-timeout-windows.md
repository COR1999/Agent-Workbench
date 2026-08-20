---
applies-to: [vitest, windows]
discovered: 2026-08
status: active
---

# On Windows, vitest's default forks pool can hang; run with --no-file-parallelism

The default `forks` pool spawns worker processes that intermittently fail to
start on this platform, and the run dies with `Timeout waiting for worker to
respond` / `Failed to start forks worker` after ~60s — the error points at the
pool machinery, not at any test, so it reads like the tests are broken when they
are fine.

**Cost:** a test run that looks like a real failure but is a worker-spawn
timeout; minutes lost before realising the tests never ran.

**Instead:** run the affected files with `vitest run <files> --no-file-parallelism`
(single worker, no cross-file forking). If it recurs across the whole suite, set
it in config — `test.pool` / `poolOptions` or `fileParallelism: false` — rather
than passing the flag every time. Confirm the tests actually executed (a real
pass count), not just that the command exited.

**Strongest rung available:** pin the setting in `vitest.config.ts`
(`fileParallelism: false` or a single-fork pool) so no one has to remember the
flag — turns "remember to add it" into a committed default.
