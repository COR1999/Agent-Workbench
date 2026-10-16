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

Files are installed as links where the OS allows it and as copies otherwise. A
copy does not follow `git pull`: re-run `install.sh --with-agents` after pulling.

Routing is the `description:` field of each file. That is what lets the main
session delegate without being told which agent to use.

Models are aliases (`haiku`, `sonnet`), which track the newest version of the
family. Pin a full model ID in the file if you need a run to be reproducible.

## The Explore override

```
bash scripts/install.sh --with-explore-override
```

Claude Code's built-in `Explore` subagent runs on the main session's model, so
every delegated search is billed at that model's price. A user or project agent
named `Explore` replaces it, and `overrides/Explore.md` is that replacement:
Haiku, low effort, `Read, Grep, Glob` only.

It is a separate flag from `--with-agents` because it replaces a built-in for
**every** session on the machine, not just adds a helper. A user's own
`Explore.md` is never overwritten.

What it costs you:

- **Fewer tools than the built-in.** The built-in can also run shell commands, so
  a search that wants `git log` or `find` is no longer possible. Add `Bash` to the
  file if you want that back.
- **Search quality is unmeasured.** A cheaper model at low effort may miss matches
  a stronger one would find. The trial in `docs/ROADMAP.md` covers delegation, not
  this. Watch for "not found" answers that turn out to be wrong.

Not installed, deliberately: `CLAUDE_CODE_SUBAGENT_MODEL=haiku`. Per the docs it
does not change Explore or Plan on its own, and with `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`
it would also move subagents that pin their own model, including these agents. It
would also move the general-purpose subagent, which does the harder research.

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
- That the override works as intended. Tested on Claude Code 2.1.296, Linux, with
  the file in a project's `.claude/agents/` and a Sonnet main session: the
  subagent's messages in the session transcript were all `claude-haiku-5-5`, and a
  control run without the file used `claude-sonnet-5-5`. One query each, a tiny
  directory, so this shows precedence, not search quality.
- That the agents load under every host. Tested: file shape and install
  behaviour (`tests/agents-invariants.sh`, `tests/install-smoke.sh`), and one
  headless Claude Code 2.1.296 run on Linux with the files in a project's
  `.claude/agents/`, which listed all three and logged no unrecognised-field
  warning. Not tested: any other host, including an SDK-driven session.
