---
applies-to: [react, typescript]
discovered: 2026-08
status: active
---

# AI-generated TSX can ship literal backslash-escapes that break compilation

Generated JSX sometimes contains `\`` where a template-literal backtick belongs
and `\${` where interpolation starts — artifacts of string-escaping applied
twice. TypeScript then fails with syntax errors (unterminated template
literal, missing parenthesis) pointing at lines far from any obvious cause,
and hand-editing each occurrence wastes time and risks touching valid code.
The tell: a backslash directly before a backtick or dollar sign never occurs
in legitimate TSX.

**Cost:** A feature commit left an entire branch uncompilable and blocked
every pending change until repaired; the error messages suggested parser bugs
rather than escape slop.

**Instead:** When template-literal syntax errors follow an AI-authored commit,
grep for `/\\(?=[`$])/` first and strip those backslashes mechanically —
verify the match count against the failing lines, then let typecheck confirm.
Treat the commit as slop-flagged and review its diff for more escaping noise.

**Strongest rung available:** a CI typecheck gate on every push — the class
then surfaces before merge instead of blocking other work. A lint rule banning
`\`` outside string literals is possible but rarely needed once CI exists.
