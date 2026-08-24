# capture-lesson — fixture corpus

Candidate lessons with a known verdict, for checking that the four-part test
separates a lesson from a preference, a fact, or project context.

**Every case is real.** Each one was actually encountered — in this repository's
history or in the session that built these fixtures — and the verdict is the one
that was actually reached at the time, not one invented to make a tidy example.
Cases where the skill should *refuse* matter more than cases where it should
write, because refusing is the behaviour nothing else measures: a firing that
produces no lesson file is indistinguishable from a failure unless the case is
known in advance.

The tests, in order. Stop at the first failure.

1. **Cost** — did it cost something real?
2. **Portable** — true in another repository, given the same condition?
3. **Non-obvious** — not findable in 30 seconds from code, docs, or the error?
4. **Changes behaviour** — not just what an agent knows?

---

## SHOULD WRITE

### W1 — GNU-only `sed` idiom empties the file under BSD
`sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}'` trims trailing blank lines on GNU and
produces an *empty* file on BSD, exit 0, no stderr.

- Cost: destroyed a project's `AGENTS.md` on macOS while reporting success. ✅
- Portable: any shell script using GNU idioms on a BSD userland. ✅
- Non-obvious: passes on two of three platforms, no error. ✅
- Changes behaviour: the next trim gets written in `awk`. ✅

**Verdict: WRITE.** Captured as `gnu-sed-idioms-empty-files-on-bsd`.

### W2 — a copy-fallback installer freezes what it installed
An installer that symlinks and falls back to copying leaves a snapshot; every
later edit to the source reaches nothing, and the directory looks correct.

- Cost: three days of edits reached no session; nearly invalidated an experiment. ✅
- Portable: any install script with a copy fallback. ✅
- Non-obvious: nothing errors; the files are all present. ✅
- Changes behaviour: verify by grepping the *installed* file for a sentinel. ✅

**Verdict: WRITE.** Captured as `copy-fallback-freezes-the-install`.

### W3 — one agent window can be several backends with separate stores
Searching one store and concluding a session does not exist.

- Cost: triggered a plan to recreate in-flight work from scratch. ✅
- Portable: any GUI shell orchestrating multiple agent backends. ✅
- Non-obvious: the UI shows one window. ✅
- Changes behaviour: enumerate every backend's store before concluding zero. ✅

**Verdict: WRITE.** Captured as `agent-sessions-live-in-multiple-stores`.

---

## SHOULD REFUSE

### R1 — "prefer static icons over `next/og` `ImageResponse`"
The surviving half of a lesson whose bug was falsified by re-testing on
next@16.3.2.

- Cost: **fails.** With the bug gone, ignoring this costs nothing. It is a
  reasonable default, not an incident.

**Verdict: REFUSE at test 1 — preference.** This is the exact case that makes R1
worth having: it *was* a lesson, the technical claim was disproved, and what
remains reads like advice. A skill that writes it back is laundering a preference
through a retired lesson.

### R2 — "`.research/` is gitignored, so nothing in it is published"
True, load-bearing, and acted on repeatedly.

- Cost: passes — misreading it wasted time in an audit.
- Portable: **fails.** It is a fact about one repository's `.gitignore`.

**Verdict: REFUSE at test 2 — project context.** Belongs in that repo's own
`AGENTS.md`. The trap is that it feels important, and importance is not
portability.

### R3 — "`grep -c` prints 0 and exits 1 when nothing matches"
Cost real time here: a `|| echo 0` fallback emitted two zeroes and a correct
check reported failure.

- Cost: passes.
- Portable: passes.
- Non-obvious: **fails.** `man grep` states the exit status plainly, and the
  behaviour is reproducible in one command.

**Verdict: REFUSE at test 3 — documentation.** Costing time is not sufficient. The
ledger is for things the documentation will not tell you.

### R4 — "`adopt.sh` handles paths containing spaces"
Verified by test, and worth knowing.

- Cost: **fails** — nothing broke; it was confirmed working.
- Non-obvious: fails.
- Changes behaviour: fails. No agent writes a different line because of it.

**Verdict: REFUSE at test 1 — a fact, and a test assertion.** Its correct home is
the assertion in `tests/import-migration.sh`, which is where it went.

### R5 — "always run the test suite before opening a PR"
Reasonable, universally applicable, and repeatedly acted on.

- Cost: passes in general.
- Portable: passes — arguably *too* well.
- Non-obvious: fails.
- Changes behaviour: passes.

**Verdict: REFUSE — unconditional, therefore a rule, not a lesson.** A lesson
needs an "if". This one has none, so it belongs in `AGENTS.md`. The failure mode
this case guards against is a ledger that fills with good advice until nothing in
it is specific enough to act on.

---

## How to use this corpus

Run the skill's Step 2 against each case and compare the verdict *and the test
number it stopped at*. Stopping at the right verdict for the wrong reason is a
miss: R1 and R4 both end in REFUSE at test 1, but for different reasons — one is a
preference, the other a fact — and a test that conflates them will misclassify the
next case.

**Not yet run as a gate.** Unlike `deslop`'s corpus, no threshold is set. Setting
one on 8 cases would imply more precision than 8 cases carry.
