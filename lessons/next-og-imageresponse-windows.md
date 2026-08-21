---
applies-to: [nextjs, windows]
discovered: 2026-07
status: unverified-since next@14.2.35 — counter-evidence at next@15.4.10
---

# Don't use next/og's ImageResponse on Windows

The `app/icon.tsx` and `app/opengraph-image.tsx` conventions, which generate
images via `next/og`'s `ImageResponse`, hit a Windows-only bug in the bundled
`@vercel/og` default font loader — `TypeError: Invalid URL` — that breaks
`next build` locally. The same build succeeds on Linux CI and on the hosting
platform, so the failure looks like a broken local environment rather than a
real incompatibility.

**Cost:** a local build that cannot be made to pass, on a machine where CI is
green, with an error that points at a URL parser rather than at the feature
that caused it.

**Instead:** static SVG or PNG icons, and metadata-based Open Graph images
(`openGraph` / `twitter` in the layout's metadata export, pointing at a real
image file). These behave identically on every OS whether or not the underlying
bug is still live, so this is the right default regardless.

**Strongest rung available:** a lint rule banning `next/og` imports would
enforce it, but is probably not worth writing for a one-line judgement call.
Prose is acceptable here.

**Staleness note:** observed on Next 14.2.35 (matches the frontmatter). An
external audit (issue #16, finding 3) reported the opposite on **next@15.4.10** —
an edge-runtime `opengraph-image.tsx` built clean on Windows across six
consecutive builds. Not reproduced here, but enough to treat the failure as
version-bounded (a fix landed somewhere after 14.2.35) or fixed upstream, rather
than a current blanket incompatibility. Re-test on your exact Next version before
treating this as live. The recommendation in **Instead** stands regardless of the
bug's status — it's the simpler, OS-independent default either way.
