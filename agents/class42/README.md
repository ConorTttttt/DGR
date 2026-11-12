# Agent 5 — ADR 2025 Class 4.2 (provisional)

**Scope:** substances liable to spontaneous combustion, including pyrophoric solids, pyrophoric liquids and self-heating substances. **Status:** independent regulatory review pending; not production-ready. No final transport classification, UN number, packing group or SDS Section 14 wording is produced.

All files are confined to \`agents/class42/\`. The branch was created from \`main\`; the module has not changed the Lead Agent contracts or other agents' paths.

## Regulatory basis

* **ADR 2025**, ECE/TRANS/352, Vol. I (English), §2.2.42.1.1–.1.8, §2.2.42.2, §2.2.42.3, §2.3.5, §2.1.3, and Chapters 3.2/3.3. Supplied printed Class 4.2 pp. 161–164.
* **UN Manual of Tests and Criteria Rev.8**, ST/SG/AC.10/11/Rev.8, Part III §33.4.1–33.4.6 (printed pp. 376–382); N.2 (§33.4.4), N.3 (§33.4.5), N.4 (§33.4.6).
* **Rev.8 Amendment 1**, supplied; a text search found no §33.4/N.2–N.4 amendment, but independent official comparison is outstanding.
* Exact SHA-256 values, edition IDs and open corrigenda items in \`sources.json\`. ADR Vol. II dependencies, Table A, Chapter 3.3 and SP conditions need separate integration. No unverified thresholds or CLP/GHS mapping.

## Files and interface

* \`class42.js\`: \`evaluateClass42(evidence)\`, pure deterministic class-scoped evaluator; no file/network access.
* \`rules.json\`: 36 exact-clause obligations, implementation status and source/edition.
* \`evidence.schema.json\`: JSON Schema 2020-12 and field units.
* \`class42.test.js\`: 59 synthetic tests covering strict/inclusive boundaries, positive, negative, missing evidence, conflicts, forbidden entries and competing classes.
* \`exceptions.json\`: 28 unsupported, uncertain, conflict, prohibition and handoff cases.
* \`test_results.json\`: transparent execution environment and results, without independent compliance claim.
* \`HANDOVER.md\`: Lead Agent review matrix, limitations, merger checklist.

The response follows the draft Lead v1.0.0-rc1 key names: \`schema_version\`, \`assessment_id\`, \`regime\`, \`edition\`, \`class\`, \`rule_id\`, \`status\`, \`primary_class_candidates\`, \`subsidiary_risks\`, \`packing_group_candidates\`, \`exclusions\`, \`unresolved_evidence\`, \`expert_decisions\`, \`table_a_candidates\`, \`special_provision_outcomes\`, \`evidence_refs\`, \`clause_refs\`, \`assignment_permitted=false\`, and \`requires_independent_review=true\`. This contract is awaiting Lead acceptance, not merged into main. Null \`final_un_number\` and \`final_packing_group\` are invariant.

## Evidence acquisition and method requirements

**Shared:** \`assessment_id\`, \`evidence_id\`, \`report_id\`, \`sample_id\`, \`pathway\`, physical state, sample form (where method-specific), \`is_mixture\`, tested formulation/grade/diluent matching the commercial form and consignment, authenticated scope of signed report, instrument/method conformance, and explicit UN MTC test identity. Report fields are evidence *claims* and must be independently authenticated upstream. \`report_scope_verified=true\` and \`protocol_conformant=true\` do not themselves authenticate a report.

**N.2 solids:** §33.4.4.3–.4: powdery material, 1–2 mL, poured from about 1 m onto a non-combustible surface, up to **six** runs. Ignition during falling or in **≤300 seconds** in any valid run -> Class 4.2, **PG I candidate** (ADR §2.2.42.1.5(a), §2.2.42.1.8(a)). Negative only after six complete 5-minute non-ignitions. Actual drop height ~1 m is an attested source-method conformance criterion, not a fabricated numerical tolerance.

**N.3 liquids:** §33.4.5.2–.4: stage one ~5 mL poured into a ~100 mm porcelain cup with ~5 mm diatomaceous earth/silica gel at room temperature. Run up to **six** times; any ignition within **≤300 s** => PG I candidate. If all six negative, stage two uses **0.5 mL** on fresh dry indented small-pore filter paper (ADR §2.2.42.1.5(b)(ii) explicitly refers to Whatman No. 3), **25±2°C** and **RH 50±5%**. Up to **three** runs; any ignition or charring within **≤300 s** => PG I candidate. The code validates stage order, 23–27°C and 45–55% RH; actual carrier/cup/filter quantity and material conformance are externally attested, and unverified test documentation must not populate true booleans.

**N.4 self-heating:** §33.4.6.1–.4: commercial-form powder or granules in open-top **25 or 100 mm** stainless-steel mesh sample cube (0.05 mm openings), circulating oven **100, 120 or 140°C ±2°C**, measured sample thermocouple (0.3 mm Chromel-Alumel), continuous records for **24 h**. Additional cover/cage construction from §33.4.6.2 must be independently verified. Positive on spontaneous ignition or actual sample temperature **strictly greater than oven temperature +60°C** within 24 h. The nominal ADR thresholds are strictly **>200°C at 140**, **>180°C at 120**, **>160°C at 100**. If the actual-oven comparison and nominal ADR interpretation disagree, the evaluator deliberately returns \`conflict\`, not a rounded answer.

### Self-heating outcomes and packaging

| N.4 evidence | Individual proposed package | Class-scoped outcome |
| --- | --- | --- |
| 100 mm at 140°C **negative** | Any | \`criteria_not_met\` for N.4 self-heating pathway |
| 25 mm at 140°C **positive** | Any (100 mm test not required under MTC footnote) | \`criteria_met\`, PG **II candidate** |
| 100 mm at 140°C positive, 25 mm negative; 100 mm at 120°C **negative** | ≤3,000 L | \`excluded_from_class\` for this packaging |
| 100 mm at 140°C positive, 25 mm negative; 100 mm at 100°C **negative** | ≤450 L | \`excluded_from_class\` for this packaging |
| 100 mm at 140°C positive, 25 mm negative; 100 mm at 100°C positive | ≤450 L | \`criteria_met\`, PG **III candidate** |
| 100 mm at 140°C positive, 25 mm negative; 100 mm at 120°C positive | >450 L to ≤3,000 L | \`criteria_met\`, PG **III candidate** |
| 100 mm at 140°C positive, 25 mm negative | >3,000 L | \`criteria_met\`, PG **III candidate** |
| 100 mm at 140°C positive, 25 mm negative; volume or required lower-temp test missing | Dependent | \`indeterminate\`, not a negative |

Sources: ADR §2.2.42.1.5(c), Notes 1–2, §2.2.42.1.8(b)–(c); MTC §33.4.6.4.2–.4.4. The special >50°C large-volume spontaneous-combustion temperature exclusions (27 m³ general and 450 L for PG II) are **not** computed from small-cube data: referral to an independent expert is required. Article-specific, non-powder and impracticable-test pathways are unsupported.

## Missingness and evidence status

* \`criteria_met\`: verified positive test **candidate only**, not assignment. A PG value is always provisional.
* \`criteria_not_met\`: complete negative for the **selected method/pathway only**; test other potentially applicable classes and the remaining 4.2 branches.
* \`excluded_from_class\`: documented N.4 volume-specific exemption; new formulation/package means reassessment.
* \`indeterminate\`: missing report, method, physical state, test runs, volumes, negative observation length, required threshold measurements or named-entry review.
* \`conflict\`: incompatible records, actual-vs-nominal temperature disagreement, more stringent experience versus lenient screening, or physically inverted N.4 results.
* \`unsupported\`: N.2 solid lumps, N.4 unusual forms/articles, nonrepresentative material.
* \`prohibited_for_carriage\`: verified UN 3255; or UN 3127 self-heating oxidizing solid when Class 1 exception explicitly fails. The potential Class 1 exception is \`authority_required\`.
* \`authority_required\`: unresolved §2.1.3.7 Class 1 exception.

No test evidence is inferred from CLP/GHS labels or an SDS statement. No absence of evidence is interpreted as non-dangerous. The code **does not authenticate** attestations or raw data.

## Cross-class and downstream handoffs

Report separately verified competitors in \`competing_evidence\` (Classes **1, 3, 4.1, 4.3, 5.1, 6.1, 8**). These are unresolved **candidates**, never final subsidiary labels. In particular **4.1/4.3/5.1** precedence is the cross-class Agent's decision under ADR §2.1.3.10. The ADR §2.3.5 **organometallic** flowchart also refers N.1/N.5 and 4.3 (and Class 3 if no pyrophoric/water-reactive hazard). Class 4.2 collective codes S1–S6, SW1/2, SO, ST1–ST4, SC1–SC4 and §2.2.42.3 cannot be turned directly into final UN assignments. Exact named entry, Chapter 3.2 Table A column (4) PG, Chapter 3.3 SP, and applicable packaging/carriage requirements require a separate integrator.

## Reproduce and release conditions

Node >=18: \`node --test agents/class42/class42.test.js\` from repository root. Submitted tests were **run synthetically in the available V8 JavaScript harness**; actual Node CLI, GitHub CI, JSON-Schema validation, external-source comparison, and real-world benchmark validations have **not** been performed here. See \`test_results.json\`.

**No independent regulatory approval has been obtained. Do not merge or enable for live SDS Section 14 decisions until the Lead Agent's schema adapter, named-entry/SP integration, source corrigenda comparison, test-report attestation, regulatory reviewer signoff and release checklist are complete.**
