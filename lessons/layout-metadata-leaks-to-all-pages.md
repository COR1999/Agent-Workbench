---
applies-to: [nextjs-app-router]
discovered: 2026-08
status: active
---

# Canonical and og:url set in the root layout leak onto every page

Next.js shallow-merges metadata from layout to page. A child page's
`metadata` export replaces only the top-level fields it sets; everything
else falls through from the parent. `alternates.canonical` and
`openGraph.url` written in `app/layout.tsx` are meant to describe the
homepage, but they silently become **every** page's canonical — each route
then tells crawlers it is a duplicate of the homepage. Nothing errors,
warns, or shows up in dev; the wrong tags are only visible in built HTML or
a search console.

**Cost:** a production site whose four content pages all emitted
`<link rel="canonical" href="https://example.com"/>`, inviting search
engines to collapse them into one indexed page — discovered only by
inspecting prerendered HTML during an audit.

**Instead:** keep `metadataBase` in the root layout, but put
`alternates.canonical` (self-referencing, e.g. `/projects`) and any
page-specific `openGraph.url` in each page's own `metadata`. Verify by
grepping the built `.html` output for `rel="canonical"` — one distinct URL
per route.

**Strongest rung available:** none mechanical without a custom lint rule;
a cheap partial guard is a CI step that asserts every built page's
canonical is unique per route.
