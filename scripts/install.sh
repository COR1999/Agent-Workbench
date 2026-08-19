#!/usr/bin/env bash
# Install the skills in this repo into every agent-harness skills dir on this
# machine. Idempotent. Re-run after `git pull` if symlinks are unavailable.
#
# Design note: lessons and rules are NOT installed — they are copied into each
# project's AGENTS.md at adoption time (see README). Only skills install globally.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"

# Harness skill directories. Add more here if you adopt another harness.
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.agents/skills"
)

link_or_copy() {
  # $1 = source skill dir, $2 = destination path
  local src="$1" dst="$2"
  rm -rf "$dst"
  if ln -s "$src" "$dst" 2>/dev/null && [ -e "$dst" ]; then
    echo "  linked  $dst"
  else
    # Windows without symlink privilege, or a filesystem that won't link:
    # fall back to a copy. A copy does NOT update on git pull — re-run this
    # script after pulling. This is the untested Windows path flagged in the
    # design spec; the copy fallback is deliberate, not a bug.
    cp -R "$src" "$dst"
    echo "  copied  $dst   (re-run after 'git pull' to refresh)"
  fi
}

for target in "${TARGETS[@]}"; do
  [ -d "$(dirname "$target")" ] || { echo "skip (no harness): $target"; continue; }
  mkdir -p "$target"
  echo "installing into $target"
  for skill in "$SKILLS_SRC"/*/; do
    [ -f "$skill/SKILL.md" ] || continue
    name="$(basename "$skill")"
    link_or_copy "${skill%/}" "$target/$name"
  done
done

echo "done. Verify a skill resolved: ls -l \"${TARGETS[0]}\""
