---
applies-to: [github-actions]
discovered: 2026-08
status: active
---

# Don't delete a stacked PR's base branch before the whole stack merges

GitHub closes a pull request when its **base** branch is deleted, and a
closed PR whose base no longer exists cannot be reopened. Stacked PRs are
usually chained this way — PR N targets PR N-1's branch — so merging the
bottom of the stack with `--delete-branch` (or any branch cleanup) silently
kills every PR above it. The work is not lost if two PRs share one head
branch, but recovering means finding or recreating an equivalent PR.

**Cost:** mid-stack merge, the second PR auto-closed as "closed, unmerged"
with conflicts, unreopenable; recovery detoured through its duplicate PR
and required retargeting every remaining link to `main` before merging.

**Instead:** when merging a chained stack, retarget each PR to `main` (or
merge without `--delete-branch`) until the entire stack is merged; delete
branches only at the end. Check `baseRefName` on every open PR first —
`gh pr list --json number,baseRefName` — because the chain is invisible in
the PR list UI.

**Strongest rung available:** none mechanical; it's GitHub platform
behaviour. A pre-merge checklist step is the practical guard.
