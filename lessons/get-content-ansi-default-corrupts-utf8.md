---
applies-to: [windows]
discovered: 2026-08
status: active
---

# Reading a BOM-less UTF-8 file without -Encoding corrupts non-ASCII content

PowerShell 5.1's `Get-Content` without `-Encoding UTF8` decodes BOM-less files
using the ANSI code page (Windows-1252). Round-tripping a config that contains
emoji or other multi-byte characters — parse with `ConvertFrom-Json`, mutate,
re-write with `Set-Content`/`WriteAllText` — silently stores mojibake
(`🟩` becomes `ðŸŸ©`) in place of every non-ASCII character. The JSON stays
syntactically valid, so nothing errors; the corruption is discovered only when
a human looks at the file.

**Cost:** Corrupted the user's opencode.jsonc (45 model display names), had to
regenerate the whole file by hand. Also lost time to a related cast trap:
`[char]0x1F7E9` throws in PS 5.1 because astral-plane code points do not fit a
single .NET char.

**Instead:** Always pass `-Encoding UTF8` when reading files that may contain
non-ASCII text, and prefer editing such files with real file tools rather than
a read-parse-mutate-write shell pipeline. For astral emoji use
`[System.Char]::ConvertFromUtf32(0x1F7E9)`, not `[char]`.

**Strongest rung available:** none portable — PS 5.1 has no utf8 default;
agent harnesses can route non-code file edits through dedicated edit tools
that handle encoding explicitly.
