# Agent 12 — Class 8 test record (local, provisional)

Executed on 2026-11-13 (UTC) against the exact source files committed in this draft PR.

Command from isolated review package root:

    python -m unittest discover -s agents/agent12/tests -v

Interpreter: Python 3.13.5.

**Result: Ran 19 tests in 0.001 s — OK.** Python compilation also passed. Each test method includes additional subtests where specified.

Exact Git blob/content identity with branch:
- agents/agent12/class8.py: 33e044223918630467b6232d031ca124ce55187d
- agents/agent12/tests/test_class8.py: dfd91dafa006c18827e77481387754bf3e680e9a

Test methods passed:
1. test_bridging_five_principles_and_missing_conditions
2. test_conflicting_human_and_animal_pg
3. test_human_and_skin_disagreement
4. test_human_positive_without_tier_needs_tier
5. test_human_requires_documented_review
6. test_metal_conditions_boundaries
7. test_metal_physical_state_scope
8. test_metal_rate_and_mixed_results
9. test_metal_thresholds_and_local_attack
10. test_missing_study_detail
11. test_mixture_gates
12. test_mixture_generic_flow_boundaries
13. test_mixture_synergy_guard_only_ii_iii
14. test_never_final_dgl_pg
15. test_non_tiering_fallback
16. test_observation_boundaries_fail_closed
17. test_oecd439_cannot_label_corrosive
18. test_only_localised_corrosion_can_prove_positive
19. test_skin_tiers_exact_boundaries

Scope of evidence: synthetic deterministic boundary/failure-mode tests only. These tests do **not** constitute independent verification of ADR 2025 interpretation, source study quality, legal applicability, final UN/DGL packing groups, special provisions, hazard precedence, CI or laboratory conformance. All release and integration gates in HANDOVER.md remain open.
