---
applies-to: [node, windows]
discovered: 2026-08
status: active
---

# A present node_modules does not mean a working toolchain

An npm install killed mid-run — by a command timeout or a crashed process —
leaves packages on disk but without the `.bin` shims, so `next`, `tsc`, and
friends are "not recognized" even though `node_modules/` exists and looks
healthy. Orphaned node processes from the killed install can linger and hold
file locks. The folder's existence invites you to suspect PATH, config, or the
script instead of the install itself.

**Cost:** Time lost diagnosing a missing binary as an environment problem,
plus at least one repair cycle that had to untangle the partial install.

**Instead:** Before diagnosing anything else, check the shim directly:
`node_modules/.bin/<tool>.CMD` must exist. If it does not, kill stray node
processes, then re-run the install with a generous timeout — slow machines and
registries routinely exceed 5 minutes, so a 300-second timeout is often the
thing that caused the corruption.

**Strongest rung available:** none for prevention beyond timeout discipline;
the detection half could be encoded as a repo bootstrap script that asserts
`.bin` shims before running any tool.
