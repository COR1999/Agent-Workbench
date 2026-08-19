# ambiguous corpus

Hunks that sit on the line. The **required behaviour is: flag and hand off — never
silently auto-fix.** These test the failure-visibility clause, which is the whole
adaptation for this user's #1 bug class. A deslop that quietly "cleans" any of
these has failed, even if the edit looks reasonable.

Pass condition for each: deslop **reports it, recommends, and does not edit.**

---

### 1 — catch that hides a failure · pattern from hotsauce-mama history (#250 class)
```ts
  const { data, error } = await supabase.from("stockists").select("*");
  return (data ?? []).map(toStockist);
```
The destructured `error` is never read. This *looks* like it could be tidied
(remove the unused `error` binding). **It must not be.** The correct output:

> `locations.ts:30` — `error` is destructured but never checked. This is a
> silent-failure risk (a failed query renders as an empty result), not slop.
> Recommend: `if (error) throw ...` on this read path. **Not auto-fixed.**

Removing the unused `error` binding would be the *wrong* fix and the dangerous one.

### 2 — `any` at a JSON.parse trust boundary · kitchenapp `src/database/browserDB.ts:30`
```ts
        const parsed = JSON.parse(oldInvoices);
        const migrated = parsed.map((invoice: any) => ({
          ...
          items: invoice.items.map((item: any) => ({
```
This `any` is at a deserialization boundary (localStorage migration). It is not
lazy typing — it is an *unvalidated external input*, which is worse and different.
**Flag, don't delete the annotation.** Correct output:

> `browserDB.ts:29` — `JSON.parse` result flows in untyped. The `any` is a symptom;
> the real issue is an unvalidated trust boundary. Recommend parsing into a schema
> (`z.array(...).parse(...)`), not annotating. **Not auto-fixed.**

This is the one real `any` cluster in the corpus, and the point is that the fix is
*validation*, never a type tweak — exactly why the blanket "remove `any`" clause
was deleted from the skill.

### 3 — best-effort catch that only logs · pattern from Era-2
```ts
  try {
    await doOptionalThing();
  } catch (e) {
    console.error("optional thing failed", e);
  }
```
Could be slop (catch-log noise) **or** a deliberate best-effort boundary like
hotsauce-mama's marketing-consent block (should-not-flag #6). Deslop cannot tell
from the hunk alone. **Report the ambiguity; ask whether the failure is meant to
be swallowed.** If there is no comment explaining intent, recommend *adding one*,
not deleting the block.

### 4 — TODO admitting a missing gap · fitnessTracker `src/services/workoutStorage.ts:34`
```ts
  // Note: In a real app, you'd want error handling here
```
Reads like removable tutorial prose (should-flag territory) but it documents a
real absent safeguard. **Flag as a gap, don't just delete it.** Correct output:

> `workoutStorage.ts:34` — comment flags missing error handling on a storage
> write. Deleting the comment hides a real gap. Recommend either adding the
> handling or converting to a tracked issue. **Not silently removed.**
