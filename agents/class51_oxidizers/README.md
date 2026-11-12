# Agent 7 — ADR 2025 Class 5.1 oxidizing substances

**DRAFT, NOT REGULATORY VALIDATED.** Isolated Agent 7 ownership: \`agents/class51_oxidizers/**\`. Branch \`agent7/adr2025-class51-oxidizers\`. Do not merge or enable for transport/SDS assignment until independent approval.

## Regulatory sources and exact edition

- **ADR 2025 English**, ECE/TRANS/352, Volume I, Chapter **2.2.51**, §§2.2.51.1.1–2.2.51.1.10, 2.2.51.2.1–2.2.51.2.2, 2.2.51.3, with Ch. 2.1 (classification/mixtures/precedence) and Chs. 3.2/3.3 as external dependencies.
- **UN Manual of Tests and Criteria, Rev.8**, ST/SG/AC.10/11/Rev.8, Part III §§34.1–34.4.1 (O.1), 34.4.2 (O.2), 34.4.3 (O.3), §§39.1–39.5.1 (ammonium-nitrate-based fertilizers), plus test series 2 and S.1 as specialized dependencies.
- **Rev.8/Amend.1** supplied; no direct Section 34/39 replacement encoded. Full amendment effect review remains an independent release task.
- **ADR 2025 Corr.1 and Corr.2 not independently reconciled**; Table A and all special provisions not yet joined or approved.

Uploaded-source SHA-256 fingerprints:

| Source | SHA-256 |
| --- | --- |
| ADR ECE/TRANS/352 Vol. I | \`abb98cdaeadc2cbda6642e5123e38635a2ab23cd610776fb375fe8c76a130f65\` |
| ADR ECE/TRANS/352 Vol. II | \`702d0ae5737d3bd228e0b332352deda626018ac9841339c0eca67e4209953f4b\` |
| MTC Rev.8 | \`d892df851727dd1cd06cf87ff02811f5b66e1f2133524e51a7c9873e65c6d533\` |
| MTC Rev.8/Amend.1 | \`534abc4b5ecdd56d615e0fa16fb38bccfc580129772f71443a2a2c892188a0db\` |

Official editions are available through the UNECE ADR and Tests and Criteria pages. This repository stores **rule paraphrases only**, not redistributed regulatory text.

## Files

- \`classify.js\`: pure deterministic candidate evaluator, fail-closed exceptions and normalized Lead-style output.
- \`rule_register.json\`: 37 individually referenced provisional rules, 28 evidence-field requirements, reference materials, method conditions and required downstream checks.
- \`exceptions.json\`: 39 prohibited, special, incomplete and unsupported pathways.
- \`classify.test.js\`: 25 synthetic test groups with boundary, contradiction, mixture, fertilizer and missing-evidence cases.
- \`test_results.json\`: execution scope and 25/25 passing V8 fixture results, **not** independent Node/CI/regulatory validation.
- \`HANDOVER.md\`: Lead Agent integration and review instructions.

## Entry point

\`\`\`js
const {evaluateClass51}=require("./agents/class51_oxidizers/classify.js");
const finding=evaluateClass51(input);
\`\`\`

When Node is available:

\`\`\`sh
node --test agents/class51_oxidizers/classify.test.js
\`\`\`

No third-party package is required.

## Output contract

\`evaluateClass51\` returns the Lead draft contract's class-scoped scaffolding:
\`schema_version\`, \`assessment_id\`, \`regime\`, \`edition\`, \`class\`, \`rule_id\`, \`status\`, \`primary_class_candidates\`, \`subsidiary_risks\`, \`packing_group_candidates\`, \`exclusions\`, \`unresolved_evidence\`, \`expert_decisions\`, \`table_a_candidates\`, \`special_provision_outcomes\`, \`evidence_refs\`, \`clause_refs\`, \`assignment_permitted\`, \`requires_independent_review\`; also includes \`specialistStatus\`, \`pgCandidate\`, \`issues\`, \`missingEvidence\` for Agent 7 diagnostics.

Normalized \`status\` values: \`criteria_met\`, \`criteria_not_met\`, \`indeterminate\`, \`conflict\`, \`unsupported\`, \`authority_required\`, \`prohibited_for_carriage\`. Class-5.1 numerical **PG candidates are never Table A final PG**. \`assignment_permitted\` is always \`false\` and \`requires_independent_review\` always \`true\`. These fields are an interoperability *proposal* requiring Lead schema validation, not certification of compatibility.

\`criteria_not_met\` means only that the specified Class 5.1 test/Section 39 route has failed on fully provided evidence; other classes, named entries, admixtures and carriage exemptions remain open. Absent input never becomes a negative finding. Explicit CLP/GHS shortcuts are rejected.

## Method-specific evidence

**O.1 solid (MTC 34.4.1).** Require five valid burning-time trials, sample/cellulose ratios 4:1 and 1:1 by mass and three method-matched KBrO3/cellulose references 3:2, 2:3, 3:7. Require recorded particle distribution, validated preparation, dry reference materials, repeatability and conditions via attested test report. Lower sample mean time means greater hazard. PG I: **strictly less** than 3:2; PG II/III: **less than or equal** to 2:3/3:7 respectively. Any ignition/burning that triggers ADR 2.2.51.1.6(a) but gives no PG comparison escalates; it is not made negative.

**O.3 solid (MTC 34.4.3).** Require five valid gravimetric burning-rate trials, 4:1 and 1:1 samples and calcium-peroxide/cellulose references 3:1, 1:1, 1:2. CaO2 reference purity 75 ±1.0%; 20–80% mass-loss profile, R² ≥0.90 per run and five-run rate dispersion ≤20% (as lab-attested %). Higher sample mean rate means greater hazard. PG I: **strictly greater** than 3:1; PG II/III: **greater than or equal** to 1:1/1:2 respectively. Suspected false positives or trace-shape anomalies require additional expert review.

**O.2 liquid (MTC 34.4.2).** Record spontaneous ignition; if none, obtain peak pressure rise in **kPa gauge**, and five times measuring the pressure-rise interval **690 to 2070 kPa gauge** for sample and each 1:1 cellulose reference (50% perchloric acid, 40% aqueous sodium chlorate, 65% aqueous nitric acid). 2070 kPa **inclusive** is the pressure gate. PG I if spontaneous ignition or mean pressure-rise time is **strictly less** than the perchloric-acid comparator; PG II/III use **less-than-or-equal** chlorate/nitric-acid comparators.

**Solid ammonium-nitrate-based fertilizers:** MTC §39 exclusively; Section 34 O.1/O.3 tests must not declassify them. Require audited Figure 39.1 **terminal** exit box, composition/compatibility review and report ID. Validate box-to-outcome mapping and enforce ADR §2.2.51.2.2 forbidden/authority exception lists. Potential UN 2067 route also requires Series 2 negative explosive properties. No composition-to-flowchart algorithm or Table A assignment is inferred.

For all pathways, \`protocolConformant\`, \`referencesConformant\`, \`testConditionsConformant\`, \`sampleRepresentative\` and \`uncertaintyResolved\` are required lab **attestations**. They do not replace reviewing original raw data, particle-size and humidity records, calibration records, sample composition, evidence authenticity and named-entry conditions. See \`rule_register.json\`.

## Safety and limits

A positive test only yields a hazard candidate. Final class precedence, primary/subsidiary decision, PG, Table A row, naming, special provisions, packaging, competent-authority records and SDS Section 14 output all remain external. Section 39 audited outcome evidence is **not authenticated** in this module. No independent release signoff. See \`HANDOVER.md\` for exact blockers.
