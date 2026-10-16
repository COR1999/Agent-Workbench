#!/usr/bin/env bash
# Locks the load-bearing fields of the Claude Code delegation agents.
#
# The agents are config, not code, so nothing fails when a field is edited out:
# a reviewer that gains Edit still loads, a patcher that loses its worktree
# isolation still runs. That is the failure this test exists to make loud.
#
# Run:  bash tests/agents-invariants.sh   (exit 0 = all held)
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$ROOT/adapters/claude-code/agents"
fails=0

ok()   { echo "  ok    $1"; }
fail() { echo "  FAIL  $1"; fails=$((fails + 1)); }

# the frontmatter block only: lines between the first two `---`
front() { awk 'NR==1 && $0!="---"{exit} NR>1 && $0=="---"{exit} NR>1{print}' "$1"; }
field() { front "$1" | grep -E "^$2:" | head -1 | sed -E "s/^$2:[[:space:]]*//"; }

check() { # <file> <field> <extended-regex the value must match> <description>
  local v; v="$(field "$1" "$2")"
  if printf '%s' "$v" | grep -qE "$3"; then ok "$4"; else fail "$4  ($2: '${v}')"; fi
}
body() { grep -qiE "$2" "$1" && ok "$3" || fail "$3  (no /$2/ in $(basename "$1"))"; }

agents="$(find "$DIR" -maxdepth 1 -name '*.md' 2>/dev/null | sort)"
if [ -z "$agents" ]; then
  fail "no agent files found in adapters/claude-code/agents"
fi

for f in $agents; do
  base="$(basename "$f" .md)"
  echo "$base:"
  check "$f" name "^${base}\$"                         "name matches the filename"
  check "$f" description '.{40,}'                      "description long enough to route on"
  check "$f" model '^(haiku|sonnet|opus|fable|inherit)$' "model is a documented alias"
  check "$f" tools '[A-Za-z]'                          "explicit tools allowlist (never inherits every tool)"
  body  "$f" 'managed by Agent-Workbench'              "carries the managed marker (installer will not overwrite a foreign file)"
  case "$base" in workbench-*) ok "name is prefixed, cannot collide with a user's own agent";; *) fail "name must start with workbench-";; esac
done

echo "read-only roles hold no write tools:"
for r in workbench-qa-runner workbench-reviewer; do
  f="$DIR/$r.md"
  if [ -f "$f" ] && ! field "$f" tools | grep -qE 'Edit|Write|NotebookEdit'; then ok "$r has no Edit/Write/NotebookEdit"; else fail "$r must exist and hold no Edit/Write/NotebookEdit"; fi
done

echo "workbench-patcher:"
f="$DIR/workbench-patcher.md"
check "$f" isolation '^worktree$'      "runs in a worktree, never the human's tree"
check "$f" maxTurns '^[0-9]+$'         "bounded by maxTurns"
body  "$f" 'only the files'            "edits only the files it was given"
body  "$f" 'never (commit|push)|do not (commit|push)' "does not commit or push"

echo "workbench-reviewer:"
f="$DIR/workbench-reviewer.md"
check "$f" effort '^(high|xhigh|max)$' "reviews at high effort or above"
body  "$f" 'verified'                  "verdict vocabulary: verified"
body  "$f" 'incorrect'                 "verdict vocabulary: incorrect"
body  "$f" 'unresolved'                "verdict vocabulary: unresolved"

echo "workbench-qa-runner:"
f="$DIR/workbench-qa-runner.md"
check "$f" model '^haiku$'             "runs on the cheap model"
body  "$f" 'focused|narrow'            "narrow checks first"
body  "$f" 'full (suite|test)'         "full suite last"
body  "$f" 'exit code'                 "reports exit codes, not impressions"

echo
if [ "$fails" -eq 0 ]; then echo "all agent invariants held."; else echo "$fails invariant(s) failed."; fi
exit "$fails"
