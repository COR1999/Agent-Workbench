#!/usr/bin/env bash
# Locks scripts/spend-scan.py against synthetic transcripts in a THROWAWAY HOME.
#
# The scanner produces the number behind the roadmap's "drop JEV below 20%" rule, so
# the failure modes that matter are the ones that move that number silently:
#   - counting one API response once per content block (inflates spend ~2.4x)
#   - pricing a streaming partial instead of the final usage
#   - zeroing an unknown model instead of surfacing it
#   - treating cache writes as removable, or a user's rejection as a failure
#   - printing anything derived from a command line (it can hold client paths)
#
# Run:  bash tests/spend-scan.sh   (exit 0 = all held)
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fails=0
ok()   { echo "  ok    $1"; }
fail() { echo "  FAIL  $1"; fails=$((fails + 1)); }
check() { if [[ "$2" = "$3" ]]; then ok "$1"; else fail "$1 (expected '$2', got '$3')"; fi; }

# Fixture generator: one scenario per throwaway HOME, so no scenario can leak into another.
cat > "$TMP/fx.py" <<'PYEOF'
import json, pathlib, sys
scenario, home = sys.argv[1], pathlib.Path(sys.argv[2])
folder = home / ".claude" / "projects" / "-p"
folder.mkdir(parents=True, exist_ok=True)
out = folder / "s.jsonl"
T = "2026-10-20T10:00:00.000Z"
n = {"i": 0}

def emit(event):
    with out.open("a") as handle:
        handle.write(json.dumps(event) + "\n")

def step(model="claude-opus-5-5", read=0, w5=0, w1h=0, inp=0, outp=0, think=0,
         blocks=None, events=None, partial=None):
    """One API request. `events` repeats it across several events, as the real store
    does (one per content block). `partial` lists output_tokens of the earlier events."""
    n["i"] += 1
    rid = "req%d" % n["i"]
    blocks = blocks if blocks is not None else [{"type": "text", "text": "ok"}]
    events = events or len(blocks)
    for index in range(events):
        final = index == events - 1
        o = outp if final or not partial else partial[min(index, len(partial) - 1)]
        usage = {"input_tokens": inp, "output_tokens": o, "cache_read_input_tokens": read,
                 "cache_creation_input_tokens": w5 + w1h,
                 "cache_creation": {"ephemeral_5m_input_tokens": w5, "ephemeral_1h_input_tokens": w1h},
                 "output_tokens_details": {"thinking_tokens": think}}
        block = blocks[min(index, len(blocks) - 1)]
        emit({"type": "assistant", "timestamp": T, "cwd": "/x", "requestId": rid,
              "message": {"id": "msg" + rid, "role": "assistant", "model": model,
                          "content": [block], "usage": usage}})

def tool(name, **given):
    n["t"] = n.get("t", 0) + 1          # real tool_use ids are unique per call
    return {"type": "tool_use", "id": "tool%d" % n["t"], "name": name, "input": given}

def bash(command):
    return tool("Bash", command=command)

def result(is_error, text="Exit code 1"):
    emit({"type": "user", "timestamp": T, "cwd": "/x",
          "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t",
                                                   "is_error": is_error, "content": text}]}})

