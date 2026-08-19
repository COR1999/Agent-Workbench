# 13 — Project Adapter

How a project connects to the central library. You proposed `.agent/{config.yml, constitution.yml, selected-skills.yml, memory/}`. I think most of that is unnecessary, and I'll say why before proposing an alternative.

---

## Challenging the proposal

### `selected-skills.yml` — don't build this

Skills install into `~/.claude/skills` and `~/.agents/skills`, which are **user-global, not project-scoped**. A project file listing selected skills has nothing to enforce it: the harness will surface all installed skills regardless of what the file says.

You'd be building a config that documents a preference nothing acts on. And the underlying problem — a Next.js skill firing in a Python repo — is better solved in the description (*"Use in Next.js App Router projects"*) where the router actually reads it.

**[RECOMMENDATION]** Skip it. If you later have 50 skills and genuinely need per-project scoping, the mechanism is Claude Code's project-level `.claude/skills/` directory, not a YAML manifest.

### `constitution.yml` — this is `AGENTS.md`

A separate constitution file duplicates what `AGENTS.md` is for, and adds a format (YAML) that's worse than markdown for rules that need explanation. Your own rules need explanation — *"A client-side Zod schema is not server-side validation"* only works with the paragraph under it.

**[RECOMMENDATION]** Rules go in `AGENTS.md`. One file.

### `config.yml` — what would be in it?

Framework, language and tooling are all detectable: `package.json`, `tsconfig.json`, `next.config.mjs`, `supabase/`. A config file restating them is a second source of truth that goes stale after a migration. **[FACT]** You have already lived this: issue #193 records a code comment claiming a route was static when it wasn't.

**[RECOMMENDATION]** Detect, don't declare.

### `memory/` — this one is real, but it already exists

You have 49KB of it in `CLAUDE.md` and 35 files of it in `senus/frontend/docs/ai-usage/`. The gap isn't a directory, it's structure — see below.

---

## What the adapter should actually be

**[RECOMMENDATION]** Three files and one directory, all of which you already have some version of:

```
<project>/
  AGENTS.md              canonical: rules + context + local style
  CLAUDE.md              one line: @AGENTS.md
  docs/
    decisions/           ADRs — one per settled decision
    work/                per-branch records (the ai-usage pattern)
```

**Nothing else.** No `.agent/` directory, no YAML.

### Why `AGENTS.md` and not `CLAUDE.md`

**[FACT]** You already solved this. `senus-board-report/frontend/CLAUDE.md` contains exactly one line:

```
@AGENTS.md
```

`AGENTS.md` is the emerging cross-harness convention (Codex, Cursor, and others read it). Claude Code reads `CLAUDE.md`. A one-line include gives you both from one source. That's the whole portability answer for section 34, it's five bytes, and it's your own invention.

---

## Splitting the 49KB CLAUDE.md

**[FACT]** `hotsauce-mama/CLAUDE.md` is 49KB, the 2nd most-edited file in the repo (40 changes), and does four distinct jobs at once:

| Section | Actually is |
|---|---|
| "What this is", "Tech stack", "Content architecture", "Commerce architecture" | **Context** — orientation for a new session |
| "Server Action conventions — two mistakes already made once" | **Rules** |
| "Visual identity — source of truth, and why it's still moving", "Placeholder-image strategy" | **Decisions + a runbook** |
| "Known placeholders / pending real content", "Roadmap: order management panel" | **State** — changes constantly |
| The CSP-nonce incident, the Supabase key-mismatch incident | **Incident history** |

**[INFERENCE]** These have completely different change rates. State changes weekly; rules almost never. Keeping them in one file means the whole 49KB is re-read on every session and the stable parts churn along with the volatile parts. It also means the "don't repeat this" rules — the most valuable content — are buried at line 378.

**[RECOMMENDATION]** Split by change rate:

