# Agent 4 — Detailed handover to Lead Agent

**Module:** `agents/class41/` | **Regulation:** ADR 2025 ECE/TRANS/352 English, Volume I, Chapter 2.2.41 | **State:** DRAFT, PROVISIONAL, UNREVIEWED.

## 1. Deliverables

- `class41.py`: seven isolated Class 4.1 evidence-scoped pathways, deterministic numeric boundaries, no final UN or PG.
- `rules.json`: **36 machine-readable regulatory rule conditions**, clause references, editions, evidence and units.
- `test_class41.py`: **10 test methods and 77 local synthetic scenario checks, all passing** after last local code corrections.
- `exceptions.json`: **26 explicit prohibition, exception, missingness, unsupported and manual-decision cases**.
- `README.md`: regulatory summary, evidence matrix, implementation contract and release conditions.

All files isolated under `agents/class41/`; no other agent's files modified.

## 2. Primary sources reviewed

1. ADR 2025, ECE/TRANS/352 (Vol. I), English: 2.1.1.3, 2.1.2–2.1.3, 2.2.41.1.1–.1.21, 2.2.41.2.1–.2.3, 2.2.41.3 collective-entry table and footnotes, 2.2.41.4 list of self-reactives, Chapter 3.2 Table A and SP386 cross-reference.
2. ADR 2025, ECE/TRANS/352 (Vol. II): dependencies for 4.1.4.1 P520, 4.1.4.2 IBC520, 4.2.5.2.6 T23 and 7.1.7; **not implemented as transport permissions**.
3. MTC Rev.8, ST/SG/AC.10/11/Rev.8: Part I series 1, 2, 6; Part II 20.4, series A–H (series H for SADT/SAPT), Part III 33.2.4 N.1 and 33.3.
4. MTC Rev.8 Amendment 1, ST/SG/AC.10/11/Rev.8/Amend.1: Section 28 terminology, 33.3.1 cross-reference update and Appendix 6 A6.5.1 screening criteria; **Appendix 6 screen not operationalized**.
5. Existing repository `regulations/adr/2025/sources.json` identifies Corr.1 and Corr.2; no independent regulatory diff for this module.

No model-derived or CLP/GHS thresholds are coded.

## 3. Normative pathways and packing-group policy

**Readily combustible solids:** Test N.1, burning time under 45 s over 100 mm or rate over 2.2 mm/s. PG II if flame passes wetted zone and burning time is under 45 s; PG III if wetted zone stops flame for at least four minutes and burning time is under 45 s. Positive experience evidence is allowed only for the unnamed organic solids covered by 2.2.41.1.4, without auto-PG.

**Metal powders:** N.1 ignition and reaction spread the whole 100 mm within 10 minutes. PG II at 5 minutes or less; III over 5 through 10 minutes. A 4.2/4.3 competing hazard prevents unilateral 4.1 classification and moves to the integrator.

**Friction solids:** Named-entry analogy or special provision required; no invented PG.

**Self-reactives:** Class 1, 5.1, 5.2 exclusions (with 5% combustible-organic oxidizing-mixture exception); heat of decomposition under 300 J/g or 50 kg SADT above 75 °C excludes the self-reactive pathway. Tested types A–G: A not accepted, B–F require exact list/authority route and *no packing group*, G outside Class 4.1 self-reactive provisions. At or below 55 °C SADT for the *actual offered package* triggers temperature control. Sample type C exception and dilution/activator gates preserved.

**Solid desensitized explosives:** Exact Table A listing is mandatory; unlisted substances are not accepted for carriage. No blanket PG or invented UN number.

**Polymerizing:** SAPT at or below 75 °C, reaction heat above 300 J/g and no other Class 1–8 criterion, with SAPT verified in the offered packaging/IBC/tank. Temperature control at or below 50 °C (packaging/IBC) or 45 °C (tank). Competing classes trigger SP386 handoff. No blanket PG.

**Related self-reactives:** MTC Part I series 1, 2 and 6 plus negative self-reactive/5.1/5.2 evidence; Table A/PG unassigned.

All `pg_candidate` values are *provisional laboratory candidates*. `final_packing_group` is always `None`, including in positive test cases.

## 4. Evidence contract and representation

Input: `evaluate(evidence: dict) -> dict`, one explicitly selected `pathway`, not global classification. Numeric data are parsed with `Decimal`; invalid, nonfinite and negative burn measurements are blocked. Core normalized fields and units are in `rules.json`. Raw underlying report must eventually bind to: method/series, report ID, issuer, date, sample formulation and concentration, stabilizer/diluent, exact container/quantity, package dimensions, measured values, uncertainty, test conclusion and confidence. This module does not have a complete evidence provenance schema and does **not** certify those documents.

Output keys: `status`, `class_candidate`, `pg_candidate`, `final_packing_group`, `temperature_control_required`, `subdivision`, `type_candidate`, `subsidiary_hazard_candidates`, `blockers`, `clauses`, `notes`, `needs_table_a_and_special_provisions`, `independently_reviewed`.

