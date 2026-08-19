#!/usr/bin/env bash
# Remove personal-agent-system's managed block from a project's AGENTS.md.
# Leaves everything you wrote yourself intact. Does not delete AGENTS.md or
# CLAUDE.md — those may hold your own content.
#
# Usage:  scripts/unadopt.sh /path/to/project
set -euo pipefail

PROJECT="${1:-}"
[ -n "$PROJECT" ] && [ -d "$PROJECT" ] || { echo "usage: unadopt.sh <project-dir>"; exit 1; }
cd "$PROJECT"

START="<!-- pas:start"
END="<!-- pas:end -->"

if [ ! -f AGENTS.md ] || ! grep -qF "$START" AGENTS.md; then
  echo "nothing to remove — no managed block in $PROJECT/AGENTS.md"
  exit 0
fi

awk -v s="$START" -v e="$END" '
  index($0,s){skip=1}
  !skip{print}
  index($0,e){skip=0; next}
' AGENTS.md > AGENTS.md.tmp
# collapse any trailing blank lines left behind
sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}' AGENTS.md.tmp > AGENTS.md
rm -f AGENTS.md.tmp
printf '\n' >> AGENTS.md

echo "removed the personal-agent-system block from $PROJECT/AGENTS.md"
echo "note: AGENTS.md and CLAUDE.md were kept (they may hold your own content)."
echo "note: machine-level skills are unaffected — remove those with your harness's skills dir."
