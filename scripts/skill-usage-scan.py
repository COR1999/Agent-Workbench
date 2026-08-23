#!/usr/bin/env python3
"""Count skill invocations across every local agent backend.

Why this exists: the trial in docs/ROADMAP.md scores a skill on whether it fired
WITHOUT the human naming it. Nothing can be judged until that is countable, and a
hook would only ever see one harness. This reads the transcripts each tool
already writes, so it works across harnesses and over history already on disk.

Why it enumerates every store before reporting: see
lessons/agent-sessions-live-in-multiple-stores.md. Reading one store and
concluding "never fired" is the exact failure that lesson records - and is what
the hand-maintained tally this replaces actually did.

stdlib only: there is no jq and no sqlite3 binary on this machine, and the
library must not acquire dependencies in order to be measurable.

Output is split on purpose:
  - stdout  aggregate counts only. Safe to paste into a public issue.
  - TSV     one row per firing, including the preceding user message. That can
            contain client material, so it is written to a gitignored path and
            must never be committed.

Usage:
  python scripts/skill-usage-scan.py [--out .usage/skill-usage.tsv]
"""
import argparse
import json
import pathlib
import re
import sqlite3
import sys
from collections import Counter, defaultdict

HOME = pathlib.Path.home()
CLAUDE_PROJECTS = HOME / ".claude" / "projects"   # Claude Code and t3 code both write here
OPENCODE_DB = HOME / ".local" / "share" / "opencode" / "opencode.db"

SNIPPET = 240


def snippet(text):
    return re.sub(r"\s+", " ", (text or "")).strip()[:SNIPPET]


# A skill can be named by an alias rather than its own name. The first version of
# this scanner scored `/grill-me` as "unnamed" for the `grilling` skill, which
# would have inflated the headline number the whole trial rests on. Add aliases
# here as they are found.
ALIASES = {
    "grilling": ["grill-me", "grill me", "grill this", "grill with docs"],
    "explain-and-open-pr": ["open a pr", "raise a pr", "pr this"],
    "sweep-the-class": ["sweep", "where else"],
    "capture-lesson": ["capture this", "that's a lesson"],
}


def named_by_user(skill, user_text):
    """Naive prompted/unprompted guess.

    Deliberately naive: the roadmap says log raw and classify in a later pass by
    reading. This is a sort key to make that pass fast, never a verdict. It
    over-reports "unnamed" whenever the human used wording this does not know
    about, so treat every "unnamed" as a candidate to read, not as a confirmed
    autonomous firing.
    """
    if not user_text:
        return "no-user-text"
    low = user_text.lower()
    bare = skill.lower()
    if "/" + bare in low:
        return "slash"
    if bare in low or bare.replace("-", " ") in low:
        return "named"
    for alias in ALIASES.get(bare, []):
        if alias in low or "/" + alias.replace(" ", "-") in low:
            return "alias"
    # The human explicitly invoked *something*; worth reading before believing
    # this firing was autonomous.
    if re.search(r"(^|\s)/[a-z][a-z0-9-]{2,}", low):
        return "slash-other"
    return "unnamed"


def scan_claude(rows, sessions, stores):
    """Claude-family JSONL: ~/.claude/projects/<project>/<session>.jsonl"""
    if not CLAUDE_PROJECTS.is_dir():
        stores.append(("claude-family jsonl", str(CLAUDE_PROJECTS), "MISSING", 0))
        return
    files = sorted(CLAUDE_PROJECTS.glob("*/*.jsonl"))
    unreadable = 0
    for path in files:
        project = path.parent.name
        session = path.stem
        sessions[("claude-family", project)].add(session)
        last_user = ""
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
                    content = (event.get("message") or {}).get("content")
                    if not isinstance(content, list):
                        continue
                    if event.get("type") == "user":
                        text = " ".join(
                            block.get("text", "")
                            for block in content
                            if isinstance(block, dict) and block.get("type") == "text"
                        )
                        if text.strip():
                            last_user = text
                        continue
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_use" and block.get("name") == "Skill":
                            skill = (block.get("input") or {}).get("skill", "?")
                            rows.append({
                                "store": "claude-family",
                                "project": project,
                                "session": session,
                                "time": event.get("timestamp", ""),
                                "skill": skill,
                                "guess": named_by_user(skill, last_user),
                                "user_text": snippet(last_user),
                            })
        except OSError:
            unreadable += 1
    status = "OK" if not unreadable else "OK (" + str(unreadable) + " unreadable)"
    stores.append(("claude-family jsonl", str(CLAUDE_PROJECTS), status, len(files)))


