#!/usr/bin/env python3
"""Build a labelled replay set from real session history.

The purpose: stop waiting for live sessions to accumulate. Every past session is
already an experiment that ran - it has a prompt, and it has an observable
outcome. If a session ended with a lesson file added, `capture-lesson` was
applicable to it, whether or not it fired. That gives a labelled example without
anyone judging anything.

  prompt  ->  a skill WAS applicable (from what the session actually produced)
          ->  did it fire?   (from the transcripts)

A skill that was applicable and did not fire is a routing failure with a concrete
prompt attached. That is the material a description can be tuned against, and it
can be replayed offline as many times as needed.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not judge whether a rewritten description "would have" fired, and it does
not score its own output. Both require a model, and a model tuning its own
triggers while also deciding whether the result improved converges on
self-agreement rather than on quality. The guards that make the loop honest:

1. Labels come from what the session PRODUCED, never from an opinion about what
   it should have produced.
2. The set is split into train and holdout on a hash of the session id, fixed and
   deterministic. Tune against train only. A gain that does not appear in holdout
   is overfitting to history, not a better trigger.
3. The metric is fixed before tuning: of the applicable-and-did-not-fire examples
   in holdout, how many would the new description catch. Changing the metric after
   seeing results is how this kind of loop lies to you.
4. Descriptions may be made sharper, never broader (docs/ROADMAP.md). A trigger
   broad enough to catch every example is worthless - it will also fire on
   everything else.

Output is gitignored: it contains raw prompts from client work.

Usage:
  python scripts/build-replay-set.py [--out .usage/replay-set.jsonl]
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import sqlite3
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent


def load_scanner():
    """Reuse the scanner's parsing rather than duplicating it.

    The filename has hyphens, so it cannot be imported normally.
    """
    path = HERE / "skill-usage-scan.py"
    spec = importlib.util.spec_from_file_location("skill_usage_scan", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# APPLICABILITY is not the same question as ARTIFACT.
#
#   ARTIFACT (in the scanner)  - did the skill produce its own output? Evidence it
#                                worked. Only exists for skills that write files.
#   APPLICABLE (here)          - was this the KIND of situation the skill exists
#                                for? A label for the replay set, and it can be
#                                derived for skills that write nothing at all.
#
# sweep-the-class never edits code, so it has no artifact - but a session whose
# commits describe a fix is objectively a session where "did I fix the instance or
# the class?" was worth asking. deslop applies to any generated diff before it is
# committed, so a session that edited files and committed them qualifies. Both
# labels come from what the session DID, not from an opinion about it, which is
# the property that keeps the loop honest.
FIX_WORDS = ("fix", "bug", "hotfix", "patch", "regression", "broken", "crash")


def applicable_extra(change, subjects, edited):
    found = []
    if any(any(word in subject.lower() for word in FIX_WORDS) for subject in subjects):
        found.append("sweep-the-class")
    if edited and change["commits"] > 0:
        found.append("deslop")
    return found


def commit_subjects(repo, start_epoch, end_epoch):
    """Commit subjects in the window. Separate from git_changes, which returns
    paths - a subject is a different kind of evidence and is only used for
    labelling, never for the did-it-help test."""
    import datetime as dt
    import subprocess
    path = pathlib.Path(repo)
    if not (path / ".git").exists():
        return []
    since = dt.datetime.utcfromtimestamp(start_epoch).isoformat()
    until = dt.datetime.utcfromtimestamp(end_epoch).isoformat()
    try:
        out = subprocess.run(
            ["git", "-C", str(path), "log", "--since=" + since,
             "--until=" + until, "--pretty=format:%s"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    return out.stdout.splitlines() if out.returncode == 0 else []


def split_for(session_id):
    """Deterministic 70/30 split. Fixed so the holdout cannot drift."""
    digest = hashlib.md5(str(session_id).encode("utf-8")).hexdigest()
    return "train" if int(digest[:2], 16) % 10 < 7 else "holdout"


def collect_claude(scan, sessions):
    if not scan.CLAUDE_PROJECTS.is_dir():
        return
    for path in sorted(scan.CLAUDE_PROJECTS.glob("*/*.jsonl")):
        entry = sessions[("claude-family", path.stem)]
        entry["repo"] = entry.get("repo") or ""
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if event.get("cwd"):
                        entry["repo"] = event["cwd"]
                    stamp = scan.iso_to_epoch(event.get("timestamp", ""))
                    if stamp:
                        entry["start"] = min(entry.get("start") or stamp, stamp)
                        entry["end"] = max(entry.get("end") or stamp, stamp)
                    content = (event.get("message") or {}).get("content")
                    if not isinstance(content, list):
                        continue
                    if event.get("type") == "user":
                        text = " ".join(
                            b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text")
                        if text.strip() and scan.is_human(text):
                            entry["prompts"].append(scan.snippet(text))
                        continue
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") != "tool_use":
                            continue
                        if block.get("name") in scan.EDIT_TOOLS:
                            entry["edited"] = True
                        if block.get("name") == "Skill":
                            entry["fired"].add(
                                (block.get("input") or {}).get("skill", "?"))
        except OSError:
            continue


def collect_opencode(scan, sessions):
    if not scan.OPENCODE_DB.exists():
        return
    con = sqlite3.connect("file:" + str(scan.OPENCODE_DB) + "?mode=ro", uri=True)
    directories = {sid: (directory or "")
                   for sid, directory in con.execute(
                       "select id, directory from session")}
    user_message_ids = set()
    for mid, data in con.execute("select id, data from message"):
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            continue
        if payload.get("role") == "user":
            user_message_ids.add(mid)

    for sid, mid, created, data in con.execute(
            "select session_id, message_id, time_created, data from part "
            "order by time_created"):
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            continue
        entry = sessions[("opencode", sid)]
        entry["repo"] = entry.get("repo") or directories.get(sid, "")
        stamp = (created or 0) / 1000.0
        if stamp:
            entry["start"] = min(entry.get("start") or stamp, stamp)
            entry["end"] = max(entry.get("end") or stamp, stamp)
        kind = payload.get("type")
        if kind == "text" and mid in user_message_ids:
            text = payload.get("text", "")
            if scan.is_human(text):
                entry["prompts"].append(scan.snippet(text))
        elif kind == "tool":
            if payload.get("tool") in scan.OPENCODE_EDIT_TOOLS:
                entry["edited"] = True
            if payload.get("tool") == "skill":
                state = payload.get("state") or {}
                if isinstance(state, dict):
                    entry["fired"].add((state.get("input") or {}).get("name") or "?")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".usage/replay-set.jsonl",
                        help="Gitignored; contains raw prompts.")
    args = parser.parse_args()

    scan = load_scanner()
    sessions = defaultdict(lambda: {"repo": "", "start": None, "end": None,
                                    "prompts": [], "fired": set(), "edited": False})
    collect_claude(scan, sessions)
    collect_opencode(scan, sessions)

    rows = []
    for (store, sid), entry in sessions.items():
        if not entry["prompts"] or not entry["repo"] or entry["start"] is None:
            continue
        change = scan.git_changes(entry["repo"], entry["start"],
                                  (entry["end"] or entry["start"]) + 1)
        if change is None:
            continue
        change = dict(change, session_edited=entry["edited"])
        subjects = commit_subjects(entry["repo"], entry["start"],
                                   (entry["end"] or entry["start"]) + 1)
        applicable = [name for name, check in scan.ARTIFACTS.items() if check(change)]
        applicable += applicable_extra(change, subjects, entry["edited"])
        applicable = sorted(set(applicable))
        if not applicable:
            continue
        rows.append({
            "store": store,
            "session": sid,
            "split": split_for(sid),
            "repo_name": pathlib.Path(entry["repo"]).name,
            "prompts": entry["prompts"][:8],
            "applicable": sorted(applicable),
            "fired": sorted(entry["fired"]),
            "missed": sorted(set(applicable) - entry["fired"]),
        })

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print("LABELLED SESSIONS: %d  (a session counts only if something it produced "
          "makes a skill applicable)" % len(rows))
    for split in ("train", "holdout"):
        subset = [r for r in rows if r["split"] == split]
        print("\n%s: %d sessions" % (split.upper(), len(subset)))
        missed = Counter(s for r in subset for s in r["missed"])
        hit = Counter(s for r in subset for s in r["applicable"] if s in r["fired"])
        for skill in sorted(set(missed) | set(hit)):
            total = missed[skill] + hit[skill]
            print("  %-22s applicable=%-3d fired=%-3d MISSED=%d"
                  % (skill, total, hit[skill], missed[skill]))
    print("\nwritten to %s" % out)
    print("Tune against TRAIN only. A gain that does not reproduce in HOLDOUT is "
          "overfitting to history.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
