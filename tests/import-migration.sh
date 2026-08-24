#!/usr/bin/env bash
# Locks the import contract: adopt.sh and unadopt.sh must handle BOTH the current
# `workbench` markers and the legacy `pas` markers, and must never touch a byte
# outside the managed block.
#
# Why this exists as a test rather than a note: the marker rename was verified by
# hand once. If a future edit drops the legacy prefixes, adopt.sh stops finding an
# old block, appends a SECOND one, and every project adopted before the rename
# ends up carrying two contradictory sets of inlined lessons. Nothing about that
# failure is loud - both blocks are valid markdown and the script exits 0.
#
# No dependencies, no network. Exit 0 = the contract holds.
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fails=0
ok()   { echo "  ok    $1"; }
fail() { echo "  FAIL  $1"; fails=$((fails + 1)); }

check() { # check <description> <expected> <actual>
  if [ "$2" = "$3" ]; then ok "$1"; else fail "$1 (expected $2, got $3)"; fi
}

make_project() { # make_project <dir> <marker-style>
  local dir="$1" style="$2"
  mkdir -p "$dir"
  echo '{"dependencies":{"next":"15.0.0"}}' > "$dir/package.json"
  {
    printf '# a project\n\nCONTENT-ABOVE\n\n'
    if [ "$style" = legacy ]; then
      printf '<!-- pas:start — managed by personal-agent-system; do not edit inside this block -->\n'
      printf '## Inherited from personal-agent-system (v0.2.0, imported 2026-08-20)\nSTALE-BLOCK-CONTENT\n'
      printf '<!-- pas:end -->\n'
    else
      printf '<!-- workbench:start — managed by Agent-Workbench; do not edit inside this block -->\n'
      printf '## Inherited from Agent-Workbench (v0.7.0, imported 2026-08-24)\nSTALE-BLOCK-CONTENT\n'
      printf '<!-- workbench:end -->\n'
    fi
    printf '\nCONTENT-BELOW\n'
  } > "$dir/AGENTS.md"
}

echo "adopt.sh — migrating a legacy block:"
P="$TMP/legacy"; make_project "$P" legacy
bash "$REPO/scripts/adopt.sh" "$P" >/dev/null 2>&1
check "exactly one managed block (no duplicate appended)" 1 "$(grep -c ':start' "$P/AGENTS.md")"
check "legacy marker replaced"                            0 "$(grep -c 'pas:start' "$P/AGENTS.md")"
check "new marker present"                                1 "$(grep -c 'workbench:start' "$P/AGENTS.md")"
check "stale block content gone"                          0 "$(grep -c 'STALE-BLOCK-CONTENT' "$P/AGENTS.md")"
check "content above the block untouched"                 1 "$(grep -c 'CONTENT-ABOVE' "$P/AGENTS.md")"
check "content below the block untouched"                 1 "$(grep -c 'CONTENT-BELOW' "$P/AGENTS.md")"

echo "adopt.sh — idempotency on the current marker:"
bash "$REPO/scripts/adopt.sh" "$P" >/dev/null 2>&1
check "re-run still leaves one block" 1 "$(grep -c ':start' "$P/AGENTS.md")"
check "user content still intact"     2 "$(grep -c 'CONTENT-ABOVE\|CONTENT-BELOW' "$P/AGENTS.md")"

echo "unadopt.sh — removing a current block:"
bash "$REPO/scripts/unadopt.sh" "$P" >/dev/null 2>&1
check "block removed"             0 "$(grep -c ':start' "$P/AGENTS.md")"
check "user content survives"     2 "$(grep -c 'CONTENT-ABOVE\|CONTENT-BELOW' "$P/AGENTS.md")"

echo "unadopt.sh — removing a legacy block:"
L="$TMP/legacy-only"; make_project "$L" legacy
bash "$REPO/scripts/unadopt.sh" "$L" >/dev/null 2>&1
check "legacy block removed"      0 "$(grep -c 'pas:start' "$L/AGENTS.md")"
check "user content survives"     2 "$(grep -c 'CONTENT-ABOVE\|CONTENT-BELOW' "$L/AGENTS.md")"

echo "adopt.sh — a project with no AGENTS.md at all:"
N="$TMP/fresh"; mkdir -p "$N"; echo '{"dependencies":{"next":"15.0.0"}}' > "$N/package.json"
bash "$REPO/scripts/adopt.sh" "$N" >/dev/null 2>&1
check "AGENTS.md created with one block" 1 "$(grep -c 'workbench:start' "$N/AGENTS.md" 2>/dev/null || echo 0)"
check "CLAUDE.md points at AGENTS.md"    1 "$(grep -c '@AGENTS.md' "$N/CLAUDE.md" 2>/dev/null || echo 0)"

echo
if [ "$fails" -eq 0 ]; then
  echo "import contract holds."
  exit 0
fi
echo "$fails check(s) failed."
exit 1