```
AGENTS.md              rules + a short context section + local style   (stable, ~150 lines)
docs/architecture.md   the commerce/content architecture               (slow)
docs/decisions/        one ADR per settled decision                    (append-only)
docs/state.md          placeholders, roadmap, what's pending           (volatile)
docs/work/             per-branch records                             (append-only)
```

Two concrete benefits: `AGENTS.md` becomes small enough to be read in full every session, and the incident notes become individually addressable rather than paragraphs inside a 49KB file. Append-only directories also never conflict, which matters at your commit rate.

**[FACT]** mattpocock's library reaches the same split independently — `CONTEXT.md` for domain vocabulary, `.agents/adr/` for decisions, `AGENTS.md` for rules.

I'd treat this as a **suggestion for the next project**, not a reason to reorganise `hotsauce-mama` mid-flight. That file is working.

---

## What belongs where

| Content | Central library | Project | Why |
|---|---|---|---|
| Skill procedures | ✅ | ❌ | Reusable by definition |
| Principles | ✅ | ❌ | Cross-cutting judgement |
| Hard rules that apply everywhere | ✅ `AGENTS.md` | ❌ | "Never claim verified what you couldn't execute" |
| Portable lessons | ✅ `lessons/` | ❌ | The gap from report 08 |
| Project-specific rules | ❌ | ✅ `AGENTS.md` | "No flames, skulls, or EXTREME HEAT language anywhere" |
| Architecture | ❌ | ✅ `docs/architecture.md` | |
| Settled decisions | ❌ | ✅ `docs/decisions/` | "Why VAT-inclusive pricing" |
| Design system / tokens | ❌ | ✅ code + `AGENTS.md` | `globals.css` is already the source |
| Local style profile | ❌ | ✅ `AGENTS.md` section | ~15 lines, report 04 §14 |
| Work records | ❌ | ✅ `docs/work/` | Per-branch, project-specific |
| Runbooks | ❌ | ✅ `README.md` | You already do this well |
| State / roadmap | ❌ | ✅ `docs/state.md` | Volatile |

**The rule:** anything that would be *true in your next project too* belongs central. Everything else stays local. Report 08 showed nine lessons currently trapped in the wrong column.

---

## Global skill + project context = project execution

Your section 26 asks how one global skill adapts. Three mechanisms, in precedence order — the same layering as `deslop` in report 09:

1. **Inference from the code being edited.** Read the file and its siblings. Handles most cases with zero configuration, and it's why one `deslop` works on both kebab-case `hotsauce-mama` and PascalCase `senus/frontend`.
2. **The project's `AGENTS.md`.** States what inference can't see: which comments are load-bearing, where copy lives, what not to use.
3. **The global skill's judgement.** Never the style. The procedure, the guardrails, the discriminators.

**The invariant:** the global skill supplies *how to decide*; the project supplies *what is true here*. A global skill that hardcodes "components are kebab-case" is broken by your second project. A global skill that says "match the local convention, and prefer `AGENTS.md` when it's explicit" works everywhere.

---

## A fourth mechanism worth knowing about

**[FACT]** poteto's `create-verification-skill` generates a **project-local** skill that drives your app the way a user does, and `maintain-verification-skill` is a periodic pass that keeps it honest.

**[INFERENCE]** That's a different and stronger answer to global-vs-project than configuration: the global skill *generates a project-specific skill* which then lives in the project. For things that are genuinely project-shaped — how to run this app, how to seed its test data, how to reach its admin — a generated local skill beats any amount of parameterisation.

Relevant to you specifically because your projects have genuinely different verification stories: `hotsauce-mama` needs `supabase start` + Docker + Stripe test keys + a mail catcher; `senus` needs a FastAPI backend on one port and Next on another. No global skill can encode both. **Worth revisiting after Tier 1**, not now.

---

## Project initialisation

Your section 33 imagines `agent-system init` detecting the stack and recommending skills.

**[RECOMMENDATION]** Design it, but make it much smaller than you're imagining. The detection is trivial and the recommendation is nearly constant:

