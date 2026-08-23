---
applies-to: [nextjs]
discovered: 2026-08
status: active
---

# `next build` against a running `next dev` server corrupts both

Running `next build` in a directory where `next dev` is currently serving
overwrites `.next` underneath the live dev server. The dev server keeps its
old webpack runtime manifest but loses the chunks it points at, and every
route starts failing with 500s - typically `Cannot find module './NNN.js'`
from `.next/server/webpack-runtime.js`, which reads like node_modules
corruption rather than a tooling self-collision. Nothing names `next build`
as the cause.

**Cost:** Two full diagnose cycles (log reading, restart attempts) across one
session before recognizing the pattern, because the error surfaces minutes
after the build ran and looks like a broken install.

**Instead:** Treat "dev server suddenly 500s on every route with webpack
MODULE_NOT_FOUND" as a `.next` ownership conflict: stop the dev process,
delete `.next`, restart dev. And never start a production build without first
stopping any dev server on the same working tree.

**Strongest rung available:** none, this is judgement - though a prebuild
script that refuses to run when a dev server holds the port would encode it
structurally if the pattern keeps recurring.
