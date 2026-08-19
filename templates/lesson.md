---
applies-to: [<one or more values from the vocabulary below>]
discovered: <YYYY-MM>
status: active
---

# <One-line claim, in the imperative or as a statement of fact>

<Two to four sentences. What is true, and why it bites. No project names, no
client names, no repository names, no issue numbers. If the claim cannot be
stated without them, this is project context, not a lesson.>

**Cost:** <What it actually broke, in generic terms. A lesson with no cost is a
preference.>

**Instead:** <What to do. A lesson without this is a complaint.>

**Strongest rung available:** <The strongest structural encoding that would
enforce this — a type, a lint rule, a CI check, a pinned version, a test — or
"none, this is judgement". This line is a standing backlog item.>

---

## How to use this template

Delete this section in a real lesson.

### The four-part test — all four must hold

Apply in order. Stop at the first failure.

1. **Did it cost something real?** Time, a bug, an outage, a revert, a re-filed
   issue. → If no: it is a preference. Not a lesson.
2. **Would it be true in a different repository, given the same condition?**
   → If no: it is project context. Leave it in the project.
3. **Is it non-obvious?** Would someone hit this and not find the answer within
   30 seconds from the code, the docs, or the error message?
   → If no: it is documentation. Not a lesson.
4. **Does it change what an agent does, not just what it knows?** State the next
   line of code someone writes differently because of it. If you cannot, it
   fails.
   → If no: it is a fact. Not a lesson.

Test 4 is the one that fails most often and matters most. "Supabase returns
`{ data, error }`" passes 1–3 and fails 4. "Read the `error`; on read paths,
throw, because a failure otherwise looks like an empty result" passes 4.

**A rule is not a lesson.** If it is true with no condition at all — no stack, no
OS, no library — it belongs in the root `AGENTS.md` instead.

**Cap: ~30 entries.** Past that you are logging, not learning. Re-apply test 4
to every entry at 15 and again at 25.

### The `applies-to` vocabulary — closed set

A lesson matches a project when **every** value in its `applies-to` is detected.
Values must be mechanically detectable. Adding a new value requires stating its
detection signal here.

| Value | Detection signal |
|---|---|
| `windows` | the machine, not the repo |
| `macos` | the machine, not the repo |
| `node` | `package.json` exists |
| `python` | `pyproject.toml` / `requirements.txt` exists |
| `typescript` | `tsconfig.json` exists |
| `react` | `react` in `package.json` dependencies |
| `nextjs` | `next` in `package.json` dependencies |
| `nextjs-app-router` | `app/` or `src/app/` contains `layout.tsx` |
| `server-actions` | `"use server"` appears in source |
| `isr` | `revalidate` export or `next: { revalidate }` in source |
| `webhooks` | a route handler verifying a signature header |
| `fastapi` | `fastapi` in Python dependencies |
| `tailwind-v3` | `tailwindcss` `^3` in `package.json` |
| `tailwind-v4` | `tailwindcss` `^4` in `package.json` |
| `shadcn` | `components.json` exists |
| `radix` | any `@radix-ui/*` dependency |
| `supabase` | `@supabase/supabase-js` dependency or `supabase/` directory |
| `postgres` | a Postgres driver or `*.sql` migrations |
| `sqlalchemy` | `sqlalchemy` in Python dependencies |
| `stripe` | `stripe` dependency |
| `resend` | `resend` dependency |
| `gemini` | `google-genai` / `google-generativeai` dependency |
| `vitest` | `vitest` dependency |
| `playwright` | `@playwright/test` dependency |
| `eslint` | `eslint` dependency |
| `github-actions` | `.github/workflows/` exists |
| `vercel` | `vercel.json`, or Vercel-specific config in `next.config.*` |
| `railway` | `railway.json` / `Procfile` |

Prefer the narrowest accurate set. `[nextjs, windows]` matches fewer projects
than `[nextjs]`, and that is the point — a lesson that matches everything is a
rule, and a lesson that matches nothing is dead weight.

**The auto-detector (`scripts/adopt.sh`) covers a subset of this vocabulary.**
Most values are detected; a few structural ones (`postgres`, `webhooks`) are not,
and `supabase` is detected by dependency and directory. A lesson tagged with an
undetected value will silently never inline — no error, it just won't appear in a
project. If you add a lesson using an undetected value, add its detection line to
`adopt.sh` at the same time, next to the others.

**Matching is AND, and this is deliberate.** Every value must be present for the
lesson to apply. The known cost is that some lessons under-reach: the truth in
`compensate-after-external-call` holds for any external call in a write path,
but the only mechanically detectable proxy is `stripe`, so a project using a
different service will not inherit it. OR semantics or a behaviour-shaped
`patterns` tier would fix that, and both were rejected at v0.1 as infrastructure
ahead of evidence. **Revisit at ~15 entries**, when there will be enough real
use to say whether under-matching actually costs anything. Do not add it before
then.
