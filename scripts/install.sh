#!/usr/bin/env bash
# Machine setup for Agent-Workbench. Run once per machine; re-run after a
# `git pull` to refresh. Idempotent. Does two things:
#
#   1. Installs the skills into each harness's skills dir (symlink, copy fallback).
#   2. Installs the machine-wide RULES into ~/.claude/CLAUDE.md so they load in
#      every session — otherwise the rules in this repo's AGENTS.md reach nobody.
#
# Per-project lessons are NOT handled here — those are imported per project with
# adopt.sh. Only machine-global things (skills, environment rules) install here.
#
# Opt-in:  --with-agents  also installs the Claude Code delegation agents from
#          adapters/claude-code/ into ~/.claude/agents. Off by default: they are
#          Claude-only, and the portable core must not depend on them.
#          --with-explore-override  installs adapters/claude-code/overrides/Explore.md,
#          which REPLACES Claude Code's built-in Explore subagent (Haiku, low effort)
#          for every session on the machine. Separate from --with-agents on purpose.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
AGENTS_SRC="$REPO_DIR/adapters/claude-code/agents"
OVERRIDES_SRC="$REPO_DIR/adapters/claude-code/overrides"

with_agents=0
with_explore_override=0
for arg in "$@"; do
  case "$arg" in
    --with-agents) with_agents=1 ;;
    --with-explore-override) with_explore_override=1 ;;
    *) echo "unknown argument: $arg" >&2
       echo "usage: install.sh [--with-agents] [--with-explore-override]" >&2
       exit 2 ;;
  esac
done

# --- 1. skills ----------------------------------------------------------------
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.agents/skills"
)

link_or_copy() {
  local src="$1" dst="$2"
  rm -rf "$dst"
  if ln -s "$src" "$dst" 2>/dev/null && [ -e "$dst" ]; then
    echo "  linked  $dst"
  else
    # No symlink privilege / filesystem won't link: copy. A copy does NOT update
    # on git pull — re-run this script after pulling. Deliberate, not a bug.
    cp -R "$src" "$dst"
    echo "  copied  $dst   (re-run after 'git pull' to refresh)"
  fi
}

installed_any=0
for target in "${TARGETS[@]}"; do
  if [ ! -d "$(dirname "$target")" ]; then
    echo "skip (no harness dir): $(dirname "$target")"
    continue
  fi
  installed_any=1
  mkdir -p "$target"
  echo "installing skills into $target"
  for skill in "$SKILLS_SRC"/*/; do
    [ -f "$skill/SKILL.md" ] || continue
    link_or_copy "${skill%/}" "$target/$(basename "$skill")"
  done
done
[ "$installed_any" = 1 ] || echo "no harness skills dir found (~/.claude or ~/.agents) — skills not installed"

# --- 1b. delegation agents (opt-in) -------------------------------------------
# A file is replaced only if it carries the managed marker (or is a dangling
# link). A user's own agent at the same name is left alone and reported, because
# overwriting it would be silent. --with-agents only ever touches workbench-*.md;
# the Explore override is a separate flag because it replaces a built-in.
install_agent_files() {
  local src dst
  mkdir -p "$HOME/.claude/agents"
  for src in "$@"; do
    [ -f "$src" ] || continue
    dst="$HOME/.claude/agents/$(basename "$src")"
    if [ -e "$dst" ] || [ -L "$dst" ]; then
      if [ -L "$dst" ] && [ ! -e "$dst" ]; then
        :
      elif ! grep -q 'managed by Agent-Workbench' "$dst" 2>/dev/null; then
        echo "  skip    $dst (not managed by Agent-Workbench; left alone)"
        continue
      fi
    fi
    link_or_copy "$src" "$dst"
  done
}

if [ "$with_agents" = 1 ] || [ "$with_explore_override" = 1 ]; then
  if [ -d "$HOME/.claude" ]; then
    echo "installing agents into $HOME/.claude/agents"
    [ "$with_agents" = 1 ] && install_agent_files "$AGENTS_SRC"/workbench-*.md
    [ "$with_explore_override" = 1 ] && install_agent_files "$OVERRIDES_SRC"/Explore.md
  else
    echo "skip agents: no ~/.claude"
  fi
fi

# --- 2. machine rules into ~/.claude/CLAUDE.md --------------------------------
# The rules are COPIED (not @-imported) on purpose: an @import with an absolute
# Windows path is exactly the kind of path-resolution fragility this project has
# a lesson about. A copy always resolves. Re-run this script to refresh after
# editing the repo's AGENTS.md.
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
START="<!-- workbench-rules:start — managed by Agent-Workbench; edit AGENTS.md at the source and re-run install.sh -->"
END="<!-- workbench-rules:end -->"
# Machines set up before the rename carry the old `pas-rules` markers. Both are
# stripped, so a re-run migrates the block rather than leaving a stale duplicate
# of the rules loaded into every session alongside the new one.
LEGACY_START="<!-- pas-rules:start"
LEGACY_END="<!-- pas-rules:end -->"

# Machine-specific facts (OS, shell quirks, what is installed) are not rules that
# hold everywhere, so they live in environments/ and only the matching file is
# appended. WORKBENCH_ENV=<file-stem> overrides the uname guess.
env_name="${WORKBENCH_ENV:-}"
if [ -z "$env_name" ]; then
  case "$(uname -s)" in
    Linux*)                env_name="linux" ;;
    MINGW*|MSYS*|CYGWIN*)  env_name="windows-git-bash" ;;
  esac
fi
ENV_FILE=""
if [ -n "$env_name" ] && [ -f "$REPO_DIR/environments/$env_name.md" ]; then
  ENV_FILE="$REPO_DIR/environments/$env_name.md"
  echo "environment: $env_name"
else
  echo "environment: none for '${env_name:-$(uname -s)}' — rules installed without an Environment section (add environments/<name>.md)"
fi

if [ -d "$HOME/.claude" ]; then
  [ -f "$CLAUDE_MD" ] || : > "$CLAUDE_MD"
  # strip any existing managed block
  awk -v s="$START" -v ls="$LEGACY_START" -v e="$END" -v le="$LEGACY_END" '
    index($0,s) || index($0,ls){skip=1}
    !skip{print}
    index($0,e) || index($0,le){skip=0; next}
  ' "$CLAUDE_MD" > "$CLAUDE_MD.tmp"
  # Drop trailing blank lines. This was `sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}'`,
  # which is GNU-specific: BSD sed (macOS) parses the label/branch differently and
  # emptied the file instead of trimming it. Found by the cross-platform CI matrix
  # (#28) on its first run — every "user content survives" assertion failed on
  # macOS while passing on Linux and Windows. awk is portable and says what it means.
  awk '{lines[NR]=$0; if (NF) last=NR} END {for (i=1;i<=last;i++) print lines[i]}' "$CLAUDE_MD.tmp" > "$CLAUDE_MD"
  rm -f "$CLAUDE_MD.tmp"
  {
    printf '\n%s\n' "$START"
    cat "$REPO_DIR/AGENTS.md"
    if [ -n "$ENV_FILE" ]; then
      printf '\n'
      cat "$ENV_FILE"
    fi
    printf '%s\n' "$END"
  } >> "$CLAUDE_MD"
  echo "installed machine rules into $CLAUDE_MD"
else
  echo "skip machine rules: no ~/.claude (add the contents of AGENTS.md to your harness's global instructions manually)"
fi

echo "done."
echo "  verify skills: ls -l \"${TARGETS[0]}\""
echo "  verify rules:  grep workbench-rules \"$CLAUDE_MD\""
