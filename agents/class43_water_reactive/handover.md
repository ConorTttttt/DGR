# Agent 6 → Lead Agent handover — ADR 2025 Class 4.3 (2026-11-12)

## Status / ownership

**Draft; independent regulatory and CI sign-off NOT performed.** Branch `agent6/adr2025-class43-water-reactive` adds files ONLY under `agents/class43_water_reactive/`. No Lead or other specialist-owned files were altered. Please do not treat this as a final ADR classification product.

## Deliverables

1. `classify.js` — pure, deterministic Class 4.3 candidate evaluator, method validity/unknown/conflict rejection, fixed-point thresholds, class-scoped negative findings, PG I/II/III intrinsic candidates, subsidiary candidate referrals and UN3133 carriage gate.
2. `evidence.schema.json` — typed transport-test input and source metadata including units, samples, conditions, evidence provenance, gas evolution, solids preparation, test repetition and explicit mixture route.
3. `rule_register.json` — 28 provisional clause-linked ADR/MTC requirements, edition IDs and PDF SHA-256 values.
4. `classify.test.js` — 43 synthetic Node test cases including cut-off/near-cut-off, missing evidence, conflicting and forbidden routes.
5. `test_results.json` — exact execution accounting: early developmental 28/28 V8 checks passed, **current 43-case Node suite NOT run**. No CI green claimed.
6. `unsupported_cases.md` — 32 blocked/unsupported routes and specialist hand-offs.
7. `README.md` — module API, safety boundaries, legal rate table, N.5 methods and test command.

## Regulatory interpretation and rule decisions

**Class:** ADR 2.2.43.1.5(a) gas spontaneously ignites at any N.5 stage OR 2.2.43.1.5(b) flammable gas **>1 L/kg/h**. N.5-specific negative requires a sufficiently complete method; missing, invalid, inconsistent or potentially stricter evidence yields `indeterminate`, not `criteria_not_met`.

**Intrinsic PG:** ADR 2.2.43.1.8(a) PG I requires vigorously water-reactive and general ignition tendency, OR **≥10 L/kg in any ONE-minute period**. PG II requires readily reacting and **≥20 L/kg/h** and demonstrably not PG I. PG III requires slowly reacting and **>1 L/kg/h** and demonstrably not I or II. Class and PG evidence may complete at different times. `packing_group_candidates` are never Table A PG assignments.

**Test:** UN MTC Rev8 Part III 33.5.3.1 and 33.5.4.3–.4. Three runs, commercial form, 20°C distilled water, atmospheric pressure, grinding condition (**>1%** <500μm or friable), 7h hourly readings with up to 5-day extension when prescribed. Gas identity/flammability is evidence-gated. Incompatible methods fail closed. The test input's base-10 decimal rate/volume fields do not conflate L/kg per hour and L/kg per one-minute period.

**Mixes and special:** ADR 2.2.43.1.6 and 2.1.3 support actual whole-mixture evidence, not ingredient extrapolation. Named-entry/solution pathways ADR 2.1.3.3 and 2.2.43.1.7 deferred. ADR 2.3.5 organometallic flowchart and 2.2.43.3 footnotes deferred. ADR 2.2.43.2 UN3133 carriage prohibition is only flagged if solid + independently confirmed oxidizer hazard; no UN assignment invented. 2.1.3.5.5 waste default PG II unavailable for Class4.3.

## Lead API and schema integration

