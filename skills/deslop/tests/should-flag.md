# should-flag corpus

Real AI-generated slop from real repositories that deslop **should remove or
rewrite**. All from Era-2 repos (`invoicing-tool`, `inventory-app`, `fitness-tracker`)
where output was shipped less reviewed. Target: ~80% caught (a miss costs one
round of surviving slop; it is not a release blocker the way a §should-not-flag
false positive is).

Each hunk states the removal and the gate that clears it: in the diff (G1),
inconsistent with the file's own conventions (G2), removal loses nothing (G3).

---

### 1 — comment restating the next line · invoicing-tool `middleware.ts:4`
```ts
  // Add security headers
  response.headers.set(...)
  // Prevent clickjacking
  response.headers.set("X-Frame-Options", "DENY")
  // Prevent MIME type sniffing
  response.headers.set("X-Content-Type-Options", "nosniff")
```
Each comment restates the call under it. **Remove.** (G3: the header name says it.)

### 2 — restating comments · invoicing-tool `src/app/api/upload/route.ts:20`
```ts
    // Validate file type
    ...
    // Validate file size (10MB limit)
```
The `10MB limit` parenthetical is borderline-useful; the labels are not.
**Remove the labels; keep any bound that isn't in the code.**

### 3 — narrating comments over self-evident calls · invoicing-tool `src/lib/export.ts:5`
```ts
  // Create a new workbook
  const workbook = new ExcelJS.Workbook()
  // Create summary worksheet
  const summary = workbook.addWorksheet("Summary")
```
**Remove.** `addWorksheet("Summary")` already says "create summary worksheet."

### 4 — aspirational production prose · invoicing-tool `src/lib/email.ts:19`
```ts
// In production, you'd use a service like SendGrid, Mailgun, or AWS SES
...
    // In production, you'd actually send the email here
```
Tutorial voice, no information about *this* code. **Remove.** (If the stub is
real, a one-line `// stub: no email sent` is the honest replacement.)

### 5 — aspirational prose · invoicing-tool `src/lib/storage.ts:4`
```ts
// In production, you'd use a database like PostgreSQL, MongoDB, etc.
```
**Remove.** Says nothing about what the code does.

### 6 — banner / tutorial comment · fitness-tracker `my-app/constants.ts:15`
```ts
/*
 * APPLICATION CONSTANTS
 *
 * This prevents "magic numbers" scattered throughout the code
 */
```
Banner + a justification for the concept of constants. **Remove the banner;**
keep the file. (G3: no information about any specific constant is lost.)

### 7 — TODO admitting missing error handling · fitness-tracker `my-app/src/services/workoutStorage.ts:34`
```ts
  // Note: In a real app, you'd want error handling here
```
Not slop to silently delete — it flags a real gap. **This is a §ambiguous case,
see ambiguous.md #4.** Listed here only to mark the boundary: do not treat it as
a plain "remove the comment."

### 8 — commented-out scaffold · fitness-tracker `playwright.config.ts:53`
```ts
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
```
Generator leftover, never enabled. **Remove.** (G3: version control has it if ever
wanted.) Note the `import dotenv`/`path` commented lines at top of the same file
are the same class.
```ts
// import dotenv from 'dotenv';
// import path from 'path';
```

### 9 — `as any` to silence the compiler · inventory-app `src/components/Dashboard.tsx:334`
```tsx
                      onClick={() => setFilter(tab.key as any)}
```
`as any` at a call site to bypass a type. **Flag.** The right fix is a proper
union for `tab.key`, but at minimum this is not idiomatic and not in the diff by
necessity. (Distinguish from a JSON.parse trust boundary — see ambiguous.md #2.)

### 10 — untyped update param · inventory-app `src/components/Dashboard.tsx:89`
```tsx
  const handleUpdateItem = (itemId: string, updates: any) => {
```
`updates: any` on an internal handler where the shape is known locally.
**Flag** — this is the lazy-typing form of `any`, not a boundary. Recommend the
real update type.