Statuses: `criteria_met`, `criteria_not_met` (pathway-only), `indeterminate`, `not_accepted_for_carriage`, `requires_authority`, `requires_expert_decision`, `external_class_review`.

**Proposed Lead Agent integration rule:** none of these specialist statuses independently licenses final SDS Section 14 assignment. A `criteria_met` containing any blocker requires unresolved-evidence handoff. Other seven statuses require explicit reconciliation; `criteria_not_met` is not global “not regulated.” Competing hazard candidates `4.2`, `4.3`, `5.1`, `6.1`, `8` are returned only when input reports independently verified transport evidence; precedence is not calculated here.

## 5. Downstream gates and authority dependencies

- **Named entries:** 2.1.2.2 and Table A column 2 must take precedence, subject to exact composition and 2.1.2.8 conditions.
- **Collective entry groups:** 2.2.41.1.2 and 2.2.41.3 F/F1–4, FO, FT1/2, FC1/2, D, DT, SR1/2, PM1/2 are *not* automatic UN assignments.
- **Self-reactive listed formulations:** 2.2.41.4 plus OP packing method and listed concentration/temperature/remarks, 4.1.4.2 IBC520 and 4.2.5.2.6 T23. Unlisted: competent authority of origin / recognition conditions (2.2.41.1.13).
- **P520, IBC520, T23, 7.1.7:** packagings, controls, emergency temps, containment and mode/quantity conditions must be independently resolved.
- **Multi-hazard precedence:** 2.1.3 and SP386, 2.2.41.3 footnotes metal powders, Class 5.1 oxidizing mixture note, Class 1 gates, Class 4.2 positive overlap note in 2.2.41.1.9.
- **PG:** resolve actual Table A row/column 4, scope exemptions, named entry, and special-provision conditions before any final PG.

## 6. Tests and reproduction

Local command: `cd agents/class41 && python -m unittest -v test_class41`.

Result (local Python 3): **10 test methods, 80 scenario checks, 0 failures, 0 errors**. Tested: N.1 time 44.999/45, rate 2.2/2.21, wetted-zone branches, metal 5/5.0001/10/10.0001, negative screening, contradiction, missing values, invalid method, no CLP shortcut, heat 299.999/300/300.001, SADT 55/55.01 and 75/75.01, polymer SAPT 45/45.01/50/50.001/75/75.001, PG guards, diluent bp/flash boundaries, self-reactive A/G/B–F, oxidizing mixture 4.99/5%, authority gate, sample 10 kg boundary, listed/unlisted desensitized explosives and competing hazards.

These are **synthetic threshold regressions**, not empirical validation. They have not been run as repository CI or independently audited.

## 7. Unresolved questions requiring Lead Agent decisions

1. Adopt/reconcile canonical schema, statuses, blockers and clause/edition registry with Agent 0; map provisional local keys to approved fields without changing other owners' files.
2. Implement verified evidence-to-report identifiers, calibration/uncertainty review, actual formulation and packed state, missing negative findings and test protocol conformance. Current normalized Boolean inputs must not be populated from general SDS prose without validation.
3. Verify 2.2.41.4 complete list, IBC520/T23, Table A column 4 and special provisions, without inventing a final UN/PG.
4. Examine MTC Rev.8 Amend.1 Appendix 6 screening for valid applicability, strong autocatalysis and fresh/aged sample requirements. It is intentionally out of scope for this deterministic draft.
5. Independently reconcile ADR 2025 Corr.1/Corr.2 against these exact clauses, 2.2.41.4, Table A and temperature-control provisions.
6. Decide class-4.1 positive precedence against Classes 1, 4.2, 4.3, 5.1, 5.2, 6.1 and 8. Neither class assignment nor subsidiary labels are final here.
7. Establish a legal reviewer signoff for prohibitions, special samples, competent-authority papers, listed concentration exceptions, named entries and packagings.
8. Author comprehensive live-fixture tests from actual MTC test reports and Table A row IDs, plus red-team contradictory-evidence tests.

## 8. Required review and release checklist

- [ ] Independent verification of each ADR and MTC clause/edition against controlled official PDFs, incl. amendments/corrigenda.
- [ ] Reproduce every boundary and negative using raw N.1/Part II reports, not invented normalized data.
- [ ] Reconcile all 26 exception/unsupported cases and record reviewer/expert decisions.
- [ ] Conform to Lead schema + enforce evidence references and sample/formulation/packaging version.
- [ ] Complete named entry and Table A/SP joins; validate PG by exact row.
- [ ] Validate all authorisations, transport-mode/packaging conditions and temperature controls.
- [ ] Check prohibited carriage and no-global-negative gates cannot be bypassed.
- [ ] Add CI, regulatory release version, audit log, approval signature.
- [ ] Merge only after independent approval; no automated public release from draft PR.

## 9. Recommended next steps

Review this PR alongside Lead Agent's schema and Agent 1's Table A-ingestion draft, then run the rule register through a signed regulatory traceability audit. Until those checks pass, keep PR draft and all class/PG candidates provisional.
