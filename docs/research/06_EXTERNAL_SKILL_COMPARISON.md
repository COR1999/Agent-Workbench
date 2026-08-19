# 06 — External Skill Comparison

Four libraries studied at source level. All four cloned and read, not summarised from READMEs.

| Library | Skills | Character |
|---|---|---|
| [cursor/plugins](https://github.com/cursor/plugins) | 82 SKILL.md across 13 plugins | Cursor's official marketplace. Plugin-packaged (manifest + skills + agents + hooks). Ships poteto's `pstack` inside it. |
| [poteto/plugins](https://github.com/poteto/plugins) | 69 | **Substantially the same repository as cursor/plugins.** Same plugin folders, same skills. poteto is the upstream author of `pstack`; cursor/plugins is a superset. Treat as one source, not two. |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 35 across 5 buckets | The closest match to what you're trying to build. Personal library, opinionated, documented, versioned, installable two ways. |
| [steipete/agent-scripts](https://github.com/steipete/agent-scripts) | 56 | Personal ops repo. Deeply macOS/Swift/Xcode-specific. Architecturally instructive, mostly not adoptable. |

---

## 1. Architecture lessons (independent of any individual skill)

### From mattpocock/skills — the template to follow

**Bucket promotion.** Skills live in `engineering/`, `productivity/`, `misc/`, `in-progress/`, `deprecated/`. Only the first two are "promoted" — they ship in the plugin, appear in the README, and get a docs page. This gives you a graveyard and a nursery without polluting routing. **Directly adoptable and solves your section 39 junk-drawer worry mechanically rather than by willpower.**

**A router skill.** `ask-matt` maps every user-reachable skill and how they relate. Their `CLAUDE.md` states the maintenance rule: *"a new skill it never mentions, or a stale one it still routes to, is a router that lies."* **Adopt** — see report 11.

**Two installation philosophies, stated explicitly.** Plugin install = read-only subscription that updates when upstream ships. `npx skills@latest add` = editable copies you fork. Their README: *"Pick one: installing both leaves you with every skill twice."* **Relevant to your section 34/35.**

**Symlink installer.** `scripts/link-skills.sh` symlinks each skill into both `~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex and other Agent-Skills-compatible harnesses), so `git pull` updates everything. **This is the concrete answer to your portability requirement, and it's twelve lines of bash.** Adopt.

**ADRs.** `.agents/adr/0002-ship-as-a-claude-code-plugin.md`. **Adopt** — matches your existing habit of recording rejected alternatives.

### From steipete/agent-scripts — the AGENTS.md discipline

His `AGENTS.MD` is telegraphic, dense, hard-rules-only, organised as Communication / Core / Routing / Project Defaults / PR-CI. One line states the boundary explicitly:

> Skills own tool workflows. This file: hard rules only.

**This validates your section 36 hypothesis.** Note that your own `senus/frontend/AGENTS.md` does *not* follow it — it's 160 lines of product context, design system and component inventory. Both are correct for their level: report 13 recommends splitting them (central AGENTS.md = rules; project AGENTS.md = context).

**Also from steipete:** a `validate-skills` script and a `skill-cleaner` skill (*"live budget, usage, duplicates, compact descriptions"*). He treats description budget as a scarce resource that needs periodic audit. Worth knowing before you have 30 skills.

### From cursor/plugins — the principle layer

`pstack` ships ~24 `principle-*` skills, all `disable-model-invocation: true`. They aren't procedures; they're compressed judgement, invoked deliberately. This is a genuinely useful third category alongside rules and skills. Several map directly onto behaviour you already exhibit (see §3).

`continual-learning` + `reflect` + `workflow-from-chats` are the three closest existing things to your "dreaming" layer, and all three are transcript-mining. Study these before building anything in that direction.

---

## 2. The comparison table

Verdicts: **ADOPT** (take as-is), **ADAPT** (take the shape, change the content), **COMBINE** (fold into one of your skills), **INSPIRE** (read it, write your own), **REJECT**.

| Skill | Source | Relevant? | Covered? | Verdict | Reasoning |
|---|---|---|---|---|---|
| `deslop` | cursor | **Yes** | No | **ADAPT** | The seed of your headline skill, but two of its four focus areas are actively wrong for your code. See report 09. |
| `unslop` | poteto | Yes | No | **ADAPT** | Excellent AI-tell taxonomy for prose. **Must drop rule 13 (ban em dashes)** — you use them constantly and they're part of your voice. Also drop the "add soul" section; your prose already has it. |
| `no-comments` | poteto | Partly | No | **COMBINE** into deslop | Its stance (spawn a reviewer, then *"offer encodings for claimed constraints"*) is smart: if a comment claims a constraint, make the constraint enforceable. Your CI already does this. Fold the idea in, don't take the skill. |
| `principle-encode-lessons-in-structure` | poteto | **Yes** | Partly — you do this by instinct | **ADOPT** | The single most valuable external artefact for you. Its "pick the strongest rung" ladder (unrepresentable state → lint/CI failure → canonical helper → runtime check → prose) is exactly the decision `capture-lesson` needs to make. |
| `principle-fix-root-causes` | poteto | Yes | Yes, behaviourally | **ADOPT** | Cheap, matches your commit-body practice, useful as an explicit reminder to agents. |
| `principle-make-operations-idempotent` | poteto | **Yes** | Partly | **COMBINE** into `concurrency-correctness` | Directly on-target for issues #81, #191, #212, #242. |
| `principle-boundary-discipline` | poteto | **Yes** | No | **COMBINE** into `boundary-validation` | *"Concentrate guards at system boundaries; trust internals"* is precisely the discipline your Server Action mistakes needed. |
| `principle-type-system-discipline` | poteto | Yes | **Yes, already** | **REJECT** | *"Make illegal states unrepresentable"* — you already do this (`ActionResult`, cents-as-base-unit, generated DB types). Nothing to add. |
| `principle-sequence-verifiable-units` | poteto | Yes | Yes | **INSPIRE** | Describes your existing PR discipline. No need to install what you already do. |
| `principle-prove-it-works` | poteto | **Yes** | Partly | **COMBINE** into `verify-for-real` | Right idea, but doesn't handle your specific constraint: an environment that *structurally cannot* verify (no Docker, Windows). Your version needs that clause. |
| `principle-laziness-protocol` / `subtract-before-you-add` | poteto | Yes | Yes | **REJECT** | You already bias to deletion and minimal diffs. Adding a skill to tell you to do what you do is noise. |
| `principle-exhaust-the-design-space` | poteto | Yes | No | **ADOPT** | *"Build 2-3 competing prototypes and compare side by side"* — this is the intellectual justification for your HTML design-exploration idea, stated as a general principle. |
| `blast-radius` | poteto | **Yes** | No | **INSPIRE** | Adjacent to `sweep-the-class` but inverted: it asks *"what could my change break"*, you need *"where else does this defect live"*. Read it for method, write your own. |
| `verify-this` | cursor | Yes | No | **INSPIRE** | Good falsifiable-claim framing (restate falsifiably → baseline → treatment → VERIFIED / NOT VERIFIED). Fold the framing into `verify-for-real`. |
| `thermo-nuclear-code-quality-review` | cursor | **Yes** | Partly (your audits) | **ADAPT** | Closest external analogue to your audit practice. Yours is better on one axis: it emits **filed issues with acceptance criteria**. Take their structure, keep your output format. |
| `thermo-nuclear-review` / `thermos` | cursor | Yes | Partly | **INSPIRE** | Parallel security+correctness subagents over a branch diff, then synthesis. Good pattern for `audit-to-issues` at scale. |
| `code-review` | mattpocock | **Yes** | No | **ADAPT** | Two-axis (Standards vs Spec) in parallel subagents, plus a Fowler smell baseline that applies when the repo documents nothing. The **Spec axis is the valuable half for you** — "requirements asked for but missing" and "behaviour not asked for (scope creep)". Your issue #192 is exactly a Spec-axis failure. |
| `diagnosing-bugs` | mattpocock | Yes | Partly | **INSPIRE** | Feeds `debug-from-production-signal`. |
| `research` | mattpocock | Yes | Partly | **ADAPT** | *"Investigate against high-trust primary sources and capture findings as a Markdown file in the repo."* You already do this (`docs/architecture.md`, IR API documentation in your README). Worth formalising cheaply. |
| `domain-modeling` / `CONTEXT.md` + ADR | mattpocock | **Yes** | Partly | **ADAPT** | Your `CLAUDE.md` is doing four jobs at once at 49KB. Their split (CONTEXT.md for domain vocabulary, ADRs for decisions) is a better decomposition. See report 13. |
| `wayfinder` | mattpocock | Maybe | No | **INSPIRE** | Planning work bigger than one session as decision tickets. Relevant to your audit→issues pipeline, but it's workflow, not skill — defer. |
| `to-tickets` / `to-spec` | mattpocock | **Yes** | Partly | **ADAPT** | You already convert audit findings to issues manually. This is the mechanism half of `audit-to-issues`. |
| `handoff` / `claude-handoff` | mattpocock | Yes | No | **INSPIRE** | Your `CLAUDE.md` + 35 `ai-usage` records are a hand-rolled persistent handoff. Their per-conversation version is a different tool; `record-work` is closer to what you need. |
| `writing-for-agents` | mattpocock | **Yes** | No | **ADOPT** | *"Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md."* You will be writing a lot of these. Take it. |
| `tdd` | both | Partly | Partly | **REJECT (as a skill)** | poteto's own gating is right: *"only when the user explicitly asks… Skip when…"*. Your test strategy is incident-driven and revenue-path-driven, not test-first. Encode "add the regression test" as a required *output* of your fix skills instead. |
| `typescript-best-practices` | poteto | Yes | **Yes, already** | **REJECT** | Zero `any` in 34k lines. Nothing for it to do. |
| `fix-ci` / `loop-on-ci` | cursor | **Yes** | No | **ADOPT (as-is)** | Cheap, deterministic, and directly useful given how much verification you push into CI. Low risk, no adaptation needed. |
| `fix-merge-conflicts` / `resolving-merge-conflicts` | both | **No** | — | **REJECT** | Zero evidence in your history. You work solo on short-lived branches merged fast; I found no merge-conflict incidents in 156 PRs. |
| `get-pr-comments` / `pr-review-canvas` / `make-pr-easy-to-review` | cursor | **No** | — | **REJECT** | You have no reviewers. 154 of 156 PRs were self-merged. These solve a team problem you don't have. |
| `new-branch-and-pr` | cursor | Yes | Yes | **REJECT — make it a script** | Deterministic. Your `feature/* → main-dev → main` train is three git commands and a `gh pr create`. |
| `weekly-review` / `what-did-i-get-done` | cursor | Maybe | No | **DEFER** | Useful for a portfolio/CV that you actively maintain (`ai-app`), but not engineering leverage. Tier 4 at best. |
| `frontend-design` | steipete | **Yes** | Partly | **ADAPT, carefully** | Strong on committing to a bold aesthetic direction and avoiding generic AI-slop UI. **But it assumes greenfield with no design system**, which is the opposite of your situation — you have `globals.css` tokens, shadcn, `ui-text.ts`, and written brand constraints ("no flames, skulls, or EXTREME HEAT language"). Take its "pick a direction and execute precisely" framing; discard its from-scratch assumption. Pair with `design-system-recon`. |
| `project-structure` | steipete | Yes | No | **INSPIRE** | Compressed symbol map of a TS repo. Good raw material for `project-onboarding`, though his is Swift/TS-tooling-specific. |
| `github-deep-review` | steipete | **Yes** | Partly | **ADAPT** | *"read code first"*, *"willing to say 'not proven' when the trail is weak"*, *"decide the best fix after reading enough code"*. This evidence discipline matches your own audit standard exactly. |
| `create-verification-skill` / `maintain-verification-skill` | poteto | **Yes** | No | **INSPIRE — important** | Generates a *project-local* verification skill that drives your app like a user, and a periodic pass that keeps it honest. This is a strong answer to the global-vs-project question in your section 26: the global skill *generates* the project-local one. See report 13. |
| `continual-learning` | cursor | **Yes** | Partly (manual) | **INSPIRE — for later** | Transcript mining → AGENTS.md updates, driven by hooks. Closest existing thing to your dreaming layer's first stage. Don't build now; read it when you get there. |
| `reflect` | poteto | **Yes** | No | **INSPIRE — for later** | Three parallel reviewers over a transcript → synthesiser → routed skill edits, **with mandatory human approval before any edit lands**: *"Skill changes affect every future agent in the org; do not auto-apply."* This is the governance model your section 37 asks for, already written down. |
| `automate-me` / `workflow-from-chats` | both | Maybe | No | **DEFER** | Turn preferences into a personal-style skill. Report 04 already did this by hand from evidence, which is better. |
| `ralph-loop` | cursor | Maybe | No | **DEFER** | Concrete loop implementation (stop-hook feeds the same prompt back, `.cursor/ralph/scratchpad.md` state, max-iterations, completion promise). Read it when you build the loops layer. Not now. |
| `arena` / `swarm` / `orchestrate` | cursor | No | — | **REJECT for now** | Parallel-agent orchestration. Real capability, wrong phase. |
| `oracle` / `interrogate` | both | Maybe | No | **DEFER** | Second-model adversarial review. Genuinely useful for a solo developer with no reviewer — arguably your best substitute for one. Revisit after Tier 1. |
| `one-password`, `beeper`, `sonos`, `whatsapp`, `xcode-sync`, `swiftui-*`, `hopper-debugger`, `instruments-profiling`, `remote-mac`, `peekaboo`, `mac-maintenance`, `release-mac-app`, `vm-lab` | steipete | **No** | — | **REJECT** | macOS/Swift/personal-infrastructure. You are on Windows and don't ship native apps. |
| `git-guardrails-claude-code` | mattpocock | Maybe | No | **DEFER** | Hooks blocking `push`, `reset --hard`, `branch -D`. You've had no such incident, but you did have a wrong-base-branch merge (#112) that you solved with CI instead — arguably the better rung. |
| `setup-pre-commit` | mattpocock | Maybe | No | **REJECT** | Your CI already runs lint/typecheck/test/build. Pre-commit hooks would duplicate it and slow your commit cadence, which is high. |
| `wizard` | mattpocock | Maybe | No | **DEFER** | Interactive bash wizard for human-only steps. Relevant to your 9 open `business-decision` issues, which are exactly "steps only a human can perform". Interesting, not urgent. |

---

## 3. Principles you already hold, confirmed by an external source

**[INFERENCE]** Worth naming, because it tells you which external principle skills you can skip:

| Principle (poteto's name) | Your evidence |
|---|---|
| `fix-root-causes` | Commit bodies systematically state root cause before mechanism |
| `encode-lessons-in-structure` | Six incident→mechanism conversions (report 02 §3) |
| `type-system-discipline` | 0 `any`, discriminated `ActionResult`, cents-as-base-unit, generated DB types |
| `sequence-verifiable-units` | 156 narrow PRs, small logical commits within each |
| `laziness-protocol` / `subtract-before-you-add` | Minimal diffs; PR #99 removes unused `next-themes` config; #207 removes a duplicate slot |
| `prove-it-works` | Playwright repro before/after; JWT payloads decoded to prove roles |
| `minimize-reader-load` | Sub-250-line files, split-by-domain forms, thin composition layers |
| `boundary-discipline` | Learned the hard way, now written into `CLAUDE.md` |
| `make-operations-idempotent` | Learned the hard way across five issues; now understood |

**[RECOMMENDATION]** Install only `encode-lessons-in-structure`, `exhaust-the-design-space`, `boundary-discipline` and `make-operations-idempotent`. The rest describe behaviour you already exhibit, and a principle you already follow is context cost with no behaviour change.

---

## 4. What none of them have

**[FACT]** I checked all 158 external skills for equivalents of your top two candidates:

- **`sweep-the-class`** — nothing. `blast-radius` is the nearest and it points the other way (forward from a change, not sideways from a defect shape). `principle-migrate-callers-then-delete-legacy-apis` covers one narrow instance of it.
- **`failure-visibility-review`** — nothing at all. No skill in any library targets "a failure representable as an empty success". This is genuinely original, and it's your #1 recurring bug class.

**[INFERENCE]** That's a good sign for the whole exercise. The two highest-leverage skills for you are ones no general-purpose library would have thought to build, because they came out of *your* incident history. That is what the archaeology was for.

Also absent everywhere: **anything Windows-aware**. All four libraries assume POSIX. steipete's assumes macOS specifically. Your library needs to carry that weight itself.

---

## 5. Provenance summary

If you build the roadmap in report 15, provenance breaks down as:

| Relationship | Count | Skills |
|---|---|---|
| **ORIGINAL** | 5 | `sweep-the-class`, `failure-visibility-review`, `nextjs-render-boundary`, `third-party-integration`, `record-work` |
| **ADAPTED** | 5 | `deslop`, `audit-to-issues`, `capture-lesson`, `verify-for-real`, `prose-deslop` |
| **INSPIRED** | 4 | `boundary-validation`, `design-system-recon`, `ui-design-exploration`, `project-onboarding` |
| **ADOPTED** | 3 | `fix-ci`, `writing-for-agents`, `principle-encode-lessons-in-structure` |
| **COMBINED** | 2 | `extract-duplication` (Fowler smells + your rule-of-three), `concurrency-correctness` (idempotence + separate-shared-state) |

Roughly a third original, a third adapted, a third borrowed. That ratio looks right for a personal library: enough borrowed that you're not reinventing, enough original that it's actually yours.
