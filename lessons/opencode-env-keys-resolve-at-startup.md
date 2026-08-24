---
applies-to: [opencode, windows]
discovered: 2026-08
status: active
---

# Provider `{env:VAR}` keys resolve once, at agent-server startup

OpenCode-style config files interpolate provider credentials like
`{env:OPENROUTER_API_KEY}` when the server process starts — not per request.
A key added (or fixed) after launch is invisible to every running server, and
the provider fails with a non-retryable auth error on every attempt. The agent
UI presents this as endless retry loops that look like a hung session, not an
auth failure.

**Cost:** a session sat overnight appearing "stuck"; repeated retries all died
on the same 401 while looking like model slowness. Diagnosis required reading
the stored API error, not watching the UI.

**Instead:**

- When provider auth fails with 401/credentials errors, check whether the
  variable existed in the environment of the *specific* process that launched
  the server — not whether it is set somewhere on the machine.
- On Windows, set machine-level variables at User scope and then fully restart
  the GUI shell, not just the windows inside it: spawned servers inherit the
  parent's environment block, so a parent that predates the change passes the
  stale environment down indefinitely.
- Read the persisted error object (session store / API) before concluding an
  agent is "stuck". Retry loops and auth failures look identical from outside.

**Strongest rung available:** startup validation — fail fast at boot when a
configured `{env:VAR}` resolves empty, instead of failing lazily on first use.
