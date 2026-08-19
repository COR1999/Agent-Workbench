---
applies-to: [nextjs]
discovered: 2026-07
status: active
---

# `next dev` does not replicate static and ISR caching

The dev server renders on every request. A production build serves cached and
statically-generated pages. Any behaviour that depends on a page being cached —
per-request values baked into static output, revalidation timing, a route that
is dynamic when it was assumed static — is invisible in `next dev` and appears
only against a real build.

**Cost:** a security-header change that passed every dev-server check shipped to
production, broke the site, and had to be reverted. The specific mechanism was a
per-request nonce serialised into a statically cached page and then served to
every subsequent visitor.

**Instead:**

- Verify anything cache-dependent against `next build && next start`, not
  `next dev`.
- Treat "is this route actually static?" as a question with an answer to look up,
  not to assume. Reading a cookie or header anywhere in the tree makes the whole
  route dynamic, silently.
- Never put a per-request value into output that can be cached.

**Strongest rung available:** one end-to-end test against a real production
build, asserting the cache-sensitive behaviour. That converts the class from
"remember to check" into a gate, and is what caught the recurrence.
