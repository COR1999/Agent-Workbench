#!/usr/bin/env python3
"""What share of real token spend goes on fork-like steps, and what may that number claim?

Why this exists: docs/ROADMAP.md makes JEV integration conditional on measurement 1:
"what fraction of real spend goes on fork-like turns, computed locally. If it is under
20%, JEV integration is dropped." This is that measurement, built to the design an
independent architect-agent run produced after checking the real store.

Definitions that decide the answer (change them and the verdict can flip):

  STEP     one API request. A response is stored once per content block, so usage is
           repeated across events and naive summing overcounts about 2.4x. Steps are
           deduped on requestId, keeping the field-wise MAXIMUM (a streamed response's
           earlier events carry partial output_tokens; the last equals the max).

  CLASS    each step takes the FIRST class that applies, in this order:
             answer      no tool call
             artifact    writes something (Edit/Write, or a Bash write)
             program     Bash running an inline script (JEV cannot write code)
             delegate    Agent/Task
             recovery    the previous tool result was a real failure (a user
                         rejection is not one)
             check       Bash that only runs a recognised check
             inspect     only read-only tools or commands
             unclassified  anything else - an uncertainty band, never silently put on
                         either side
           Fork-like = recovery, check, inspect.

  COST     list price per step from the usage fields, with 5-minute and 1-hour cache
           writes priced separately and the Haiku tier chosen by prompt size. A model
           missing from the price table is COUNTED but not priced - never zeroed.

Three ceilings, and none is called a saving:

  gross          everything a fork-like step cost. A cap, but a loose one.
  removable      gross minus cache WRITES. If a router skipped step k, the context
                 delta k would have cached is written by step k+1 instead: writes are
                 deferred, not removed. This is the number the 20% rule reads. Still an
                 upper bound: it assumes a free, perfect router that never escalates.
  deliberation   thinking tokens priced as output: what remains if the large model must
                 still write the arguments.

Verdict, on the removable basis, with the unclassified band as the range:
  DROP             the high end is under 20%
  NOT DROPPED      the low end is 20% or more (it goes on to measurement 2)
  UNDETERMINED     otherwise: hand-label the in_sample rows before reading anything

Honesty about how this was set: the architect ran a crude draft classifier on the real
store BEFORE this definition was fixed, and saw figures either side of 20%. So "fixed
before the number exists" holds for the 20% threshold but not for the definition, and
the roadmap says so.

Privacy: stdout prints only fixed class labels and numbers. A Bash command can hold a
client path and an MCP tool name carries a product name, so nothing derived from either
is printed; they go to the gitignored TSV, which --out confines to the working directory.

stdlib only. Usage:
  python scripts/spend-scan.py [--since YYYY-MM-DD[THH:MM:SS]] [--out .usage/spend.tsv]
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import re
import shlex
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("delegation_scan", HERE / "delegation-scan.py")
dscan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dscan)

HOME = pathlib.Path.home()

# USD per million tokens. Source: the Anthropic pricing page, read 2026-10-16. The page
# footnote on cache-hit prices was not read. A list-price equivalent: if the account is on
# a subscription this is notional, not an invoice. Models absent here are surfaced as
# unpriced. Tiers: (prompt-token ceiling, prices); None = no ceiling.
PRICES_CHECKED = "2026-10-16"
PRICES = {
    "claude-opus-5-5": [(None, dict(inp=4.0, w5=5.0, w1h=8.0, hit=0.20, out=20.0))],
    "claude-sonnet-5-5": [(None, dict(inp=2.0, w5=2.5, w1h=4.0, hit=0.10, out=10.0))],
    "claude-haiku-5-5": [
        (100000, dict(inp=0.10, w5=0.125, w1h=0.20, hit=0.01, out=0.50)),
        (None, dict(inp=0.50, w5=0.625, w1h=1.0, hit=0.05, out=2.50)),
    ],
}

CLASSES = ["answer", "artifact", "program", "delegate", "recovery", "check", "inspect",
           "unclassified"]
FORK = ("recovery", "check", "inspect")
THRESHOLD = 20.0   # percent; fixed in docs/ROADMAP.md before any figure existed
SAMPLE_PER_CLASS = 15

TSV_COLUMNS = ["project", "session", "time", "model", "class", "tools", "command",
               "gross", "removable", "thinking", "in_sample", "label"]
TSV_HEADER = "\t".join(TSV_COLUMNS)

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
READ_TOOLS = {"Read", "Grep", "Glob", "LS", "WebFetch", "WebSearch", "ToolSearch"}
DELEGATE_TOOLS = {"Agent", "Task"}
REJECTION = ("doesn't want to proceed", "was rejected", "user rejected",
             "interrupted by user", "request interrupted")

READ_VERBS = {
    "cat", "head", "tail", "grep", "egrep", "fgrep", "rg", "ugrep", "ls", "wc", "stat", "file",
    "diff", "cmp", "sort", "uniq", "cut", "tr", "awk", "echo", "printf", "pwd", "which",
    "command", "type", "true", "date", "whoami", "id", "uname", "printenv", "basename",
    "dirname", "realpath", "readlink", "du", "df", "tree", "jq", "xxd", "od", "strings",
    "column", "seq", "test", "[", "[[", "sleep", "nl", "tac", "rev", "paste", "comm", "hexdump",
}
# A segment led by one of these changes shell state and does nothing else: skip it whole.
# (Stripping only the verb left `cd /tmp` reading as a command called "/tmp", which
# made every `cd dir && grep ...` unclassified.)
SKIP_SEGMENT = {"cd", "pushd", "popd", "export", "set", "unset", "source", ".", ":", "shopt"}
WRAPPERS = {"sudo", "time", "nohup", "env", "exec"}
WRITE_VERBS = {"mkdir", "cp", "mv", "rm", "rmdir", "touch", "chmod", "chown", "ln", "tee",
               "install", "truncate", "dd", "kill", "pkill", "mktemp"}
GIT_READ = {"status", "log", "diff", "show", "rev-parse", "ls-files", "ls-remote", "remote",
            "describe", "blame", "shortlog", "cat-file", "merge-base", "fetch", "grep",
            "rev-list", "for-each-ref", "show-ref", "name-rev", "count-objects"}
GH_READ = {"view", "list", "checks", "diff", "status", "watch", "get", "show"}
FORGE_CLIS = {"gh", "glab"}
FORGE_GROUPS = {"pr", "mr", "issue", "release", "repo", "run", "ci", "pipeline"}
CHECK_PATTERNS = re.compile(
    r"(?:^|[\s/])tests?/[\w./-]*\.(?:sh|py)\b|\bpytest\b|\bnpm\s+(?:run\s+)?(?:test|lint|typecheck|build)\b"
    r"|\bvitest\b|\bjest\b|\bshellcheck\b|preflight|lesson-audit|\btsc\b|\beslint\b"
    r"|\bcargo\s+(?:test|check|clippy)\b|\bgo\s+(?:test|vet)\b|\bmake\s+(?:test|check|lint)\b"
    r"|\bruff\b|\bmypy\b|\bflake8\b")
PROGRAM_PATTERNS = re.compile(
    r"<<|\b(?:python3?|node|ruby|perl|bash|sh|zsh)\s+-[ce]\b|\bfor\s+\w+\s+in\b"
    r"|\bwhile\s+(?:read|true|false|\[|\(|:)")


def strip_noise(command):
    """Drop redirects to /dev/null and fd duplication, which are not writes."""
    # `\d?` and not `\d*`: a file descriptor is one digit, and an unbounded run retried at
    # every start position is quadratic on a long digit string (transcripts are untrusted).
    return re.sub(r"\d?>\s*&\d|&>\s*/dev/null|\d?>>?\s*/dev/null", " ", command)


def without_quotes(command):
    return re.sub(r"'[^']*'|\"[^\"]*\"", "''", command)


def segments(command):
    return [seg.strip() for seg in re.split(r"&&|\|\||;|\||\n", command) if seg.strip()]


def tokens_of(segment):
    try:
        parts = shlex.split(segment)
    except ValueError:
        parts = segment.split()
    while parts:
        head = parts[0]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", head) or head in WRAPPERS:
            parts = parts[1:]
        elif head == "timeout":
            parts = parts[2:]
        else:
            break
    return [] if parts and parts[0] in SKIP_SEGMENT else parts


def bash_writes(command):
    """True if the command writes something (a file, a repo, a remote)."""
    cleaned = without_quotes(strip_noise(command))
    if re.search(r"(?<![-=<>])>{1,2}(?![>=])", cleaned):
        return True
    for seg in segments(cleaned):
        parts = tokens_of(seg)
        if not parts:
            continue
        verb = pathlib.PurePosixPath(parts[0]).name
        rest = parts[1:]
        if verb in WRITE_VERBS:
            return True
        if verb == "sed" and any(a == "-i" or a.startswith("-i") or a == "--in-place" for a in rest):
            return True
        if verb == "git" and rest:
            sub = rest[0]
            if sub in GIT_READ:
                continue
            if sub == "branch":
                if any(a in ("-d", "-D", "-m", "-M") for a in rest) or any(not a.startswith("-") for a in rest[1:]):
                    return True
                continue
            if sub == "config" and any(a in ("--get", "--list", "-l") for a in rest):
                continue
            return True
        if verb in FORGE_CLIS and len(rest) >= 2 and rest[0] in FORGE_GROUPS:
            if rest[1] not in GH_READ:
                return True
        if verb in FORGE_CLIS and rest and rest[0] == "api" and any(
                a in ("-X", "--method") and nxt.upper() != "GET"
                for a, nxt in zip(rest, rest[1:] + [""])):
            return True
        if verb == "curl" and any(a in ("-X", "-d", "--data", "--data-raw", "-F", "-T", "-o", "-O")
                                  for a in rest):
            return True
        if verb in ("npm", "pip", "pip3", "apt", "dnf", "brew", "cargo", "go") and rest and \
                rest[0] in ("install", "i", "add", "remove", "uninstall", "publish", "get"):
            return True
    return False


def bash_read_only(command):
    """True only if every segment is a recognised read-only verb (neutral ones allowed)."""
    seen_read = False
    for seg in segments(without_quotes(strip_noise(command))):
        parts = tokens_of(seg)
        if not parts:
            continue
        verb = pathlib.PurePosixPath(parts[0]).name
        rest = parts[1:]
        if verb in READ_VERBS:
            seen_read = True
        elif verb == "sed" and not any(a.startswith("-i") or a == "--in-place" for a in rest):
            seen_read = True
        elif verb == "find" and not any(a in ("-delete", "-exec", "-execdir", "-fprint", "-ok")
                                        for a in rest):
            seen_read = True
        elif verb == "git" and rest and (rest[0] in GIT_READ or (
                rest[0] == "branch" and not bash_writes(seg))):
            seen_read = True
        elif verb in FORGE_CLIS and len(rest) >= 2 and rest[0] in FORGE_GROUPS and rest[1] in GH_READ:
            seen_read = True
        elif verb in FORGE_CLIS and rest and rest[0] == "api" and not bash_writes(seg):
            seen_read = True
        elif verb == "curl" and not bash_writes(seg):
            seen_read = True
        else:
            return False
    return seen_read


def bash_runs_check(command):
    """True if some segment RUNS a recognised check. A reader that merely names one
    (`sed -n 1,5p eslint.config.js`) does not: matching the text anywhere scored those
    as check runs, found when an independent labeller disagreed."""
    for seg in segments(strip_noise(command)):
        parts = tokens_of(seg)
        if not parts:
            continue
        verb = pathlib.PurePosixPath(parts[0]).name
        if verb in READ_VERBS or verb in ("sed", "find", "git", "gh", "glab", "curl"):
            continue
        if CHECK_PATTERNS.search(seg):
            return True
    return False


def call_class(name, given):
    """The class one tool call belongs to, ignoring recovery (which is about context)."""
    if name in WRITE_TOOLS:
        return "artifact"
    if name in DELEGATE_TOOLS:
        return "delegate"
    if name in READ_TOOLS:
        return "inspect"
    if name == "Bash":
        command = str((given or {}).get("command") or "")
        if bash_writes(command):
            return "artifact"
        if PROGRAM_PATTERNS.search(command):
            return "program"
        if bash_runs_check(command):
            return "check"
        if bash_read_only(command):
            return "inspect"
    return "unclassified"


def classify_step(calls, after_failure):
    if not calls:
        return "answer"
    classes = [call_class(name, given) for name, given in calls]
    for wanted in ("artifact", "program", "delegate"):
        if wanted in classes:
            return wanted
    if after_failure:
        return "recovery"
    if "check" in classes:
        return "check"
    if all(c == "inspect" for c in classes):
        return "inspect"
    return "unclassified"


def price_for(model, prompt_tokens):
    tiers = PRICES.get(model)
    if not tiers:
        return None
    for ceiling, prices in tiers:
        if ceiling is None or prompt_tokens <= ceiling:
            return prices
    return None


def usage_fields(usage):
    cache = usage.get("cache_creation") or {}
    w5 = cache.get("ephemeral_5m_input_tokens")
    w1h = cache.get("ephemeral_1h_input_tokens")
    if w5 is None and w1h is None:
        w5, w1h = usage.get("cache_creation_input_tokens") or 0, 0
    details = usage.get("output_tokens_details") or {}
    return {
        "inp": usage.get("input_tokens") or 0,
        "read": usage.get("cache_read_input_tokens") or 0,
        "w5": w5 or 0, "w1h": w1h or 0,
        "out": usage.get("output_tokens") or 0,
        "think": details.get("thinking_tokens") or 0,
    }


def cost_of(model, fields):
    prices = price_for(model, fields["inp"] + fields["read"] + fields["w5"] + fields["w1h"])
    if prices is None:
        return None
    m = 1e6
    parts = {
        "read": fields["read"] * prices["hit"] / m,
        "write": (fields["w5"] * prices["w5"] + fields["w1h"] * prices["w1h"]) / m,
        "inp": fields["inp"] * prices["inp"] / m,
        "out": fields["out"] * prices["out"] / m,
        "think": min(fields["think"], fields["out"]) * prices["out"] / m,
    }
    parts["gross"] = parts["read"] + parts["write"] + parts["inp"] + parts["out"]
    parts["removable"] = parts["gross"] - parts["write"]
    return parts


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") if isinstance(b, dict) and isinstance(b.get("text"), str)
                        else (b.get("content", "") if isinstance(b, dict) and isinstance(b.get("content"), str) else "")
                        for b in content)
    return ""


def merge_max(into, new):
    for key, value in new.items():
        if isinstance(value, dict):
            merge_max(into.setdefault(key, {}), value)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            if value > into.get(key, 0):
                into[key] = value
    return into


def read_store(files, since_epoch):
    """Deduped steps and cost-state totals from every transcript file."""
    steps, cost_state = {}, {}
    events = partial_ids = 0
    for path in files:
        subagent = path.parent.name == "subagents"
        session = path.parent.parent.name if subagent else path.stem
        project = path.parent.parent.parent.name if subagent else path.parent.name
        pending_failure = False
        try:
            handle = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                kind = event.get("type")
                if kind == "cost-state":
                    sid = event.get("sessionId") or session
                    total = event.get("totalCostUSD")
                    if isinstance(total, (int, float)):
                        cost_state[sid] = max(cost_state.get(sid, 0.0), float(total))
                    continue
                message = event.get("message") or {}
                content = message.get("content")
                if kind == "user" and isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_result" \
                                and block.get("is_error") is True:
                            low = text_of(block.get("content")).lower()
                            if not any(marker in low for marker in REJECTION):
                                pending_failure = True
                    continue
                usage = message.get("usage")
                model = message.get("model")
                if kind != "assistant" or not isinstance(usage, dict) or not model \
                        or model == "<synthetic>":
                    continue
                events += 1
                key = event.get("requestId") or message.get("id")
                if not key:
                    continue
                stamp = event.get("timestamp", "")
                step = steps.get(key)
                if step is None:
                    epoch = dscan.scan.iso_to_epoch(stamp)
                    step = steps[key] = {
                        "usage": {}, "model": model, "calls": [], "ids": set(), "events": 0,
                        "after_failure": pending_failure, "session": session, "project": project,
                        "time": stamp, "epoch": epoch, "subagent": subagent, "outs": set(),
                    }
                    pending_failure = False
                step["events"] += 1
                step["outs"].add(usage.get("output_tokens"))
                merge_max(step["usage"], usage)
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            ident = block.get("id") or id(block)
                            if ident not in step["ids"]:
                                step["ids"].add(ident)
                                step["calls"].append((block.get("name") or "", block.get("input") or {}))
    partial_ids = sum(1 for s in steps.values() if len(s["outs"]) > 1)
    kept = {k: s for k, s in steps.items() if s["epoch"] >= since_epoch}
    return kept, cost_state, events, partial_ids


def pct(part, whole):
    return 100.0 * part / whole if whole > 0 else 0.0


def side(klass):
    return "fork" if klass in FORK else ("unclassified" if klass == "unclassified" else "non-fork")


AGREEMENT_FLOOR = 80.0   # percent; below this the classes are not trusted, whatever they say


def agreement(path_text):
    """Compare a labelled copy of the spend TSV against the rules, and say what follows.

    The verdict is only as good as the classifier behind it, and the classifier is a list
    of Bash verbs. Labelling the in_sample rows (by hand or by an independent labeller that
    never saw the rules' class) and running this is the gate before the verdict is read.
    """
    try:
        target = dscan.resolve_out(path_text, TSV_HEADER)
    except (ValueError, OSError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2
    if not target.is_file():
        print("error: no such file: " + str(target), file=sys.stderr)
        return 2
    with target.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    labelled = [r for r in rows if (r.get("label") or "?") not in ("?", "")]
    if not labelled:
        print("agreement: no labelled rows in " + str(target) + ": nothing to compare")
        return 0
    agree = sum(1 for r in labelled if r["label"] == r["class"])
    share = pct(agree, len(labelled))
    print("agreement: %.1f%% (%d of %d labelled rows)" % (share, agree, len(labelled)))
    same_side = sum(1 for r in labelled if side(r["label"]) == side(r["class"]))
    print("decision-level agreement (fork / non-fork / unclassified, which is what the verdict "
          "depends on): %.1f%% (%d of %d). Informational: the gate below stays on the strict figure."
          % (pct(same_side, len(labelled)), same_side, len(labelled)))
    wrong = Counter(r["class"] for r in labelled if r["label"] != r["class"])
    for klass, count in sorted(wrong.items(), key=lambda kv: (-kv[1], kv[0])):
        print("  %s: %d disagreement(s) (the rules said %s; the label differed)" % (klass, count, klass))
    if share >= AGREEMENT_FLOOR:
        print("rules usable (>= %.0f%%): the verdict may be read, still provisional on the router "
              "measurements" % AGREEMENT_FLOOR)
    else:
        print("do not read the verdict: agreement is under %.0f%%. Fix the classes, then relabel."
              % AGREEMENT_FLOOR)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--since", help="YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS (UTC). Default: all of it.")
    parser.add_argument("--out", default=".usage/spend.tsv",
                        help="TSV of every step. May contain client text; confined to the working directory.")
    parser.add_argument("--sample-round", type=int, default=0, metavar="N",
                        help="Which slice of each class is marked in_sample for hand-labelling. "
                             "Tune the classes on round 0; validate on round 1, which shares no row with it.")
    parser.add_argument("--agreement", metavar="TSV",
                        help="Compare the label column of an existing spend TSV with the rules, then exit.")
    args = parser.parse_args()
    if args.agreement:
        return agreement(args.agreement)
    try:
        out = dscan.resolve_out(args.out, TSV_HEADER)
    except (ValueError, OSError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2
    since_epoch = 0
    if args.since:
        try:
            since_epoch = dscan.parse_since(args.since).timestamp()
        except ValueError:
            print("error: --since must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS", file=sys.stderr)
            return 2

    projects = HOME / ".claude" / "projects"
    print("spend-scan")
    print("stores:")
    files = (sorted(projects.glob("*/*.jsonl")) + sorted(projects.glob("*/*/subagents/*.jsonl"))
             if projects.is_dir() else [])
    print("  claude-family jsonl  %s  %s  (%d files, including subagent transcripts)"
          % (projects, "OK" if projects.is_dir() else "MISSING", len(files)))
    print("  opencode sqlite      not scanned: the delegation adapter is Claude Code only")
    print("window: " + (args.since + " onward (UTC)" if args.since else "everything in the store"))

    steps, cost_state, events, partial_ids = read_store(files, since_epoch)
    print("step = one API request, deduped by requestId, field-wise max usage kept")
    print("steps: %d (from %d usage events; %d with streaming partials)"
          % (len(steps), events, partial_ids))
    print("pricing: list prices checked %s; a list-price equivalent, notional on a subscription"
          % PRICES_CHECKED)

    per_class = {c: Counter() for c in CLASSES}
    split = Counter()
    by_session = Counter()
    unpriced = Counter()
    rows = []
    for key, step in steps.items():
        fields = usage_fields(step["usage"])
        klass = classify_step(step["calls"], step["after_failure"])
        costs = cost_of(step["model"], fields)
        if costs is None:
            unpriced[step["model"]] += 1
            continue
        bucket = per_class[klass]
        bucket["steps"] += 1
        for name in ("gross", "removable", "think"):
            bucket[name] += costs[name]
        for name in ("read", "write", "inp", "out", "think"):
            split[name] += costs[name]
        by_session[step["session"]] += costs["gross"]
        names = [name for name, _ in step["calls"]]
        command = " ; ".join(str((given or {}).get("command", ""))[:160]
                             for name, given in step["calls"] if name == "Bash")
        rows.append([step["project"], step["session"], step["time"], step["model"], klass,
                     ",".join(names), dscan.scan.snippet(command), "%.6f" % costs["gross"],
                     "%.6f" % costs["removable"], "%.6f" % costs["think"], "0", "?", key])

    priced_steps = sum(c["steps"] for c in per_class.values())
    total = sum(c["gross"] for c in per_class.values())
    unpriced_n = sum(unpriced.values())
    if unpriced_n:
        print("unpriced: %d step(s) on %d unrecognised model(s); tokens counted, cost unknown, "
              "excluded from every figure below" % (unpriced_n, len(unpriced)))
    print("priced steps: %d" % priced_steps)
    print("total list-price spend: $%.4f (priced steps only)" % total)

    if cost_state and not args.since:
        theirs = sum(cost_state.values())
        diff = pct(abs(theirs - total), theirs) if theirs else 0.0
        print("cross-check: Claude Code's own cost-state totals $%.4f over %d session(s); "
              "computed differs by %.1f%%" % (theirs, len(cost_state), diff))
    else:
        print("cross-check: not available" + (" with --since" if args.since else ": no cost-state events"))

    if total > 0:
        print("spend split: cache read $%.4f (%.0f%%) | cache write $%.4f (%.0f%%) | uncached input "
              "$%.4f (%.0f%%) | output $%.4f (%.0f%%, of which thinking $%.4f)"
              % (split["read"], pct(split["read"], total), split["write"], pct(split["write"], total),
                 split["inp"], pct(split["inp"], total), split["out"], pct(split["out"], total),
                 split["think"]))
    print()
    print("classes (first applicable, in this order):")
    for klass in CLASSES:
        c = per_class[klass]
        print("  %-13s steps=%d gross=$%.4f removable=$%.4f thinking=$%.4f"
              % (klass, c["steps"], c["gross"], c["removable"], c["think"]))
    biggest = max(by_session.values()) if by_session else 0.0
    print("concentration: %d session(s); the largest is %.0f%% of spend. This author's own scanner "
          "and verification sessions are in the store unless --since excludes them." % (
              len(by_session), pct(biggest, total)))

    fork_gross = sum(per_class[c]["gross"] for c in FORK)
    fork_rem = sum(per_class[c]["removable"] for c in FORK)
    fork_think = sum(per_class[c]["think"] for c in FORK)
    unc_rem = per_class["unclassified"]["removable"]
    low, high = pct(fork_rem, total), pct(fork_rem + unc_rem, total)
    print()
    print("fork share (removable ceiling; assumes a free, perfect router that never escalates and "
          "needs no generated arguments; NOT a saving estimate): %.1f%% [band %.1f-%.1f%%]"
          % (low, low, high))
    print("fork share (gross, for reference; includes cache writes no router can remove): %.1f%%"
          % pct(fork_gross, total))
    print("fork share (deliberation-only: thinking tokens as output, if the large model still "
          "writes the arguments): %.1f%%" % pct(fork_think, total))
    if total <= 0:
        verdict = "UNDETERMINED (no priced spend in the window)"
    elif high < THRESHOLD:
        verdict = "DROP"
    elif low >= THRESHOLD:
        verdict = "NOT DROPPED (goes on to measurement 2)"
    else:
        verdict = "UNDETERMINED: hand-label the in_sample rows; if rules and labels agree on " \
                  "under ~80%, do not read this number at all"
    print("verdict (roadmap measurement 1, removable basis, threshold %.0f%%): %s" % (THRESHOLD, verdict))
    print("validity: provisional until the in_sample rows are labelled and --agreement reports >= %.0f%% "
          "(rules against labels)" % AGREEMENT_FLOOR)
    print("not established by this: the router's own cost and escalation rate (measurement 2/3), "
          "re-caching behaviour, and whether spend is invoiced or notional.")

    by_class = defaultdict(list)
    for row in rows:
        by_class[row[4]].append(row)
    for klass_rows in by_class.values():
        klass_rows.sort(key=lambda r: hashlib.sha256(r[-1].encode("utf-8")).hexdigest())
        first = max(args.sample_round, 0) * SAMPLE_PER_CLASS
        for row in klass_rows[first:first + SAMPLE_PER_CLASS]:
            row[10] = "1"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        handle.write(TSV_HEADER + "\n")
        for row in rows:
            handle.write("\t".join(str(cell).replace("\t", " ") for cell in row[:-1]) + "\n")
    print("TSV: %s (%d rows; may contain client text; keep it gitignored)" % (out, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
