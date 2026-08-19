# Personal Agent System — Phase 1 Research

Research and design only. Nothing was changed in any of your projects.

Read in this order:

| # | Report | What it answers |
|---|---|---|
| 01 | [GitHub Archaeology](01_GITHUB_ARCHAEOLOGY.md) | What's actually in your history |
| 02 | [Development Patterns](02_MY_DEVELOPMENT_PATTERNS.md) | How you actually work |
| 03 | [Recurring Problems](03_RECURRING_PROBLEMS.md) | What keeps coming back, and why |
| 04 | [Personal Style Profile](04_PERSONAL_STYLE_PROFILE.md) | Your implicit conventions |
| 05 | [Skill Discovery](05_SKILL_DISCOVERY.md) | Scored candidate skills |
| 06 | [External Skill Comparison](06_EXTERNAL_SKILL_COMPARISON.md) | Adopt / adapt / reject |
| 07 | [Personal Skill Tree](07_PERSONAL_SKILL_TREE.md) | The tree derived from evidence |
| 08 | [Skill Gaps](08_SKILL_GAPS.md) | What's missing |
| 09 | [Deslop Design](09_DESLOP_DESIGN.md) | Full deslop spec |
| 10 | [Skill Format](10_SKILL_FORMAT.md) | Minimum viable metadata |
| 11 | [Skill Routing](11_SKILL_ROUTING.md) | How skills get found |
| 12 | [Skill Testing](12_SKILL_TESTING.md) | How skills get proven |
| 13 | [Project Adapter](13_PROJECT_ADAPTER.md) | Global vs project split |
| 14 | [Repository Architecture](14_REPOSITORY_ARCHITECTURE.md) | The repo design |
| 15 | [Skill Roadmap](15_SKILL_ROADMAP.md) | Tiers, top 5, top 15 |
| 16 | [Open Questions](16_OPEN_QUESTIONS.md) | Decisions I need from you |

## Evidence labelling

Throughout, findings are tagged:

- **[FACT]** — directly verifiable in your repos. File paths, PR numbers, counts.
- **[INFERENCE]** — my reading of the facts. Could be wrong.
- **[RECOMMENDATION]** — what I think you should do.

## The four things you should read even if you read nothing else

1. **`any` is not your problem** — [03](03_RECURRING_PROBLEMS.md#the-typescript-premise-does-not-hold). Zero occurrences in 24,856 lines of your flagship project.
2. **Deslop as specified would damage your best code** — [09](09_DESLOP_DESIGN.md#why-the-reference-deslop-is-dangerous-here). Two of its four focus areas target patterns that are load-bearing in your repos.
3. **Your highest-leverage missing skill is `sweep-the-class`** — [05](05_SKILL_DISCOVERY.md), [08](08_SKILL_GAPS.md). You have documented, repeated evidence of the same fix being applied to one call site and missed on nine others.
4. **Nothing you learn escapes the project that taught it** — [08](08_SKILL_GAPS.md#the-missing-capability-you-did-not-ask-for). This is the real gap.
