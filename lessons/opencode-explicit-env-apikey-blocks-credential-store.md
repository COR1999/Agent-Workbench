---
applies-to: [windows, opencode]
discovered: 2026-08
status: active
---

# An explicit `apiKey: {env:X}` in opencode config blocks the credential-store fallback

Two independent facts stack into a confusing provider "runtime error":

1. Environment variables only reach processes started after they are set. A
   long-running T3 Code session predating the variable sees an empty value
   forever, even though `[Environment]::GetEnvironmentVariable(x,"User")`
   shows it present.
2. When a custom provider block declares `options.apiKey: "{env:X}"` and `X`
   resolves empty, opencode does **not** fall back to its credential store
   (`~/.local/share/opencode/auth.json`). It fails with the opaque
   `Error: No cookie auth credentials found`. Writing a correct auth.json
   entry changes nothing until the `{env:...}` line is removed.

**Cost:** Two wrong hypotheses before the real one — first blamed the
OpenRouter 429 (real but unrelated), then assumed auth.json alone would fix
it (it did not; the error persisted). Only removing the config line fixed it.

**Instead:** Store API keys in the auth store and keep provider blocks free of
`{env:...}` apiKey lines entirely. `opencode auth login <name>` only handles
OAuth URL flows; for plain API keys write auth.json directly:
`{"<provider-id>": {"type": "api", "key": "..."}}`, then verify with
`opencode auth list`. Resolution becomes independent of how the host process
was launched.

**Strongest rung available:** structural — no env references in config means
the stale-environment failure mode is not representable. Verify per provider
with a cold shell (`$env:X` unset in-process) `opencode run -m ...` probe.
