---
applies-to: [supabase]
discovered: 2026-07
status: active
---

# Read the error, or a failure looks identical to an empty result

A query returns `{ data, error }` and `data` is null both when the query failed
and when nothing matched. `const { data } = await client.from(...)` followed by
`(data ?? []).map(...)` is correct-looking code for both cases, and the type
system cannot help — `data` is declared nullable regardless of `error`, so strict
mode never complains.

**Cost:** the worst recurring bug class encountered so far. A missing migration
made one read fail while a second read path for the same record succeeded, so
one page showed a product as unavailable while another showed it in stock — same
record, two contradictory answers, decided entirely by which path had swallowed
its error. The same shape has appeared in list views ("no results" when the query
failed), in transactional email (reported as sent when the provider rejected it),
and in a rate limiter that failed open silently.

**Instead:**

- **Read paths: throw.** A genuine query failure is an outage, and it should
  reach error tracking rather than render as absence.
- **Write paths: return a discriminated result** the caller must branch on.
- Never let the failure path and the empty path converge on one return.

When fixing one instance, search for the others before closing it. This defect
arrives in families — the same missing check tends to exist at every read path
written in the same sitting.

**Strongest rung available:** a lint rule flagging a destructured `error` binding
that is never read in scope. Directly enforceable, not yet written. This is the
highest-value item in this ledger's backlog.
