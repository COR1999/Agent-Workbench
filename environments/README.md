# environments

Machine-specific facts, one file per kind of machine. `scripts/install.sh` picks
one and appends it to the rules block it writes into `~/.claude/CLAUDE.md`, so
`AGENTS.md` stays true on every machine and nothing here leaks onto another.

Selection is by `uname -s` — `Linux` → `linux.md`, `MINGW*`/`MSYS*`/`CYGWIN*` →
`windows-git-bash.md` — or by name with `WORKBENCH_ENV=<file-stem> bash
scripts/install.sh`. A machine with no matching file (macOS, today) gets the rules
without an Environment section, and install.sh says so.

Each file is a complete `## Environment` section. Only put in it what is
unconditionally true of that machine and verified; anything conditional is a
lesson.
