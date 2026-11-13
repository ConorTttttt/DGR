# Agent 11 — ADR 2025 Class 7 radioactive material (PROVISIONAL)

**Status:** draft specialist subsystem. NOT independently validated. DO NOT use for unsupervised consignments or SDS Section 14 sign-off.

This is a standalone proposed interface; Lead Agent must approve the shared schema and integration. The implementation NEVER outputs a final UN number, proper shipping name, packing group or an overall "not regulated" conclusion. A packing group is not applicable as a proxy for radioactive classification.

## Files

- class7.py: deterministic classify(data) with dated and unit-tagged evidence, activity-fraction mixtures, strict Class 7 scope gate and provisional fissile/LSA/SCO material assessment.
- radionuclides.json: eight curated examples from Table 2.2.7.2.2.1, NOT the complete radionuclide table; Table 2.2.7.2.2.2 fallback values recorded but not selected without expert review.
- rules.json: 18 machine-readable decision-rule descriptions with clause references, predicates and implementation states.
- regulatory_register.csv: 27 traceable regulatory rows including blocked external references.
- SOURCE_MANIFEST.json: exact editions and associated reference metadata.
- UNSUPPORTED.md: exceptions, inadequate evidence and radiological expert hand-offs.
- HANDOVER.md: delivery, test and outstanding Lead Agent actions.
- tests/test_class7.py and test_results.txt: 30 regression fixtures and local execution result.

## Regulatory boundary

ADR 2025 ECE/TRANS/352 Volume I: 1.7.1.4 (exceptions), 1.7.5 (other hazardous properties), 2.2.7.1.1 (definition requiring BOTH criteria), 2.2.7.1.3 (nuclide and fissile definitions), 2.2.7.2.2.1-2.2.7.2.2.6 (radionuclide limits, notes, mixtures), 2.2.7.2.3 (LSA, SCO, special form, low dispersible and fissile), 2.2.7.2.4 (packages), Table 2.2.7.2.1.1 (UN entry route) and 2.2.7.2.5 (special arrangements). Chapter 3.3 special provisions 290/369 are downstream named-entry dependencies.

ADR 2025 ECE/TRANS/352 Volume II (post-classification only): 4.1.9, 5.1.5, 5.2.2, 6.4 and 7.5.11 CV33. Neither the UN Manual of Tests and Criteria Rev.8 nor its Amendment 1 is a replacement for ADR radioactive thresholds or approval conditions.

## Input / evidence contract (proposed, not Lead-approved)

The entire consignment is a single homogeneous material, with mass excluding shielding. Mandatory top-level flags: complete_radionuclide_inventory=true, single_homogeneous_material=true, mass_excludes_shielding=true, activity_covers_entire_consignment=true, and activity_reference_date in ISO YYYY-MM-DD format.

Require material_mass {value,unit,source_id,measured_on,method}, with positive mass in g or kg, and a nonempty radionuclides array with each {id,activity}. Every activity object must provide {value,unit,source_id,measured_on,method}. Value must be an exact decimal string or integer, NEVER a floating-point input. Units: Bq, kBq, MBq, GBq or TBq. All radionuclide measurements must have the same measured_on and activity_reference_date, otherwise expert-reviewed decay correction must occur upstream.

Other quantities: SCO contamination in Bq/cm2, surface and 1m dose rates in mSv/h or uSv/h, tritium activity concentration in Bq/l or TBq/l, fissile mass in g or kg. A source_id must resolve to a dated and retained radiological assay, calibrated surface survey, weighing record or competent-authority evidence. CLP/GHS classifications and undated SDS labels alone are insufficient. The code still treats user-asserted inventory completeness and certificate flags as unverified claims requiring independent review.

## Output interpretation

- CLASS7_RADIOACTIVE_MATERIAL_CRITERIA_MET: both complete single-material activity concentration and total consignment activity strictly exceed the applicable Table 2.2.7.2.2.1 limits or reciprocal-mixture limits (2.2.7.1.1 and 2.2.7.2.2.4). Even this is not a transport authorization.
- CLASS7_DEFINITION_NOT_MET_FOR_ASSESSED_MATERIAL: one or both of those strict thresholds is not exceeded WITH complete evidence. It is not a "not dangerous goods" conclusion; remaining material and other hazards must be investigated.
- INDETERMINATE: missing, inconsistent or out-of-coverage evidence; no negative inference allowed.

LSA-I/II/III and SCO-I/II are material-characteristic candidates, not approved industrial package type or UN assignments. SCO-III, fissile exceptions 2.2.7.2.3.5(a)-(f), special form and low-dispersible approvals require separate human/competent authority verification. Fissile mass below 0.25 g is at most a provisional definition exclusion if no other fissile material is present in package or unpackaged consignment (2.2.7.1.3).

package_screen includes only post-classification arithmetic: Type A activity ratio, material activity for excepted package Column 4 and single-package TI/category calculation. It NEVER approves a package, verifies its design, resolves a category under special arrangement, evaluates overpack/tank geometry, or assigns a UN number. The special-form certificate input is a claim for numeric screening, not an independently verified authority record.

## Run test suite

Run from repository root:

    python -m unittest discover -s agents/agent11/tests -v

Local development result: 30 tests passed (2026-11-13). Developer testing is not independent regulatory validation. A full nuclide-table/footnote audit, Table A checks, package eligibility, criticality, source-date uncertainty, exemptions, other-hazard precedence and competent-authority approvals remain outstanding.

See HANDOVER.md and UNSUPPORTED.md for the exact blocker register and tasks.
