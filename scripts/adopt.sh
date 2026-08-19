#!/usr/bin/env bash
# Import personal-agent-system into a project: detect its stack, inline the
# matching lessons + the record-work reminder + a version marker into the
# project's AGENTS.md, and ensure CLAUDE.md points at it.
#
# Idempotent: the managed block (between the pas:start / pas:end markers) is
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
START="<!-- pas:start — managed by personal-agent-system; do not edit inside this block -->"
END="<!-- pas:end -->"
# Match existing blocks on the STABLE prefix, not the full START text — otherwise
# editing the START wording between versions would leave old blocks unrecognised
# and a re-run would append a duplicate. unadopt.sh uses the same prefix.
START_PREFIX="<!-- pas:start"

# ---- detect stack -------------------------------------------------------------
cd "$PROJECT"
det=" "
add() { det="${det}$1 "; }
[ -f package.json ]     && add node
[ -f tsconfig.json ]    && add typescript
[ -f pyproject.toml ] || [ -f requirements.txt ] && add python
grep -q '"react"'   package.json 2>/dev/null && add react
grep -q '"next"'    package.json 2>/dev/null && add nextjs
{ [ -f src/app/layout.tsx ] || [ -f app/layout.tsx ]; } && add nextjs-app-router
grep -rqs 'use server' src app 2>/dev/null && add server-actions
grep -q '"tailwindcss": *"\^3' package.json 2>/dev/null && add tailwind-v3
grep -q '"tailwindcss": *"\^4' package.json 2>/dev/null && add tailwind-v4
[ -f components.json ]  && add shadcn
grep -q '@supabase'  package.json 2>/dev/null && add supabase
grep -q '"stripe"'   package.json 2>/dev/null && add stripe
grep -q '"resend"'   package.json 2>/dev/null && add resend
grep -q '"eslint"'   package.json 2>/dev/null && add eslint
grep -q '@radix-ui'  package.json 2>/dev/null && add radix
grep -q '"vitest"'   package.json 2>/dev/null && add vitest
grep -q '@playwright/test' package.json 2>/dev/null && add playwright
{ [ -f supabase ] || [ -d supabase ]; } 2>/dev/null && add supabase   # dir form, in addition to the dep grep above
grep -rqs 'export const revalidate\|next: *{ *revalidate' src app 2>/dev/null && add isr
[ -f vercel.json ] && add vercel
{ [ -f railway.json ] || [ -f Procfile ]; } && add railway
grep -rqsi 'fastapi' pyproject.toml requirements.txt 2>/dev/null && add fastapi
grep -rqsi 'sqlalchemy' pyproject.toml requirements.txt 2>/dev/null && add sqlalchemy
grep -rqsi 'google-genai\|google-generativeai' pyproject.toml requirements.txt package.json 2>/dev/null && add gemini
[ -d .github/workflows ] && add github-actions
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) add windows;; Darwin) add macos;; esac
# Not auto-detected (rare / structural): postgres, webhooks. A lesson tagged with
# one of these will simply never match until detection is added — see the note in
# templates/lesson.md. No error; it just won't inline.

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
## Inherited from personal-agent-system (v${VERSION}, imported ${TODAY})

<!-- Rules and lessons here are copied from the workbench. Edit them at the
     source and re-run scripts/adopt.sh; edits made inside this block are lost. -->

**Work record:** commit bodies carry the durable account — how it was found, the
root cause, the mechanism chosen and why, and how it was verified. Not a one-line
subject.

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
awk -v s="$START_PREFIX" -v e="$END" '
  index($0,s){skip=1}
  !skip{print}
  index($0,e){skip=0; next}
' AGENTS.md > AGENTS.md.tmp

# drop trailing blank lines, then append block with one separating blank line
sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}' AGENTS.md.tmp > AGENTS.md
rm -f AGENTS.md.tmp
printf '\n%s\n' "$block" >> AGENTS.md

# ---- ensure CLAUDE.md points at AGENTS.md -------------------------------------
if [ ! -f CLAUDE.md ]; then
  echo '@AGENTS.md' > CLAUDE.md
  echo "created CLAUDE.md"
elif ! grep -q '@AGENTS.md' CLAUDE.md; then
  echo "note: CLAUDE.md exists without '@AGENTS.md' — left as-is. Add it manually if you want AGENTS.md loaded."
fi

echo "adopted personal-agent-system v${VERSION} into $PROJECT"
echo "  stack:  ${det# }"
echo "  lessons inlined: $(printf '%s' "$matched" | grep -c '^-' || true)"
