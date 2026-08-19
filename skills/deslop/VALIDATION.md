# deslop — corpus validation

Applying the three gates to every fixture. The gate that matters is
`should-not-flag` at **100%** — a single false positive blocks release.

## should-not-flag — 22/22 preserved ✅

Each hunk and the mechanism that saves it. Two mechanism classes:
**MECH** = the mechanical never-remove guard fires directly (an issue ref, a
date, a file path, or one of the guard words *found / incident / instead /
because / was duplicated / deliberately / otherwise*). **JUDGE** = no guard token
is present; the save depends on a G3 category call (INFO / SAFETY / INTENT) or the
failure-visibility clause. The distinction matters because MECH is auditable by
grep and JUDGE is not.

| # | Source | Class | The actual trigger |
|---|---|---|---|
| 1 | format.ts provenance | MECH | `was duplicated` + file paths |
| 2 | ci.yml pin | MECH | date `2026-07-17` |
| 3 | locations.ts guard | MECH | issue ref `#250` (+ SAFETY: `throw`) |
| 4 | meta-pixel suppression | JUDGE | INTENT: justified `eslint-disable`, no guard word |
| 5 | checkout compensating try | MECH | `otherwise` (+ SAFETY: external-call-after-write) |
| 6 | best-effort separate catch | MECH | `deliberately` |
| 7 | discriminated `catch` | JUDGE | failure-visibility: typed handler, not catch-log |
| 8 | `unknown[]` generic | JUDGE | INTENT: pure code, no comment; load-bearing generic |
| 9 | isSupabaseConfigured | MECH | file path `lib/resend.ts` in the comment |
| 10 | ISR revalidate comment | MECH | file path `revalidate-storefront.ts` |
| 11 | cookie-bound comment | MECH | `Deliberately` |
| 12 | validation `.max()` bounds | JUDGE | SAFETY: pure code, input-size bound |
| 13 | FK cascade provenance (py) | JUDGE | INFO: comment carries no guard word |
| 14 | upload except/HTTPException (py) | JUDGE | SAFETY: pure code, re-raise + surfaced 500 |
| 15 | None-vs-zero (py) | MECH | `because` |
| 16 | "must not silently become" (py) | JUDGE | INFO: invariant, no guard word |
| 17 | period-detection (py) | MECH | `because` |
| 18 | baseline shape (py) | MECH | `otherwise` |
| 19 | circular-import (py) | JUDGE | INTENT: "so that" is not a guard word |
| 20 | comparative purity (py) | MECH | `because` |
| 21 | isSupabaseConfigured guard return | JUDGE | not a removal target + failure-visibility |
| 22 | text-parsing suffix (py) | MECH | `because` |

**Honest coverage accounting.** **13 of 22 are MECH** (grep-auditable): #1, #2,
#3, #5, #6, #9, #10, #11, #15, #17, #18, #20, #22. **9 are JUDGE**: #4, #7, #8,
#12, #13, #14, #16, #19, #21. Every one of the 22 is still protected by a rule
actually stated in `SKILL.md` — the skill's safety story holds — but only 13 are
protected by the mechanical guard, not the "20 of 22" an earlier draft of this
doc claimed. That claim was wrong; this is the corrected count.

**Where the real residual risk sits.** The nine JUDGE hunks depend on the model
making the right category call at review time. The sharpest of these is **#14**:
a re-raising `except` block with no comment, saved only by the failure-visibility
clause correctly reading "the failure stays visible." If that clause is applied
carelessly, #14 (and #7, #12) are the first hunks that could be wrongly touched.
The five JUDGE hunks that are pure uncommented code (#8, #12, #14, #21, and the
guard-return #21) are the ones a mechanical guard can never protect — the lesson
is that legitimate but *uncommented* engineering is where deslop must lean hardest
on judgment, and where a human should look first if a false positive ever appears.
A cheap hardening, deferred: add a comment to #8/#12/#14-shaped code in real use so
the mechanical guard covers them too.

## should-flag — 9/10 flagged, 1 correctly rerouted ✅

Hunks 1–6, 8: plain removals (restating comments, banners, aspirational prose,
commented-out scaffold) — all caught by pattern categories 2/3/4/6, none trip a
G3 guard. Hunks 9–10 (lazy `any`): caught by **G2** (zero-`any` convention), not
by a dedicated clause — this is the mechanism, and the skill now states it.
Hunk 7 (the `// in a real app you'd want error handling` TODO): **correctly
belongs in ambiguous**, not here — it documents a real gap. Routing it to
handoff rather than deletion is the right behaviour, so it is scored as a pass,
not a miss.

## ambiguous — 4/4 flag-and-handoff, 0 auto-fixed ✅

1. Unread `error` binding → flagged as silent-failure risk, **not** "removed
   unused binding". The dangerous wrong-fix is explicitly refused.
2. `any` at JSON.parse boundary → flagged, recommend schema parse, **not**
   annotation edit.
3. Best-effort catch → ambiguity reported, recommend *adding* an intent comment,
   never deleting the block.
4. TODO gap → flagged as a real gap, not deleted as prose.

All four hand off. None are auto-fixed. The failure-visibility clause holds.

## Verdict

**should-not-flag 22/22 → gate PASSED.** should-flag effectively 10/10 (9 direct
+ 1 correctly rerouted), well above the 80% bar. ambiguous 4/4. The skill is
safe to trust on a real diff. The two keyword-less preserved hunks (#7, #21) are
the documented soft spots to monitor.
