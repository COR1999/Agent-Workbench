# 14 — Repository Architecture

---

## Recommended structure

```
personal-agent-system/
├── README.md                  what this is, install, the skill table (generated)
├── AGENTS.md                  HARD RULES ONLY — incl. the Windows/Git Bash rules
├── CLAUDE.md                  one line: @AGENTS.md
│
├── skills/
│   ├── find/                  sweep-the-class, audit-to-issues,
│   │                          failure-visibility-review, extract-duplication
│   ├── change/                deslop, boundary-validation,
│   │                          nextjs-render-boundary, third-party-integration
│   ├── design/                design-system-recon, ui-design-exploration
│   ├── prove/                 verify-for-real
│   ├── remember/              capture-lesson, record-work, project-onboarding
│   ├── write/                 prose-deslop
│   ├── in-progress/           not installed, not routed
│   └── deprecated/            kept for history
│
├── principles/                encode-lessons-in-structure.md, boundary-discipline.md,
│                              exhaust-the-design-space.md, make-operations-idempotent.md
│
├── lessons/                   THE THING THAT DOESN'T EXIST YET (report 08)
│   └── <slug>.md              portable, stack-tagged, date-stamped
│
├── templates/
│   ├── project-AGENTS.md
│   ├── skill-SKILL.md
│   └── lesson.md
│
├── scripts/
│   ├── link-skills.sh         symlink into ~/.claude/skills + ~/.agents/skills
│   ├── validate-skills.sh     CI gate (report 12 level 1)
│   ├── generate-registry.sh   filesystem -> README table
│   └── eval-skill.sh          fixture runner
│
└── docs/
    ├── research/              THESE 16 REPORTS — the origin record
    ├── decisions/             ADRs going forward
    └── vision.md              the layered architecture, honestly scoped
```

**Deliberately absent** (each argued in reports 10–13): `registry/skills.yml` (generate it), `profiles/*.yml` (project `AGENTS.md`), per-skill `version` (git), `.agent/` in projects (three files, no directory).

---

## Deviations from your proposal, and why

| You proposed | Recommended | Reason |
|---|---|---|
| `skills/{typescript,nextjs,react,github,ui,testing,infrastructure}` | `skills/{find,change,design,prove,remember,write}` | Technology is a constant across all your projects, so it carries no routing information. Verbs match how your PR corpus is actually organised. Report 07. |
| `profiles/*.yml` | ~15 lines in each project's `AGENTS.md` | A YAML profile tree is a second source of truth that drifts from the code. Report 13. |
| `registry/skills.yml` | `scripts/generate-registry.sh` + CI diff check | The filesystem is the registry. A hand-maintained one can disagree with it. Report 11. |
| `tests/` at root | `tests/` inside each skill | Fixtures belong next to the thing they test, and only ~2 skills need them. Report 12. |
| `docs/vision/{system,architecture,principles}.md` | one `docs/vision.md` + `principles/` as real skills | Principles that are installable get used; principles in a docs folder get read once. |
| (not proposed) | `lessons/` | The largest gap found. Report 08. |

---

## The repository as a report

You asked for it to be both a working library and a living research record. That works, with one discipline: **separate the origin record from the ongoing record.**

- `docs/research/` — these 16 reports. Written once, dated, **not edited later.** They are the evidence base as of 2026-08-19. If a conclusion turns out wrong, an ADR supersedes it; the report stays as written. Editing them destroys the audit trail, which is the thing that makes them valuable.
- `docs/decisions/` — ADRs from here on. `0001-skills-organised-by-stage-not-technology.md`, `0002-no-registry-file.md`, `0003-lessons-ledger.md`. Each names what was decided, what was rejected, and why.
- `README.md` — how someone (including future you) actually uses the thing.

**[INFERENCE]** This mirrors what you already do — your commit bodies and `CLAUDE.md` incident notes are an append-only origin record, and your `ai-usage/*.md` files are per-unit records. You've independently arrived at the right shape; this just gives it a home outside one repo.

---

## Repo name and visibility

