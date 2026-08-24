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

# grep -c prints 0 AND exits 1 when there are no matches, so a `grep -c ... || echo 0`
# fallback emits two zeroes on separate lines and every zero-expecting check then
# fails on a value that was actually correct. Always count through this helper.
count() { # count <pattern> <file>
  local n
  n="$(grep -c "$1" "$2" 2>/dev/null | head -1)"
  echo "${n:-0}"
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
check "AGENTS.md created with one block" 1 "$(count 'workbench:start' "$N/AGENTS.md")"
check "CLAUDE.md points at AGENTS.md"    1 "$(count '@AGENTS.md' "$N/CLAUDE.md")"

echo "adopt.sh — stack detection, positive and negative:"
# postgres and webhooks were declared in the lesson vocabulary long before
# adopt.sh could detect them, so any lesson using them was unreachable and
# nothing said so. Both directions are asserted: a detector that fires on
# everything is as useless as one that never fires.
D="$TMP/detect"; mkdir -p "$D/src/app/api/webhook" "$D/supabase/migrations"
printf '{"dependencies":{"next":"15.0.0","pg":"^8.11.0"}}\n' > "$D/package.json"
printf 'export async function POST(r){ r.headers.get("stripe-signature"); }\n' \
  > "$D/src/app/api/webhook/route.ts"
printf 'create table t (id int);\n' > "$D/supabase/migrations/0001_init.sql"
stack="$(bash "$REPO/scripts/adopt.sh" "$D" 2>/dev/null | sed -n 's/^  stack: *//p')"
case "$stack" in *postgres*) ok "postgres detected";; *) fail "postgres not detected";; esac
case "$stack" in *webhooks*) ok "webhooks detected";; *) fail "webhooks not detected";; esac

B="$TMP/bare"; mkdir -p "$B"
printf '{"dependencies":{"next":"15.0.0"}}\n' > "$B/package.json"
bare="$(bash "$REPO/scripts/adopt.sh" "$B" 2>/dev/null | sed -n 's/^  stack: *//p')"
case "$bare" in *postgres*) fail "postgres false positive on a bare project";; *) ok "no postgres false positive";; esac
case "$bare" in *webhooks*) fail "webhooks false positive on a bare project";; *) ok "no webhooks false positive";; esac

echo "adopt.sh — lesson status is honoured:"
# README's staleness table has always said a superseded lesson must never inline.
# Nothing read the status field until 2026-08, so a claim proven FALSE would have
# kept being copied into every matching project. Both directions asserted: the
# superseded one is excluded, and ordinary ones for the same stack still arrive.
ST="$TMP/status"; mkdir -p "$ST"
printf '{"dependencies":{"next":"15.0.0","react":"18.0.0"}}\n' > "$ST/package.json"
bash "$REPO/scripts/adopt.sh" "$ST" >/dev/null 2>&1
superseded="$(grep -l '^status: *superseded' "$REPO"/lessons/*.md 2>/dev/null | head -1)"
if [ -n "$superseded" ]; then
  slug="$(basename "$superseded" .md)"
  check "superseded lesson is not inlined" 0 "$(count "$slug" "$ST/AGENTS.md")"
else
  ok "no superseded lesson in the ledger to exclude"
fi
check "other lessons for the stack still inline" 1 \
  "$([ "$(count '^- \*\*' "$ST/AGENTS.md")" -gt 0 ] && echo 1 || echo 0)"

echo "adopt.sh — hostile paths and file shapes:"
# These were raised as "harden adopt.sh" (#27). Testing first found the script
# already handled all of them, so what was missing was not hardening but proof
# that it stays handled. A path with spaces and a CRLF AGENTS.md are the two most
# likely shapes on the machine this runs on.
S="$TMP/a project (v2)"; mkdir -p "$S"
printf '{"dependencies":{"next":"15.0.0"}}\n' > "$S/package.json"
bash "$REPO/scripts/adopt.sh" "$S" >/dev/null 2>&1
check "path with spaces and parentheses" 1 "$(count ':start' "$S/AGENTS.md")"
bash "$REPO/scripts/unadopt.sh" "$S" >/dev/null 2>&1
check "unadopt on a path with spaces"    0 "$(count ':start' "$S/AGENTS.md")"

C="$TMP/crlf"; mkdir -p "$C"
printf '{"dependencies":{"next":"15.0.0"}}\n' > "$C/package.json"
printf '# p\r\n\r\nCRLF-ABOVE\r\n\r\n<!-- workbench:start — managed by Agent-Workbench; do not edit inside this block -->\r\nOLD\r\n<!-- workbench:end -->\r\n\r\nCRLF-BELOW\r\n' > "$C/AGENTS.md"
bash "$REPO/scripts/adopt.sh" "$C" >/dev/null 2>&1
check "CRLF file: one block after migration" 1 "$(grep -c ':start' "$C/AGENTS.md")"
check "CRLF file: old block content gone"    0 "$(grep -c 'OLD' "$C/AGENTS.md")"
check "CRLF file: user content survives"     2 "$(grep -c 'CRLF-ABOVE\|CRLF-BELOW' "$C/AGENTS.md")"

W="$TMP/nonewline"; mkdir -p "$W"
printf '{"dependencies":{"next":"15.0.0"}}\n' > "$W/package.json"
printf '# p\n\nNO-TRAILING-NEWLINE' > "$W/AGENTS.md"
bash "$REPO/scripts/adopt.sh" "$W" >/dev/null 2>&1
check "file with no trailing newline: content kept" 1 "$(grep -c 'NO-TRAILING-NEWLINE' "$W/AGENTS.md")"
check "file with no trailing newline: one block"    1 "$(grep -c ':start' "$W/AGENTS.md")"

# A script that fails silently is worse than one that fails loudly.
bash "$REPO/scripts/adopt.sh" "$TMP/no-such-dir" >/dev/null 2>&1
check "nonexistent project exits non-zero" 1 "$?"
bash "$REPO/scripts/adopt.sh" >/dev/null 2>&1
check "adopt with no argument exits non-zero" 1 "$?"
bash "$REPO/scripts/unadopt.sh" >/dev/null 2>&1
check "unadopt with no argument exits non-zero" 1 "$?"

echo
if [ "$fails" -eq 0 ]; then
  echo "import contract holds."
  exit 0
fi
echo "$fails check(s) failed."
exit 1
