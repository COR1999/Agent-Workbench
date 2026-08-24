#!/usr/bin/env bash
# Machine setup for Agent-Workbench. Run once per machine; re-run after a
# `git pull` to refresh. Idempotent. Does two things:
#
#   1. Installs the skills into each harness's skills dir (symlink, copy fallback).
#   2. Installs the machine-wide RULES into ~/.claude/CLAUDE.md so they load in
#      every session — otherwise the rules in this repo's AGENTS.md reach nobody.
#
# Per-project lessons are NOT handled here — those are imported per project with
# adopt.sh. Only machine-global things (skills, environment rules) install here.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"

# --- 1. skills ----------------------------------------------------------------
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.agents/skills"
)

link_or_copy() {
  local src="$1" dst="$2"
  rm -rf "$dst"
  if ln -s "$src" "$dst" 2>/dev/null && [ -e "$dst" ]; then
    echo "  linked  $dst"
  else
    # No symlink privilege / filesystem won't link: copy. A copy does NOT update
    # on git pull — re-run this script after pulling. Deliberate, not a bug.
    cp -R "$src" "$dst"
    echo "  copied  $dst   (re-run after 'git pull' to refresh)"
  fi
}

installed_any=0
for target in "${TARGETS[@]}"; do
  if [ ! -d "$(dirname "$target")" ]; then
    echo "skip (no harness dir): $(dirname "$target")"
    continue
  fi
  installed_any=1
  mkdir -p "$target"
  echo "installing skills into $target"
  for skill in "$SKILLS_SRC"/*/; do
    [ -f "$skill/SKILL.md" ] || continue
    link_or_copy "${skill%/}" "$target/$(basename "$skill")"
  done
done
[ "$installed_any" = 1 ] || echo "no harness skills dir found (~/.claude or ~/.agents) — skills not installed"

# --- 2. machine rules into ~/.claude/CLAUDE.md --------------------------------
# The rules are COPIED (not @-imported) on purpose: an @import with an absolute
# Windows path is exactly the kind of path-resolution fragility this project has
# a lesson about. A copy always resolves. Re-run this script to refresh after
# editing the repo's AGENTS.md.
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
START="<!-- workbench-rules:start — managed by Agent-Workbench; edit AGENTS.md at the source and re-run install.sh -->"
END="<!-- workbench-rules:end -->"
# Machines set up before the rename carry the old `pas-rules` markers. Both are
# stripped, so a re-run migrates the block rather than leaving a stale duplicate
# of the rules loaded into every session alongside the new one.
LEGACY_START="<!-- pas-rules:start"
LEGACY_END="<!-- pas-rules:end -->"

if [ -d "$HOME/.claude" ]; then
  [ -f "$CLAUDE_MD" ] || : > "$CLAUDE_MD"
  # strip any existing managed block
  awk -v s="$START" -v ls="$LEGACY_START" -v e="$END" -v le="$LEGACY_END" '
    index($0,s) || index($0,ls){skip=1}
    !skip{print}
    index($0,e) || index($0,le){skip=0; next}
  ' "$CLAUDE_MD" > "$CLAUDE_MD.tmp"
  sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}' "$CLAUDE_MD.tmp" > "$CLAUDE_MD"
  rm -f "$CLAUDE_MD.tmp"
  {
    printf '\n%s\n' "$START"
    cat "$REPO_DIR/AGENTS.md"
    printf '%s\n' "$END"
  } >> "$CLAUDE_MD"
  echo "installed machine rules into $CLAUDE_MD"
else
  echo "skip machine rules: no ~/.claude (add the contents of AGENTS.md to your harness's global instructions manually)"
fi

echo "done."
echo "  verify skills: ls -l \"${TARGETS[0]}\""
echo "  verify rules:  grep workbench-rules \"$CLAUDE_MD\""
