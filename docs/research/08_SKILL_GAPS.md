# 08 — Skill Gaps

---

## 1. Skills you already have implicitly

**[FACT]** Capabilities you demonstrably exercise but that exist nowhere as a reusable artefact:

| Implicit skill | Where it lives now | Cost of it being implicit |
|---|---|---|
| **Whole-system audit → filed issues** | One 98KB markdown file on your Desktop, produced ad hoc | Not repeatable. The next audit will be re-derived from scratch, in a different shape. |
| **Incident → structural mechanism** | Six instances, all reactive (report 02 §3) | Applied only when the failure hurt. Issue #113/#200-class findings stayed as prose. |
| **Per-branch work record** | 35 files in one repo (`senus/frontend/docs/ai-usage/`) | Practice died when you moved to `hotsauce-mama`. That knowledge is now scattered in commit bodies. |
| **Project memory maintenance** | `CLAUDE.md`, 2nd most-edited file, 40 changes | Entirely manual and unbounded — 49KB doing four different jobs. |
| **Design brief with named references** | Two AGENTS.md files, written from scratch each time | Re-derived per project. |
| **Rule-of-three extraction with provenance comment** | Consistent across 5 years and 10 repos | Detection is manual and late. |
| **Verification honesty** (*"not independently re-verified against a real run"*) | Scattered CI comments | You do this in comments to yourself, not in the completion report where it would change a decision. |
| **Pin-with-a-reason** | `shadcn@2.10.0`, `supabase/setup-cli@2.109.1`, exact `eslint-config-next` | Consistent instinct, no trigger. |

**[INFERENCE]** Every one of these is a *practice you invented and validated on real work*. That's the strongest possible basis for a skill. Formalising them is mostly transcription, not invention — which is why the roadmap in report 15 is achievable.

---

## 2. Skills you should formalise (you have them, they need a name and a file)

Ranked by how much is already written versus how much needs inventing:

| Skill | Already written | Needs inventing |
|---|---|---|
| `record-work` | The template, from 35 real examples | Almost nothing. Transcription. |
| `audit-to-issues` | The output format, in full, in your scalability review | The traversal strategy and axis scoping |
| `capture-lesson` | Six worked examples; poteto's "strongest rung" ladder | The trigger, and the routing decision |
| `verify-for-real` | Your honesty clauses, verbatim from CI comments | The report format |
| `extract-duplication` | The threshold (three) and the provenance-comment convention | The detection method |
| `design-system-recon` | Two full component/token inventories to model on | The discovery order |
| `project-onboarding` | `CLAUDE.md`'s structure is the answer to "what does a new session need" | The extraction procedure |

---

## 3. Skills you are missing entirely

