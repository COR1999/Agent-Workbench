---
applies-to: [server-actions]
discovered: 2026-07
status: active
---

# A Server Action is a public POST endpoint, not a function call

Everything about the ergonomics implies a trusted internal boundary: you import
it, you call it with typed arguments, the compiler checks the call. None of that
constrains an attacker, who can invoke the action directly with any payload that
never passed through the form. A client-side Zod schema wired into
react-hook-form validates the form, not the endpoint.

**Cost:** an action reached with input the form could never have produced.
Found once with two independent instances in a single checkout action: no
server-side re-validation, and a state-changing write left uncleaned when the
external call after it failed.

**Instead:** every Server Action that takes user-controlled input re-validates
that input itself with its own schema and `.safeParse()`. Keep it separate from
the form's schema — the action's real input shape (nested objects, ids) usually
differs from the flat field shape the form validates, and sharing one schema
forces a bad compromise on both.

Bounds count as validation: maximum lengths on anything interpolated into an
email or a query, upper bounds on prices and rates, format checks on anything
rendered as a link, and rejection of duplicate ids in a collection.

**Strongest rung available:** a branded `Validated<T>` type that the action's
body requires and only `.safeParse()` can produce, making an unvalidated call
path fail to compile. Stronger than any review or lint rule.
