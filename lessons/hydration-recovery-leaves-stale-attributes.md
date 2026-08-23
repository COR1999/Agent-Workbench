---
applies-to: [react, nextjs]
discovered: 2026-08
status: active
---

# Hydration-mismatch recovery leaves stale DOM attributes behind

Reading environment-dependent state (`window.location.search`,
`localStorage`) in `useState` initializers makes the server render defaults
while the client's first render uses real values. React detects the mismatch
and recovers by re-rendering - but recovery patches the DOM it believes it
already owns, so stale attributes from the server HTML can survive into the
steady state while text and structure update correctly. The symptom is
baffling: React DevTools/state shows one value while the DOM shows another
(e.g., two filter chips rendering "active" at once, or a list filtered to
one category under an unselected-looking chip).

**Cost:** A live bug that looked impossible - a single component instance
with correct hooks rendering contradictory UI - and cost a fiber-walking
session to prove state was right while DOM was wrong.

**Instead:** Initialize all state to defaults and apply environment-derived
values in a post-mount effect (`useEffect(..., [])`). The brief default-
state flash is invisible next to the alternative. This applies equally to
URL params, localStorage, sessionStorage, and anything else the server
cannot see.

**Strongest rung available:** an ESLint rule (custom `react-hooks` extension)
flagging `window.`/`localStorage` references inside `useState` initializer
functions; until that exists, this is judgement.
