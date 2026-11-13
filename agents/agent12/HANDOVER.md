# Agent 12 — ADR 2025 Class 8 handover to Lead Agent

**STATUS: PROVISIONAL — NOT INDEPENDENTLY VALIDATED. No safety-critical SDS Section 14 classification is authorised.**

## Ownership and integration

Audit baseline: ConorTttttt/DGR draft PR #2, Agent 3 file agents/agent3/adr2025/class8.py, source blob 630d07742ac3fc1fa5bff3adee77c24628c674b0. This branch is based on agent3/adr2025-classification-rules and changes ONLY agents/agent12. Agent 3 and the Lead control the original path, schema and integration. No other agent's files were modified. The module is a self-contained, proposed alternative implementation requiring explicit Lead authorisation to integrate.

## Regulatory clause register (English)

1. ADR 2025 ECE/TRANS/352 Vol. I §§2.2.8.1.1–.3: corrosive skin and goods/vehicle damage, water-activated corrosive liquids/vapour/mist, and metal corrosion for liquids or solids which become liquid in carriage.
2. ADR §§2.2.8.1.4.1–.4.4: classification codes, degree-of-danger PG, existing Table A allocations, tests for new substances and step-wise alternatives for mixtures. A calculated PG IS NOT a verified Table A PG.
3. ADR §2.2.8.1.4.5 and §2.2.61.1.7.2: defined Class 8 versus inhalation-toxicity overlap (further precedence to Agent 2).
4. ADR §§2.2.8.1.5.1–.2: primary existing human and animal data, accidental human exposure, OECD 404 (2015), 435 (2015), 431 (2016), 430 (2015), and non-classified OECD 439 (2015); fallback when test cannot discriminate packing groups.
5. ADR §2.2.8.1.5.3(a), Table 2.2.8.1.5.3: PG I irreversible skin damage with exposure <=3 minutes, observation <=60 minutes.
6. ADR §2.2.8.1.5.3(b): PG II exposure >3 to <=60 minutes, observation <=14 days (20,160 minutes).
7. ADR §2.2.8.1.5.3(c)(i): PG III exposure >60 to <=240 minutes, observation <=14 days.
8. ADR §2.2.8.1.5.3(c)(ii) and NOTE: PG III if steel OR aluminium test rate >6.25 mm/year at 55°C, both eligible metals evaluated for fully negative evidence; a qualifying positive initial test eliminates need for the second.
9. ADR §2.2.8.1.6.1 and Figure 2.2.8.1.6.1: whole-mixture testing, then similar-mixture bridging, then constituent method.
10. ADR §2.2.8.1.6.2(a)–(e): dilution with non-corrosive compatible diluent, equivalent production batching, concentration of tested PG I mixture, interpolation, and substantially similar mixtures.
11. ADR §§2.2.8.1.6.3.1–.5 and Figure 2.2.8.1.6.3: skin mixture 1% PG-I gate and 5% branch thresholds, relevant ingredients below 1%, synergy restriction for PG II and III, SCL weighted-calculation override where Table A/special provisions assign them.
12. ADR §§2.2.8.1.7–.8 and 2.1.3: changes to named mixtures and potentially non-subject mixtures require entry-specific review.
13. ADR §§2.2.8.2.1–.2: carriage restrictions including unstable Class 8 substances, UN 1798 and specified unstable acid mixtures; these checks are OUTSIDE the evaluator.
14. UN Manual of Tests and Criteria, Rev. 8 (2023), ST/SG/AC.10/11/Rev.8, Part III §§37.1–37.4, Test C.1 §§37.4.1.2–37.4.1.4, Tables 37.4.1.1/37.4.1.2. 2 mm steel/aluminium plates, >=3 specimen sets, full/half/vapour specimens, >=1.5 l medium, 55 +/-1°C throughout, laboratory-controlled preparation and durations. For 7/14/21/28 days, uniform mass-loss positives only above 13.5/26.5/39.2/51.5%; local intrusion positives only above 120/240/360/480 micrometres. Alternate metal materials only the ADR-specified steel/aluminium grades.
15. UN Manual Rev. 8 Amendment 1, ST/SG/AC.10/11/Rev.8/Amend.1: English §37.4.1.3 and §37.4.1.4.1 unchanged (the listed amendment is Spanish-only).

## Audit findings in draft PR #2

