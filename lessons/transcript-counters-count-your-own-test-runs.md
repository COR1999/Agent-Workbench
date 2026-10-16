---
applies-to: [multi-agent]
discovered: 2026-10
status: active
---

# A counter over agent transcripts counts your own test sessions, and a whole-day window counts sessions that predate the thing measured

Any script that reads the session transcripts an agent tool writes will count
every session that wrote one, including the headless runs you launched to test
the counter or the capability it measures. And capabilities such as agents,
skills and config are loaded when a session starts, so a session that began
before an install cannot have used it, however recent the day.

**Cost:** The first real run of a delegation counter reported four sessions in its
window. Two were the author's own verification runs from a temporary directory;
two began hours before the install. The baseline would have started at four
instead of zero, and the trial's denominator was inflated from the first
reading. Neither showed up in the tests, only in listing the sessions behind the
number.

**Instead:** Start the window at the install's exact time, not its date. Run
verification sessions from a throwaway working directory you can recognise, and
delete their transcripts afterwards. Before trusting a count, list the sessions
behind it (start time and working directory) and read them.

**Strongest rung available:** a time-of-day window in the counter itself, pinned
by a test (done). Excluding by working-directory pattern would hide legitimate
work that happens to run under a temp path, so that part stays a reading step.
