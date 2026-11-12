# Agent 2 handover — ADR 2025 input model v0.1 (2026-11-12)

## Deliverables created
204-field `field_catalog.csv`; evidence-aware JSON Schema; 13-class/division `decision_requirements.v0.1.json` with 10 cross-cutting decisions; relevance examples; 8+ model structure/safety tests; README/source manifest. Work is on an isolated Agent 2 branch, not merged to main.

## Regulatory sources used
ADR 2025, **ECE/TRANS/352 (Vol.I)**, Parts 1–3 (§§1.1.2–1.1.4, 2.1.1–2.1.6, 2.2.1–2.2.9, 2.3, 3.1–3.5), and **Vol.II** Parts 4–9 for applicable operational/packaging input; UN Manual of Tests and Criteria **ST/SG/AC.10/11/Rev.8** (2023), Parts I–III; EU Regulation **2020/878 Annex II §14**. Links and additional corrigenda status in README.

## Rules and decisions made
**Engineering, not regulatory determinations:** explicit five-state datum; evidence required for known or not-applicable states; screens for each of 13 hazard pathways; candidate evidence fields vs conditionally triggered inputs; exemptions separate from dangerous-goods status; no inference from CLP; no global non-DG while pathways are unassessed. No numerical thresholds or classifications were implemented.

## Assumptions requiring approval
Proposed dot-path field IDs and five-state envelope; completeness of 13 class screens as a conservative precondition; provenance contract; relationship between authority declarations and direct test evidence; mode-specific SDS output interface; applicability of the EU SDS reporting format in target jurisdiction. Lead Agent shared schema was not present in reviewed repo tree.

## Outstanding questions and missing evidence
Exact named entry/Table A/SP lookup; mixtures and waste of uncertain composition; authority-approved test and classification routes; 2025 English ADR Corr.1/Corr.2 not reconciled; Manual Rev.8 Amend.1 not reconciled; missing all non-ADR mode edition sources; no specific product test records; external regulatory expert approval not obtained. Input catalog does not prove that every field is mandatory or that a class is excluded when a named test is absent.

## Tests performed and results
Local suite: 8 tests passed, including 13-screen coverage, unique 204 fields, schema linkage, evidence requirements for known and inapplicable values, provenance for negative status, incomplete-screen fail-safe cases. Tests validate proposed data/model coherence **only**; no regulatory threshold or transport result verified.

## Dependencies / interfaces required
**Lead Agent:** shared schemas, versioning, canonical outcome/status and missingness interfaces. **Agent 1:** complete authoritative Table A and special provisions, source manifest, corrigenda. **Other rule agents:** class decisions, UN/PG/subsidiary assignment, competent-authority approvals. **SDS agent:** §14 per-mode serialization. **Independent reviewer:** legal and scientific validation.

## Recommended next tasks
1. Obtain Lead interface and create versioned adapter without modifying another agent's files.
2. Reconcile ADR Corr.1/Corr.2 and Rev.8 Amend.1, mark verified clauses.
3. Choose one modest class pathway (e.g. Class 3) to encode/review with adversarial missing-data tests.
4. Add RID/ADN/IMDG/ICAO TI official rules separately.
5. Independent regulatory review before machine classification is enabled.
