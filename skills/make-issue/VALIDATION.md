# make-issue — validation

**Evidence class: none yet, and stated plainly.** This skill has not been fired in a
real session, so there is no field record (the kind `explain-and-open-pr` has) and
no fixture corpus (the kind `deslop` has). Do not read its presence in the library
as evidence that it works.

## What was checked when it was written

Run by hand against a real private repository, read-only, before the skill was saved:

| Step the skill relies on | Command | Result |
|---|---|---|
| Live visibility check | `gh repo view --json nameWithOwner,visibility` | returned `PRIVATE` |
| Live label set with descriptions | `gh label list --limit 100 --json name,description` | returned the 9 default labels |
| Duplicate search | `gh issue list --state all --search "<keywords>"` | found the two matching open issues |
| Title style | `gh issue list --limit N --json title` | returned the existing titles |

Not run: `gh issue create` and `gh issue view` as the skill orders them (running
them would have filed a throwaway issue). The same two commands were used by hand
for five real issues the same day, with the label set the skill's table produces.

## What would count as evidence

- Fired from a plain "make issue" with no skill named: **routed**, not primed.
- The issue exists, with at least one type label that is in the repo's live label
  list, within the same session.
- No duplicate was filed when an open issue already covered it.
- The human did not have to ask for labels, or ask "did you search first?".

Record each firing here with its outcome. After about ten firings, keep, sharpen or
cut.
