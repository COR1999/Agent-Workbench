#!/usr/bin/env bash
# Remove Agent-Workbench's managed block from a project's AGENTS.md.
# Leaves everything you wrote yourself intact. Does not delete AGENTS.md or
# CLAUDE.md — those may hold your own content.
#
# Usage:  scripts/unadopt.sh /path/to/project
set -euo pipefail

PROJECT="${1:-}"
[ -n "$PROJECT" ] && [ -d "$PROJECT" ] || { echo "usage: unadopt.sh <project-dir>"; exit 1; }
cd "$PROJECT"

START="<!-- workbench:start"
END="<!-- workbench:end -->"
# Projects adopted before the rename carry the old `pas` marker. unadopt must
# remove those too, or it would report success and leave the block in place.
LEGACY_START="<!-- pas:start"
LEGACY_END="<!-- pas:end -->"

if [ ! -f AGENTS.md ] || { ! grep -qF "$START" AGENTS.md && ! grep -qF "$LEGACY_START" AGENTS.md; }; then
  echo "nothing to remove — no managed block in $PROJECT/AGENTS.md"
  exit 0
fi

awk -v s="$START" -v ls="$LEGACY_START" -v e="$END" -v le="$LEGACY_END" '
  index($0,s) || index($0,ls){skip=1}
  !skip{print}
  index($0,e) || index($0,le){skip=0; next}
' AGENTS.md > AGENTS.md.tmp
# collapse any trailing blank lines left behind
# Drop trailing blank lines. This was `sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}'`,
# which is GNU-specific: BSD sed (macOS) parses the label/branch differently and
# emptied the file instead of trimming it. Found by the cross-platform CI matrix
# (#28) on its first run — every "user content survives" assertion failed on
# macOS while passing on Linux and Windows. awk is portable and says what it means.
awk '{lines[NR]=$0; if (NF) last=NR} END {for (i=1;i<=last;i++) print lines[i]}' AGENTS.md.tmp > AGENTS.md
rm -f AGENTS.md.tmp
printf '\n' >> AGENTS.md

echo "removed the Agent-Workbench block from $PROJECT/AGENTS.md"
echo "note: AGENTS.md and CLAUDE.md were kept (they may hold your own content)."
echo "note: machine-level skills are unaffected — remove those with your harness's skills dir."
