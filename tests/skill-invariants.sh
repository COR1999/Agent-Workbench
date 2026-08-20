#!/usr/bin/env bash
# Locks each skill's load-bearing rules. If someone edits one of these
# invariants out of a SKILL.md, this fails — the rule can't be silently lost.
#
# Deliberately a handful of invariant-locks, not exhaustive coverage: grep-tests
# on prose get brittle if overused. Only rules that would be dangerous to lose.
#
# Run:  bash tests/skill-invariants.sh   (exit 0 = all held)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fails=0

# check <file> <grep-pattern> <human description>
check() {
  local file="$ROOT/$1" pat="$2" desc="$3"
  if grep -qiE "$pat" "$file" 2>/dev/null; then
    echo "  ok    $desc"
  else
    echo "  FAIL  $desc  ($1 no longer contains /$pat/)"
    fails=$((fails + 1))
  fi
}

echo "sweep-the-class:"
check skills/sweep-the-class/SKILL.md "never edits"        "never edits code (hard anti-scope-explosion constraint)"
check skills/sweep-the-class/SKILL.md "coverage"           "reports a coverage statement"

echo "deslop:"
check skills/deslop/SKILL.md "information, safety, or intent" "G3: never removes information, safety, or intent"
check skills/deslop/SKILL.md "failure-visibility clause"      "keeps the failure-visibility clause"
check skills/deslop/SKILL.md "no dedicated .any. clause"      "no dedicated any gate (any is not a special problem)"

echo "capture-lesson:"
check skills/capture-lesson/SKILL.md "four-part test"      "applies the four-part test"

echo
if [ "$fails" -eq 0 ]; then
  echo "all skill invariants held."
else
  echo "$fails invariant(s) missing — a load-bearing rule was edited out."
fi
exit "$fails"
