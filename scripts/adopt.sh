#!/usr/bin/env bash
# Import Agent-Workbench into a project: detect its stack, inline the
# matching lessons + the record-work reminder + a version marker into the
# project's AGENTS.md, and ensure CLAUDE.md points at it.
#
# Idempotent: the managed block (between the workbench:start / workbench:end markers) is
# stripped and re-appended at the end of AGENTS.md on every run. Your own edits
# outside the markers are never touched, though content you place *after* the
# block will end up above it after a re-run (relocated, never lost).
#
# Usage:  scripts/adopt.sh /path/to/project
#
# This does NOT install skills — those are machine-level; run install.sh once.
set -euo pipefail

PROJECT="${1:-}"
[ -n "$PROJECT" ] && [ -d "$PROJECT" ] || { echo "usage: adopt.sh <project-dir>"; exit 1; }

WORKBENCH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(cat "$WORKBENCH/VERSION" 2>/dev/null || echo "unknown")"
TODAY="$(date +%Y-%m-%d)"
LESSONS_DIR="$WORKBENCH/lessons"
START="<!-- workbench:start — managed by Agent-Workbench; do not edit inside this block -->"
END="<!-- workbench:end -->"
# Match existing blocks on the STABLE prefix, not the full START text — otherwise
# editing the START wording between versions would leave old blocks unrecognised
# and a re-run would append a duplicate. unadopt.sh uses the same prefixes.
START_PREFIX="<!-- workbench:start"
# The marker was `pas` before the rename to Agent-Workbench. Projects adopted
# under the old name still carry it, so both prefixes are recognised when
# stripping: a re-run MIGRATES an old block instead of appending a second one.
# Do not remove these until no adopted project carries the old marker.
LEGACY_START_PREFIX="<!-- pas:start"
LEGACY_END="<!-- pas:end -->"

# ---- detect stack -------------------------------------------------------------
cd "$PROJECT"
det=" "
# Idempotent: a signal detected twice (e.g. supabase by dep and by directory)
# is recorded once, so the stack line and matching stay clean.
add() { case "$det" in *" $1 "*) ;; *) det="${det}$1 ";; esac; }

# Collect all package.json and requirements.txt files (root + common monorepo
# subdirs). Arrays, not space-joined strings, so a path is never re-split on
# whitespace and each file is passed to grep as one argument.
pkgs=(package.json)
reqs=(pyproject.toml requirements.txt)
for sub in frontend backend web app client server; do
  [ -f "$sub/package.json" ]     && pkgs+=("$sub/package.json")
  [ -f "$sub/pyproject.toml" ]   && reqs+=("$sub/pyproject.toml")
  [ -f "$sub/requirements.txt" ] && reqs+=("$sub/requirements.txt")
done

# Node / Python presence
for p in "${pkgs[@]}"; do [ -f "$p" ] && { add node; break; }; done
for sub in . frontend backend web app client server; do [ -f "$sub/tsconfig.json" ] && { add typescript; break; }; done
for r in "${reqs[@]}"; do [ -f "$r" ] && { add python; break; }; done

# JS deps (grep across all package.jsons)
grep -qh '"react"' "${pkgs[@]}" 2>/dev/null && add react
grep -qh '"next"' "${pkgs[@]}" 2>/dev/null && add nextjs
# app-router: check root and the same monorepo subdirs used for package.json,
# not just src/app|app|frontend/app — otherwise web/, client/, etc. were missed.
for base in . frontend backend web client server; do
  { [ -f "$base/app/layout.tsx" ] || [ -f "$base/src/app/layout.tsx" ]; } && { add nextjs-app-router; break; }
done
grep -rqs 'use server' src app frontend/app frontend/src 2>/dev/null && add server-actions
grep -qh '"tailwindcss": *"\^3' "${pkgs[@]}" 2>/dev/null && add tailwind-v3
grep -qh '"tailwindcss": *"\^4' "${pkgs[@]}" 2>/dev/null && add tailwind-v4
{ [ -f components.json ] || [ -f frontend/components.json ]; } && add shadcn
grep -qh '@supabase' "${pkgs[@]}" 2>/dev/null && add supabase
grep -qh '"stripe"' "${pkgs[@]}" 2>/dev/null && add stripe
grep -qh '"resend"' "${pkgs[@]}" 2>/dev/null && add resend
grep -qh '"eslint"' "${pkgs[@]}" 2>/dev/null && add eslint
grep -qh '@radix-ui' "${pkgs[@]}" 2>/dev/null && add radix
grep -qh '"vitest"' "${pkgs[@]}" 2>/dev/null && add vitest
grep -qh '@playwright/test' "${pkgs[@]}" 2>/dev/null && add playwright
[ -d supabase ] && add supabase
grep -rqs 'export const revalidate\|next: *{ *revalidate' src app frontend/app frontend/src 2>/dev/null && add isr
[ -f vercel.json ] && add vercel
{ [ -f railway.json ] || [ -f Procfile ] || [ -f backend/Procfile ]; } && add railway

# Python deps (grep across all requirements/pyproject)
grep -qhsi 'fastapi' "${reqs[@]}" 2>/dev/null && add fastapi
grep -qhsi 'sqlalchemy' "${reqs[@]}" 2>/dev/null && add sqlalchemy
grep -qhsi 'google-genai\|google-generativeai' "${reqs[@]}" "${pkgs[@]}" 2>/dev/null && add gemini