| Skill | Why it's missing | What it costs you today |
|---|---|---|
| **`sweep-the-class`** | Nothing in your workflow asks the question, and no external library has it | Issues #192, #250, #131 exist *only* because a fix was declared complete and wasn't. PR #249 was a live customer-facing bug caused by the same. |
| **`failure-visibility-review`** | The defect is invisible on read — correct-looking code | Your #1 recurring bug class. 11 references, 2 projects, 2 languages. |
| **`nextjs-render-boundary`** | Render mode is implicit; the framework gives no signal | Your only production outage (#137) and your only revert (#153). |
| **`boundary-validation`** | Server Actions look like function calls | An exploitable stock-corruption bug (#188), an open redirect (#114). |
| **`ui-design-exploration`** | You go straight from brief to implementation | Unknown — no failure evidence. This is a *wanted capability*, not an observed gap. I flag that honestly. |
| **`prose-deslop`** | — | Low. Your prose is already good. |

---

## 4. Skills that would prevent repeated problems

Mapping report 03's ranked problems to coverage:

| Problem | Prevented by | Coverage |
|---|---|---|
| 1. Silent failure | `failure-visibility-review` + `deslop` | **Full** |
| 2. Incomplete sweep | `sweep-the-class` | **Full** |
| 3. Render/caching mismatch | `nextjs-render-boundary` + `verify-for-real` | Partial — sub-cause 1 already solved structurally by your Playwright suite |
| 4. Missing bounds | `boundary-validation` | **Full** |
| 5. Check-then-act races | `concurrency-correctness` | Partial — needs integration tests you can only run in CI |
| 6. Third-party scripts | `third-party-integration` | **Full** |
| 7. Local env can't verify | `verify-for-real` | Partial — mitigates, cannot fix (you'd need Docker/WSL2) |
| 8. Duplication | `extract-duplication` | **Full** |
| 9. A11y one at a time | `a11y-sweep` (via `sweep-the-class`) | **Full** |
| 10. AI slop | `deslop` | **Full** |

**[INFERENCE]** Seven of ten fully covered by six skills. That's the case for a small library.

---

## 5. Skills that would save the most time

**[INFERENCE]** Estimated from your actual PR history, not from general principle:

1. **`sweep-the-class`** — the unbounded-query thread alone (#121 → #192 → #223 → PR #219 → PR #239) is four issues and two PRs for one defect class. One sweep at #121 collapses it to one.
2. **`audit-to-issues`** — your scalability review produced 18 issues and drove at least four PRs. That is the highest single-invocation payoff in your history. Making it repeatable multiplies it.
3. **`extract-duplication`** — PRs #70–#77 are seven PRs of work that a periodic sweep would have surfaced as one.
4. **`project-onboarding`** — you have 39 repos and add client projects regularly. Every re-entry currently costs a full re-derivation.
5. **`design-system-recon`** — cheap, and it prevents the most common rework in UI generation (inline hex, inline strings, duplicated components).

---

## 6. Skills that would most improve quality

1. **`failure-visibility-review`** — turns invisible failures into visible ones. Nothing else on the list changes user-facing correctness as directly.
2. **`boundary-validation`** — closes an exploit class, not a style class.
3. **`deslop`** — keeps agent output at the standard you already hold, on the fast client work where you currently skip review.
4. **`verify-for-real`** — changes what "done" means, which changes every downstream decision.
5. **`ui-design-exploration`** — the only one that improves the *product* rather than the *code*.

---

## 7. Skills that support the future workflow layer

**[INFERENCE]** Workflows are sequences of skills. The ones that will be composed most:

- `project-onboarding` → opens nearly every workflow
- `sweep-the-class` → the natural second step of any fix workflow
- `verify-for-real` → the natural last step of every workflow
- `record-work` → the natural artefact of every workflow
- `design-system-recon` → opens every UI workflow

Your "design this" workflow, decomposed:
```
design-system-recon → ui-design-exploration → [you choose] → implement → verify-for-real → record-work
```
Note that only two of those six are new skills. That's the point of decomposing rather than building "the UI workflow".

---

## 8. Skills that support the future dreaming layer

**[INFERENCE]** Dreaming needs an experience corpus with consistent structure. Today your experience is stored in four incompatible shapes: commit bodies, issue text, `CLAUDE.md` prose, and `ai-usage/*.md` files — and only in one repo each.

The two skills that create the substrate:

- **`record-work`** — produces one structured record per unit of work, in a stable shape, in a predictable location
- **`capture-lesson`** — produces one structured record per lesson, tagged with the artefact it became

Without those two, a dreaming layer would have to mine unstructured git history, which is exactly what `continual-learning` and `reflect` do and exactly why they're complex. **Build the substrate now and the dreaming layer gets dramatically cheaper later.** This is the strongest argument for putting `record-work` and `capture-lesson` in Tier 1 despite modest immediate payoff.

---

## The missing capability you did not ask for

You asked me to think independently about what you're missing. Here it is.

### Nothing you learn escapes the project that taught it.

**[FACT]** Your global agent configuration is empty. `~/.claude/` contains no `CLAUDE.md`, no `skills/`, no `commands/`, and a `settings.json` whose entire content is 34 auto-accumulated permission entries — `curl` calls to `127.0.0.1:8021`, a one-off `sleep 6 && cat /tmp/frontend3.log`, a hardcoded Gemini-key grep. Not one durable instruction.

**[FACT]** Meanwhile, these facts exist in exactly one project each and nowhere else:

| Lesson | Trapped in | Applies to |
|---|---|---|
| `next/og`'s `ImageResponse` breaks `next build` on Windows | `hotsauce-mama/CLAUDE.md` | Every Next.js project you'll ever build on this machine |
| Pin `shadcn@2.10.0`; `@latest` emits Tailwind-v4-only CSS | `hotsauce-mama/CLAUDE.md` | Every shadcn + Tailwind v3 project |
| A client Zod schema is not server-side validation for a Server Action | `hotsauce-mama/CLAUDE.md` | Every Next.js App Router project |
| Always check Supabase's `error`, or failure looks like emptiness | 4 issues + 5 PRs | Every Supabase project, and every `{data, error}` API |
| An external call after a state-changing write needs a compensating cleanup | `hotsauce-mama/CLAUDE.md` | Every payment/inventory flow anywhere |
| `supabase/setup-cli@latest` calls GitHub's release API and hits rate limits | one CI comment | Every repo using that action |
| Git Bash rewrites POSIX-looking arguments into Windows paths | nowhere — it silently corrupted issue #223's title | **Every command you or an agent runs on this machine** |
| Unit tests need Supabase unconfigured; e2e needs it configured; job-wide env breaks that | one CI comment | Every project with both test layers |
| `next dev` doesn't replicate ISR caching, so cache bugs escape to production | `CLAUDE.md` + a Playwright spec | Every Next.js project |

**[FACT]** `senus-board-report` was built one week before `hotsauce-mama`, on the same stack, on the same Windows machine, and shares **none** of this. Two of the nine would have applied directly.

**[INFERENCE]** This is the actual gap, and it's larger than any individual skill. You have an excellent, disciplined per-project memory practice and **zero cross-project memory**. Every new repo starts from nothing and re-learns by re-suffering. The skill library you're designing will have exactly the same problem unless you build the layer that catches these.

### What it should be

Not a skill. A **portable lessons ledger** in the central repository, plus one skill that writes to it and one rule that reads from it.

```
personal-agent-system/
  lessons/
    windows-git-bash-path-mangling.md
    nextjs-og-imageresponse-windows.md
    shadcn-pin-tailwind-v3.md
    server-action-is-a-public-endpoint.md
    supabase-error-must-be-checked.md
    compensate-after-external-call.md
    next-dev-is-not-production.md
```

Each file is short and has a fixed shape:

```markdown
---
name: supabase-error-must-be-checked
applies-to: [supabase, postgrest, any {data,error} client]
discovered: 2026-07-24 (hotsauce-mama #180, #249, #250)
strength: rule          # rule | lint | test | pin | note
---

A destructured `error` that is never read makes a genuine query failure
indistinguishable from an empty result. On read paths, throw. On write
paths, return a discriminated result.

**Cost when missed:** PR #249 — an in-stock product showed as Coming Soon
on its detail page while showing Available Now on the listing page.

**Strongest available rung:** an ESLint rule on unused destructured `error`
bindings from Supabase clients would enforce this. Not yet written.
```

That last field matters. It converts your existing prose-only lessons into a **backlog of structural encodings**, which is exactly what poteto's `encode-lessons-in-structure` says to do and what you currently do only when a failure hurt enough.

`capture-lesson` writes these. `project-onboarding` reads the ones matching the project's stack. That closes the loop that is currently open.

### Why this is the right thing to build now rather than later

It is the cheapest item on the entire roadmap — a directory and a template. It requires no engine, no database, no CLI. And it is the **only** part of the design that gets *more* expensive the longer you wait, because every project you ship without it buries more lessons. You have nine identified already, from two projects, in a single afternoon of reading. You will not remember the next nine.

### A second, smaller one

**You have no mechanism for work blocked on a human decision.** Nine open `business-decision` issues in `hotsauce-mama` block launch: VAT number, courier pricing, hosting plan, which of three Island Sauce label versions is real. They sit in the same tracker as code tasks, unlabelled as to *who* must act and *what specifically* they must decide.

mattpocock's `wizard` ("interactive bash wizard for steps only a human can perform") and `to-questionnaire` ("turn a decision you can't fully answer into a questionnaire for someone else") both target this. For you it matters more than for most, because you're doing client work — those nine decisions are the client's, not yours, and there's no artefact you can hand them. Not Tier 1, but worth knowing it's a real gap with an existing solution shape.
