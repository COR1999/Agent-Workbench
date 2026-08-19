# sweep-the-class — retrospective validation

Run against real history in `hotsauce-mama`, at the commit *before* each known
fix, scoring the sweep's output against the files the human fix actually
changed. Read-only: a scratch inspection via `git show <ref>:<path>`, no
checkout, no edit to any working copy.

## Case A — silent Supabase errors (#250 / PR #252)

**Ground truth:** PR #252 fixed 10 files. Pre-fix ref `0feea49`.

**Sweep as run:**
- Mechanical signature: files under `src/lib` destructuring `{ data }` / `{ data, error }` from a Supabase call.
- Semantic condition: `error` never read before `data` is used, and failure is not otherwise distinguishable from an empty result.

**Result: 10 / 10 same-class files recalled** (after a scope correction, below).

| Ground-truth file | Surfaced? |
|---|---|
| admin/analytics.ts | ✅ |
| admin/list-customers.ts | ✅ |
| admin/list-pickup-locations.ts | ✅ |
| admin/list-products.ts | ✅ |
| admin/list-shipping-zones.ts | ✅ |
| admin/list-stockists.ts | ✅ |
| commerce/storefront.ts | ✅ |
| orders/get-order-summary.ts | ✅ |
| orders/search-order-ids.ts | ✅ |
| **locations.ts** | ⚠️ missed on first run, found after scope fix |

**Extra sites the sweep flagged that PR #252 did *not* touch** — the interesting part:

| File | Verdict | Reasoning |
|---|---|---|
| `orders/shipping.ts` | **same-class — a real miss** | Swallows the `shipping_zones` query error. Still unfixed in the current tree. The human sweep behind #252 missed it; this sweep found it. |
| `admin/require-admin.ts` | **similar-not-same** | Same mechanical shape, but `if (!adminRow) throw NotAuthorizedError()` — a failed query fails *closed* (denies access). The dangerous half of the semantic condition doesn't hold. Flag, don't lump in. |
| `journal.ts` | **false-positive** | `const { data } = matter(raw)` is gray-matter frontmatter, not a DB read. Correctly excluded by the semantic condition. |
| `rate-limit.ts` | **false-positive** | Destructures `error` **and checks it** (`if (error)`), failing open by documented design. Correctly excluded. |

**Findings folded back into the skill:**

1. **Glob-pathspec bug (the `locations.ts` miss).** `git grep -- 'src/lib/**/*.ts'`
   silently matches **zero** files sitting directly in `src/lib/` — the `**` glob
   requires an intermediate directory. `locations.ts` was invisible until the
   pathspec was corrected to `-- src/lib` (recursive by default). A sweep whose
   scope is expressed as a `**` glob under-reports without erroring. **The skill
   now warns against this explicitly.**
2. **The value case is real:** the sweep surfaced `orders/shipping.ts`, a genuine
   same-class site the human fix missed and that is *still* unfixed — the exact
   "fixed the instance, not the class" failure the skill exists to catch.

## Case B — unbounded full-table scans (#121/#219 → #192)

**Ground truth:** issue #192 names `list-customers.ts` and `analytics.ts` as
still scanning after the orders-table pagination fix. Pre-#192-fix ref
`af75a5f` (parent of `1d9e6a5`).

**Result: 2 / 2 named files recalled.**

- First signature (no `.range`/`.limit` **+ Node-side aggregation**) caught
  `analytics.ts` cleanly but caught `list-customers.ts` only incidentally, via a
  `.map`. Tightening the aggregation term dropped `list-customers` entirely.
- Re-derived signature (reads from an unbounded-growth table — `orders`,
  `profiles`, `order_items` — with neither `.range` nor `.limit`) recalled
  **both** named files reliably.

**Honest precision caveat:** the re-derived signature also flagged eight other
files. Several are false-positives that share the shape but are bounded by an
equality filter (`create-pending-order.ts`, `send-order-emails.ts`,
`webhook-handlers.ts`, `gdpr.ts` — all `.eq("id", …)` single-row or single-user
reads). The distinguishing condition — *"the result set grows with table size,
i.e. there is no equality filter bounding it to O(1) rows"* — is only partly
mechanizable. This is why the skill outputs an inventory with a per-hit verdict
rather than a fix: the semantic call is the human's, and for this class it is
load-bearing.

**Finding folded back into the skill:** the unbounded-scan class has two
mechanical shapes (fetch-all-then-aggregate; fetch-all-return). A single
signature under-serves it. When a signature fails to discriminate, the skill's
"re-derive the shape, don't widen it" rule applied and worked.

## Verdict

**Recall: strong** — 10/10 and 2/2 on ground truth, once the pathspec pitfall is
avoided. **Precision: entirely dependent on the semantic-verdict step**, which is
by design manual. The skill is usable: it finds the siblings, it found a real
miss the human overlooked, and its false-positives are caught at the verdict step
rather than turned into edits. Both real weaknesses discovered here (the `**`
glob pitfall; single-signature classes) are now written into `SKILL.md`.
