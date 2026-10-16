#!/usr/bin/env bash
# Locks scripts/delegation-scan.py against synthetic transcripts in a THROWAWAY HOME.
#
# The scanner decides whether the delegation-adapter trial in docs/ROADMAP.md has
# failed, so its failure modes matter more than its happy path. What this pins:
#   - only an UNPROMPTED delegation counts as task-routed: naming the agent, naming
#     its role, or opening the session by pointing at the library each remove it
#   - sessions outside the window, and subagent transcripts, are not counted
#   - stdout is aggregate-only; prompt text appears only in the gitignored TSV
#   - an absent store is reported, not a crash
#
# Run:  bash tests/delegation-scan.sh   (exit 0 = all held)
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fails=0
ok()   { echo "  ok    $1"; }
fail() { echo "  FAIL  $1"; fails=$((fails + 1)); }
check() { if [ "$2" = "$3" ]; then ok "$1"; else fail "$1 (expected '$2', got '$3')"; fi; }

H="$TMP/home"
P="$H/.claude/projects/-proj"
mkdir -p "$P"

# user <file> <ts> <text>
user()  { printf '{"type":"user","timestamp":"%s","cwd":"/x/y","message":{"role":"user","content":[{"type":"text","text":"%s"}]}}\n' "$2" "$3" >> "$1"; }
# delegate <file> <ts> <subagent_type>
deleg() { printf '{"type":"assistant","timestamp":"%s","cwd":"/x/y","message":{"role":"assistant","content":[{"type":"tool_use","id":"t","name":"Agent","input":{"description":"d","prompt":"SECRET-CLIENT-PHRASE","subagent_type":"%s"}}]}}\n' "$2" "$3" >> "$1"; }

D=2026-10-20T10:00:00.000Z
# A: unprompted. An ordinary task, then the model delegates on its own.
user  "$P/a.jsonl" $D "fix the failing build"
deleg "$P/a.jsonl" $D workbench-qa-runner
# B: the human named the agent.
user  "$P/b.jsonl" $D "use workbench-architect to decide how to split this"
deleg "$P/b.jsonl" $D workbench-architect
# C: the human named only its role.
user  "$P/c.jsonl" $D "ask the reviewer to look at this diff"
deleg "$P/c.jsonl" $D workbench-reviewer
# D: opened by pointing at the library, task later. Priming persists.
user  "$P/d.jsonl" $D "use agent workbench methods for this repo"
user  "$P/d.jsonl" $D "now fix the failing build"
deleg "$P/d.jsonl" $D workbench-qa-runner
# E: a built-in, not part of the adapter.
user  "$P/e.jsonl" $D "look into the auth flow"
deleg "$P/e.jsonl" $D general-purpose
# F: before the window. Must not count anywhere.
user  "$P/f.jsonl" 2026-09-01T10:00:00.000Z "fix the failing build"
deleg "$P/f.jsonl" 2026-09-01T10:00:00.000Z workbench-qa-runner
# G: a subagent's own transcript. Not a session.
mkdir -p "$P/a/subagents"
user  "$P/a/subagents/agent-1.jsonl" $D "fix the failing build"
deleg "$P/a/subagents/agent-1.jsonl" $D workbench-qa-runner

run() { HOME="$H" "$PY" -I "$REPO/scripts/delegation-scan.py" --since 2026-10-01 --out "$TMP/out.tsv" "$@" 2>&1; }

echo "delegation-scan — classifying who occasioned each delegation:"
out="$(run)"
totals="$(printf '%s\n' "$out" | grep '^totals:')"
check "one unprompted delegation (A), and only A"          "task=1"            "$(printf '%s' "$totals" | grep -o 'task=[0-9]*')"
check "naming the agent is not unprompted (B)"             "named=1"           "$(printf '%s' "$totals" | grep -o 'named=[0-9]*')"
check "naming only its role is not unprompted (C)"         "role-mentioned=1"  "$(printf '%s' "$totals" | grep -o 'role-mentioned=[0-9]*')"
check "a library-primed session is not unprompted (D)"     "primed=1"          "$(printf '%s' "$totals" | grep -o 'primed=[0-9]*')"

echo "delegation-scan — what is counted at all:"
check "sessions in the window: a-e, not the old one, not the subagent file" "sessions=5" "$(printf '%s' "$totals" | grep -o 'sessions=[0-9]*')"
check "built-in subagents are reported apart from the adapter" 1 "$(printf '%s\n' "$out" | grep -c 'general-purpose')"
check "the pre-window delegation is absent from the TSV" 0 "$(grep -c '2026-09-01' "$TMP/out.tsv")"

