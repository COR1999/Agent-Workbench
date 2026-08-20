---
name: design-handbook
description: >
  Use when asked to design, redesign, restyle, or improve the look of a UI, or
  to "show what this could look like" / "give me HTML" / prototype a visual
  direction. Produces a browsable standalone HTML handbook the human picks from
  BEFORE any production code changes. Triggers on "design this", "make this look
  better", "redesign the <component>", "visualise", "prototype the UI", "branding",
  "give me HTML/CSS for this". Not for tiny one-off style tweaks.
---

# design-handbook

A visual approval layer before implementation. The agent proposes, the human sees
it in a browser and picks, then the agent implements. Prevents the "asked for a
design → edited 30 files blind" failure.

## Two hard phases — never blur them

**Phase 1 — Design.** Analyse → propose → generate a standalone HTML handbook →
the human visualises and picks → iterate. **No production code changes.**
**Phase 2 — Implement.** Only after explicit approval ("approved — implement").

## Phase 1

1. **Recon (read-only).** Learn the real stack, tokens, fonts, components, and any
   brand assets. Read the actual code; don't assume.
2. **Propose ≤3 coherent directions**, each a genuinely different reading (not
   colour swaps), and **mark one recommended** with a one-line why.
3. **Build ONE self-contained HTML handbook** in a scratch folder *outside* the
   app (real fonts via CDN, real palette, real assets copied in). Give the human a
   `file://` path to open. It must be visual, not a written doc.
4. **Consistent choices.** For each component show **at most 3 options, one
   recommended**, and use one consistent answer convention throughout (e.g.
   "reply: buttons=B, card=1"). Keep it easy to pick from — fewer options beats
   more.
5. **Current vs proposed.** Show the existing design next to options; never hide it.
6. Wait. Update the handbook first on feedback; touch production only on approval.

## Phase 2 (after approval)

Implement the approved direction by editing existing components and tokens — not a
rewrite. Preserve behaviour, accessibility, responsiveness; keep TS strict; no
`any`; follow local conventions. Then run **deslop** on the diff and report.

## Guardrails

- **Never touch production code in Phase 1.** The browser preview is the contract.
- **≤3 options per component, one recommended, one consistent answer format.**
- Optimise for brand fit, clarity, usability, accessibility — not "modern". Avoid
  generic purple-gradient/glassmorphism/AI-SaaS defaults unless the brand's own
  evidence supports them.
- Project brand decisions (palette, type, personality) stay project-specific.

## TODO
Attaching before/after images to the resulting PR needs image hosting (issue #5).
