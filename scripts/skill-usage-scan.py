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
# Tool names that mean the session actually changed files. Used to tell a session
# that produced work from one that only read - only the former could have wanted a
# PR opened for it.
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
OPENCODE_EDIT_TOOLS = {"edit", "write", "patch"}

# The harness injects text that LOOKS like a user turn: a skill's own load banner,
# slash-command expansions, system reminders. Counting those as "the human's next
# message" contaminated both the pushback detector and the prompted/unprompted
# guess - a second skill call in a session was being compared against the FIRST
# skill's banner rather than against anything a human wrote.
NOT_HUMAN = (
    "base directory for this skill",
    "<command-name>",
    "<command-message>",
    "caveat: the messages below were generated",
    "<system-reminder>",
    "this session is being continued from a previous",
)

# The human pointing AT the library ("use agent workbench methods", "report back
# to agentworkbench with any new lessons") is not the same as the model routing a
# skill from an ordinary task. Both are unprompted by skill NAME, and conflating
# them overstates autonomous routing.
LIBRARY_REFS = (
    "agent workbench", "agentworkbench", "agent-workbench",
    "workbench method", "any new lessons", "self learning system",
)
# A batch instruction accepting a list the model already proposed. Also not
# autonomous routing on a fresh task.
BATCH_REFS = ("do all", "do both", "do it all", "do them all", "all of them")

PUSHBACK = [
    "no ", "nope", "don't", "dont ", "stop", "undo", "revert", "wrong",
    "that's not", "thats not", "not what i", "instead", "actually no",
]


# Signatures take the whole change set: touched paths, ADDED paths, commit count,
# and whether the session itself edited files. The first version used touched
# paths and a bare commit count, which over-credited opportunities badly - any
# commit at all counted as a chance for explain-and-open-pr, and brushing an
# existing test file counted as a chance for tdd.


def artifact_lessons(change):
    # A lesson is a NEW file. Editing an existing one is not capture-lesson's job.
    return any(p.startswith("lessons/") for p in change["added"])


def artifact_commit(change):
    # Only a session that actually edited files could have wanted a PR. A commit
    # during a read-only session is the human's own work, not a missed skill.
    return change["commits"] > 0 and change["session_edited"]


def artifact_html(change):
    return any(p.lower().endswith(".html") for p in change["added"])


def artifact_handoff(change):
    return any("handoff" in p.lower() for p in change["added"])


def artifact_test(change):
    # A NEW test file. Touching an existing test is ordinary maintenance and is
    # not evidence that test-first work was on the table.
    low = [p.lower() for p in change["added"]]
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


def is_human(text):
    low = (text or "").strip().lower()
    if not low:
        return False
    return not any(low.startswith(marker) or marker in low[:200]
                   for marker in NOT_HUMAN)


def context_of(user_text):
    """How the firing was occasioned. Not a verdict; a category for reading."""
    low = (user_text or "").lower()
    if not low:
        return "no-user-text"
    if any(ref in low for ref in LIBRARY_REFS):
        return "library-invoked"
    if any(ref in low for ref in BATCH_REFS):
        return "batch"
    return "task"


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
             "--name-status", "--pretty=format:%H"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        _git_cache[key] = None
        return None
    if out.returncode != 0:
        _git_cache[key] = None
        return None
    paths, added, commits = set(), set(), 0
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{40}", line):
            commits += 1
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, target = parts[0], parts[-1]
        paths.add(target)
        if status.startswith("A"):
            added.add(target)
    result = {"paths": sorted(paths), "added": sorted(added), "commits": commits}
    _git_cache[key] = result
    return result


def outcome_for(skill, repo, epoch, window_hours, next_user, session_edited):
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
    change = git_changes(repo, epoch, epoch + window_hours * 3600)
    if change is None:
        return "repo-unavailable"
    change = dict(change, session_edited=session_edited)
    return "artifact" if check(change) else "no-artifact"


def iso_to_epoch(value):
    if not value:
        return 0
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0


def record_session(session_info, key, repo, epoch, skill=None, edited=False):
    """Accumulate a session's repo, time span, and the skills that fired in it.

    This is what makes MISSES visible: a session whose artifact appeared but whose
    skill never fired is an opportunity the library did not take.
    """
    info = session_info.setdefault(key, {
        "repo": repo or "", "start": None, "end": None, "skills": set(),
        "edited": False})
    if repo and not info["repo"]:
        info["repo"] = repo
    if epoch:
        info["start"] = epoch if info["start"] is None else min(info["start"], epoch)
        info["end"] = epoch if info["end"] is None else max(info["end"], epoch)
    if skill:
        info["skills"].add(skill)
    if edited:
        info["edited"] = True


def find_misses(session_info):
    """Sessions where a skill's own artifact appeared but the skill never fired.

    Only the skills with an artifact signature can be checked this way. For
    sweep-the-class, grilling, deslop and agentic-vocabulary a miss is
    undetectable by machine — they leave nothing behind either way — so they are
    absent here rather than reported as zero.

    Caveat kept deliberately visible: an artifact committed by hand during a
    session, with no agent involvement, counts as a miss. On a solo repo that is
    usually the right reading; it is still a guess, not a fact.
    """
    misses = Counter()
    for info in session_info.values():
        repo, start, end = info["repo"], info["start"], info["end"]
        if not repo or start is None:
            continue
        change = git_changes(repo, start, (end or start) + 1)
        if not change:
            continue
        change = dict(change, session_edited=info["edited"])
        for skill, check in ARTIFACTS.items():
            if skill in info["skills"]:
                continue
            if check(change):
                misses[skill] += 1
    return misses


