---
applies-to: [nextjs, windows]
discovered: 2026-07
status: superseded — falsified by direct re-test on next@16.3.2 (2026-08)
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

**Falsified 2026-08-24, by building it rather than reasoning about it.** A minimal
App Router project with an edge-runtime `opengraph-image.tsx` using
`ImageResponse` was scaffolded on Windows and built with **next@16.3.2**:
`next build` completed successfully, generated the route, and produced no
`TypeError: Invalid URL`. Combined with the earlier external counter-evidence at
next@15.4.10, the failure is bounded to versions at or below 14.2.35 and is not a
current incompatibility.

**Kept, not deleted, and no longer inlined.** The claim is false for any Next
version anyone is realistically running, so `adopt.sh` now skips it — a superseded
lesson must not travel into projects. The file remains because why it was believed
and what disproved it is itself the record.

**What does not survive as a lesson:** the *recommendation* — prefer static icons
and metadata-based Open Graph images — is still reasonable, but with the bug gone
it is a preference rather than a lesson. It costs nothing to ignore, so by the
four-part test it does not belong in the ledger.

**The transferable part:** a lesson pinned to a dependency version has a shelf
life, and nothing expires it automatically. This one sat at `unverified-since` for
a month while still being inlined into every matching project, because the tooling
did not read `status` at all. That gap was found and closed by re-testing this
lesson.
