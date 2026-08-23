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
  # Repository names. Added 2026-08 after a sweep found EIGHT real repo names in
  # the tracked tree while this list guarded only three brand strings: the guard
  # was watching the wrong class of identifier. Genericized to client-reporting,
  # client-site, client-site-2..4, invoicing-tool, fitness-tracker, inventory-app.
  'senus'
  'achara'
  'pierogals'
  'quadWeb'
  'gscWeb'
  'invoiceToSheet'
  'fitnessTracker'
  'kitchenapp'
)

# Private-repo issue/PR references. The owner's own public repos' numbers are
# allowed; anything else with a
# bare "#NNN" next to a known private context is not expressible as a pattern,
# which is exactly why rule 4 of the sanitization policy exists: genericize at
# write time. These catch the historical classes.
ISSUE_PATTERNS=(
  '#249|#250|#252|#256|#180|#121|#192|#171|#206|#103|#127|#131|#189|#223'
)

have_rg() { command -v rg >/dev/null 2>&1; }

matches=0

# Scan TRACKED files only. The published surface is what git will push, not what
# happens to sit in the working directory: scanning "." also read .git/ and the
# gitignored .research/ clones of real client repos, so this script failed every
# single time it ran. A check that always fails is a check nobody reads, which is
# worse than no check - it was reported as "pre-existing false positive" and
# waved through, twice, while eight real repository names sat in the tracked tree
# unnoticed.
run_search() {
  local label="$1" pattern="$2"
  local out
  if git rev-parse --git-dir >/dev/null 2>&1; then
    out=$(git grep -I -n -i -E -e "$pattern" -- . ':(exclude)scripts/preflight-public.sh' 2>/dev/null)
  elif have_rg; then
    out=$(rg -i -n -e "$pattern" . --glob '!scripts/preflight-public.sh' \
          --glob '!.git' --glob '!.research' 2>/dev/null)
  else
    out=$(grep -rInE -i -e "$pattern" . 2>/dev/null \
          | grep -v 'scripts/preflight-public.sh' \
          | grep -v '^\./\.git/' | grep -v '^\./\.research/')
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
