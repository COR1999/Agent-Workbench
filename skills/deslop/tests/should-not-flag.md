# should-not-flag corpus

Real hunks from real repositories that deslop **must leave untouched**. Every one
is legitimate engineering — provenance, deliberate error visibility, a justified
suppression, a load-bearing type, or a defensive check that looks redundant but
isn't. A single false positive here is a release blocker (design spec, gate on
Step 3).

Sources: `hotsauce-mama` (TS), `senus-board-report` (Python + TS). Paths are as of
the reviewed commit; verbatim.

Gate 3 category legend: **INFO** = information a reader can't recover from code ·
**SAFETY** = makes failure visible or undoes a partial write · **INTENT** = a
recorded deliberate choice.

---

### 1 — provenance comment (INFO) · hotsauce-mama `src/lib/format.ts:12`
```ts
/** Inverse of eurCentsToEuroString — was duplicated across edit-price-form.tsx, edit-shipping-zone-rate-form.tsx, and admin-shipping-zones.ts before being centralized here. */
export function euroStringToEurCents(euroString: string): number {
  return Math.round(Number(euroString) * 100);
}
```
Records why this function exists in one place. Deleting it invites re-duplication.

### 2 — dated incident pin (INFO+INTENT) · hotsauce-mama `.github/workflows/ci.yml:45`
```yaml
      # Pinned rather than "latest" -- resolving "latest" makes this action
      # call GitHub's release API on every run, which hit a rate limit and
      # failed CI outright (2026-07-17) for a reason completely unrelated to
      # the PR being tested. A pinned version skips that lookup entirely.
      - uses: supabase/setup-cli@v1
        with:
          version: 2.109.1
```
Comment + the pin itself. Both are the fix for a real outage.

### 3 — silent-failure guard with consequence note (SAFETY+INFO) · hotsauce-mama `src/lib/locations.ts:35`
```ts
  const { data, error } = await supabase...
  // A genuine query failure must not look like "no stockists nearby" (#250)
  // — this backs the public /find-us page, so a silent failure could read
  // to a customer as "not sold anywhere" rather than a real outage.
  if (error) {
    throw new Error(`Failed to load stockists: ${error.message}`);
  }
```
This *is* the fix for the #1 bug class. Removing the throw re-introduces it.

### 4 — justified lint suppression (INTENT) · hotsauce-mama `src/components/shared/meta-pixel.tsx:91`
```tsx
{/* eslint-disable-next-line @next/next/no-img-element -- Meta's official pixel fallback requires a plain <img>, not next/image (no optimization applies to a 1x1 tracking pixel). */}
```
Suppression carries its own justification. Exactly what a suppression should look like.

### 5 — compensating try/catch (SAFETY+INFO) · hotsauce-mama `src/app/actions/checkout.ts:96`
```ts
  // Everything below creates the actual Stripe Checkout Session — stock is
  // already reserved and the order already exists at this point. If any of
  // this throws (or Stripe just doesn't return a session URL), there's no
  // Stripe session for checkout.session.expired to ever fire on, so the
  // reservation would otherwise be stuck forever — clean it up the same way
  // an expired session does rather than leaving it orphaned.
  try {
```
Load-bearing error handling. The comment explains an invariant no code shows.

### 6 — deliberately-separate best-effort catch (SAFETY+INTENT) · hotsauce-mama `src/app/actions/checkout.ts:171`
```ts
    // Best-effort, and deliberately its own try/catch rather than sharing
    // the one below: the order/Stripe session already succeeded above, and
    // an optional marketing opt-in failing must never cancel a real order
```
Looks like it could be merged with the adjacent block. Must not be — the comment says why.

### 7 — discriminated error handling (SAFETY) · hotsauce-mama `src/app/actions/checkout.ts:84`
```ts
  } catch (error) {
    if (error instanceof OutOfStockError) {
      return { success: false, message: "One of the items in your cart just sold out." };
```
Typed branch on a domain error. Not a catch-log-rethrow to be flattened.

### 8 — load-bearing generic (INTENT) · hotsauce-mama `src/lib/hooks/use-server-action.ts:14`
```ts
export function useServerAction<TArgs extends unknown[]>(action: (...args: TArgs) => Promise<ActionResult>) {
```
`unknown[]` is the correct variance-preserving bound. Not lazy typing; do not "simplify."

### 9 — null-safe integration guard (SAFETY+INFO) · hotsauce-mama `src/lib/commerce/storefront.ts:41`
```ts
 * than crashing. Same null-safe philosophy as lib/resend.ts.
 */
function isSupabaseConfigured() {
  return Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
}
```
Exists so tests and previews run unconfigured. The cross-reference is information.

