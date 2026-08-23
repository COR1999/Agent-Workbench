# Contributing

Small, evidence-based changes. No premature abstraction. When a rule can be
mechanically checked, encode it as a check rather than as prose.

## Checks

Two guard scripts protect this repo. CI runs both on every push and PR to
`main` (`.github/workflows/checks.yml`); run them locally before pushing too:

```bash
bash tests/skill-invariants.sh     # load-bearing SKILL.md rules can't be silently lost
bash scripts/preflight-public.sh   # no client-identifying material enters the public tree
```

Both exit non-zero on failure. If you add a new class of invariant or of
identifying material caught by hand, add its pattern to the relevant script so
the next catch is mechanical, not remembered.