def scan_claude(rows, sessions, stores, window_hours, session_info):
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
        timeline, cwd, edited = [], "", False
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
                        if text.strip() and is_human(text):
                            timeline.append(("user", text, stamp, cwd))
                        continue
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") != "tool_use":
                            continue
                        if block.get("name") in EDIT_TOOLS:
                            edited = True
                        if block.get("name") == "Skill":
                            skill = (block.get("input") or {}).get("skill", "?")
                            timeline.append(("skill", skill, stamp, cwd))
        except OSError:
            unreadable += 1
            continue

        for kind, value, stamp, where in timeline:
            record_session(session_info, ("claude-family", session), where,
                           iso_to_epoch(stamp),
                           value if kind == "skill" else None, edited)

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
                "context": context_of(before),
                "outcome": outcome_for(value, where, epoch, window_hours, after,
                                       edited),
                "user_text": snippet(before),
                "next_user": snippet(after),
            })
    status = "OK" if not unreadable else "OK (" + str(unreadable) + " unreadable)"
    stores.append(("claude-family jsonl", str(CLAUDE_PROJECTS), status, len(files)))


def scan_opencode(rows, sessions, stores, window_hours, session_info):
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
    edited_sessions = set()
    skill_parts = []
    for sid, mid, created, data in con.execute(
            "select session_id, message_id, time_created, data from part "
            "order by time_created"):
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            continue
        fired = None
        if payload.get("type") == "text" and mid in user_message_ids:
            text = payload.get("text", "")
            if is_human(text):
                user_text_by_session[sid].append((created or 0, text))
        elif payload.get("type") == "tool" and payload.get("tool") == "skill":
            skill_parts.append((sid, created or 0, payload))
            state = payload.get("state") or {}
            if isinstance(state, dict):
                fired = (state.get("input") or {}).get("name")
        if payload.get("type") == "tool" and payload.get("tool") in OPENCODE_EDIT_TOOLS:
            edited_sessions.add(sid)
        record_session(session_info, ("opencode", sid), directories.get(sid),
                       (created or 0) / 1000.0, fired)

    for sid in edited_sessions:
        record_session(session_info, ("opencode", sid), directories.get(sid),
                       0, None, True)

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
            "context": context_of(user_text),
            "outcome": outcome_for(skill, directories.get(sid), epoch,
                                   window_hours, next_user,
                                   sid in edited_sessions),
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
    session_info = {}
    scan_claude(rows, sessions, stores, args.window_hours, session_info)
    scan_opencode(rows, sessions, stores, args.window_hours, session_info)

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

    print("\nWHAT OCCASIONED IT?   (library-invoked = the human pointed at the "
          "workbench; batch = accepting a list already proposed; task = routed "
          "from ordinary work)")
    per_context = defaultdict(Counter)
    for row in rows:
        per_context[row["skill"]][row["context"]] += 1
    for skill, _ in per_skill.most_common():
        contexts = per_context[skill]
        print("  %-24s %s" % (skill, ", ".join(
            "%s=%d" % (k, v) for k, v in contexts.most_common())))

    print("\nDID IT HELP?   (artifact = the skill's own output appeared within "
          "%dh; no-signature = the skill writes no file by design and must be read)"
          % args.window_hours)
    for skill, _ in per_skill.most_common():
        outcomes = per_outcome[skill]
        parts = ", ".join("%s=%d" % (k, v) for k, v in outcomes.most_common())
        print("  %-24s %s" % (skill, parts))

    print("\nCOULD IT HAVE FIRED AND DIDN'T?   (the skill's artifact appeared in a "
          "session where it never fired)")
    misses = find_misses(session_info)
    for skill in sorted(ARTIFACTS, key=lambda k: -(per_skill[k] + misses[k])):
        fired, missed = per_skill[skill], misses[skill]
        total = fired + missed
        rate = ("%d%%" % round(100.0 * fired / total)) if total else "n/a"
        print("  %-24s fired=%-3d missed=%-3d took %s of its chances"
              % (skill, fired, missed, rate))
    print("  (sweep-the-class, grilling, deslop and agentic-vocabulary leave no "
          "trace either way - for them a miss is undetectable by machine, not zero)")

    print("\nBY STORE")
    for store, count in Counter(row["store"] for row in rows).most_common():
        print("  %4d  %s" % (count, store))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        handle.write("store\tproject\tsession\ttime\tskill\tguess\tcontext"
                     "\toutcome\tkept\tuser_text\tnext_user\n")
        for row in sorted(rows, key=lambda r: (r["store"], str(r["time"]))):
            handle.write("\t".join([
                row["store"], row["project"], row["session"], str(row["time"]),
                row["skill"], row["guess"], row["context"], row["outcome"], "",
                row["user_text"].replace("\t", " "),
                row["next_user"].replace("\t", " "),
            ]) + "\n")
    print("\nrows written to %s  (gitignored; 'kept' is filled in by hand during "
          "the classification pass)" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
