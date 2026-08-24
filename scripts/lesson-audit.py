#!/usr/bin/env python3
"""Audit the lessons ledger against the matching rule that governs it.

A lesson is inlined into a project only when EVERY value in its `applies-to` is
detected there. That AND rule was adopted deliberately and marked for revisit at
15 entries. The ledger passed 15 without the revisit happening, which is what this
makes cheap enough to repeat: it is the revisit as a script rather than as an
opinion someone has to remember to form.

Three failure modes the rule can produce, all of them silent:

  UNREACHABLE  the lesson names a value `adopt.sh` cannot detect, so it can never
               match any project no matter how apt it is. Dead weight by
               construction, and nothing reports it - adopt.sh just does not
               inline it, with no error.
  UNIVERSAL    the lesson matches every project. A lesson that always applies is
               a rule, and belongs in AGENTS.md where it loads unconditionally.
  UNMATCHED    the lesson is reachable in principle but matches none of the
               projects actually checked. Not necessarily wrong - it may be
               waiting for the right project - but worth seeing.

The detectable vocabulary is read out of `scripts/adopt.sh` itself rather than
restated here. Restating it would create a second source of truth that drifts,
which is the same class of problem this script exists to find.

Usage:
  python scripts/lesson-audit.py [project-dir ...]
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def detectable_values():
    """Values adopt.sh can actually detect, read from its own `add` calls."""
    text = (REPO / "scripts" / "adopt.sh").read_text(encoding="utf-8")
    body = text.split("---- detect stack")[1].split("---- match lessons")[0]
    found = set(re.findall(r"\badd ([a-z0-9-]+)", body))
    found.discard("")
    return found


def vocabulary_values():
    """Values the template declares, i.e. what a lesson author may choose from."""
    text = (REPO / "templates" / "lesson.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| `([a-z0-9-]+)` \|", text, flags=re.MULTILINE))


def lessons():
    out = []
    for path in sorted((REPO / "lessons").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^applies-to:\s*\[(.*?)\]", text, flags=re.MULTILINE)
        status = re.search(r"^status:\s*(.+)$", text, flags=re.MULTILINE)
        values = []
        if match:
            values = [v.strip() for v in match.group(1).split(",") if v.strip()]
        out.append({
            "slug": path.stem,
            "applies_to": values,
            "status": (status.group(1).strip() if status else "?"),
        })
    return out


def detect_project(project):
    """Approximate adopt.sh's detection well enough to compare matching rules.

    Deliberately a subset: it covers the file-and-dependency signals, which is
    what nearly every lesson keys on. Machine-level values (windows/macos) are
    added because they are true of the machine running this.
    """
    project = pathlib.Path(project)
    found = set()
    if sys.platform.startswith("win"):
        found.add("windows")
    elif sys.platform == "darwin":
        found.add("macos")

    pkgs = [project / "package.json"]
    reqs = [project / "pyproject.toml", project / "requirements.txt"]
    for sub in ("frontend", "backend", "web", "app", "client", "server"):
        pkgs.append(project / sub / "package.json")
        reqs += [project / sub / "pyproject.toml", project / sub / "requirements.txt"]

    pkg_text = ""
    for p in pkgs:
        if p.is_file():
            found.add("node")
            pkg_text += p.read_text(encoding="utf-8", errors="replace")
    req_text = ""
    for r in reqs:
        if r.is_file():
            found.add("python")
            req_text += r.read_text(encoding="utf-8", errors="replace")

    for sub in (".", "frontend", "backend", "web", "app", "client", "server"):
        if (project / sub / "tsconfig.json").is_file():
            found.add("typescript")
            break

    deps = {
        '"react"': "react", '"next"': "nextjs", '@supabase': "supabase",
        '"stripe"': "stripe", '"resend"': "resend", '"eslint"': "eslint",
        '@radix-ui': "radix", '"vitest"': "vitest",
        '@playwright/test': "playwright",
    }
    for needle, value in deps.items():
        if needle in pkg_text:
            found.add(value)
    if re.search(r'"tailwindcss": *"\^3', pkg_text):
        found.add("tailwind-v3")
    if re.search(r'"tailwindcss": *"\^4', pkg_text):
        found.add("tailwind-v4")
    for name in ("fastapi", "sqlalchemy"):
        if name in req_text.lower():
            found.add(name)

    # Machine-level values, mirroring adopt.sh: these describe the machine the
    # agent runs on, not the repository, and without them the agent-environment
    # lessons look unmatched when they are simply not project-scoped.
    home = pathlib.Path.home()
    if (home / ".local/share/opencode").is_dir() or (home / ".config/opencode").is_dir():
        found.add("opencode")
    if sum((home / d).is_dir() for d in (".claude", ".agents", ".config/opencode")) >= 2:
        found.add("multi-agent")

    if (re.search(r'"(pg|postgres|@vercel/postgres|postgres\.js)"', pkg_text)
            or re.search(r"psycopg|asyncpg|postgresql", req_text, flags=re.I)):
        found.add("postgres")
    for pattern in ("supabase/migrations", "migrations", "db/migrations"):
        d = project / pattern
        if d.is_dir() and any(d.glob("*.sql")):
            found.add("postgres")
            break

    for base in (".", "frontend", "backend", "web", "client", "server"):
        if ((project / base / "app" / "layout.tsx").is_file()
                or (project / base / "src" / "app" / "layout.tsx").is_file()):
            found.add("nextjs-app-router")
            break
    if (project / "components.json").is_file() or (project / "frontend" / "components.json").is_file():
        found.add("shadcn")
    if (project / "supabase").is_dir():
        found.add("supabase")
    if (project / "vercel.json").is_file():
        found.add("vercel")
    if (project / ".github" / "workflows").is_dir():
        found.add("github-actions")
    for src in ("src", "app", "frontend"):
        root = project / src
        if not root.is_dir():
            continue
        for path in list(root.rglob("*.ts"))[:400] + list(root.rglob("*.tsx"))[:400]:
            try:
                body = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "use server" in body:
                found.add("server-actions")
            if "export const revalidate" in body:
                found.add("isr")
    return found


def readme_linked_slugs():
    """Slugs listed as ROWS of the README lessons table.

    Scoped to table rows on purpose. Matching any link to `lessons/` counted a
    passing prose mention elsewhere in the README as an index entry, so a lesson
    could be missing from the table and still pass — which is precisely the drift
    this is meant to catch. Verified by removing a row and confirming the check
    fails.
    """
    text = (REPO / "README.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\|\s*\[[^\]]+\]\(lessons/([a-z0-9-]+)\.md\)",
                          text, flags=re.MULTILINE))


def run_checks(entries, detectable, declared):
    """Fail on the drift this ledger can accumulate silently.

    Each of these was a real state of the repository, not a hypothetical:
    lessons naming values nothing could detect, values in use that the "closed"
    vocabulary never declared, and four lessons on disk that the README index
    had never listed. None of it produced an error anywhere.
    """
    problems = []
    used = {v for e in entries for v in e["applies_to"]}

    for entry in entries:
        if not entry["applies_to"]:
            problems.append("%s: no applies-to values could be parsed from its "
                            "frontmatter" % entry["slug"])

    for value in sorted(used - declared):
        problems.append("value %r is used by a lesson but not declared in "
                        "templates/lesson.md" % value)

    for entry in entries:
        blocking = [v for v in entry["applies_to"] if v not in detectable]
        if blocking:
            problems.append("%s can never match any project: adopt.sh cannot "
                            "detect %s" % (entry["slug"], ", ".join(blocking)))

    linked = readme_linked_slugs()
    for slug in sorted({e["slug"] for e in entries} - linked):
        problems.append("%s is in lessons/ but absent from the README table"
                        % slug)
    for slug in sorted(linked - {e["slug"] for e in entries}):
        problems.append("%s is linked from the README but has no lesson file"
                        % slug)
    return problems


def main():
    argv = [a for a in sys.argv[1:] if a != "--check"]
    check_mode = "--check" in sys.argv[1:]
    projects = argv
    detectable = detectable_values()
    declared = vocabulary_values()
    entries = lessons()

    if check_mode:
        problems = run_checks(entries, detectable, declared)
        if problems:
            print("lesson-audit --check: %d problem(s)" % len(problems))
            for problem in problems:
                print("  FAIL  " + problem)
            return 1
        print("lesson-audit --check: ledger consistent (%d lessons)" % len(entries))
        return 0

    print("LEDGER: %d lessons" % len(entries))
    print("adopt.sh can detect %d values; the template declares %d\n"
          % (len(detectable), len(declared)))

    used = {v for e in entries for v in e["applies_to"]}
    undeclared = sorted(used - declared)
    undetectable = sorted(used - detectable)
    if undeclared:
        print("VALUES USED BY A LESSON BUT NOT IN THE TEMPLATE VOCABULARY:")
        print("  " + ", ".join(undeclared))
        print("  (the vocabulary is supposed to be closed; these entered anyway)\n")

    unreachable = [e for e in entries
                   if any(v not in detectable for v in e["applies_to"])]
    print("UNREACHABLE — can never match any project, because adopt.sh cannot "
          "detect one of their values:")
    if not unreachable:
        print("  none")
    for entry in unreachable:
        blocking = [v for v in entry["applies_to"] if v not in detectable]
        print("  %-46s blocked by: %s" % (entry["slug"], ", ".join(blocking)))
    print("  %d of %d lessons (%.0f%%)\n"
          % (len(unreachable), len(entries), 100.0 * len(unreachable) / len(entries)))

    # The finding that answers the AND-matching revisit. A value like `windows`
    # describes the MACHINE, so it is true of every project on it. A lesson whose
    # applies-to contains only machine-level values therefore matches everything
    # — AND-matching cannot narrow it, because there is no project-level term to
    # narrow on. Such a lesson is a machine rule wearing a lesson's frontmatter.
    machine_level = {"windows", "macos", "opencode", "multi-agent"}
    machine_only = [e for e in entries
                    if e["applies_to"] and set(e["applies_to"]) <= machine_level]
    print("MACHINE-ONLY — every applies-to value describes the machine, not the "
          "project, so\n  AND-matching cannot narrow these: they inline into "
          "every project on this machine:")
    if not machine_only:
        print("  none")
    for entry in machine_only:
        print("  %-46s %s" % (entry["slug"], ", ".join(entry["applies_to"])))
    print("  %d of %d lessons (%.0f%%)\n"
          % (len(machine_only), len(entries), 100.0 * len(machine_only) / len(entries)))

    sizes = {}
    for entry in entries:
        sizes[len(entry["applies_to"])] = sizes.get(len(entry["applies_to"]), 0) + 1
    print("APPLIES-TO SIZE (narrower is better; 1 value is close to a rule):")
    for size in sorted(sizes):
        print("  %d value(s): %d lesson(s)" % (size, sizes[size]))
    print()

    if not projects:
        print("No project directories given, so match rates were not measured.")
        print("Usage: python scripts/lesson-audit.py <project-dir> [...]")
        return 0

    print("MATCHING (AND: every value must be present)")
    match_counts = {e["slug"]: 0 for e in entries}
    for project in projects:
        detected = detect_project(project)
        matched = [e["slug"] for e in entries
                   if e["applies_to"] and all(v in detected for v in e["applies_to"])]
        for slug in matched:
            match_counts[slug] += 1
        print("  %-28s %2d/%d lessons match" % (
            pathlib.Path(project).name, len(matched), len(entries)))

    total = len(projects)
    universal = [s for s, c in match_counts.items() if c == total and total > 0]
    unmatched = [e["slug"] for e in entries
                 if match_counts[e["slug"]] == 0 and e not in unreachable]
    print("\n  UNIVERSAL (matched every project — a lesson that always applies is "
          "a rule):")
    print("    " + (", ".join(universal) if universal else "none"))
    print("  UNMATCHED (reachable, but matched none of these projects):")
    print("    %d lesson(s)" % len(unmatched))
    for slug in unmatched:
        print("      " + slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