[ -d .github/workflows ] && add github-actions

# Postgres: a driver in either ecosystem, or SQL migrations on disk.
grep -qh '"pg"\|"postgres"\|"@vercel/postgres"\|"postgres.js"' "${pkgs[@]}" 2>/dev/null && add postgres
grep -qhsi 'psycopg\|asyncpg\|postgresql' "${reqs[@]}" 2>/dev/null && add postgres
{ ls supabase/migrations/*.sql migrations/*.sql db/migrations/*.sql; } >/dev/null 2>&1 && add postgres

# Webhooks: a handler verifying a signature header. The signature check is the
# detectable part — "a route called webhook" is a naming convention, the
# verification is the thing the lessons are actually about.
grep -rqsi 'stripe-signature\|x-hub-signature\|svix-signature\|x-signature-ed25519\|constructEvent'   src app frontend backend web client server 2>/dev/null && add webhooks

# Machine-level values. Detected from the machine, not the repo — same basis as
# windows/macos below. Without these, lessons about the agent's own environment
# can never match any project: they are not wrong, they are unreachable, and
# nothing reports that (see scripts/lesson-audit.py).
{ [ -d "$HOME/.local/share/opencode" ] || [ -d "$HOME/.config/opencode" ]; } && add opencode
harnesses=0
for d in "$HOME/.claude" "$HOME/.agents" "$HOME/.config/opencode"; do
  [ -d "$d" ] && harnesses=$((harnesses + 1))
done
[ "$harnesses" -ge 2 ] && add multi-agent

case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) add windows;; Darwin) add macos;; esac

# ---- match lessons (AND: every applies-to value must be present) ---------------
matched=""
for f in "$LESSONS_DIR"/*.md; do
  [ -f "$f" ] || continue
  slug="$(basename "$f" .md)"
  req="$(sed -n 's/^applies-to: *\[\(.*\)\].*/\1/p' "$f" | tr ',' ' ')"
  date="$(sed -n 's/^discovered: *\([0-9-]*\).*/\1/p' "$f")"
  claim="$(sed -n 's/^# *//p' "$f" | head -1)"
  ok=1
  for r in $req; do case "$det" in *" $r "*) ;; *) ok=0;; esac; done
  [ "$ok" = 1 ] && matched="${matched}- **${slug}** (${date}) — ${claim}"$'\n'
done

# ---- build the managed block --------------------------------------------------
block="$START
## Inherited from Agent-Workbench (v${VERSION}, imported ${TODAY})

<!-- Rules and lessons here are copied from the workbench. Edit them at the
     source and re-run scripts/adopt.sh; edits made inside this block are lost. -->

**Work record:** commit bodies carry the durable account — how it was found, the
root cause, the mechanism chosen and why, and how it was verified. Not a one-line
subject.

**Citing a lesson:** when one of the lessons below changes what you do, name
it in the commit body or PR as: lesson: <slug>. That citation is the only
evidence a lesson earned its place.

**Lessons matched to this stack:**
"
if [ -n "$matched" ]; then
  block="${block}${matched}"
else
  block="${block}- (none matched this stack)"$'\n'
fi
block="${block}${END}"

# ---- ensure AGENTS.md exists --------------------------------------------------
if [ ! -f AGENTS.md ]; then
  proj_name="$(basename "$PROJECT")"
  printf '# %s — agent context\n\n' "$proj_name" > AGENTS.md
  echo "created AGENTS.md"
fi

# ---- replace the managed block idempotently -----------------------------------
# Strip any existing block, then append the fresh one.
awk -v s="$START_PREFIX" -v ls="$LEGACY_START_PREFIX" -v e="$END" -v le="$LEGACY_END" '
  index($0,s) || index($0,ls){skip=1}
  !skip{print}
  index($0,e) || index($0,le){skip=0; next}
' AGENTS.md > AGENTS.md.tmp

# drop trailing blank lines, then append block with one separating blank line
# Drop trailing blank lines. This was `sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}'`,
# which is GNU-specific: BSD sed (macOS) parses the label/branch differently and
# emptied the file instead of trimming it. Found by the cross-platform CI matrix
# (#28) on its first run — every "user content survives" assertion failed on
# macOS while passing on Linux and Windows. awk is portable and says what it means.
awk '{lines[NR]=$0; if (NF) last=NR} END {for (i=1;i<=last;i++) print lines[i]}' AGENTS.md.tmp > AGENTS.md
rm -f AGENTS.md.tmp
printf '\n%s\n' "$block" >> AGENTS.md

# ---- ensure CLAUDE.md points at AGENTS.md -------------------------------------
if [ ! -f CLAUDE.md ]; then
  echo '@AGENTS.md' > CLAUDE.md
  echo "created CLAUDE.md"
elif ! grep -q '@AGENTS.md' CLAUDE.md; then
  echo "note: CLAUDE.md exists without '@AGENTS.md' — left as-is. Add it manually if you want AGENTS.md loaded."
fi

echo "adopted Agent-Workbench v${VERSION} into $PROJECT"
echo "  stack:  ${det# }"
echo "  lessons inlined: $(printf '%s' "$matched" | grep -c '^-' || true)"
