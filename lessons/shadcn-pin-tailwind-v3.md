---
applies-to: [shadcn, tailwind-v3]
discovered: 2026-07
status: active
---

# Pin the shadcn CLI on a Tailwind v3 project

`npx shadcn@latest add <component>` resolves to the current major, which
generates Tailwind-v4-only CSS and Base UI primitives. On a Tailwind v3 project
this produces components that look correct in the diff and do not work — the
generated styles reference syntax the installed Tailwind cannot compile.

**Cost:** components added late in a project that fail to style correctly, with
the cause sitting in a generator invocation rather than in the component.

**Instead:** pin the CLI to the last version matching the project's Tailwind
major — `npx shadcn@2.10.0 add <component>` for Tailwind v3 — and record the pin
and its reason in the project's own `AGENTS.md`. Check compatibility before
bumping it.

**Strongest rung available:** a `shadcn` entry under `devDependencies` with an
exact version, invoked via a `package.json` script rather than `npx @latest`.
That makes the pin structural instead of a thing to remember.
