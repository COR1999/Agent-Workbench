---
applies-to: [windows]
discovered: 2026-08
status: active
---

# A native command's stderr output is not a failure verdict

PowerShell surfaces a native executable's stderr stream as error-shaped text
even when the command succeeds — git prints its own progress there by design.
A mutating command can look like it failed while having fully applied, and an
agent or script that retries on the appearance of failure duplicates
state-changing work.

**Cost:** Nearly duplicated a git commit after misreading progress noise as
failure; time lost re-verifying history that was already correct.

**Instead:** After any native command that looks like it failed, check
`$LASTEXITCODE` and the resulting state (`git log`, filesystem) before
re-running it. Treat stderr text as untrusted signal; treat the exit code as
ground truth.

**Strongest rung available:** none in PowerShell 5.1 itself; agent harnesses
can capture exit codes separately from merged output streams and surface them
alongside the text.
