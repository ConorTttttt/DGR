# Agent 14 synthetic test report — ADR 2025 precedence

**Regulatory review status:** NOT INDEPENDENTLY VALIDATED. Tests are mock/synthetic engineering assertions, not a class- or UN-number classification authority.

## Test inventory

- File: agents/agent14/test_precedence.py
- 34 named unittest test methods committed, using one shared synthetic packet fixture with all 13 class findings.
- Positive, class-scoped negative, incomplete, conflicting candidate PG, missing source evidence, unconditional priority Classes 1/2/5.2/7, Class 7 excepted package with SP290, toxic inhalation/Class 8 carveout, physical form SOL/LIQ boundary, pesticide footnote, three-hazard precedence, missing toxicity route, oxidizer/Class 1 gate, Table A row and PG, classification label, SP codes, and named vs generic exception.
- Test fixture intentionally uses UN '9999' and MOCK row identity: no actual ADR shipping-name selection implied.
- Code: agents/agent14/precedence.py. Matrix data: 198 occupied cells, 22 row keys x 18 columns.
- Command: python -m unittest discover -s agents/agent14 -p 'test_*.py' -v
- Compile: python -m py_compile agents/agent14/precedence.py agents/agent14/test_precedence.py

## Execution provenance

A related **local preliminary prototype** passed 30/30 tests earlier in development; that prototype was not byte-identical to the GitHub-committed code. **Do not treat the local result as proof that these 34 committed test methods passed.** GitHub Actions on the draft PR is the intended source of truth for the committed version. CI outcome: PENDING at this report revision; update it only after inspecting the actual workflow run.

No independent golden-case validation, no class-scoped laboratory/UN-specific regulatory cross-check, no complete 198-cell independent audit, and no end-to-end integration with Agent0/Agent1/Agent4 was performed.

Release invariants: publishable=false and assignment_permitted=false for both blocked and reconciled-provisional returns. Module remains provisional regardless of CI success.
