# 16 — Open Questions

Decisions I couldn't make for you, things I couldn't verify, and where I might be wrong.

---

## 1. Questions only you can answer

### Q1. Is `hotsauce-mama` representative of where you're going, or an outlier?

**Why it matters.** Almost the entire design leans on it — 474 commits, 156 PRs, 100 issues, and the great majority of the evidence in reports 03 and 04. If your next twelve months look like `hotsauce-mama` (long-running product work with real users), the roadmap in report 15 is right. If they look like Era 2 (fast client sites, 3–50 commits, no tests, ship and move on), then `deslop` and `project-onboarding` rise and `sweep-the-class`, `audit-to-issues` and `concurrency-correctness` mostly idle.

**My read:** it's directional, not an outlier — the trajectory from 2025 to 2026 is one-way. But you know your pipeline and I don't.

### Q2. Do you actually want to publish this repo?

Report 14 recommends public, mainly because you're job-searching and this is a stronger artefact than another CRUD app. But it means scrubbing `hotsauce-mama` specifics — brand direction, pricing decisions, the Instagram token workaround — from any lesson derived from client work. Your call, and it changes how lessons get written from day one.

### Q3. Which harnesses must this work in?

I've assumed Claude Code (`~/.claude/skills`) and Codex (`~/.agents/skills`), based on your portfolio listing both plus `~/.codex/` existing on disk. Cursor is a third possibility. This changes only the installer, but it's cheaper to know now.

### Q4. Is `ui-design-exploration` a real need or an aspiration?

I flagged this honestly in report 05: it's the weakest-evidenced high-scoring skill. What I *observed* is written design briefs, a standalone dashboard review, and a lot of standalone HTML documents on your Desktop. What I did **not** observe is you generating and comparing visual options before implementing. If it's a real recurring frustration, it moves up. If it's "this would be cool", it stays at 14.

### Q5. Are you willing to run skills that mostly report "nothing found"?

`deslop` on `hotsauce-mama` will often find nothing — that codebase is clean. `sweep-the-class` will sometimes find one instance and stop. This is correct behaviour, but if it reads as failure you'll stop invoking them, and the library dies quietly. Worth deciding up front that a clean result is a pass.

---

## 2. Things I could not verify

| Claim | Why unverified | Impact if wrong |
|---|---|---|
| The 2026 velocity is agent-assisted | Inferred from cadence and commit prose. I did not read any transcripts. | Low — the recurring problems are real regardless of who wrote the code |
| Era-2 repos are "unreviewed" rather than "less skilled" | Inference from the Era-3 contrast | Medium — if it's a skill gap rather than a review gap, `deslop` matters less than teaching |
| Windows symlinks will work for the installer | **Not tested.** Report 14 flags this. | High for install UX. Test on day one. |
| The loop-engineering article's specifics | **Paywalled.** I got only the free intro (the Steinberger and Cherny quotes, the "design loops that prompt your agents" framing). The 14-step roadmap and 41 templates are behind the paywall. | Low for phase one — nothing in this design depends on it. Worth reading yourself before the loops layer. |
| `senus-board-report` PR count (~67) | From the GraphQL contributions API, not enumerated per-repo | Negligible |
| `boutique_ado_v1` and the 2019–2020 repos | Commit logs and language stats only; no source read | Negligible — Era 1 informs the arc, nothing else |

---

## 3. Where I might be wrong

**On `any`.** I measured zero across 34,000+ lines of your two serious projects and concluded it isn't your problem. If your actual concern is *agents writing `any` in your code* rather than *you writing it*, the evidence can't see that — I only measured what survived into commits. You may be catching it manually every time, in which case it's a real cost that leaves no trace. Worth telling me if so; it would restore part of the deslop clause I removed.

**On rejecting merge-conflict and PR-review skills.** Justified by "you work solo, 154 of 156 PRs self-merged". If you're heading toward team work or open source, that reverses.

**On the stage-based tree.** It's derived from your PR corpus, but it's still my imposed structure. The honest test is whether "FIND / CHANGE / PROVE" is how you'd describe what you're about to do. If it isn't, the folders are wrong even if the skills are right.

**On `audit-to-issues` at complexity 4.** It might be simpler than I think, since you've already written the output format in full. If so it should move ahead of `deslop` — its payoff in your history is larger than anything else on the list.

**On splitting `CLAUDE.md`.** Report 13 argues for splitting by change rate. But that file is working, it's the 2nd most-edited in the repo, and "working" beats "well-factored". I recommended applying it to the *next* project rather than reorganising this one, and I'd hold that line unless you find yourself skimming past the rules section.

---

## 4. Design questions I deliberately left open

**How does `sweep-the-class` characterise a "shape"?** This is the hard part of the highest-value skill and I've specified the interface, not the method. Grep patterns work for `#250` (destructured `error` never read) but not for `#189` (a Postgres `FOR UPDATE` + `LIMIT` interaction). My instinct: start with the mechanical cases, accept that the subtle ones need a model reading code, and let the first ten real uses teach you the taxonomy. Don't try to design it fully up front.

**What's the trigger for `capture-lesson`?** Skills fire on request. Lessons arrive unbidden. Options: manual only (reliable, but you'll forget), chained from `verify-for-real` and `deslop` (catches technical lessons, misses conversational ones), or a session-end hook (catches everything, high noise). I'd start manual and add chaining once you know what a good lesson looks like.

**Should `principles/` be installable skills or documentation?** poteto ships ~24 as skills with `disable-model-invocation: true`. That makes them invocable and keeps them out of automatic routing. But four principles as four skills is four descriptions of budget for content you could paste into `AGENTS.md`. At your scale, documentation may win. Revisit if the set grows past six.

---

## 5. What I'd want to know in three months

The questions that would tell you whether this worked:

1. How many issues filed after 2026-09 say "same class as #X"? Target: zero.
2. How many `lessons/` entries exist, and how many came from a project *other* than the one that discovered them?
3. Did `deslop` ever delete something you had to restore? (If yes, the fixture set failed and needs that case added.)
4. Which skills have you never invoked? Those are routing failures or wrong skills — delete or fix them.
5. Is `AGENTS.md` still under 150 lines?

**[RECOMMENDATION]** Put these five in the repo's README as an explicit review checkpoint with a date. That's `encode-lessons-in-structure` applied to the library itself, and it's the cheapest possible version of the evaluation layer.