```
$ agent-system init

Detected:
  Next.js 16 (App Router)   package.json + next.config.mjs
  TypeScript strict         tsconfig.json
  Tailwind v3 + shadcn      tailwind.config.ts + components.json
  Supabase                  supabase/config.toml
  Vitest + Playwright       package.json scripts

Skills are installed globally — nothing to select.

Relevant lessons for this stack (from lessons/):
  ! next/og ImageResponse breaks `next build` on Windows
  ! Pin shadcn@2.10.0 — @latest emits Tailwind-v4-only CSS
  ! A client Zod schema is not server-side validation for a Server Action
  ! Always check Supabase's error — a failure looks like an empty result

Create AGENTS.md from template, with these lessons inlined? [y/N]
Create CLAUDE.md (@AGENTS.md)?                                [y/N]
Create docs/decisions/ and docs/work/?                        [y/N]
```

**[INFERENCE]** The valuable part is not skill selection — skills are global, there's nothing to select. It's **surfacing the portable lessons that apply to the detected stack**. That's the mechanism that closes report 08's gap, and it's the only reason to build an `init` at all.

Implementation: one shell or Node script reading `package.json` and a handful of config files, matching against `lessons/*.md` frontmatter `applies-to:`. Perhaps 150 lines. No CLI framework, no database.

---

## Versioning

Your section 35 asks for versions, changelogs, compatibility, rollback, breaking changes and overrides. **[RECOMMENDATION]** For a single-user library, most of that is cost without benefit:

| Concern | Recommendation |
|---|---|
| Versions | **Git.** Don't number skills. |
| Latest vs pinned | Symlink install = always latest. This is right for you: you're the only author, and a skill improvement should reach every project immediately. |
| Changelog | A root `CHANGELOG.md` if you enjoy writing them. Nothing depends on it. |
| Rollback | `git revert`. You already do this well — PR #153. |
| Breaking changes | A skill can't break a project; it just behaves differently. The only real risk is a skill that edits code, which is why `deslop` has guardrails and fixtures. |
| Project overrides | `AGENTS.md`, as above. |

**[INFERENCE]** Pinning matters when many consumers depend on one publisher. You are both. If you later publish this and other people install it, revisit — and the answer will be mattpocock's: ship as a plugin for subscribers, keep the repo forkable for hackers.

The one thing worth doing now: **date-stamp lessons** (`discovered: 2026-07-24`), because a lesson about `next/og` on Next 14 may not hold on Next 18, and your own `CLAUDE.md` already models this — *"Not re-verified against 16.2.10 … re-check whether this bug still reproduces before assuming this note is current."* That habit should be built into the lesson template.

---

## The Windows rule that belongs in central `AGENTS.md`

**[FACT]** Git Bash's MSYS path conversion rewrote `/admin/customers` into `C:/Program Files/Git/admin/customers` inside a committed GitHub issue title (#223). This is silent, it happens to any POSIX-looking argument passed to a native `.exe`, and it has already corrupted a real artefact.

**[RECOMMENDATION]** A hard rule in the central `AGENTS.md`, because it applies to every project on this machine:

```markdown
## Environment (Windows + Git Bash)

- Git Bash rewrites POSIX-looking arguments into Windows paths before passing
  them to native executables. `gh issue create --title '/admin/customers is slow'`
  becomes `C:/Program Files/Git/admin/customers`. This already corrupted issue
  #223's title in hotsauce-mama.
  Prefix with `MSYS_NO_PATHCONV=1`, or use PowerShell for `gh` calls with
  path-like arguments.
- No Docker on this machine. Anything needing `supabase start`, a real Postgres,
  or a container runs in CI only. Never report such a step as verified locally.
- `next dev` does not replicate ISR/static caching. Cache-dependent behaviour is
  only observable against `next build && next start`.
- next/og `ImageResponse` breaks `next build` on Windows (Next 14.2.35; not
  re-verified since). Use static SVG/PNG icons and metadata-based OG images.
```

Four rules, thirteen lines, and each one has already cost you something real.