**[RECOMMENDATION]** Public. Three reasons grounded in your situation:

1. You maintain a portfolio (`ai-app`, cianorourke.com) and are visibly job-searching. A well-documented personal agent system with an evidence-based design record is a stronger artefact than another CRUD app.
2. It forces the discipline that keeps these libraries from rotting — mattpocock's and steipete's are good *because* they're public.
3. Nothing in it is sensitive. Lessons reference public repos; the one private repo (`hotsauce-mama`) only contributes issue numbers and pattern descriptions.

**Caveat:** scrub client specifics before publishing anything derived from `hotsauce-mama`. Brand direction, pricing decisions and the Instagram token workaround are the client's business, not yours to publish. Lessons should be phrased generically ("always check the `error` from a `{data, error}` client"), not with client context attached.

Name: `personal-agent-system` is fine and descriptive.

---

## Installation

```bash
git clone https://github.com/COR1999/personal-agent-system.git
cd personal-agent-system
./scripts/link-skills.sh          # symlinks into ~/.claude/skills and ~/.agents/skills
```

Updates: `git pull`. That's the whole mechanism.

**[WARNING — test this first]** Symlinks on Windows require Developer Mode or an elevated shell; Git Bash's `ln -s` silently falls back to copying otherwise, which breaks the "`git pull` updates everything" property without any error. Verify on day one. If it's unreliable, ship `scripts/sync-skills.sh` (copy, re-run after pull) and document that instead of pretending symlinks work. This is exactly the class of Windows assumption that report 08 says keeps costing you.

---

## Layered architecture

What each layer does, and what exists today.

```
                    PERSONAL AGENT SYSTEM
                              │
              ┌───────────────┴───────────────┐
              │                               │
            SKILLS                        KNOWLEDGE
      procedures with                rules · principles ·
      judgement, guardrails,         lessons · project memory ·
      and a defined output           decisions
              │                               │
              └───────────────┬───────────────┘
                              │
                         WORKFLOWS          ordered sequences of skills
                              │             toward one objective
                            LOOPS           workflows that run without
                              │             a prompt each time
                        EXPERIENCES         structured records of what
                              │             happened (record-work output)
                          DREAMING          periodic review of accumulated
                              │             experience → proposals
                         EVALUATION         does the proposal beat the
                              │             current version on fixtures?
                              ▼
                      SYSTEM IMPROVEMENT    approved changes merged
```

| Layer | What it does | Status today |
|---|---|---|
| **Knowledge** | Facts and judgement. Rules (always true), principles (heuristics), lessons (portable), project memory (local). | Exists, trapped per-project. `lessons/` is the missing piece. |
| **Skills** | Repeatable procedures with judgement, guardrails, output. Composable, independently useful. | **Build now.** Nothing exists globally. |
| **Workflows** | Ordered skill sequences. "Design this" = recon → explore → choose → implement → verify → record. | Emerges once ~8 skills exist. Don't build. |
| **Loops** | Workflows that self-trigger. Cursor's `ralph-loop` is one concrete implementation. | Not now. |
| **Experiences** | Structured records: what was attempted, what worked, what didn't, which skills were used. | You have 35 hand-written examples. `record-work` makes them systematic. |
| **Dreaming** | Periodic review of accumulated experience proposing skill/workflow changes. poteto's `reflect` is a working reference. | Not now. Needs the experience corpus first. |
| **Evaluation** | Gate before any proposal lands: fixtures must fail on the old skill and pass on the new. Human approves. | Design it now (report 12), build later. |

**[INFERENCE]** The dependency chain is strict and it explains the phasing: dreaming needs experiences, experiences need `record-work`, evaluation needs fixtures, fixtures need skills. **Everything downstream of "skills" is blocked on skills existing.** That's why phase one is skills plus the two REMEMBER skills that create the substrate — and why building the loop engine now would produce a loop with nothing to loop over.

Note also that Knowledge sits *beside* Skills, not under them. That's deliberate: a lesson isn't a skill, a rule isn't a skill, and the most common failure mode in these systems is turning every fact into a procedure.
