# Agent 3 handover — ADR 2025, Class 3 / 6.1 / 8 / 9

**Status:** prototype for independent review; not validated; do not use to publish SDS Section 14 without a full-class determination, specific UN entry and approval.

## 1. Deliverables created

- `adr2025/common.py`, `class3.py`, `class61.py`, `class8.py`, `class9.py`, `__init__.py`: pure deterministic rule evaluators.
- `rules_catalog.json`: human/machine-readable rule register with inputs, thresholds, scope, exceptions, outcomes and exact citations.
- `tests/test_classes.py`: 34 executable unittest cases with multiple subcases.
- `README.md`: inputs/outputs, limits and execution.
- `HANDOVER.md`: handover to Lead Agent and other specialist agents.

## 2. Regulatory sources used

- **ADR 2025, ECE/TRANS/352 (Vol. I)**, Part 2 §§2.1.3.10, 2.2.3.1.1, 2.2.3.1.3–2.2.3.1.5.2, 2.2.61.1.6–2.2.61.1.10, 2.2.8.1.5.1–2.2.8.1.6, 2.2.9.1.10.3.1–2.2.9.1.10.6, 2.2.9.1.13, 2.2.9.3, Part 3 §§3.2–3.3 (named entries/special provisions recognized as outstanding). Official PDF: https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf
- ADR 2025 UNECE index/corrigenda: https://unece.org/adr-2025-files (Corr.1 and Corr.2 require formal delta assessment).
- UN Manual of Tests and Criteria **ST/SG/AC.10/11/Rev.8** (2023) §32.2.5 and §37, user-supplied PDF. Note test procedures are supporting sources, ADR is the transport classification authority.
- User-supplied ADR 2025 **ECE/TRANS/352 (Vol. II)** applies to downstream transport procedures, not Part 2 core class criteria.

## 3. Rules and decisions made

- **C3:** Standard liquid cutoff FP ≤60°C, PG I boiling point ≤35°C, PG II FP<23°C with IBP>35°C, PG III 23≤FP≤60°C with IBP>35°C; carefully gated named diesel (60<FP≤100°C), heated liquid, and confirmed non-sustained combustion (FP>35°C) exceptions.
- **C6.1:** Primary substance/whole-material acute toxicity thresholds; conditional route priority; four-hour to one-hour conversions; vapour saturation concentration conditions; conservative human/class-priority gates.
- **C8:** Direct skin damage duration / onset / corrosion and tested metal rate criteria; special non-discriminating valid skin-study fallback.
- **C9:** Substance aquatic thresholds for Acute 1 and Chronic 1/2 and elevated-temperature Class 9 only where all other hazard classes excluded. Candidate UN 3077/3082 (aquatic) and 3257/3258 (elevated) are not final assignments.
- **All:** `criteria_not_met` is a **single-pathway observation only**; unresolved mixture/special/named-entry/precedence cases are `indeterminate`. No source-independent GHS→ADR mapping.

## 4. Assumptions requiring approval

- Temporary input/output shape until Lead Agent versioned schemas are available; status values `criteria_met`, `criteria_not_met`, `indeterminate` and no global `not_regulated` state.
- Booleans such as `named_entry_checked`, `other_hazards_assessed`, `human_experience_reviewed` stand in for reviewed evidence records. **Approval required** for evidence provenance and attestation contract; boolean flags alone are not robust enough for production.
- Caller supplies genuine validated measurement/test units and specifies substance vs fully tested mixture; mapping from SDS raw data to these inputs needs a trusted extractor and reviewer.
- For no adequate chronic data, the aquatic branch uses only stated degradability/bioaccumulation evidence; does not silently impute a default. This deliberately conservative implementation decision may be more restrictive than source's allowed fallback and needs Lead/legal review.
- Named-entry checks are hard gates in some positive pathways; returning a candidate UN is informative only. No production interpretation of `all_other_hazard_classes_excluded=True` without full evaluation and review.

## 5. Outstanding questions and missing evidence

- Obtain Lead Agent's unified input/output JSON schemas, evidence type/provenance, rule ID catalog and engine API, plus source clause register from Agent 1 and precedence framework from Agent 2.
- Complete formal impact review of ADR 2025 Corr.1/Corr.2; reconcile current 2026 use with ADR 2027 adoption plan separately.
- Resolve complex Class 3 viscosity/mixture exceptions, Class 6.1 untested-mixture inhalation algorithms and human data, Class 8 mixture bridging/tier-test specifics, Class 9 aquatic mixtures/M factors, batteries/other Class 9 subclasses.
- Resolve all Chapter 3.2 Table A specific entries, special provisions under Chapter 3.3, 2.1.3.10 precedence, subsidiary hazards, assignment basis and packing group overrides.
- Review effect of strong chemical instability, prohibited-for-carriage rules, temperature limits and modes other than ADR road (IMDG, IATA, RID).

## 6. Tests performed and results

- **34 unittest test cases passing**, with multiple boundary subcases, on local Python runtime. Examples test FP 23/60°C, IBP 35°C, LD50 5/50/300, 4h LC50 conversion, skin exposures 3/60/240 min, corrosion rate 6.25 mm/year, aquatic threshold and 100/240°C elevated temperature.
- `python -m compileall -q adr2025 tests` successful.
- Failure-mode tests verify `{}` returns `indeterminate` for all modules and never provides global `not_regulated` or final Section 14 status.
- **No** independent regulatory review, external conformance benchmark, CI acceptance or production validation has occurred.

## 7. Dependencies and interfaces required

- Lead Agent: versioned transport-evidence schema; rule engine pipeline and determinations interface; clause ID style, exception taxonomy, evidence provenance and reviewer sign-off.
- Agent 1: approved ADR 2025 clause register, dangerous goods list lookup and special provisions resolution; corrigenda tracking.
- Agent 2/precedence: hazard class prioritization, combined hazards, UN named/generic/N.O.S. selection, subsidiary risk and packing group selection.
- SDS extraction agent: transparent mapping of Section 9/11/12 and composition evidence to normalized methods/units, including data quality, measurement temperatures and missingness.
- CI/regulatory QA: golden expert cases, test artifacts, review state, edition pinning, reproducible reruns.

## 8. Recommended next tasks

1. Lead approval of versioned interface and evidence attestation policy.
2. Integrate exact ADR 2025 named-entry/special provisions and 2.1.3.10 precedence gates; fail closed.
3. Expand mixture rules per class, especially Class 9 M-factor summation and Class 8/6.1 mixture methods, with independent clause-by-clause review.
4. Create controlled test dataset of substances/mixtures independently classified by dangerous-goods specialists, include counterexamples and negative cases.
5. Implement auditable Section 14 output only when all mandatory mode-specific checks, evidence and sign-off are resolved.