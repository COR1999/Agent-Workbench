---
applies-to: [stripe]
discovered: 2026-07
status: active
---

# An external call after a state-changing write needs a compensating path

The dangerous shape is: reserve or write something locally, then call a third
party, and let the third party's failure escape uncaught. The local write
survives with nothing to undo it. It is especially easy to miss when the normal
cleanup is triggered by an event from that same third party — if the session or
job was never created, the event that would have released the reservation can
never fire, so the orphan is permanent rather than temporary.

**Cost:** stock reserved against an order that will never exist, invisible until
inventory stops adding up.

**Instead:** before considering the write done, ask *"what undoes this if the
external call fails?"* Wrap the whole post-write block, and on any failure call
the same cleanup an expired or cancelled external session would have triggered —
reached from a different failure moment, but doing the same work. Reuse the
existing cleanup rather than writing a second one; two cleanup paths drift.

This is the one place where `try/catch` is load-bearing rather than defensive
noise. Do not remove it during cleanup passes.

**Strongest rung available:** an integration test that kills the external call
mid-flight and asserts the local state is released. Needs a real database, so it
runs in CI only on this machine.