K = 1000
if scenario == "classes":
    step(read=K)                                                   # answer
    step(read=K, blocks=[tool("Read", file_path="a")])             # inspect
    step(read=K, blocks=[bash("SECRETCLIENT=1 cat SECRET-CLIENT-PHRASE.txt | head -5")])  # inspect
    step(read=K, blocks=[bash("bash tests/foo.sh")])               # check
    step(read=K, blocks=[tool("Edit", file_path="a")])             # artifact
    step(read=K, blocks=[bash("git commit -m x")])                 # artifact
    step(read=K, blocks=[bash("python3 - <<'EOF'\nprint(1)\nEOF")])  # program
    step(read=K, blocks=[tool("Agent", subagent_type="Explore", prompt="p")])  # delegate
    result(True)
    step(read=K, blocks=[bash("cat b")])                           # recovery
    result(True, "The user doesn't want to proceed with this tool use. The tool use was rejected")
    step(read=K, blocks=[bash("cat c")])                           # inspect: a rejection is not a failure
    step(read=K, blocks=[bash("somethingweird --x")])              # unclassified
    step(read=K, blocks=[tool("Read", file_path="a"), tool("Edit", file_path="a")])  # artifact beats inspect
    step(read=K, blocks=[bash("ls > /dev/null 2>&1")])             # inspect: /dev/null is not a write
    step(read=K, blocks=[bash("echo hi > out.txt")])               # artifact
    step(read=K, blocks=[bash("cd /tmp && grep -v x notes.md | sed -n 1,9p | cut -c1-80")])   # inspect: cd takes an argument
    step(read=K, blocks=[bash("sed -n 1,5p eslint.config.js; git diff --stat upstream/main")])  # inspect: naming a linter is not running one
    step(read=K, blocks=[bash("cd /tmp && npx eslint src/")])      # check: here the linter IS run
    step(read=K, blocks=[bash("glab mr create --title x")])        # artifact: GitLab's CLI writes too
    step(read=K, blocks=[bash("glab mr view 5")])                  # inspect
    step(read=K, blocks=[bash("echo \"local: $(git rev-parse --short HEAD)\"; echo \"remote: $(git ls-remote origin main | cut -c1-7)\"")])  # inspect
elif scenario == "dedupe":
    # one response, three content blocks, output growing as it streamed: 400k, 700k, 1M
    step(outp=1000000, blocks=[{"type": "text", "text": "a"}, {"type": "text", "text": "b"},
                               {"type": "text", "text": "c"}], partial=[400000, 700000])
elif scenario == "pricing":
    step(read=1000000, w5=1000000, w1h=1000000, outp=1000000)
elif scenario == "tier":
    step(model="claude-haiku-5-5", inp=200000, outp=1000)
    step(model="claude-haiku-5-5", inp=1000, outp=1000)
elif scenario == "unknown":
    step(model="claude-mystery-9", read=5000000, outp=1000)
    step(read=1000000)
elif scenario == "sample":
    for i in range(20):                      # 20 inspect steps: round 0 takes 15, round 1 the other 5
        step(read=K, blocks=[bash("cat file%d" % i)])
elif scenario == "crosscheck":
    step(read=1000000)                       # computed: $0.20
    emit({"type": "cost-state", "sessionId": "s", "totalCostUSD": 0.10})
    emit({"type": "cost-state", "sessionId": "s", "totalCostUSD": 0.25})   # the max per session counts
elif scenario == "removable":
    step(read=1000000, w5=1000000, blocks=[tool("Read", file_path="a")])
elif scenario == "verdict-drop":
    step(read=1000000, blocks=[tool("Edit", file_path="a")])
elif scenario == "verdict-notdrop":
    step(read=1000000, blocks=[tool("Read", file_path="a")])
elif scenario == "verdict-undetermined":
    step(read=100000, blocks=[tool("Read", file_path="a")])
    step(read=100000, blocks=[bash("somethingweird")])
    step(read=800000, blocks=[tool("Edit", file_path="a")])
PYEOF

mkhome() { rm -rf "$TMP/h-$1"; mkdir -p "$TMP/h-$1"; "$PY" -I "$TMP/fx.py" "$1" "$TMP/h-$1"; }
mkdir -p "$TMP/work"; cd "$TMP/work" || exit 1
run() { local s="$1"; shift; HOME="$TMP/h-$s" "$PY" -I "$REPO/scripts/spend-scan.py" --out "out-$s.tsv" "$@" 2>&1; }
line() { printf '%s\n' "$1" | grep -E "$2" | head -1; }

echo "spend-scan — one API response is one step:"
mkhome dedupe; o="$(run dedupe)"
check "three content-block events are one step"        1 "$(printf '%s\n' "$o" | grep -c 'steps: 1 ')"
check "the final streamed usage is priced, not a partial" '$20.0000' "$(line "$o" '^total list-price spend' | grep -o '\$[0-9.]*')"

