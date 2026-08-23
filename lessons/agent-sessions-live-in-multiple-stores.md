---
applies-to: [windows, diagnostics, multi-agent]
discovered: 2026-08
status: active
---

# One "agent window" can be several backends with separate session stores

GUI shells that orchestrate coding agents spawn multiple backends under the
hood (a local agent server per window, plus external CLIs like Claude Code as
subprocesses). Each backend persists sessions in its own store. Searching only
the primary tool's database for a session the user can plainly see in their UI
returns nothing, and the conclusion "that session does not exist" is wrong.

**Cost:** a missing-image bugfix session was absent from the first store
searched, triggering a plan to recreate the work from scratch — duplicating an
in-flight task — before process-ancestry tracing revealed a second backend
owned the session.

**Instead:**

- Locate the real backend by walking `Win32_Process` `ParentProcessId`
  ancestry from the shell down to the worker, then read each backend's own
  storage (its DB, or JSONL transcripts keyed by project directory).
- Treat "session not in store X" as "wrong store", not "no session".
- Before recreating lost-looking work, prove no backend currently owns it;
  duplicates run concurrently and both edit the same tree.

**Strongest rung available:** a discovery script that enumerates all local
agent backends and their session stores once, so triage starts from inventory
instead of guesswork.
