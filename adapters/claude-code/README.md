# adapters/claude-code

Delegation agents for Claude Code. **Opt-in, Claude-only, and outside the portable
core:** nothing in `skills/`, `lessons/` or `AGENTS.md` depends on anything here.

```
bash scripts/install.sh --with-agents
```

A plain `install.sh` installs none of this. With the flag, three files are placed
in `~/.claude/agents/`. Only `workbench-*.md` names are touched, and a file at one
of those names that does not carry the managed marker is left alone and reported.

## The agents

| Agent | Model | Tools | Use it for |
|---|---|---|---|
| `workbench-qa-runner` | haiku | Read, Grep, Glob, Bash | Running checks whose output is long. Focused checks first, full suite last. Returns commands, exit codes and the first failure. |
| `workbench-reviewer` | sonnet, effort high | Read, Grep, Glob, Bash | A second look before declaring done or merging. Returns a table of claim, verdict (`verified` / `incorrect` / `unresolved`), evidence, correction. |
| `workbench-patcher` | sonnet | Read, Grep, Glob, Edit, Write, Bash | Independent multi-file edits in parallel, each patch owning distinct files. Runs in a git worktree, never commits. |

Routing is the `description:` field of each file. That is what lets the main
session delegate without being told which agent to use.

Models are aliases (`haiku`, `sonnet`), which track the newest version of the
family. Pin a full model ID in the file if you need a run to be reproducible.

## What this does not do

- **Agent teams are not used.** They are experimental, need an interactive
  session, and the docs say a subagent that Claude names launches as a teammate
  once the experimental flag is on. Setting that flag globally would change
  delegation in every session on the machine.
- **Bash cannot be made read-only by `tools:`.** The Claude Code docs offer no
  frontmatter option for it, only a `PreToolUse` hook in the agent's frontmatter.
  `workbench-qa-runner` and `workbench-reviewer` have no Edit or Write tool and
  are told not to change the tree, but a shell command could still do it. If that
  matters, add the hook.
- **Delegation costs context.** A subagent does not see the main conversation.
  It pays off for parallel, isolated or noisy work, and loses on small edits.

## Not yet established

Written 2026-10-16 from the Claude Code documentation, not from use:

- That the main session actually delegates to these on its own. The library's
  central measurement is that skills are reached about one time in ten, and a
  description-routed agent faces the same problem. The trial in `docs/ROADMAP.md`
  counts it.
- That the patcher's worktree result is handed back the way the description
  assumes.
- That the agents load under every host. Tested: file shape and install
  behaviour (`tests/agents-invariants.sh`, `tests/install-smoke.sh`), and one
  headless Claude Code 2.1.296 run on Linux with the files in a project's
  `.claude/agents/`, which listed all three and logged no unrecognised-field
  warning. Not tested: any other host, including an SDK-driven session.
