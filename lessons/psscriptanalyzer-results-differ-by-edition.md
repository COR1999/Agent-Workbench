---
applies-to: [windows]
discovered: 2026-10
status: active
---

# PSScriptAnalyzer findings depend on the PowerShell edition it runs under

Some rules check your code against the cmdlets of the host running the
analyzer, not against a fixed list. `PSAvoidOverwritingBuiltInCmdlets` flags a
function named `Write-Log` only under pwsh 6.1+, which ships a cmdlet with that
name. Windows PowerShell 5.1 has no such cmdlet. A lint run that comes back clean
on 5.1 says nothing about pwsh, even though a script that targets both will run
under pwsh too.

**Cost:** A lint step that was clean locally failed in CI on the pwsh leg,
costing a round trip. Without the CI leg, the name would have shipped
shadowing a built-in for anyone running the script under pwsh.

**Instead:** Run the analyzer (and the tests) under every edition the script
claims to support. A CI matrix of `shell: [powershell, pwsh]` on a Windows
runner covers both. Give helper functions project-prefixed names
(`Write-RunnerLog`, not `Write-Log`) so they cannot collide with a future
built-in.

**Strongest rung available:** A CI matrix that lints and tests under both
editions.
