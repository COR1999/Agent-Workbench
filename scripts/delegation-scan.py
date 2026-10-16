#!/usr/bin/env python3
"""Count delegations to the adapter's agents, and who occasioned each one.

Why this exists: docs/ROADMAP.md reopened #42 as a trial with a decision rule fixed
before any data - zero task-routed delegations by 35 sessions means cut the adapter
or replace its description routing. Nothing could be judged until delegations were
countable, so this makes them countable, the same way skill-usage-scan.py does for
skills. An agent is reached the way a skill is (a model reads a description and
decides), so it gets the same honesty: the score is UNPROMPTED use, and naming the
agent, naming its role, or opening the session by pointing at the library each
remove a delegation from that count.

What it reads: Claude Code transcripts only (~/.claude/projects). The adapter is
Claude-only, so OpenCode is reported as not applicable rather than as zero.

Sessions counted: top-level sessions that STARTED on or after --since. Agents load
when a session starts, so a session that began before install cannot have delegated
to them; counting it would only dilute the denominator. Subagent transcripts live in
a subfolder and are not sessions.

--since takes a date or a date-time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), both UTC.
It defaults to the newest modification time among the installed agent files, which
is the LATEST install, not the first: install.sh relinks every file each time it
runs. Pass --since explicitly for a stable window. Time of day matters because
agents load when a session starts: a session begun at 12:45 cannot use an agent
installed at 14:19, and a whole-day window would count it anyway.

Output is split on purpose:
  - stdout  aggregate counts only. Safe to paste into a public issue.
  - TSV     one row per delegation, including the human's message and the delegated
            prompt. That can contain client material, so it is written to a
            gitignored path and must never be committed.

Neither answer is a verdict. "Unprompted" is guessed from the preceding human
message and is labelled as a candidate to read. Whether an architect use was
WARRANTED cannot be decided by machine at all: the TSV lists them for reading.

stdlib only, like the scanner it borrows from.

Usage:
  python scripts/delegation-scan.py [--since YYYY-MM-DD[THH:MM:SS]] [--target 35]
                                    [--out .usage/delegation.tsv]
"""
import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent

# Borrow the human-message and priming logic rather than copy it: a second copy of
# NOT_HUMAN or LIBRARY_REFS would drift, and the two scanners would then disagree
# about what "unprompted" means.
_spec = importlib.util.spec_from_file_location("skill_usage_scan", HERE / "skill-usage-scan.py")
scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan)

HOME = pathlib.Path.home()

ADAPTER_PREFIX = "workbench-"
ADAPTER_EXTRA = {"Explore"}   # the override; counted only if the override is what ran
DELEGATION_TOOLS = {"Agent", "Task"}   # "Task" is the older name for the same tool
BUCKETS = ["task", "named", "role-mentioned", "primed", "batch", "no-user-text"]


def is_adapter_agent(name):
    return name.startswith(ADAPTER_PREFIX) or name in ADAPTER_EXTRA


def role_words(agent):
    """Words a human might use for the role without typing the agent's full name."""
    if agent == "Explore":
        return ["explore"]
    role = agent[len(ADAPTER_PREFIX):]
    words = {role, role.replace("-", " "), role.replace("-", "")}
    return sorted(words)


def has_word(text, word):
    return re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", text) is not None


def classify(agent, before, earlier):
    """Who occasioned the delegation. A category for reading, not a verdict.

    Precedence matters: the human NAMING the agent is the strongest reason it ran,
    so it wins over every other bucket. The role word comes next, and is checked
    only against the message immediately before the delegation.
    """
    low = (before or "").lower()
    if low and agent.lower() in low:
        return "named"
    if low and any(has_word(low, w) for w in role_words(agent)):
        return "role-mentioned"
    context = scan.context_of(before, earlier)
    if context in ("primed-session", "library-invoked"):
        return "primed"
    if context == "batch":
        return "batch"
    if context == "no-user-text":
        return "no-user-text"
    return "task"


