---
name: agentic-vocabulary
description: >
  Reference skill. Consult when you hit an agentic-coding term that is unfamiliar,
  ambiguous, or overloaded (skill vs tool vs subagent vs workflow, handoff,
  harness, context window, progressive disclosure, etc.) and you'd otherwise
  guess. Look up the definition here before proceeding. NOT for every task — only
  when a term's meaning is genuinely uncertain.
disable-model-invocation: false
---

# agentic-vocabulary

A canonical glossary so the model looks a term up instead of inventing a meaning.
Aligned with Matt Pocock's **AI Coding Dictionary** (aicodingdictionary.com /
github.com/mattpocock/dictionary-of-ai-coding) for the terms it defines; entries
marked *(our usage)* are ones the dictionary doesn't cover, defined the way this
project uses them (consistent with our `WAYFINDING.md`, `CONTEXT-LOOP.md`, and the
skill files). When in doubt, the dictionary is canonical for shared terms.

Consult when unsure, apply the definition, move on.

## Glossary

- **Agent** — an LLM given tools and a goal that acts in a loop (reason → act →
  observe) until done. Not a single prompt/response.
- **Harness** — the runtime hosting the agent (e.g. Claude Code): supplies tools,
  manages context, renders output, enforces permissions. The agent runs *inside*
  it and doesn't control it.
- **Session** — one continuous run of an agent with one accumulating context. Ends
  at a reset; durable state must outlive it (see handoff).
- **Context window** — the token budget the model can attend to at once. Fills with
  conversation, tool output, and files; performance degrades as it fills (see
  `CONTEXT-LOOP.md`).
- **Turn** — one step in the loop: the agent's message plus the tool calls in it
  and their results.
- **Tool** — a deterministic capability the agent invokes (read a file, run a
  command, call an API). Same input, same output; no judgement of its own.
- **Skill** *(our usage)* — a packaged, reusable *procedure with judgement* the
  agent follows for a kind of task. Has steps and guardrails. Distinct from a tool
  (mechanical) and a subagent (an actor).
- **Subagent** *(our usage)* — a separate agent instance spawned to do a scoped
  task in its own fresh context, reporting a result back. An actor, not a procedure.
- **Workflow** *(our usage)* — an ordered sequence of skills/steps toward one
  objective. Composes skills; a skill doesn't compose workflows.
- **Handoff** — passing an effort between sessions. The *tactical* baton (current
  blocker, files, next action), distinct from the strategic map. See
  `skills/handoff`.
- **Handoff artifact** — the concrete file/issue-comment a handoff is written to,
  read by the next session.
- **Spec** — a settled description of what to build, handed off from
  wayfinding/design into implementation. Decisions resolved, not open questions.
- **Automated check** — a deterministic gate (typecheck, tests, lint, a grep
  guard) that passes or fails without judgement.
- **Automated review** — a model reading a diff for issues (e.g. `deslop`,
  `sweep-the-class`). Judgement, but no human.
- **Human review** — a person deciding (approve a design, merge a PR). The final
  gate for anything outward-facing or hard to reverse.
- **Progressive disclosure** — surfacing only what's relevant now (a skill routed
  by its `description`, detail fetched on demand) so the context stays small.

## Guardrail

If a needed term isn't here and matters to the task, say so and add it via
`capture-lesson`/a doc edit rather than inventing a definition silently.