- Bare skin corrosion result and durations could produce a packing group without OECD study ID, method or validity metadata.
- Boolean non-discriminating tier flags were not adequately anchored to eligible study results.
- Metal rates were accepted without demonstrating Test C.1, 55 +/-1°C, permitted metal grades, full/half/vapour setup, material volume, or localised corrosion assessment. This particularly affects negative metal conclusions.
- No mixture bridging or generic skin mixture concentration calculation was implemented; human/animal disagreement was not represented.
- Table A PG and property-derived PG must be separated, with distinct class/entry/precedence outputs.

## Implemented pathways

The standalone evaluator returns status criteria_met, criteria_not_met, or indeterminate. A calculated_packing_group/candidate_packing_group is always separate from dgl_packing_group=null and dgl_entry=null; no result is a final transport finding.

- Structured human evidence and human/animal disagreement gating.
- Qualified OECD 404 exposure/observation cutoffs, OECD 439 non-corrosive support and the two documented non-discriminating fallbacks.
- Metal C.1 rate, mass loss and local intrusion test thresholds; one-positive/two-negative metal logic; mandatory C.1 report/protocol fields.
- Five conditional mixture bridging principles with tested-source evidence IDs and condition-specific attestations.
- Generic untested-mixture calculation: PG I sum >=5% -> I; otherwise PG I sum >=1%, or PG I+II >=5%, -> II; otherwise sum PG I+II+III >=5% -> III. Other outcomes are scoped negative/indeterminate, never overall transport exclusion.
- Guards for absence of human review, missing study detail, sub-1% relevance, missing composition/SCL lookup, synergistic mixtures, conflicting reports and invalid measurement units.

## Tests and reproducibility

The exact-source Python implementation and exact-source test file were locally verified against matching Git blob hashes on the Agent 12 branch. 18 unittest methods passed, with numerous subtests for 3/60/240-minute skin thresholds, 14-day observation limits, 6.25 mm/year metal rate, local and uniform corrosion, 54/56°C, C.1 inputs, five bridging scenarios, mixture 1%/5% edges, human-animal disagreements and missing data. Python compilation passed. No remote CI, external benchmarks, laboratory evidence audits or independent regulatory QA have been performed.

## Unsupported-case and exception register / blockers

1. SCL mixture calculations: ADR §§2.2.8.1.6.3.4–.5 override generic thresholds and require a weighted specific-limit calculation. All such cases BLOCK (indeterminate) until Agent 1 provides authoritative DGL/special-provision limit sources and the Lead approves the combined PG 1%/5% interpretation. Do not substitute generic thresholds.
2. Human review: existence of human experience and accidental exposure evidence is an input attestation. Conflicting human/animal grades need qualified adjudication; the evaluator does not infer a PG from generic GHS category labels.
3. Test C.1: protocol_confirmed and other attestation flags must be backed by a qualified laboratory report. The code checks major metadata, but does not independently verify all procedural steps such as cleaning, separate receptacles, specimen weighing, and chemical stability; these are release blockers.
4. Solids: the metal branch presently does not require affirmative evidence that a solid can become liquid in carriage. This scope check must be inserted before production use.
5. Bridging: source PG, same-mixture identity, concentrations and lack of enhanced corrosion must be checked against source study records, not accepted solely from booleans. Synergistic interaction blocks generic PG II/III and negative mixture results.
6. Other Class 8 pathways: wet-air corrosive vapours and reactive-to-water corrosion, chemically unstable materials, and prohibited-for-carriage scenarios are not implemented.
7. Named-entry gates: Chapter 3.2 Table A, special provisions Chapter 3.3, exemptions, named mixtures §§2.2.8.1.7–.8, classification code, DGL PG and actual UN selection remain to Lead/Agent 1. No final PG has been assigned.
8. Multiple hazards: candidate hazards Classes 6.1, 3, 4.3, 5.1 and any other subsidiary risks are for Agent 2/precedence; no final combined PG here.
9. Corrigenda and edition: pin ADR 2025 to ECE/TRANS/352; UNECE lists Corr.1 and Corr.2, formal English corrigenda delta check remains outstanding. No claim of regulatory validation.
10. Lead schema and attestation: this temporary interface is NOT a production schema. It needs evidence provenance, versioned input/output, precedence integration, reviewer sign-off and reproducible CI.

## Required Lead Agent actions

Confirm Agent 12 ownership boundaries; review each rule against English ADR 2025 and UN Manual Rev.8, including amendment/corrigenda; approve or amend SCL/mixture exclusions; request Agent 1 Table A/SP and Agent 2 hazard-precedence inputs; approve structured evidence attestations and physical state gate; adapt the self-contained proposal into the Agent 3-owned package only with coordinated approval; run CI and independent expert-labeled benchmark tests; keep PR as draft until approval. Never treat the current code as production-ready.