def human_text(content):
    """The text of a user event, whether content is a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def read_session(path):
    """One transcript -> (start epoch, timeline). Timeline entries are
    ("user", text) and ("delegate", agent, stamp, input_dict)."""
    timeline, start, cwd = [], None, ""
    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return None, [], ""
    with handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            stamp = event.get("timestamp", "")
            epoch = scan.iso_to_epoch(stamp)
            if epoch:
                start = epoch if start is None else min(start, epoch)
            cwd = event.get("cwd") or cwd
            message = event.get("message") or {}
            content = message.get("content")
            if event.get("type") == "user":
                text = human_text(content)
                if text.strip() and scan.is_human(text):
                    timeline.append(("user", text))
                continue
            if not isinstance(content, list):
                continue
            for block in content:
                if (isinstance(block, dict) and block.get("type") == "tool_use"
                        and block.get("name") in DELEGATION_TOOLS):
                    given = block.get("input") or {}
                    if given.get("subagent_type"):
                        timeline.append(("delegate", given["subagent_type"], stamp, given))
    return start, timeline, cwd


def parse_since(text):
    """A date or date-time, as an aware UTC datetime. Raises ValueError if malformed."""
    value = dt.datetime.fromisoformat(text) if "T" in text else \
        dt.datetime.combine(dt.date.fromisoformat(text), dt.time())
    return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)


TSV_COLUMNS = ["project", "session", "time", "agent", "bucket", "per_call_model",
               "user_text", "description", "prompt", "warranted"]
TSV_HEADER = "\t".join(TSV_COLUMNS)


def resolve_out(text):
    """Where the TSV may be written. Validated at the boundary, before any read.

    The TSV can hold client text, so it must stay inside the working tree (where
    .usage/ is gitignored) rather than land wherever an argument points. And an
    existing file is overwritten only if it is a previous scan's TSV: without that,
    `--out ~/.bashrc` is a clobber. Symlinks are resolved first, so a link that
    leads out of the working directory is refused too.
    """
    cwd = pathlib.Path.cwd().resolve()
    target = (cwd / text).resolve()
    if cwd not in target.parents:
        raise ValueError("--out must be a file inside the current directory (" + str(cwd) + ")")
    if target.is_dir():
        raise ValueError("--out is a directory")
    if target.exists():
        with target.open(encoding="utf-8", errors="replace") as handle:
            if handle.readline().rstrip("\n") != TSV_HEADER:
                raise ValueError("refusing to overwrite " + str(target)
                                 + ": it is not a previous delegation-scan TSV")
    return target


def detect_install(agents_dir):
    """Newest mtime among the installed adapter files, as a UTC datetime, or None."""
    newest = None
    if agents_dir.is_dir():
        for path in agents_dir.glob("*.md"):
            if not is_adapter_agent(path.stem):
                continue
            try:
                stamp = path.lstat().st_mtime
            except OSError:
                continue
            newest = stamp if newest is None else max(newest, stamp)
    if newest is None:
        return None
    return dt.datetime.fromtimestamp(newest, dt.timezone.utc)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--since", help="YYYY-MM-DD (UTC). Default: the latest install date.")
    parser.add_argument("--target", type=int, default=35,
                        help="Sessions after which the roadmap's decision rule applies.")
    parser.add_argument("--out", default=".usage/delegation.tsv",
                        help="TSV of every delegation. Gitignored; may contain client text.")
    args = parser.parse_args()
    try:
        out = resolve_out(args.out)
    except (ValueError, OSError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2

    projects = HOME / ".claude" / "projects"
    agents_dir = HOME / ".claude" / "agents"

    print("delegation-scan")
    print("stores:")
    files = sorted(projects.glob("*/*.jsonl")) if projects.is_dir() else []
    status = "OK" if projects.is_dir() else "MISSING"
    print("  claude-family jsonl  %s  %s  (%d files)" % (projects, status, len(files)))
    print("  opencode sqlite      not scanned: the adapter is Claude Code only")

    if args.since:
        try:
            since = parse_since(args.since)
        except ValueError:
            print("error: --since must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS", file=sys.stderr)
            return 2
        since_note = since.isoformat() + " (given)"
    else:
        since = detect_install(agents_dir)
        since_note = (since.isoformat(timespec="seconds") + " (latest install, from " + str(agents_dir) + ")"
                      if since else "not detected: no adapter agents installed; counting every session")
    since_epoch = since.timestamp() if since else 0
    print("window: sessions started on or after " + since_note)

    counts = defaultdict(Counter)       # agent -> bucket -> n
    others = Counter()                  # non-adapter subagents
    rows, sessions = [], 0
    for path in files:
        start, timeline, cwd = read_session(path)
        if start is None or start < since_epoch:
            continue
        if not any(kind == "user" for kind, *_ in timeline):
            continue
        sessions += 1
        for index, entry in enumerate(timeline):
            if entry[0] != "delegate":
                continue
            _, agent, stamp, given = entry
            if not is_adapter_agent(agent):
                others[agent] += 1
                continue
            earlier = [e[1] for e in timeline[:index] if e[0] == "user"]
            before = earlier[-1] if earlier else ""
            bucket = classify(agent, before, earlier[:-1])
            counts[agent][bucket] += 1
            rows.append([
                path.parent.name, path.stem, stamp, agent, bucket,
                str(given.get("model") or ""), scan.snippet(before),
                scan.snippet(given.get("description", "")),
                scan.snippet(given.get("prompt", "")), "?",
            ])

    print("sessions in window: %d (target %d)" % (sessions, args.target))
    print()
    print("adapter agents, by who occasioned the delegation:")
    header = "  %-24s" % "agent" + "".join("%15s" % b for b in BUCKETS)
    print(header)
    total = Counter()
    for agent in sorted(counts):
        print("  %-24s" % agent + "".join("%15d" % counts[agent][b] for b in BUCKETS))
        total.update(counts[agent])
    if not counts:
        print("  (no delegations to adapter agents in the window)")
    if others:
        print()
        print("other subagents, not part of the adapter: "
              + ", ".join("%s %d" % (name, n) for name, n in sorted(others.items())))
    print()
    print("task = unprompted: nobody named the agent or its role, and the session was not")
    print("primed. It is a guess from the preceding human message: read the TSV rows")
    print("before believing any of them.")
    architect = sum(counts["workbench-architect"].values())
    if architect:
        print("architect uses: %d. Whether each was WARRANTED needs reading (TSV, last column)." % architect)

    print()
    print("totals: " + " ".join("%s=%d" % (b, total[b]) for b in BUCKETS)
          + " sessions=%d" % sessions)
    task = total["task"]
    if task > 0:
        print("rule: not triggered. %d unprompted delegation(s) already, so 'zero by %d "
              "sessions' can no longer hold." % (task, args.target))
    elif sessions >= args.target:
        print("rule: TRIGGERED. %d sessions, zero unprompted delegations. docs/ROADMAP.md: "
              "cut the adapter or replace the description routing with an explicit rule." % sessions)
    else:
        print("rule: not yet. %d of %d sessions, zero unprompted so far." % (sessions, args.target))

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        handle.write(TSV_HEADER + "\n")
        for row in rows:
            handle.write("\t".join(cell.replace("\t", " ") for cell in row) + "\n")
    print("TSV: %s (%d rows; may contain client text; keep it gitignored)" % (out, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
