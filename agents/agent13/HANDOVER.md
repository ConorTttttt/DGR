# Handover — Agent 13 ADR 2025 Class 9

**Status: PROVISIONAL; unvalidated; draft branch only.** Lead must approve interface, evidence provenance, UN list, SP resolution and regulatory interpretations before merge.

## 1. Deliverables created

- `class9.py`: standalone deterministic Class 9 candidate evaluator, separate from Agent 3-owned prototype, with three family pathways and environmental/primary separation.
- `rules.json`: machine-readable rule and clause register, source editions, measured units, exception paths, M-factor and summation/additivity formulas.
- `tests/test_class9.py`: 41 locally passing `unittest` cases, including repeated threshold subcases; `README.md`; `UNSUPPORTED.md`.
- Draft PR opened against `main` from `agent13/adr2025-class9-audit`, referencing but not editing PR #2. Integrate only under Lead permission.

## 2. Regulatory material examined

- Supplied **ADR 2025 ECE/TRANS/352 Vol. I** English (2024 publication): §2.1.3.8; Chapter 2.2.9 (§§2.2.9.1.1–.15; §2.2.9.2; §2.2.9.3); Table 2.2.9.1.10.3.1; Figure 2.2.9.1.10.3.1; Figure 2.2.9.1.10.4.2; Tables 2.2.9.1.10.4.6.2.2 / .3.3 / .4; Parts 3.2/3.3 remain external dependencies.
- Supplied **UN Manual of Tests and Criteria Rev.8 ST/SG/AC.10/11/Rev.8** (2023): §§38.3.2, 38.3.3, 38.3.4, 38.3.5 battery tests/summaries.
- Supplied **Rev.8 Amendment 1** (2025), Section 38, amendments to §§38.3.2.2, .2.3, .4.5.2–.4.6.3. Amendment's application to the ADR 2025 baseline requires Lead review.

## 3. Rules and decisions

1. **Substance hazard:** Acute 1 L(E)C50≤1 mg/L. Chronic 1/2 based on adequate chronic data and rapid degradability. Where chronic data inadequate, apply NRD or bioaccumulation branch (BCF≥500 or, where BCF absent and justified, log Kow≥4); ADR Note 4 directs NRD when no useful degradation data. Algal sensitivity >100x, species coverage and test method adequacy require review.
2. **Mixture hierarchy:** whole-mixture acute/chronic test; then verified bridging; then constituent summation/additivity. Positive known summations retained provisionally if other ingredient hazards are unknown; no definitive negative with unknown/unlisted ingredients. Acute 1 sum Σ(C*M)≥25%; Chronic 1 Σ(C*M)≥25%; Chronic 2 10Σ(C*M for Chronic1)+Σ(C for Chronic2)≥25%, with table-defined separate M factors. Additivity uses ADR 4.5.2 acute and chronic denominators and then categorizes the tested fraction before summing.
3. **Role/entry:** An aquatic criterion alone does not force primary Class 9; 2.1.3.8 allows environmental hazard in addition to another class. Only cross-class and named-entry reviewed solid/liquid candidates are 3077/3082. Packing group III is emitted **only** with matching, externally attested 2025 Table A row and the 2.2.9.1.10.6 criterion; attestation is not verification by this evaluator.
4. **Elevated temp:** liquid ≥100°C and below actual flash point if present; solid ≥240°C. If liquid at or above FP, Class 3 specialist must review. Class 9 criterion applies only if no other class.
5. **Other:** M1 asbestos; M2 PCB/PCT mixtures >50 mg/kg (≤50 mg/kg M2 mixture exception); M3 flammable vapour polymers with contained liquid FP≤55°C; M4 lithium/sodium type tests and documented safety/QMP/test-summary/SP gates; M5/M8/M11 require external entries, SP or authority evidence. All outputs are tentative.

## 4. Assumptions requiring Lead approval

- Agent 3-compatible temporary result vocabulary plus `aquatic_categories`; no common versioned Lead schema yet.
- Documents referenced by identifiers in evidence are assumed authentic, not cryptographically verified or retrieved. Table A row checks establish internal *consistency* only, never official confirmation.
- Summation conservatively includes all known potentially hazardous ingredients, including below default relevance concentrations, to avoid overlooking high M-factor contributions.
- For a positive known-ingredient sum with unknown other data, status `criteria_met` means **known evidence positively meets that scoped formula**, not a definitive/complete mixture hazard class (set `categories_definitive=false`).
- Whole-substance model uses minimum accepted acute and chronic endpoint values and requires explicit trophic-level/edge case review; it does not fully implement Figure 2.2.9.1.10.3.1 for partial species data.
- Additivity is restricted to constituents with both acute and chronic endpoints plus documented taxonomic selection. Other legitimate cases are blocked instead of assumed negative.
- CLP fallback under ADR §2.2.9.1.10.5 requires separate explicit regulatory approval and evidence when direct aquatic data are unavailable; no automatic CLP/GHS mapping.

## 5. Outstanding blockers

- Obtain Agent 1 complete, edition-verified 2025 Table A columns 1–6 and Chapter 3.3 applicability (incl. UN3077/3082/3257/3258, all M1–M11 entries), and confirm PG-blank entries.
- Agent 2 precedence and environmental mark/descriptor pipeline including environmental hazard on Classes 1–6.2, 8, 9 other than 3077/3082.
- Lead shared input and result schema, evidence units/source quality and actual evidence record verification; GHS/CLP fallback policy.
- Corrigenda assessment, OECD testing GLP evidence, entire mixed chronic trophic approach, special guidance on metals and poorly soluble inorganics, SP exceptions, damage/prototype battery handling, MTC Rev8 Amendment1 temporal integration.
- Independently labelled benchmark suite and domain sign-off. Do not merge for production.

## 6. Tests run

`python -m unittest discover -s tests -v` — **41 test methods passed** locally (multiple boundary subcases); `python -m py_compile class9.py` and `python -m json.tool rules.json` passed. Tests include Acute/Chronic summation and M-factor boundaries, additivity, unlisted constituents, unknown evidence, CLP-only evidence rejection, physical state, PG Table A checks, 100/240°C cutoffs, PCB 50 mg/kg, polymer 55°C and lithium/sodium battery type/SP gates. These are **implementation behavior tests only**; no external conformance study or independent validation was performed.

## 7. Required handoffs and next actions

Lead: review this branch against PR #2 and authorize any edits to Agent 3's `class9.py`; decide whether to replace or adapt and wire the common schema. Agent 1: install DGL/SP service and verify PG row provenance. Agent 2: connect precedence, additional environment status, primary Class 9, and marking logic. Tests/QA: independent experts evaluate difficult mixtures and lithium/sodium condition cases; replay boundary cases in CI. All claims remain provisional until independent approval.