def scan_opencode(rows, sessions, stores):
    """OpenCode: a SQLite database, not transcripts. Opened read-only."""
    if not OPENCODE_DB.exists():
        stores.append(("opencode sqlite", str(OPENCODE_DB), "MISSING", 0))
        return
    try:
        con = sqlite3.connect("file:" + str(OPENCODE_DB) + "?mode=ro", uri=True)
    except sqlite3.Error as exc:
        stores.append(("opencode sqlite", str(OPENCODE_DB), "UNREADABLE: " + str(exc), 0))
        return

    directories = {}
    top_level = 0
    for sid, parent, directory in con.execute(
            "select id, parent_id, directory from session"):
        directories[sid] = directory or "?"
        if not parent:
            top_level += 1
            sessions[("opencode", pathlib.Path(directory or "?").name)].add(sid)

    user_message_ids = set()
    for mid, data in con.execute("select id, data from message"):
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            continue
        if payload.get("role") == "user":
            user_message_ids.add(mid)

    user_text_by_session = defaultdict(list)
    skill_parts = []
    for sid, mid, created, data in con.execute(
            "select session_id, message_id, time_created, data from part "
            "order by time_created"):
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            continue
        if payload.get("type") == "text" and mid in user_message_ids:
            user_text_by_session[sid].append((created or 0, payload.get("text", "")))
        elif payload.get("type") == "tool" and payload.get("tool") == "skill":
            skill_parts.append((sid, created or 0, payload))

    for sid, created, payload in skill_parts:
        state = payload.get("state") or {}
        skill = "?"
        if isinstance(state, dict):
            skill = (state.get("input") or {}).get("name") or "?"
        prior = [text for (ts, text) in user_text_by_session.get(sid, []) if ts <= created]
        user_text = prior[-1] if prior else ""
        rows.append({
            "store": "opencode",
            "project": pathlib.Path(directories.get(sid, "?")).name,
            "session": sid,
            "time": created,
            "skill": skill,
            "guess": named_by_user(skill, user_text),
            "user_text": snippet(user_text),
        })
    stores.append(("opencode sqlite", str(OPENCODE_DB), "OK", top_level))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out", default=".usage/skill-usage.tsv",
        help="TSV of every firing. Gitignored; may contain client text.")
    args = parser.parse_args()

    rows, stores = [], []
    sessions = defaultdict(set)
    scan_claude(rows, sessions, stores)
    scan_opencode(rows, sessions, stores)

    print("STORES CHECKED  (MISSING is not a zero - it is unmeasured)")
    for name, path, status, count in stores:
        print("  %-26s %-22s %4d sessions  %s" % (status, name, count, path))

    total_sessions = sum(len(ids) for ids in sessions.values())
    print("\nSESSIONS (denominator): %d" % total_sessions)
    for (store, project), ids in sorted(sessions.items(), key=lambda kv: -len(kv[1])):
        print("  %4d  %s/%s" % (len(ids), store, project))

    print("\nSKILL FIRINGS: %d" % len(rows))
    per_skill = Counter(row["skill"] for row in rows)
    per_guess = defaultdict(Counter)
    for row in rows:
        per_guess[row["skill"]][row["guess"]] += 1
    if not per_skill:
        print("  none found in any readable store")
    for skill, count in per_skill.most_common():
        guesses = per_guess[skill]
        print("  %4d  %-24s unnamed=%d slash-other=%d alias=%d named=%d slash=%d "
              "no-user-text=%d" % (
                  count, skill, guesses["unnamed"], guesses["slash-other"],
                  guesses["alias"], guesses["named"], guesses["slash"],
                  guesses["no-user-text"]))

    print("\nBY STORE")
    for store, count in Counter(row["store"] for row in rows).most_common():
        print("  %4d  %s" % (count, store))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        handle.write("store\tproject\tsession\ttime\tskill\tguess\tkept\tuser_text\n")
        for row in sorted(rows, key=lambda r: (r["store"], str(r["time"]))):
            handle.write("\t".join([
                row["store"], row["project"], row["session"], str(row["time"]),
                row["skill"], row["guess"], "",
                row["user_text"].replace("\t", " "),
            ]) + "\n")
    print("\nrows written to %s  (gitignored; the 'kept' column is filled in by "
          "hand during the classification pass)" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
