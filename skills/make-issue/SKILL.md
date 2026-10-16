---
name: make-issue
description: >
  Use whenever the user asks to file, log, open, raise or create a GitHub issue
  and you are about to run `gh issue create`. Reads the repository's live labels,
  searches for a duplicate first, picks the labels from the content of the issue
  (never invented, never left to chance), writes a body with the evidence and a
  "done when" list, adds the model's `Co-Authored-By` line, creates it, then
  reads it back to confirm what was applied. Triggers on "make issue", "make an
  issue", "open an issue", "log an issue", "file an issue", "create an issue",
  "raise an issue", "add this to the backlog", "make a ticket".
---

# make-issue

An issue that arrives without labels, without a duplicate check and without
evidence is a note, not a backlog item. This skill makes the labelling and the
checks the default, so "make issue" always produces the same quality of ticket.

Filing an issue is **not** working it. Create the issue and stop, unless the
human also asked for the work.

## Steps

1. **Read the live repository, not memory.**
   - `gh repo view --json nameWithOwner,visibility` — which repo, and whether it
     is public. Check it; do not trust a README that says "private".
   - Read the project's own rules for issues (`CLAUDE.md`, `AGENTS.md`,
     `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/`). Where they name a label set,
     a title style, an assignment rule or a template, **they win over this skill.**
   - `gh label list --limit 100 --json name,description` — the only labels you
     may apply. Match by name *and* description, since custom repos rename things.
   - `gh issue list --limit 10 --json title` — copy the title style already in use.

2. **Search for a duplicate before writing anything.**
   `gh issue list --state all --search "<2-3 distinctive keywords>" --limit 20`,
   twice with different keywords. If an open issue already covers it, add a
   comment there with the new evidence and stop. If a closed one covers it,
   say so and ask whether to reopen. Report what you searched for either way: a
   null result must be distinguishable from not having looked.

3. **Choose the labels from the content.** One *type* label is required; add
   modifiers only when they are true. Use this table, mapped onto whatever the
   repository's labels are actually called:

   | The issue is... | Type label | Add also |
   |---|---|---|
   | Something is broken or behaves wrongly | `bug` | `accessibility` if a person is blocked by it |
   | A new capability or an improvement | `enhancement` | |
   | Docs are wrong, missing or stale | `documentation` | |
   | Waiting on a human decision before work can start | `needs-decision` if it exists, else `question` | the type label for the work itself |
   | A question with no work attached yet | `question` | |

   Modifiers, each only if it is true:
   - `good first issue` — small, self-contained, the cause and the fix are both clear.
   - `help wanted` — needs someone with access or knowledge the author lacks.
   - `accessibility` — affects people using assistive tech, contrast, keyboard or zoom.
   - `dependencies`, `security`, `performance`, area labels — only if the repo has them.

   Rules: at most three labels. Never apply `duplicate`, `invalid` or `wontfix` at
   creation. **Never invent a label and never create one silently.** If the right
   label does not exist (the project's own docs may even name it), use the closest
   existing one, and say in the reply which label was missing so the human can
   decide whether to create it.

4. **Write the body** to a file (`/tmp/issue-<slug>.md`), not inline:

   ```markdown
   ## Problem            (or "What is missing" / "What")
   <what is wrong or wanted, in plain English, one short paragraph>

   ## Evidence
   <how it was found; what was run or read; the exact command, file or page.
   Say what was checked and what was only inferred. No claim you did not verify.>

   ## Suggested approach
   <the smallest sensible fix, or the options with a recommendation. Say "not
   confirmed" where the cause is a guess.>

   ## Done when
   - [ ] <observable check, not an activity>

   Related: #<n> (only real, checked numbers)

   Co-Authored-By: <your actual model name and version> <noreply@<provider-domain>>
   ```

   - Name the model that is actually writing it (for example
     `Claude Sonnet 5.5 <noreply@anthropic.com>`). Never a placeholder.
   - If step 1 showed the repository is **public**, genericise at the moment of
     writing: no client, brand or private repository names, no private issue
     numbers, no real internal paths, no credentials or personal data. If you
     cannot describe it without them, tell the human and stop.
   - A security vulnerability in a public repo is **not** filed as an issue.
     Point the human to a private security advisory instead.
   - Split unrelated problems into separate issues. One problem, one issue.
   - A decision only the owner can make belongs in the issue, stated as a
     question with the options, not buried in the approach.

5. **Create it.**
   `gh issue create --title "<title>" --label "<a>,<b>" --body-file /tmp/issue-<slug>.md`
   - Title: short, specific, in the repo's existing style; say what is wrong or
     wanted, not "Bug" or "Improvement".
   - Assign (`--assignee @me`) only if the human is taking it now, or the
     project's rules say to assign on pick-up and work is starting.

6. **Read it back.** `gh issue view <n> --json number,url,labels,assignees,state`.
   Confirm the labels you asked for were actually applied.

7. **Reply** with, in this order: the issue URL; each label and a few words on
   why; what you searched for duplicates (and what you found); anything missing
   (a label that does not exist, a decision that is the owner's). Keep it short.

## Not for

- Pull requests (use `explain-and-open-pr`).
- Adding a comment to an existing issue (do that directly; step 2 only routes to it).
- Starting the work on the issue.
- Bulk-creating issues from a list the human has not seen. Show the list first.
