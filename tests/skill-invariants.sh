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

echo "handoff:"
check skills/handoff/SKILL.md "boundaries, not percentages" "resets on boundaries, not context %"
check skills/handoff/SKILL.md "tactical"                    "carries tactical state only (durable goes to map/lessons)"

echo "design-handbook:"
check skills/design-handbook/SKILL.md "[Nn]ever touch production code in Phase 1" "no production changes before approval"
check skills/design-handbook/SKILL.md "one recommended"     "<=3 options, one recommended"

echo "explain-and-open-pr:"
check skills/explain-and-open-pr/SKILL.md "never sweep in unrelated" "isolates changes, never sweeps in unrelated work"
check skills/explain-and-open-pr/SKILL.md "[Pp]lain-[Ee]nglish section is mandatory" "plain-English section required"

echo "tdd:"
check skills/tdd/SKILL.md "[Nn]ever write implementation before a failing test" "no code before a failing test"
check skills/tdd/SKILL.md "right reason"                    "red must fail for the right reason"

echo "grilling:"
check skills/grilling/SKILL.md "[Nn]ever answer your own questions" "human-in-the-loop; never self-answers"
check skills/grilling/SKILL.md "[Ii]nterrogate, don't implement" "interrogates, does not build"

echo "agentic-vocabulary:"
check skills/agentic-vocabulary/SKILL.md "inventing a definition" "look up, don't invent, unknown terms"

echo
if [ "$fails" -eq 0 ]; then
  echo "all skill invariants held."
else
  echo "$fails invariant(s) missing — a load-bearing rule was edited out."
fi
exit "$fails"