### 10 — ISR reasoning (INFO+INTENT) · hotsauce-mama `src/app/products/page.tsx:18`
```ts
// the highest-traffic page in the app, so under a real spike this caps DB
// load/server invocations instead of scaling 1:1 with visitors. Freshness
// comes primarily from revalidatePath("/products") calls at every real
// stock/price/purchasable change (see revalidate-storefront.ts); this is
// just the worst-case fallback if one of those is ever missed.
export const revalidate = 300;
```
`300` is not a magic number — the comment is its entire justification.

### 11 — deliberate client-choice comment (INTENT) · hotsauce-mama `src/lib/commerce/storefront.ts:46`
```ts
/**
 * Deliberately still the cookie-bound client, unlike getAllCommerceProducts
 * below — this is the individual product detail page's read, exactly where
```
Prevents a "consistency" refactor that would break auth context.

### 12 — deliberate validation bounds (SAFETY) · hotsauce-mama `src/lib/validation.ts:5`
```ts
  name: z.string().min(1, "Please enter your name.").max(200, "Name must be 200 characters or fewer."),
  message: z.string().min(10, "...").max(5000, "Message must be 5000 characters or fewer."),
```
Upper bounds are input-size defense, not verbosity. Removing `.max()` is a regression.

### 13 — ORM-cascade provenance (INFO) · senus-board-report `backend/app/api/routes/documents/_core.py:280`
```python
    # A bulk `delete(Document).where(...)` statement issues a direct SQL
    # DELETE that bypasses the ORM-level `cascade="all, delete-orphan"` on
    # Document's relationships -- there's no DB-level ON DELETE CASCADE
    # foreign key, so that used to fail with a ForeignKeyViolationError on
    # any document that actually had FinancialMetrics/... rows attached.
    # Loading the instance and deleting it through the session lets the ORM
    # cascade fire correctly.
    document = await db.get(Document, document_id)
```
Explains why the code looks less efficient than a bulk delete. Deleting the
comment invites the "optimization" that reintroduces the bug.

### 14 — error visibility at a boundary (SAFETY) · senus-board-report `backend/app/api/routes/documents/_core.py:45`
```python
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")
```
Re-raises HTTPException untouched, logs the unexpected, surfaces a clean 500.
This is correct boundary handling — not a swallow to be trimmed.

### 15 — None-vs-zero reasoning (INFO+SAFETY) · senus-board-report `backend/app/api/routes/metrics/dashboard_summary.py:300`
```python
        # Narrative-extracted, no prior-period comparative exists for this
        # field -- change/trend are always 0/neutral, never a fabricated
        # delta. `build()` isn't reused here because its formatter would
        # render a missing value as "€0", which would misrepresent
        # "not extracted" as a real zero-value figure.
        value = latest.bookings_value
```
Explains why an obvious reuse is deliberately avoided. Pure information.

### 16 — integrity comment (INFO) · senus-board-report `backend/app/api/routes/metrics/_shared.py:46`
```python
# must not silently become "the" board-facing number just because it
```
Guards a domain invariant about which figure is authoritative.

### 17 — domain-logic reason (INFO) · senus-board-report `backend/app/services/financial_metrics_extractor/_period_detection.py:63`
```python
        # because both half-year and full-year filings compare like-for-like
```
Explains a comparison rule that the code alone doesn't justify.

### 18 — baseline-shape note (INFO) · senus-board-report `backend/app/services/report_service.py:345`
```python
            # baseline would otherwise still be {"value": N} dicts here.
```
Documents a data-shape hazard a maintainer would otherwise trip on.

### 19 — circular-import resolution (INFO+INTENT) · senus-board-report `backend/app/api/routes/documents/__init__.py:238`
```python
# router instead. Imported after the definitions above so that, by the
# ... the standard pattern for resolving an otherwise-circular package/
```
The unusual import position is deliberate; the comment is why it can't move.

### 20 — comparative-purity reason (INFO) · senus-board-report `backend/app/services/report_service.py:292`
```python
                # document's real FY2024 comparative, purely because nothing
```
Explains an intentional data choice; removing it loses the rationale.

### 21 — validation guard reused as parse (INTENT) · hotsauce-mama `src/lib/commerce/storefront.ts:67`
```ts
  if (!isSupabaseConfigured()) return null;
```
Early-return guard, not dead defensiveness — pairs with #9. Removing it crashes
previews/tests.

### 22 — text-parsing suffix reason (INFO) · senus-board-report `backend/app/services/financial_metrics_extractor/_text_parsing.py:113`
```python
    # suffix position (e.g. "FY2028", "EBITDA") cannot match because the
```
Explains a non-obvious matching constraint. Information a reader can't reconstruct.
