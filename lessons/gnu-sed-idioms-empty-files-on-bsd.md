---
applies-to: [macos]
discovered: 2026-08
status: active
---

# A GNU-only `sed` idiom does not error on BSD — it silently produces the wrong file

The loop-and-branch form used to trim trailing blank lines,
`sed -e :a -e '/^[[:space:]]*$/{$d;N;ba}'`, is a GNU construct. BSD `sed`, which
is what macOS ships, parses the label and branch differently and emits an empty
result instead of a trimmed one. It exits 0 and writes nothing to stderr, so a
script that pipes a file through it and redirects the output replaces that file
with nothing while reporting success. The same script is correct on Linux and
under Git Bash on Windows, so the fault is invisible on the machine it was
written on.

**Cost:** a script whose entire promise was to edit one delimited block of a file
and leave the rest untouched instead destroyed the whole file on one platform.
Everything the human had written outside the managed block was gone, with a
success message. It had shipped and could only ever have been caught on a Mac.

**Instead:**

- Do not use `sed` label/branch constructs, in-place `-i` without an argument, or
  `\+`/`\?` in a script that may run on more than one OS. Reach for `awk`, which
  behaves the same everywhere: remember the last line with content and print up to
  it.
- Treat "passes on my machine and on Linux CI" as covering two of the three common
  platforms, not as portability.
- When a text-munging step can produce an empty result, assert the content
  survived rather than that the command exited 0 — this failure mode has a zero
  exit status by construction. Related in kind to
  [[check-lastexitcode-not-stderr]]: the exit code and the outcome are different
  questions.

**Strongest rung available:** a CI matrix that runs the scripts on macOS. This
bug was found within one minute of adding one, having survived every prior review
and every local run. Nothing short of executing on a BSD userland would have
found it.
