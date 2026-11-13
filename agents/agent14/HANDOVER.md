# Detailed Agent 14 handover to Lead Agent

**Regime:** ADR 2025 English, ECE/TRANS/352 Vol I. **Review:** pending; never claim compliance validation. **Exclusive branch:** agent14/adr2025-cross-class-precedence. **PR base:** main. **Owner:** Agent14. Files changed only in agents/agent14 plus separately owned Agent14 workflow.

## Architecture and data handoff

Read Agent0 draft contract PR #6 and Agent4 UN-entry selector draft PR #1; Agent1 Table A importer draft PR #5 supplies exact row data. This module is a proposal for the missing precedence stage, not a change to their code. Its evaluate(packet, context, selection) function first demands 13 evidence-scoped, complete hazard evaluations then applies all qualifying §2.1.3.5.3 absolute priorities, then the 198 normalized intersections of §2.1.3.10 for remaining hazards. The resulting primary class and matrix PG are only **provisional candidates**. PG is not final without a source-authenticated exact Table A row and reconciliation of columns (3a),(3b),(4),(5),(6), followed by all actual SPs at §3.3.1. Conflicting candidate PG or row PG blocks output; does not silently overwrite.

Lead v0.1.0 packet: regulatory_context ADR-2025-EN + source_set_id adr2025-en-provisional-v1, class_evaluations for each of 1,2,3,4.1,4.2,4.3,5.1,5.2,6.1,6.2,7,8,9; each has evidence_ids, references, criteria_status, coverage_status, primary_class_candidates, packing_group_candidates, exclusions, unresolved_evidence. Evidence must have sample identity, method/units where measured, provenance source document locator and SHA. Missing/unknown/not_measured/conflicting do not become negative.

Precedence context: externally verified predicates and evidence_ids for absolute_subtypes (Class3 liquid desensitized; Class4.1 self-reactive or solid desensitized; Class4.2 pyrophoric), Class7 excepted package SP290 and UN3507 exclusion, 6.1 toxicity_route (DERMAL/ORAL/INHAL), Class8 inhalation-corrosive carveout, pesticide footnote, material_form (SOL/LIQ). Oxidizer explosive screening, waste, articles, environmental hazards and competent authority route are external and fail closed. The current oxidizer_explosive_screen='cleared' input is only asserted, not cryptographically validated, and requires a Lead evidence adapter.

Selection adapter: selector_status='table_a_verified', candidate_set_complete=true, named_entry_screening='complete'; selected_row carries row_id, un_number, proper_shipping_name, source_id='ADR25_VOL1', verification edition/cells/corrigenda flags, raw columns '3a','3b','4','5','6', evidence-reviewed normalized label classes; every column6 SP must have status, source_clause, evidence IDs and verification. A named_exception under §2.1.3.3 or 2.1.3.4.x may apply only with evidence and unique corresponding positive class. These are provisional agreed-shape proposals, **not approved by other agents**. Test row UN 9999 is intentionally fictional and not legal data.

## Deliverables

1. precedence.py, pure deterministic no-external-package engine, evidence gates, absolute and matrix precedence, multiple-hazard permutations and contradictions, row/SP/PG checks, audit trace with cell identifiers and reasons for rejected alternatives.
2. precedence_matrix.json, 22 table rows x 18 column positions, 198 occupied cells; source printed 107 (PDF p.127), 2.1.3.10. Solid-vs-liquid variants, footnote a Class6.1 pesticides.
3. regulatory_register.csv and decision_rules.json, 24 source-linked rule records and pending review.
4. unsupported_cases.csv, 30 unresolved/exception cases, effect codes and handoff to specialist, Agent1, Agent4, authority or Lead.
5. source_manifest.json with full edition and supporting reference metadata.
6. test_precedence.py + TEST_RESULTS.md, synthetic-only coverage.
7. This handover.

## Source and release review

ADR §2.1.1.3 defines PG concept and no-PG classes; §2.1.3.5.3(a)–(i) absolute priority, §2.1.3.5.4 delegates remaining hazards to §2.1.3.10; §§2.1.3.3–4 special named products and mixtures; §2.1.3.7 oxidizer explosive restriction; §2.1.3.8 additional environmental hazard; §2.1.3.5.5 wastes; §2.1.5.5 articles; §3.2.1 and §3.3.1 exact row and provisions. Supporting MTC Rev.8/Amend1 covers specialist test methods only, not matrix. ADR 2025 Corr.2 modifies note example UN1921 wording; full English Corr.1/Corr.2 reconciliation pending.

Critical unresolved dependencies for Lead: independent expert double-entry review of all 198 cells, absolute exception pathways, 3+ hazard examples, physical state and toxicity route evidence; resolve Source Set and exact TableA row data including multiple-UN-number rows and blank PG; external SP 290, 274, 318 and all assigned SP; named vs generic selector hierarchy; authenticated source/authority evidence; special articles/mixtures/wastes/explosive oxidizers/environmental subs; align adapter to Agent0 schema and Agent4's actual implementation; run class integration golden tests; independent regulatory sign-off; outer release gate. Since the repo is public, confirm redistribution rights for source text. Do not auto-commit bulk official Table A data.

## Acceptance and limitations

Run python -m unittest discover -s agents/agent14 -p 'test_*.py' -v and Python compilation, then capture actual CI result. Tests are synthetic only. A reconciled result must still set publishable=false and assignment_permitted=false; no production SDS output or regulatory approval.

**Lead action:** review draft PR and agree interface/exception ownership. Do not merge/enable until independent regulatory and technical review.