- Returns a `class_evaluation`-shaped object following **Agent 0 PR #6** `integration/agent0/schemas/integration_packet.schema.json`: `module_id`, `hazard_class="4.3"`, `coverage_status`, `criteria_status`, `evidence_ids`, clause `references`, `primary_class_candidates`, `subsidiary_risk_candidates`, `packing_group_candidates`, `exclusions`, `unresolved_evidence`, `expert_decision_ids`, `limitations`, `rule_ids`.
- `criteria_met` means one **intrinsic** Class4.3 predicate is positively supported; `criteria_not_met` is class-scoped only. `coverage_status=incomplete` for unresolved PG, and a positive candidate may still contain a blocking `unresolved_evidence` item (e.g. prohibited carriage).
- The Lead integration packet's **separate evidence-array** still requires an adapter mapping `test_report` into canonical document/field evidence objects. The function **does not authenticate** document hashes or perform official Table A matching; no release signature.
- **Important conflict:** PR #6 Agent0 `class_evaluation` schema and PR #8 `contracts/v1/status_policy.json` use different status-level structures (`coverage_status` vs supplementary authority/prohibition statuses). Lead must approve one version and add adapter tests; Agent6 did not edit either contract.
- Other hazard candidates are added only when separately provided as `other_class_findings[{hazard_class,status:'criteria_met',evidence_id}]`. They are referrals, not determination of primary/subsidiary class. Final precedence is out of scope.

## Assumptions requiring approval

- `test_report` is syntactically checked for a source document SHA-256 and issuer but is **not authenticated**; in untrusted environments this is provisional data only.
- Three terminal repeats with seven hourly values each and one-minute observational evidence are mandatory to issue class-negative or completed PG via the numeric route. This is deliberately conservative fail-closed engineering, not a claim that all ADR-compliant reports must use the identical JSON format.
- The N.5 §33.5.4.3.5 **100–250 ml** target is treated as a strict tested-run data check for positive gas yields; assess atypical scientifically valid tests separately.
- `pg_I_absence_documented` and `pg_II_absence_documented` booleans are documentary attestations, NOT proof by themselves. Require source-authenticated negative evidence under Lead policy before accepting downstream PG.
- Documenting `reacts_vigorously_at_ambient` plus `general_spontaneous_ignition_tendency` is a PG I alternative, independent of minute volume, but the current implementation requires a confirmed flammable gas at >1 L/kg/h for that **numeric** branch when there is no recorded ignition. A historical vigorous/ignition tendency with conflicting/current low rates must go to expert review rather than forced PG; revise after legal sign-off.
- Earlier test fixtures are synthetic, sometimes physically simplified; do not use them as laboratory benchmark evidence.

## Blocking questions

1. Settle **ADR 2.2.43.1.3** ("shall not" apply method to pyrophoric) vs **UN MTC §33.5.3.1** (nitrogen-atmosphere pyrophoric procedure). Module blocks both, requires Class 4.2 and authority review.
2. Adopt and version one canonical Lead schema between PRs **#6** and **#8**; add adapter with class-evidence provenance, prohibited carriage status and named-entry/authority gates.
3. Independently check ADR 2025 English **Corr.1/Corr.2** for any effect; check MTC Amendment 1. Source local digests registered, not official authenticity attestations.
4. Independently verify every clause, all Table A Class4.3 named/generic entries, classification code and PG row, special provisions, carriage acceptance and organometallic/mixture cross-refs.
5. Execute and review Node `node --test agents/class43_water_reactive/classify.test.js` in trusted CI, then add laboratory-provenance-backed golden cases and contradictions.
6. Review if added subsidiary candidate evidence should use directly linked class findings or new reference IDs, and ensure unresolved Class4.3 candidate never triggers final UN/PG before complete screens.
7. Determine admissibility of actual negative test for a named material under 2.2.43.1.7 and handling of non-standard but authoritative tests.

## Recommended next actions

Lead Agent 0: review contract adapter and blocked statuses; Agent 4: match exact Table A rows/SPs/packing groups and control UN3133; Class 4.2/organometallic specialists: handle pyrophoric and N.1–N.5 chart; precedence agent: resolve Class3/4.1/4.2/5.1/6.1/8 flags; regulatory reviewer: initial clause-by-clause sign-off and source-corrigenda report; CI owner: run tests and independently verify boundary fixtures. **No production release until all are approved.**