echo "spend-scan — pricing:"
mkhome pricing; o="$(run pricing)"
check "cache read + 5m write + 1h write + output priced separately" '$33.2000' "$(line "$o" '^total list-price spend' | grep -o '\$[0-9.]*')"
mkhome tier; o="$(run tier)"
check "the Haiku price tier switches at 100k prompt tokens" '$0.1031' "$(line "$o" '^total list-price spend' | grep -o '\$[0-9.]*')"
mkhome unknown; o="$(run unknown)"
check "an unknown model is counted but not priced"       1 "$(printf '%s\n' "$o" | grep -c 'unpriced: 1 step')"
check "...and does not enter the total as zero spend"    '$0.2000' "$(line "$o" '^total list-price spend' | grep -o '\$[0-9.]*')"
check "...and its name is never printed as-is"            0 "$(printf '%s\n' "$o" | grep -c 'mystery')"

echo "spend-scan — classifying steps:"
mkhome classes; o="$(run classes)"
cls() { printf '%s\n' "$o" | grep -cE "^  $1 +steps=$2 "; }
check "answer"       1 "$(cls answer 1)"
check "inspect (Read, env prefix, a rejection, >/dev/null, cd then read, naming a linter, glab view, echo of git reads)" 1 "$(cls inspect 8)"
check "check (a test script, and a linter that is actually run)" 1 "$(cls check 2)"
check "artifact (Edit, git commit, Read+Edit in one step, echo > file, glab mr create)" 1 "$(cls artifact 5)"
check "program (a heredoc into an interpreter)"                               1 "$(cls program 1)"
check "delegate"     1 "$(cls delegate 1)"
check "recovery (only after a real failure)"                                  1 "$(cls recovery 1)"
check "unclassified is reported, never folded into either side"                1 "$(cls unclassified 1)"

echo "spend-scan — privacy:"
check "no command-derived text on stdout"   0 "$(printf '%s\n' "$o" | grep -c 'SECRET')"
check "the TSV holds it (gitignored)"       1 "$([[ "$(grep -c 'SECRET-CLIENT-PHRASE' out-classes.tsv)" -ge 1 ]] && echo 1 || echo 0)"

echo "spend-scan — the computed total is checked against Claude Code's own:"
mkhome crosscheck; o="$(run crosscheck)"
check "the per-session maximum of cost-state is the reference, and the gap is printed" 1 \
  "$(printf '%s\n' "$o" | grep -c 'cost-state totals \$0.2500 over 1 session(s); computed differs by 20.0%')"

echo "spend-scan — what the number may and may not claim:"
mkhome removable; o="$(run removable)"
check "cache writes are not removable: the ceiling excludes them" '3.8%' \
  "$(line "$o" '^fork share \(removable' | grep -o '[0-9.]*%' | head -1)"
check "the ceiling states its own assumptions inline"             1 "$(printf '%s\n' "$o" | grep -c 'free, perfect router')"
check "and says it is not a saving estimate"                      1 "$(printf '%s\n' "$o" | grep -c 'NOT a saving')"
mkhome verdict-drop; o="$(run verdict-drop)"
check "no fork spend: DROP"                  1 "$(printf '%s\n' "$o" | grep -c 'verdict.*: DROP')"
mkhome verdict-notdrop; o="$(run verdict-notdrop)"
check "all fork spend: NOT DROPPED"          1 "$(printf '%s\n' "$o" | grep -c 'verdict.*: NOT DROPPED')"
mkhome verdict-undetermined; o="$(run verdict-undetermined)"
check "band straddles 20%: UNDETERMINED, not a guess" 1 "$(printf '%s\n' "$o" | grep -c 'verdict.*: UNDETERMINED')"

