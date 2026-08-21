#!/usr/bin/env bash
# preflight-public.sh — fail if client-identifying material is in the tree.
#
# Run before any push to the public remote:
#   bash scripts/preflight-public.sh
#
# Exit 0 = clean. Exit 1 = at least one pattern matched (paths + lines printed).
# Exit 2 = ripgrep not found and no fallback available.
#
# The denylist holds patterns that should NEVER appear in this public repo.
# When a new class of identifying material is caught by hand, add its pattern
# here so the next catch is mechanical, not remembered.

set -u

PATTERNS=(
  'hotsauce'
  'mama.?amaya'
  'jungle.?sauce'
  'stockist'
  'EXTREME HEAT'
)

# Private-repo issue/PR references. senus-board-report / kitchenapp are the
# owner's own public repos — their numbers are allowed; anything else with a
# bare "#NNN" next to a known private context is not expressible as a pattern,
# which is exactly why rule 4 of the sanitization policy exists: genericize at
# write time. These catch the historical classes.
ISSUE_PATTERNS=(
  '#249|#250|#252|#256|#180|#121|#192|#171|#206|#103|#127|#131|#189|#223'
)

have_rg() { command -v rg >/dev/null 2>&1; }

matches=0

run_search() {
  local label="$1" pattern="$2"
  local out
  if have_rg; then
    out=$(rg -i -n -e "$pattern" . --glob '!scripts/preflight-public.sh' 2>/dev/null)
  else
    out=$(grep -rInE -i -e "$pattern" . 2>/dev/null | grep -v 'scripts/preflight-public.sh')
  fi
  if [ -n "$out" ]; then
    echo "FAIL [$label] pattern: $pattern"
    echo "$out"
    echo
    matches=$((matches + 1))
  fi
}

for p in "${PATTERNS[@]}"; do
  run_search "identifier" "$p"
done

for p in "${ISSUE_PATTERNS[@]}"; do
  run_search "private-ref" "$p"
done

if [ "$matches" -gt 0 ]; then
  echo "preflight-public: $matches pattern group(s) matched. Sanitize before pushing."
  exit 1
fi

echo "preflight-public: clean."
exit 0
