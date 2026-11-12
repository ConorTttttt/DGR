# Agent 7 to Lead Agent — ADR 2025 Class 5.1 handover

**Handover date:** 2026-11-12  
**Branch:** \`agent7/adr2025-class51-oxidizers\`  
**Owned directory:** \`agents/class51_oxidizers/**\` (no other agent files changed)  
**Regulatory state:** **PROVISIONAL — unreviewed, draft only, not approved for real SDS Section 14**  
**Edition pinned:** ADR 2025 English ECE/TRANS/352 Vol. I; MTC ST/SG/AC.10/11/Rev.8, Part III Sections 34 and 39; supplied Rev.8/Amend.1 inspected for relevance.

## Delivery manifest

| Item | Artifact | Present status |
|---|---|---|
| Legal clause and rule register | \`rule_register.json\` | 37 provisional ADR/MTC rules, source/edition keys |
| Deterministic evaluation | \`classify.js\` | Method-specific threshold and exception gates |
| Evidence and reference metadata | \`rule_register.json\` | 28 typed/conditional fields, measurement units, manuals, trial conditions |
| PG logic | \`classify.js\` | O.1/O.2/O.3 **candidates only**, reference-comparator strictness preserved |
| Unsupported/prohibited register | \`exceptions.json\` | 39 cases plus explicit implementation boundaries |
| Test suite | \`classify.test.js\` | 24 independent synthetic test blocks with multiple subcases |
| Results | \`test_results.json\` | 24/24 blocks passed in V8 compatibility harness, zero failures |
| Contributor/API explanation | \`README.md\` | Usage, provenance, source hashes and blockers |
| Lead handover | this file | Review and integration requirements |

The tests were run using a V8 execution environment against **GitHub-fetched exact source and test file**, with a compatibility shim for Node \`node:test\` and \`node:assert/strict\`. **Node CLI, GitHub Actions CI, real laboratory samples, regulatory accreditation and independent review have not been executed.**

## Scientific and regulatory decision mechanics

### Ordinary solids — ADR 2.2.51.1.6–1.8; MTC 34.4.1 and 34.4.3

Two alternative methods, NOT interchangeable numerical scales:

- **O.1:** burning *times* with potassium bromate/cellulose reference standards 3:2, 2:3, 3:7. Test sample to cellulose **4:1 OR 1:1** controls the classification. PG I when sample mean time is **strictly shorter** than PG I reference; PG II/III when **equal or shorter** than the corresponding reference, after excluding stronger PG. A pure ignition/burning positive without matching numerical PG is a class candidate with **blocked PG/expert review**.
- **O.3:** gravimetric burning *rates* with calcium peroxide/cellulose reference standards 3:1, 1:1, 1:2. PG I requires **strictly higher** than PG I reference; PG II/III require **equal or higher** than respective reference after excluding stronger PG. Require verified five-run traces, regression R² ≥0.90, method-defined 20–80% mass loss, and ≤20% rate dispersion. Reference CaO2 must meet MTC purity and size specifications.

Both sample ratios and three reference standards are demanded for a complete PG candidate, conservatively. For O.1, no-ignition evidence may use certified five non-ignitions rather than invented numeric times. Negative only means that this specific oxidizer method's criteria do not hold; it is **not** a global ADR clearance or entry override.

### Ordinary liquids — ADR 2.2.51.1.9–1.10; MTC 34.4.2

O.2 only. Require 1:1 cellulose mixture, five-run pressure-rise data from **690 to 2070 kPa gauge**, documented sample concentration and reference runs with 50% perchloric acid, 40% aqueous sodium chlorate and 65% aqueous nitric acid. At **2070 kPa gauge exactly**, the pressure gate is satisfied; less than that is a method-limited negative. Without spontaneous ignition, PG I is sample mean pressure time **strictly less** than perchloric standard; PG II and III use **less or equal** chlorate and nitric acid comparators. Verified spontaneous ignition is PG I route without artificial pressure data.

### Ammonium-nitrate-based solid fertilizers — ADR 2.2.51.1.7; 2.2.51.2.2; MTC 39

**Do not** reuse O.1/O.3 for fertilizers. Require composition/compatibility analysis, audited terminal exit box from **Figure 39.1(a)-(c)**, record identifier, and prior Class 1 screening. Valid terminal outcomes are constrained:
- Potential Class 5.1/UN2067 dependency: exit boxes **9, 18, 19, 36, 42**, plus no-explosive-properties Series 2 report under MTC 39.4.2.
- Class 9 candidate: exit **25**, requiring S.1 trough test per 38.2.4 and specialist handoff.
- Flowchart not classified: exits **26, 35, 43, 44, 45** (does not clear other hazard classes).
- ADR prohibited pending Class 1 route: **4, 6, 8, 15, 31, 33**.
- ADR prohibited unless Class 1 or demonstrated/competent-authority-approved alternative Class 5.1 (not UN2067): **20, 23, 39**.

Node IDs that are *connector or decisions*, such as **10 and 27**, must never be treated as terminal exits. The module verifies terminal/outcome consistency, but **does not** compute a complete Figure 39.1 decision path from quantitative compositions; full path validation and authentic approval remain delegated to expert workflow. Section 39.4.4 directs certain compositions to Class 1 even if Series 2 testing is negative. Fertilizer PG is **never inferred** from O.1/O.3.

### Prohibitions and competing hazards

ADR 2.2.51.2.1 chemically unstable material gate; ADR 2.2.51.2.2 separate checks for specific oxidizer/formulation bans: hydrogen peroxide, tetranitromethane, concentrated perchloric/chloric acids, restricted halogenated fluor compounds, ammonium chlorate/chlorite/bromate/permanganate/nitrite salt combinations, ammonium nitrate containing **>0.2%** combustibles, potassium-nitrate/sodium-nitrite/ammonium-salt mixtures, and combined oxidizing-solid/flammable/self-heating/water-reactive pathways OF/OS/OW. The Class 1 exception, if relevant, is **not granted by Agent 7**.

Separate subsidiary hazard candidates for classes **4.1, 4.2, 4.3, 6.1, 8**; do not use the hazard-precedence table locally. For OC/OT/OTC coding, the Lead must resolve Table A entry selection and ADR 2.1.3.10; the OTC class code lacks a direct generic collective entry under ADR 2.2.51.3.

## Proposed Lead integration adapter

The evaluator exposes the Lead v1 candidate structure as best-effort:
- \`schema_version\`, \`assessment_id\`, \`regime\`, \`edition\`, \`class\`, \`rule_id\`, \`status\`;
- \`primary_class_candidates\`, \`subsidiary_risks\`, \`packing_group_candidates\`;
- \`exclusions\`, \`unresolved_evidence\`, \`expert_decisions\`;
- \`table_a_candidates\`, \`special_provision_outcomes\`, \`evidence_refs\`, \`clause_refs\`;
- \`assignment_permitted=false\`, \`requires_independent_review=true\`.

Status normalization matches candidate modes \`criteria_met\`/\`criteria_not_met\` and blocker modes \`indeterminate\`, \`authority_required\`, \`conflict\`, \`unsupported\`, \`prohibited_for_carriage\`. The original diagnostic state remains in \`specialistStatus\` and reason IDs in \`issues\`. \`assessment_id\` may be null when the caller has not supplied one; the Lead adapter must require a valid value and persistent evidence IDs. The schema has not been run through the Lead's canonical JSON Schema verifier; **do not claim canonical validation**.

Lead responsibilities before moving this out of draft:

1. Confirm the actual canonical schema version, rule identifier and evidence-ref formats. Normalize multi-clause references and \`assessment_id\`; validate all outputs against canonical JSON Schema and signed evidence.
2. Join 2.2.51.3 classifications to **official** Chapter 3.2 Table A **row IDs**, UN numbers/PSNs, row-specific PG column (4), and all column (6) special provisions. In particular, neither a named oxidizer nor UN 2067 may be silently selected from a positive laboratory threshold.
3. Resolve Part 2 **2.1.3 mixture provisions, conflicting hazard precedence** and subsidiary class outcomes. Separate class not met from global ADR applicability and exemptions.
4. Cross-check exact Class 1 requirements (including MTC test series 2 and explosive-property screening), organic peroxide Class 5.2 routing, solid oxidizer Class 4 overlap, and fertiliser Class 9 route.
5. Implement a **trusted authority-decision registry** (country of origin/first ADR contracting country, signed decisions, expiry/conditions, applicability to actual consignment, suitability-for-carriage evidence). Boolean flags in synthetic fixtures do not authenticate approvals.
6. Verify sample identity, mixture formulation, particle distribution and coating/grinding, raw trials, apparatus, cellulose moisture, reference purity/concentration, temperature and humidity, calibration, O.2 unexpected pressure mechanism, O.3 false positives and known-experience discrepancies against original laboratory evidence.
7. Validate **all Section 39 flowchart paths** against measured composition and incompatible material list (not just supplied terminal box); check the 39.4.6 ammonium sulphate exception and any Class 9 S.1 reports.
8. Independently inspect English ADR 2025 Corr.1/Corr.2, all applicable MTC Amend.1 changes and any subsequent authenticated revisions; record change-control dispositions by rule.
9. Run a real \`node --test\` suite and repository CI with additional independently curated, physically plausible golden cases; test dangerous negative claims, inconsistent authority approvals, valid/invalid signed evidence, named entries, Table A missing/multiple rows and SP uncertainty.
10. Obtain independent regulatory, legal, security and QA approval in the Lead release checklist. Until then the PR stays **draft**, and no production transport classification or Section 14 publication.

## Known limitations and review questions

- Whether the conservative choice to require *all three* standard reference sets in O.1/O.2/O.3 should be replaced with a progressive reference sequence exactly following each manual's test decision process, while maintaining fail-closed partial-data behaviour.
- Interpretation of the O.3 laboratory expression “standard deviation ... should not exceed 20% in total”: this implementation requires attested relative standard deviation ≤20%; validate independent laboratory calculation formula and repeatability test.
- Quantitative uncertainty treatment, rounding at exact PG/pressure boundaries and calibrated instrument tolerance must be independently decided; the program never manufactures uncertainty intervals or reference constants.
- Report-level compliance flags, including \`uncertaintyResolved\`, are **not** instrument/raw-data verification and must be checked in a trusted pipeline.
- Some mixtures, named entries, specialized industrial articles, untestable substances, oxidizers that are also combustible/organic peroxide and formulations needing inert controls remain outside the executable route.
- The \`isHalogenatedFluorCompound\` named-UN allowlist is a **prohibition-filter dependency only**, not a positive Class 5.1 assignment or endorsement of the Class 2 named entries.
- Prohibition identity ontology is not exhaustive; users must supply verified compositional identity or go through expert review. Never infer a missing flag means false.
- Normalized statuses are a best-effort proposal; additional canonical mapping/schema validation is required.
- The test suite uses synthetic values not from chemical substances and is **not** evidence of actual regulatory performance.

## Release checklist (all must be checked by independent reviewers)

- [ ] Correct file ownership and Lead contract/schema approval.
- [ ] ADR 2025 Clauses/figures/Table A/SPs and official Corr.1/Corr.2 reconciled.
- [ ] MTC Rev.8/Amend.1 methods, references, raw data conditions and Section39 flow paths independently checked.
- [ ] Signed authority decisions verified and Class1/Class9 referrals covered.
- [ ] Validated numeric rounding, comparators, particle size, humidity and calibration provenance.
- [ ] Real Node/CI pass and independent golden-case dataset.
- [ ] End-to-end multi-hazard/mixture/entry/SP integration pass.
- [ ] Independent regulatory/QA/security signoff recorded before production release.

**Decision requested from Lead:** accept as *provisional draft module* for architectural review only, or request changes. No regulatory approval is implied by accepting the contribution.