echo "spend-scan — sampling for the validity gate (tune on one round, validate on another):"
mkhome sample
run sample >/dev/null
run sample --sample-round 1 --out out-sample1.tsv >/dev/null
sampled() { "$PY" -I -c "import csv,sys; print(','.join(sorted(r['command'] for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['in_sample']=='1')))" "$1"; }
r0="$(sampled out-sample.tsv)"; r1="$(sampled out-sample1.tsv)"
check "round 0 samples 15 of the 20"                  15 "$(printf '%s' "$r0" | tr ',' '\n' | grep -c .)"
check "round 1 samples the remaining 5"                5 "$(printf '%s' "$r1" | tr ',' '\n' | grep -c .)"
check "the two rounds share no row (a validation sample is unseen)" 0 \
  "$(comm -12 <(printf '%s' "$r0" | tr ',' '\n' | sort) <(printf '%s' "$r1" | tr ',' '\n' | sort) | grep -c .)"

echo "spend-scan — the validity gate: do the rules agree with a human (or an independent labeller)?"
"$PY" -I - <<'PYEOF'
import pathlib
cols = "project session time model class tools command gross removable thinking in_sample label".split()
rows = [["p", "s", "t", "m", c, "Bash", "x", "0", "0", "0", "1", lab] for c, lab in
        [("inspect", "inspect")] * 5 + [("check", "check")] * 3 + [("artifact", "inspect")] * 2 + [("inspect", "?")] * 4]
with open("labelled.tsv", "w") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
PYEOF
o="$(HOME="$TMP/h-empty" "$PY" -I "$REPO/scripts/spend-scan.py" --agreement labelled.tsv 2>&1)"; rc=$?
check "agreement is computed over labelled rows only"  1 "$(printf '%s\n' "$o" | grep -c 'agreement: 80.0% (8 of 10 labelled rows)')"
check "at 80% or above the rules are usable"           1 "$(printf '%s\n' "$o" | grep -c 'rules usable')"
check "the decision-level figure is printed beside it"  1 "$(printf '%s\n' "$o" | grep -c 'decision-level agreement.*80.0%')"
check "a disagreement is reported by class, not text"  1 "$(printf '%s\n' "$o" | grep -c 'artifact: 2 disagreement')"
check "it exits 0 and scans nothing"                   0 "$rc"
"$PY" -I -c "import pathlib; p = pathlib.Path('labelled.tsv'); p.write_text(''.join(l.replace('\t1\tinspect\n', '\t1\tartifact\n') for l in p.read_text().splitlines(True)))"
o="$(HOME="$TMP/h-empty" "$PY" -I "$REPO/scripts/spend-scan.py" --agreement labelled.tsv 2>&1)"
check "below 80% the verdict must not be read"         1 "$(printf '%s\n' "$o" | grep -c 'do not read the verdict')"
HOME="$TMP/h-empty" "$PY" -I "$REPO/scripts/spend-scan.py" --agreement ../labelled.tsv >/dev/null 2>&1; rc=$?
check "--agreement is confined to the working directory too" 1 "$([[ $rc -ne 0 ]] && echo 1 || echo 0)"
o="$(run classes)"
check "every verdict says it is provisional until labelled" 1 "$(printf '%s\n' "$o" | grep -c 'provisional')"

echo "spend-scan — boundaries:"
HOME="$TMP/h-classes" "$PY" -I "$REPO/scripts/spend-scan.py" --out ../escape.tsv >/dev/null 2>&1; rc=$?
check "--out outside the working directory is refused" 1 "$([[ $rc -ne 0 && ! -e "$TMP/escape.tsv" ]] && echo 1 || echo 0)"
mkdir -p "$TMP/h-empty"
o="$(HOME="$TMP/h-empty" "$PY" -I "$REPO/scripts/spend-scan.py" --out out-empty.tsv 2>&1)"; rc=$?
check "a missing store exits 0"              0 "$rc"
check "...and says so"                       1 "$(printf '%s\n' "$o" | grep -c 'MISSING')"

echo
if [[ "$fails" -eq 0 ]]; then echo "spend-scan holds."; else echo "$fails check(s) failed."; fi
exit "$fails"
