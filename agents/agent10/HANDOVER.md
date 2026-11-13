# Agent 10 handover to Lead Agent — Class 6.2

**Handover state:** DRAFT. Not independently validated, not approved for operational SDS Section 14 assignment.

## Deliverables
`class62.mjs`: deterministic, side-effect-free decision function; `class62.test.mjs`: 77 table-driven regression cases; `regulatory_register.csv`: requirements with exact references; `decision_rules.json`: machine-readable rules and priority; `special_entry_dependencies.json`: checked Table A fields for five Class 6.2 UN candidates; `indicative_category_a.json`: indicative list with culture-only and diagnostic exception flags; `unsupported_cases.csv`: handoff blockers; `edition_metadata.json`: source and change-control metadata; `test_results.json`: results and test environment; this file and `README.md`.

## Clause and decision highlights
1. §2.2.62.1.1 and .1.3 define the scope, including pathogens, prions, cultures, patient specimens, biological products and clinical waste. Laboratory samples are neither always regulated nor always exempt. Negative results require a documented basis.
2. Category A requires transported-form severity under §2.2.62.1.4.1. Source medical history, symptoms, endemic conditions or professional judgement justify human/animal target determination. Record genuine doubt under Note2 and classify as A if documented; missing data goes to `requires_expert_review` or `insufficient_evidence`.
3. Category B follows §2.2.62.1.4.2 only when infectious status and non-Category-A judgement are supported. No CLP/GHS direct mapping.
4. Exemptions §2.2.62.1.5.1–.5.9 are independent and fact-specific: nonpathogenic, inactive, naturally encountered with insignificant risk, dried blood spots, faecal occult screening, qualifying transfusion/transplant purposes, professionally judged minimal-risk specimens with packaging and marking, used medical device with expressly limited relief (exclude medical waste UN3291/3549 by explicit source status; require overpack and packaging states). Specimen tripack outer 100x100 mm and device retention at 1.2 m are implemented boundaries.
5. Biological product §2.2.62.1.9(a) qualifies only with appropriate national manufacture/packaging and personal healthcare final-packaging/distribution evidence; §.1.9(b) is infectious A/B evaluation; check the local competent authority note.
6. Medical waste §2.2.62.1.11.1–.11.3: Category B and low probability can generate UN3291 candidates; eligible solid Category A waste for disposal can generate competing 3549 and 2814/2900 candidates; liquids, bio-research waste and non-disposal waste cannot be routed to 3549; note special waste codes and diagnosis requirements. Contradictory CatA vs low-risk coding is blocked for expert adjudication.
7. Intentionally infected live animals: competent-authority gate §2.2.62.1.12.1 and §2.2.62.2; natural/unintentional infection: origin/transit/destination national rules per §.1.1 Note 1. Noninfectious GMOs -> §2.2.9; noninfectious toxins -> Class6.1 reference.
8. §3.2.1 Table A: checked rows for 2814/2900/3291/3373/3549 show **blank packing group**. SPs in column (6) respectively 318/318/565/319/395. Do not add generic PG. SP318 is a documentation dependency; SP319 requires actual P650 and marking proof; SP395 restricts entry 3549; SP565 has its own waste condition.

## Decision and evidence interfaces requested from the Lead
- Agree shared `hazard_evidence` schema: source identifier, sampled material, sampling date, source clinical history/symptoms/endemic conditions, suspected and known pathogen, culture versus nonculture, infectious form and exposure basis, human/animal host potential, Category A criterion assessment, professional role and dated record reference.
- Agree `patient_specimen`, `waste`, `device`, `biological_product`, `animal` typed records; preserve tri-state booleans and reject undocumented exemptions. Define provenance and revocation for corrected laboratory or clinical assessments.
- Table A row resolver must select exact variant and proper shipping name, then full SP and packing instructions (P620/P621/P622/P650) and relevant labelling/consignment provisions from the official edition.
- Main hazard resolver must arbitrate named entries and multi-hazard precedence, consider Class6.1, Class9, other dangerous classes, and scope/exception of ADR Part1. The current module returns only Class6.2 candidates or local exceptions.
- Mode agent must handle non-road classifications independently (IATA/ICAO, IMDG, RID). For minimal-risk specimens, ADR Note2 alone is not a full air classification.
- Independent professional and regulatory reviewer needed for discretionary footnote a cultures, new/emerging pathogens, local biological product and infected live animal authority requirements.
- Reconcile ADR 2025 English Corr.1 and Corr.2 and check whether any rule changed. UN Manual Rev8 and Amend1 are provided but no Class6.2 numerical criteria are invented from those materials.

## Test execution
77 fixtures passed by executing the `class62.mjs` classifier content fetched from GitHub in a V8 JavaScript evaluator, compared with the committed `class62.test.mjs` fixtures. Categories cover positive Category A/B, Category A doubt, culture/person specimens, drying/transfusion, packaging 99/100 mm, device 1.19/1.20 m, biological products, low-probability/coded/decontaminated waste, bio-research and liquid exclusions for 3549, Category A contradictions, medical-waste device exclusion, unmarked overpacks, unknown specimen state, animal permissions and unsupported mode. **GitHub Actions / actual Node.js `node --test` execution has not yet been reported.** Tests passing is code consistency, not legal validation.

## Unsupported/high-risk states
See `unsupported_cases.csv` (20 cases): missing medical evidence, alternate exempt specimens package, diagnostic-culture footnote, waste code diagnosis, infection vs low-risk contradictions, Table A named variant, SP318/319/395 compliance, other modes, other classes, national competent authority decisions, unknown pathogen, corrections.

## Next decisions
1. Lead agent reviews and approves the interface and whether independent clinician/virologist judgement can be represented by signed classification evidence.
2. Table A ingestion agent resolves exact row variants, Part 4/5/7 requirements, actual special provision applicability and entry uniqueness.
3. Specialist reviewer rechecks full source clauses, SP395 and all exclusions against ADR Corrigenda 1/2; annotates acceptance decisions.
4. Integrator runs `node --test agents/agent10/class62.test.mjs` in CI, adds named-entry and cross-hazard end-to-end tests, resolves any discrepancy.
5. Only after independent review should `final_sds_section14_assignment_permitted` become actionable in a *separate approved integration layer*; this module itself is intentionally not an assignment engine.

**No agent-owned files outside agents/agent10 were modified.**