echo "delegation-scan — privacy:"
check "stdout carries no prompt text"        0 "$(printf '%s\n' "$out" | grep -c 'SECRET-CLIENT-PHRASE')"
check "the TSV does (it is gitignored)"      1 "$([ "$(grep -c 'SECRET-CLIENT-PHRASE' "$TMP/out.tsv")" -ge 1 ] && echo 1 || echo 0)"

echo "delegation-scan — the roadmap's decision rule:"
check "one unprompted already: zero-by-target can no longer hold, so not triggered" 1 \
  "$(printf '%s\n' "$out" | grep -c 'rule: not triggered')"
out2="$(run --target 5)"
check "target reached with one unprompted: not triggered" 1 "$(printf '%s\n' "$out2" | grep -c 'rule: not triggered')"
H2="$TMP/home2"; mkdir -p "$H2/.claude/projects/-p"
printf '{"type":"user","timestamp":"%s","cwd":"/x","message":{"role":"user","content":[{"type":"text","text":"fix the failing build"}]}}\n' "$D" > "$H2/.claude/projects/-p/s.jsonl"
out3="$(HOME="$H2" "$PY" -I "$REPO/scripts/delegation-scan.py" --since 2026-10-01 --target 1 --out "$TMP/o3.tsv" 2>&1)"
check "target reached with none unprompted: TRIGGERED"    1 "$(printf '%s\n' "$out3" | grep -c 'rule: TRIGGERED')"
out3b="$(HOME="$H2" "$PY" -I "$REPO/scripts/delegation-scan.py" --since 2026-10-01 --target 35 --out "$TMP/o3b.tsv" 2>&1)"
check "below target with none unprompted: not yet"        1 "$(printf '%s\n' "$out3b" | grep -c 'rule: not yet')"

echo "delegation-scan — the window has time-of-day precision (agents load at session start):"
H4="$TMP/home4"; mkdir -p "$H4/.claude/projects/-p"
printf '{"type":"user","timestamp":"2026-10-20T09:00:00.000Z","cwd":"/x","message":{"role":"user","content":[{"type":"text","text":"fix the failing build"}]}}\n' > "$H4/.claude/projects/-p/early.jsonl"
printf '{"type":"user","timestamp":"2026-10-20T11:00:00.000Z","cwd":"/x","message":{"role":"user","content":[{"type":"text","text":"fix the failing build"}]}}\n' > "$H4/.claude/projects/-p/late.jsonl"
out5="$(HOME="$H4" "$PY" -I "$REPO/scripts/delegation-scan.py" --since 2026-10-20T10:00:00 --out "$TMP/o5.tsv" 2>&1)"
check "a session started before the install time that day is not counted" "sessions=1" \
  "$(printf '%s\n' "$out5" | grep '^totals:' | grep -o 'sessions=[0-9]*')"
out6="$(HOME="$H4" "$PY" -I "$REPO/scripts/delegation-scan.py" --since 2026-10-20 --out "$TMP/o6.tsv" 2>&1)"
check "a bare date still means midnight UTC"                              "sessions=2" \
  "$(printf '%s\n' "$out6" | grep '^totals:' | grep -o 'sessions=[0-9]*')"
HOME="$H4" "$PY" -I "$REPO/scripts/delegation-scan.py" --since nonsense --out "$TMP/o7.tsv" >/dev/null 2>&1
check "a malformed --since exits non-zero rather than counting everything" 1 "$([ $? -ne 0 ] && echo 1 || echo 0)"

echo "delegation-scan — a missing store is reported, not a crash:"
H3="$TMP/home3"; mkdir -p "$H3"
out4="$(HOME="$H3" "$PY" -I "$REPO/scripts/delegation-scan.py" --out "$TMP/o4.tsv" 2>&1)"; rc=$?
check "exits 0 with no ~/.claude"            0 "$rc"
check "says the store is missing"            1 "$(printf '%s\n' "$out4" | grep -c 'MISSING')"
check "says no install was detected"         1 "$(printf '%s\n' "$out4" | grep -c 'not detected')"

echo
if [ "$fails" -eq 0 ]; then echo "delegation-scan holds."; else echo "$fails check(s) failed."; fi
exit "$fails"
