#!/usr/bin/env bash
# Smoke test for install.sh against a THROWAWAY HOME.
#
# install.sh is the only script that writes outside a project: it installs skills
# into the harness skills directories and copies the machine rules into
# ~/.claude/CLAUDE.md. That made it the one script nobody could test, because
# running it meant modifying the real machine. Overriding HOME removes the excuse.
#
# What it locks:
#   - the rules block is written, and re-running does not duplicate it
#   - a legacy `pas-rules` block is MIGRATED, not appended alongside
#   - content outside the managed block survives
#   - every skill directory ends up installed (symlink or copy — either is fine,
#     the point is that all nine arrive)
#
# The duplicate case is the one worth a test: two copies of the machine rules load
# into every session on the machine, and nothing reports it.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fails=0
ok()   { echo "  ok    $1"; }
fail() { echo "  FAIL  $1"; fails=$((fails + 1)); }
check() { if [ "$2" = "$3" ]; then ok "$1"; else fail "$1 (expected $2, got $3)"; fi; }
count() { local n; n="$(grep -c "$1" "$2" 2>/dev/null | head -1)"; echo "${n:-0}"; }

FAKE_HOME="$TMP/home"
mkdir -p "$FAKE_HOME/.claude"

echo "install.sh — first run into a clean HOME:"
HOME="$FAKE_HOME" bash "$REPO/scripts/install.sh" >/dev/null 2>&1
check "rules block written"        1 "$(count 'workbench-rules:start' "$FAKE_HOME/.claude/CLAUDE.md")"
check "rules block closed"         1 "$(count 'workbench-rules:end' "$FAKE_HOME/.claude/CLAUDE.md")"
expected="$(find "$REPO/skills" -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
# -L because install.sh SYMLINKS the skills when the OS allows it, and find
# will not descend into a symlinked directory without it. Without -L this
# reported 0 skills installed on Linux while reporting 9 on Windows, where
# the copy fallback had run — a difference in the test, not in the subject.
installed="$(find -L "$FAKE_HOME/.claude/skills" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
check "every skill installed" "$expected" "$installed"

echo "install.sh — re-run is idempotent:"
HOME="$FAKE_HOME" bash "$REPO/scripts/install.sh" >/dev/null 2>&1
check "still one rules block" 1 "$(count 'workbench-rules:start' "$FAKE_HOME/.claude/CLAUDE.md")"

echo "install.sh — migrating a legacy pas-rules block:"
LEGACY_HOME="$TMP/legacy-home"
mkdir -p "$LEGACY_HOME/.claude"
{
  printf 'MY-OWN-NOTES-ABOVE\n\n'
  printf '<!-- pas-rules:start — managed by personal-agent-system; edit AGENTS.md at the source and re-run install.sh -->\n'
  printf 'STALE-RULES\n'
  printf '<!-- pas-rules:end -->\n\n'
  printf 'MY-OWN-NOTES-BELOW\n'
} > "$LEGACY_HOME/.claude/CLAUDE.md"
HOME="$LEGACY_HOME" bash "$REPO/scripts/install.sh" >/dev/null 2>&1
check "legacy block gone"            0 "$(count 'pas-rules:start' "$LEGACY_HOME/.claude/CLAUDE.md")"
check "exactly one rules block"      1 "$(count 'workbench-rules:start' "$LEGACY_HOME/.claude/CLAUDE.md")"
check "stale rules content gone"     0 "$(count 'STALE-RULES' "$LEGACY_HOME/.claude/CLAUDE.md")"
check "own notes above survive"      1 "$(count 'MY-OWN-NOTES-ABOVE' "$LEGACY_HOME/.claude/CLAUDE.md")"
check "own notes below survive"      1 "$(count 'MY-OWN-NOTES-BELOW' "$LEGACY_HOME/.claude/CLAUDE.md")"

echo "install.sh — a HOME with no harness directory:"
BARE_HOME="$TMP/bare-home"; mkdir -p "$BARE_HOME"
HOME="$BARE_HOME" bash "$REPO/scripts/install.sh" >/dev/null 2>&1
rc=$?
check "exits 0 rather than failing on an unconfigured machine" 0 "$rc"
check "creates no CLAUDE.md where there is no harness" 0 \
  "$([ -f "$BARE_HOME/.claude/CLAUDE.md" ] && echo 1 || echo 0)"

echo
if [ "$fails" -eq 0 ]; then
  echo "install contract holds."
  exit 0
fi
echo "$fails check(s) failed."
exit 1
