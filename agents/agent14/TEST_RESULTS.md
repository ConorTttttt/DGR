# Agent 14 synthetic test report — ADR 2025 precedence

**Status:** 34/34 GitHub Actions synthetic tests PASS; Python compilation PASS. **Regulatory review: NOT INDEPENDENTLY VALIDATED.** No real dangerous-goods classification is approved.

## Reproducible committed-code result

- Repository: ConorTttttt/DGR, draft PR #34
- Branch: agent14/adr2025-cross-class-precedence
- Tested PR merge ref based on code commit: 3bfc7c5ac07089a3af11842aca2cfb14dd299b28
- Workflow run ID: 43341951125
- Workflow link: https://github.com/ConorTttttt/DGR/actions/runs/43341951125
- Job ID: 131612121729
- Job conclusion: success
- Python version: 3.12.16
- Test invocation: python -m unittest discover -s agents/agent14 -p 'test_*.py' -v
- Results: Ran 34 tests in 0.016s. OK. 34 passed, 0 failures, 0 errors.
- Compilation invocation: python -m py_compile agents/agent14/precedence.py agents/agent14/test_precedence.py
- Compile result: success.

## Synthetic coverage

Tests assert explicit positives, 13-class scope and class-scoped negative, incomplete/unknown evidence, conflicting PG candidates, conditional SOL/LIQ source cells, Class6.1 route and pesticide footnote, three-way precedence, absolute priorities including Class7 excepted SP290 and 6.1 inhalation/Class8 carveout, oxidizer explosive gate, unique named vs generic row exception, incorrect class/PG/column5 labels, unverified row/corrigenda and missing/valid SP set.

Fixtures use a purposely **fictional** UN '9999' and mock source row; no real Table A entry or SDS material was classified. The normalized 198 matrix entries have not been independently double-checked against the official ADR PDF. The local preliminary 30-test prototype was not byte-identical to this commit; only this GitHub run is used to claim the above committed-code result.

## Non-merge blockers

No independent legal/regulatory sign-off, no source-authenticated Table A/SP integration, no actual Agent0/Agent1/Agent4 end-to-end test, no external expert golden cases, no full hazard/PG/labeling authority review, no complete English Corr.1/2 reconciliation, and no authenticated release/signature service.

Every result, even when successfully reconciled, has publishable=false and assignment_permitted=false. Provisional only.
