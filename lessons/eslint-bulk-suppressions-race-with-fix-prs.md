---
applies-to: [node, eslint]
discovered: 2026-10
status: active
---

# ESLint bulk suppressions make the rule MR and the fix MRs depend on each other

ESLint's bulk suppressions file stores a violation count per file and rule. A
fixed violation whose entry is still listed makes lint exit 2 ("suppressions
left that do not occur anymore"), and a file that exceeds its count reports
every violation in it, not only the new one. So an MR that fixes violations
and an MR that adds the suppressions file both pass alone and fail once both
are merged, unless the second one prunes.

**Cost:** a throwaway merge of a rule-plus-suppressions branch with a branch
that fixed six of its fourteen violations failed lint with exit 2 until
`--prune-suppressions` was run; found before merge only because the merge was
tried.

**Instead:**

- Document `npm run lint -- --prune-suppressions` next to the suppressions
  file, and have every fix MR run it.
- Before opening either MR, merge both branches in a throwaway worktree and run
  the real lint script; record which MR must prune.
- Do not read the "all errors of the file are shown" output as a bug in the
  new code: check the stored count first.

**Strongest rung available:** none beyond the CI lint job itself, which already
fails the second MR; the lesson only moves the failure from post-merge to
pre-merge.
