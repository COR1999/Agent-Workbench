---
applies-to: [nextjs, windows]
discovered: 2026-07
status: unverified-since next@16.2.10
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

**Staleness note:** observed on Next 14.2.35. Not re-verified since. If a future
project wants `ImageResponse`, re-check whether it still reproduces before
treating this as current.
