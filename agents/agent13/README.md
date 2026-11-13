# Agent 13 — ADR 2025 Class 9 specialist review

**Status: provisional; independent regulatory review required.** This branch is owned by Agent 13 and intentionally does not alter Agent 3's PR #2 or any other agent-owned files.

Regulatory scope: ADR 2025 ECE/TRANS/352 Vol. I §§2.2.9, 2.1.3.8, Chapter 3.2 Table A, Chapter 3.3 and relevant UN Manual of Tests and Criteria Rev.8 (+ Amendment 1).

Deliverables under development: `class9.py` (evidence-scoped deterministic Class 9 evaluation), `rules.json` (clause and input register), `tests/test_class9.py`, `UNSUPPORTED.md`, `HANDOVER.md`. Class 9 is not a catch-all for missing evidence. Incomplete constituent data do not imply absence of environmental hazard. A candidate PG requires a verified Table A row; no final UN or SDS Section 14 assignment can be made by this specialist module. Cross-class hazard precedence, environmental markings, DGL/SP dependencies, and CLP fallback require separate signed-off services.

This README is a branch-scope declaration; see subsequent module commits for the executable implementation and tests.