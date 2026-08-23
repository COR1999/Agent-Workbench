#!/usr/bin/env python3
"""Count skill invocations across every local agent backend, and ask whether they helped.

Why this exists: the trial in docs/ROADMAP.md scores a skill on whether it fired
WITHOUT the human naming it, and on whether that firing was KEPT. Nothing can be
judged until both are countable, and a hook would only ever see one harness. This
reads the transcripts each tool already writes, so it works across harnesses and
over history already on disk.

Why it enumerates every store before reporting: see
lessons/agent-sessions-live-in-multiple-stores.md. Reading one store and
concluding "never fired" is the exact failure that lesson records - and is what
the hand-maintained tally this replaces actually did.

Two questions, two different kinds of answer:

  DID IT FIRE UNPROMPTED?  Guessed from the preceding user message. Naive, and
  labelled as a sort key rather than a verdict: it already produced one false
  "unnamed" when /grill-me invoked `grilling` under an alias.

  DID IT HELP?  Some skills leave a trace in git. capture-lesson should produce a
  file under lessons/; explain-and-open-pr should produce a commit; tdd should
  touch a test. If the firing is followed by its own artifact inside the window,
  that is mechanical evidence the skill did its job. Skills that produce no file
  BY DESIGN (sweep-the-class never edits, grilling never builds) report
  no-signature and must be judged by reading - the tool says so rather than
  scoring them zero.

Neither answer is a verdict. Both exist to make the reading pass fast and to stop
it starting from memory.

stdlib only: there is no jq and no sqlite3 binary on this machine, and the
library must not acquire dependencies in order to be measurable.

Output is split on purpose:
  - stdout  aggregate counts only. Safe to paste into a public issue.
  - TSV     one row per firing, including the surrounding user messages. That can
            contain client material, so it is written to a gitignored path and
            must never be committed.

Usage:
  python scripts/skill-usage-scan.py [--out .usage/skill-usage.tsv] [--window-hours 6]
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict

HOME = pathlib.Path.home()
CLAUDE_PROJECTS = HOME / ".claude" / "projects"   # Claude Code and t3 code both write here
OPENCODE_DB = HOME / ".local" / "share" / "opencode" / "opencode.db"

SNIPPET = 240

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

# Wording that suggests the human rejected what the skill did. Crude on purpose:
# it flags a row for reading, it does not decide anything.
PUSHBACK = [
    "no ", "nope", "don't", "dont ", "stop", "undo", "revert", "wrong",
    "that's not", "thats not", "not what i", "instead", "actually no",
]


def artifact_lessons(paths, commits):
    return any(p.startswith("lessons/") for p in paths)


def artifact_commit(paths, commits):
    return commits > 0


def artifact_html(paths, commits):
    return any(p.lower().endswith(".html") for p in paths)


def artifact_handoff(paths, commits):
    return any("handoff" in p.lower() for p in paths)


def artifact_test(paths, commits):
    low = [p.lower() for p in paths]
    return any("test" in p or ".spec." in p for p in low)


# Only skills that produce a file of their own can be checked mechanically. The
# rest are absent from this map ON PURPOSE and report "no-signature": a skill that
# never writes anything cannot be scored by looking for what it wrote.
ARTIFACTS = {
    "capture-lesson": artifact_lessons,
    "explain-and-open-pr": artifact_commit,
    "design-handbook": artifact_html,
    "handoff": artifact_handoff,
    "tdd": artifact_test,
}


def snippet(text):
    return re.sub(r"\s+", " ", (text or "")).strip()[:SNIPPET]


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


_git_cache = {}


def git_changes(repo, start_epoch, end_epoch):
    """Paths changed and commits made in `repo` within the window.

    Returns (paths, commit_count) or None when the repo is unavailable. Commits by
    anything else working in that repo during the window are indistinguishable
    from the skill's own - a solo operator makes that acceptable, a shared repo
    would not.
    """
    if not repo:
        return None
    key = (str(repo), int(start_epoch), int(end_epoch))
    if key in _git_cache:
        return _git_cache[key]
    path = pathlib.Path(repo)
    if not (path / ".git").exists():
        _git_cache[key] = None
        return None
    since = dt.datetime.utcfromtimestamp(start_epoch).isoformat()
    until = dt.datetime.utcfromtimestamp(end_epoch).isoformat()
    try:
        out = subprocess.run(
            ["git", "-C", str(path), "log", "--since=" + since, "--until=" + until,
             "--name-only", "--pretty=format:%H"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        _git_cache[key] = None
        return None
    if out.returncode != 0:
        _git_cache[key] = None
        return None
    paths, commits = set(), 0
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{40}", line):
            commits += 1
        else:
            paths.add(line)
    result = (sorted(paths), commits)
    _git_cache[key] = result
    return result


def outcome_for(skill, repo, epoch, window_hours, next_user):
    """Mechanical evidence about whether the firing helped. Never a verdict."""
    if next_user:
        low = next_user.lower()
        if any(low.startswith(w) or (" " + w) in low[:120] for w in PUSHBACK):
            return "pushback?"
    check = ARTIFACTS.get(skill)
    if check is None:
        return "no-signature"
    if not epoch:
        return "no-timestamp"
    changes = git_changes(repo, epoch, epoch + window_hours * 3600)
    if changes is None:
        return "repo-unavailable"
    paths, commits = changes
    return "artifact" if check(paths, commits) else "no-artifact"


def iso_to_epoch(value):
    if not value:
        return 0
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0


def scan_claude(rows, sessions, stores, window_hours):
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
        timeline, cwd = [], ""
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
                    cwd = event.get("cwd") or cwd
                    content = (event.get("message") or {}).get("content")
                    if not isinstance(content, list):
                        continue
                    stamp = event.get("timestamp", "")
                    if event.get("type") == "user":
                        text = " ".join(
                            block.get("text", "")
                            for block in content
                            if isinstance(block, dict) and block.get("type") == "text"
                        )
                        if text.strip():
                            timeline.append(("user", text, stamp, cwd))
                        continue
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_use" and block.get("name") == "Skill":
                            skill = (block.get("input") or {}).get("skill", "?")
                            timeline.append(("skill", skill, stamp, cwd))
        except OSError:
            unreadable += 1
            continue

        for index, (kind, value, stamp, where) in enumerate(timeline):
            if kind != "skill":
                continue
            before = next((v for k, v, _, _ in reversed(timeline[:index]) if k == "user"), "")
            after = next((v for k, v, _, _ in timeline[index + 1:] if k == "user"), "")
            epoch = iso_to_epoch(stamp)
            rows.append({
                "store": "claude-family",
                "project": project,
                "session": session,
                "time": stamp,
                "skill": value,
                "guess": named_by_user(value, before),
                "outcome": outcome_for(value, where, epoch, window_hours, after),
                "user_text": snippet(before),
                "next_user": snippet(after),
            })
    status = "OK" if not unreadable else "OK (" + str(unreadable) + " unreadable)"
    stores.append(("claude-family jsonl", str(CLAUDE_PROJECTS), status, len(files)))


def scan_opencode(rows, sessions, stores, window_hours):
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
        directories[sid] = directory or ""
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
        texts = user_text_by_session.get(sid, [])
        before = [text for (ts, text) in texts if ts <= created]
        after = [text for (ts, text) in texts if ts > created]
        user_text = before[-1] if before else ""
        next_user = after[0] if after else ""
        # OpenCode stores milliseconds.
        epoch = (created or 0) / 1000.0
        rows.append({
            "store": "opencode",
            "project": pathlib.Path(directories.get(sid) or "?").name,
            "session": sid,
            "time": created,
            "skill": skill,
            "guess": named_by_user(skill, user_text),
            "outcome": outcome_for(skill, directories.get(sid), epoch,
                                   window_hours, next_user),
            "user_text": snippet(user_text),
            "next_user": snippet(next_user),
        })
    stores.append(("opencode sqlite", str(OPENCODE_DB), "OK", top_level))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out", default=".usage/skill-usage.tsv",
        help="TSV of every firing. Gitignored; may contain client text.")
    parser.add_argument(
        "--window-hours", type=int, default=6,
        help="How long after a firing its artifact is still credited to it.")
    args = parser.parse_args()

    rows, stores = [], []
    sessions = defaultdict(set)
    scan_claude(rows, sessions, stores, args.window_hours)
    scan_opencode(rows, sessions, stores, args.window_hours)

    print("STORES CHECKED  (MISSING is not a zero - it is unmeasured)")
    for name, path, status, count in stores:
        print("  %-26s %-22s %4d sessions  %s" % (status, name, count, path))

    total_sessions = sum(len(ids) for ids in sessions.values())
    print("\nSESSIONS (denominator): %d" % total_sessions)
    for (store, project), ids in sorted(sessions.items(), key=lambda kv: -len(kv[1])):
        print("  %4d  %s/%s" % (len(ids), store, project))

    print("\nDID IT FIRE, AND WAS IT NAMED?   (guess = sort key, not verdict)")
    per_skill = Counter(row["skill"] for row in rows)
    per_guess = defaultdict(Counter)
    per_outcome = defaultdict(Counter)
    for row in rows:
        per_guess[row["skill"]][row["guess"]] += 1
        per_outcome[row["skill"]][row["outcome"]] += 1
    print("  firings: %d" % len(rows))
    if not per_skill:
        print("  none found in any readable store")
    for skill, count in per_skill.most_common():
        guesses = per_guess[skill]
        print("  %4d  %-24s unnamed=%d slash-other=%d alias=%d named=%d slash=%d "
              "no-user-text=%d" % (
                  count, skill, guesses["unnamed"], guesses["slash-other"],
                  guesses["alias"], guesses["named"], guesses["slash"],
                  guesses["no-user-text"]))

    print("\nDID IT HELP?   (artifact = the skill's own output appeared within "
          "%dh; no-signature = the skill writes no file by design and must be read)"
          % args.window_hours)
    for skill, _ in per_skill.most_common():
        outcomes = per_outcome[skill]
        parts = ", ".join("%s=%d" % (k, v) for k, v in outcomes.most_common())
        print("  %-24s %s" % (skill, parts))

    print("\nBY STORE")
    for store, count in Counter(row["store"] for row in rows).most_common():
        print("  %4d  %s" % (count, store))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        handle.write("store\tproject\tsession\ttime\tskill\tguess\toutcome\tkept"
                     "\tuser_text\tnext_user\n")
        for row in sorted(rows, key=lambda r: (r["store"], str(r["time"]))):
            handle.write("\t".join([
                row["store"], row["project"], row["session"], str(row["time"]),
                row["skill"], row["guess"], row["outcome"], "",
                row["user_text"].replace("\t", " "),
                row["next_user"].replace("\t", " "),
            ]) + "\n")
    print("\nrows written to %s  (gitignored; 'kept' is filled in by hand during "
          "the classification pass)" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
