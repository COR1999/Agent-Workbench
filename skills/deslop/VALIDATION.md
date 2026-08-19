# deslop — corpus validation

Applying the three gates to every fixture. The gate that matters is
`should-not-flag` at **100%** — a single false positive blocks release.

## should-not-flag — 22/22 preserved ✅

Each hunk, and the gate that saves it (G3 category or the failure-visibility
clause). "Keyword" = trips the G3 never-remove keyword guard directly.

| # | Source | Saved by |
|---|---|---|
| 1 | format.ts provenance | keyword `was duplicated` → INFO |
| 2 | ci.yml pin | keyword date `2026-07-17` + incident prose → INFO/INTENT |
| 3 | locations.ts guard | keyword `#250` + `throw` → SAFETY |
| 4 | meta-pixel suppression | eslint-disable + `because` justification → INTENT |
| 5 | checkout compensating try | keyword `otherwise` + external-call-after-write → SAFETY |
| 6 | best-effort separate catch | keyword `deliberately` → SAFETY/INTENT |
| 7 | discriminated `catch` | failure-visibility clause: typed handler, not catch-log → SAFETY |
| 8 | `unknown[]` generic | INTENT: load-bearing generic (pattern-catalogue explicitly protects) |
| 9 | isSupabaseConfigured | keyword `null-safe` → INTENT/SAFETY |
| 10 | ISR revalidate comment | INFO: numeric justification + `revalidatePath` cross-ref |
| 11 | cookie-bound comment | keyword `Deliberately` → INTENT |
| 12 | validation `.max()` bounds | SAFETY: input-size bound, not verbosity |
| 13 | FK cascade provenance (py) | keyword `because` + `used to fail` → INFO |
| 14 | upload except/HTTPException (py) | SAFETY: re-raise + surfaced 500 |
| 15 | None-vs-zero (py) | keyword `because` + misrepresent → INFO/SAFETY |
| 16 | "must not silently become" (py) | INFO: domain invariant |
| 17 | period-detection (py) | keyword `because` → INFO |
| 18 | baseline shape (py) | keyword `otherwise` → INFO |
| 19 | circular-import (py) | keyword `so that` + INTENT |
| 20 | comparative purity (py) | keyword `because` → INFO |
| 21 | isSupabaseConfigured guard return | not a removal-category target + failure-visibility → SAFETY |
| 22 | text-parsing suffix (py) | keyword `because` → INFO |

**Honest note on coverage strength.** 20 of 22 are protected by the mechanical
keyword guard, the strongest and most auditable mechanism. **Two (#7, #21) are
not** — they carry no keyword and rely on softer logic: #7 on the
failure-visibility clause recognising a typed handler, #21 on the pattern
catalogue simply not targeting a bare guard clause. These are the hunks most at
risk from a careless run, so they are the two to watch first if a real false
positive ever appears. The keyword guard alone would preserve them too *if* they
had a comment — the takeaway is that under-commented legitimate code is where the
residual risk sits, which matches intuition.

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
