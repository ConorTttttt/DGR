# Agent 10 — ADR 2025 Class 6.2 infectious substances

**PROVISIONAL — UNREVIEWED.** This self-contained module never issues a final SDS Section 14 classification or a global "not regulated" decision. It does not derive transport hazards from CLP/GHS. Branch ownership: `agent10/class-6-2-adr2025`. Only `agents/agent10/**` files are changed.

## Source authority
ADR 2025, English `ECE/TRANS/352 (Vol.I)`, §2.2.62.1–2.2.62.3, Table A §3.2.1, SPs in §3.3.1. The user-supplied Vol.II supplies later packing instruction follow-up. This is a draft implementation, not independent certification. See `edition_metadata.json`.

## Usage
```js
import { classifyClass62 } from './class62.mjs';
const result = classifyClass62({
  mode:'ADR_ROAD', kind:'patient_specimen',
  pathogen_state:'known', category_a_assessment:'not_met',
  evidence_refs:['lab assay and medical judgement record 123']
});
// result.decision = "class62_candidate"; un_entry_candidates=["3373"]; never a final UN assignment
```
Run regression tests using `node --test agents/agent10/class62.test.mjs` from repository root (Node.js 18+). The test report describes separately what was actually executed.

## Core input contract
- **Mandatory:** `mode:'ADR_ROAD'` and `kind` from `substance | culture | patient_specimen | biological_product | medical_waste | medical_device | live_animal | gmo | toxin`.
- **General infectious decision:** `pathogen_state:'known'|'reasonably_expected'|'no_infectious_substances'|'nonpathogenic_microorganisms'|'unknown'`; `category_a_assessment:'met'|'not_met'|'doubt'|'unknown'`; `affects_humans` / `affects_animals` as explicit booleans where Category A; `evidence_refs` nonempty array of source/provenance references. Do not infer false from missing.
- **Human judgement:** `professional_judgement:{record_ref,basis}` for documented Category A doubt and minimal-likelihood exemptions. Clinical source history, symptoms, endemic conditions, and transported form belong in the basis and evidence record.
- **Patient specimen:** `specimen_exclusion`, `specimen_purpose`, `specimen_purpose_verified`, `blood_drop_on_absorbent`, `minimal_pathogen_likelihood`, `specimen_species`, `specimen_is_liquid`, `multiple_fragile_primaries`, `specimen_packaging`. For deemed-compliant exemption: `method:'tripack'`, primary and secondary leakproof, adequate outer, packaging verified, outer width and height **>=100 mm**, correct literal exempt marking, all-content absorbent if liquid, separation if multiple fragile primaries. `method:'alternative_no_leakage'` is held for expert review.
- **Medical waste:** `waste_state:'solid'|'liquid'`, `waste_origin:'human_medical_treatment'|'animal_veterinary_treatment'|'bio_research'`, `waste_carriage_purpose:'disposal'|...`, `waste_low_probability`, `waste_catalogue_code`, `waste_catalogue_verified`, `diagnosis_recorded`, `waste_decontaminated`. Eligible solid Category A disposal waste returns **two competing candidates** (2814/2900 and 3549); selection is explicitly deferred.
- **Biological products:** `national_authority_manufacture_packaging_verified`, `healthcare_personal_use`, `biological_carriage_purpose:'final_packaging'|'distribution'|...`. National restrictions remain open.
- **Used medical devices:** `device_category_a` and `device_other_class_dangerous` must be explicit false for §2.2.62.1.5.9 relief. Enumerated `device_carriage_purpose` plus `device_packaging` proof of break/puncture/leak protection, 6.1.4/6.6.4 construction, 4.1.1.1/4.1.1.2, 1.2 m drop, correct "USED MEDICAL..." mark, and overpack mark/visibility where relevant. `drained_of_free_liquid` is a separate §2.2.62.1.5.3 route.
- **Live animals:** `infection_origin` and `competent_authority_approval`, with evidence of authority scope, alternative carriage and national animal rules.
- **Other pathways:** `inactivation_verified`, `natural_pathogen_level` plus `no_significant_infection_risk`, `toxin_without_infectious_agent`; `other_hazard_cues` are returned unchanged for the cross-class agent.

## Output contract
`decision` is one of `class62_candidate`, `conditional_adr_non_subject`, `limited_provisions_exemption`, `insufficient_evidence`, `requires_expert_review`, `named_entry_review_required`, `requires_competent_authority_approval`, `requires_competent_authority_review`, `national_animal_rules_review`, `referred_to_other_class`, `mode_not_supported`. Always emits `packing_group:null`, `final_sds_section14_assignment_permitted:false`, `other_class_integration_required:true`, `decision_trace`, `missing_evidence`, `review_gates`, class and UN **candidates** only. Negative Class 6.2 finding is never proof of a global non-dangerous material.

## Reviewed regulatory findings and restrictions
- Positive Category A/B severity and target-species routes: §2.2.62.1.4.1–.4.2; genuine recorded Category A doubt resolves A (Note 2); absent pathogen evidence does **not** equal doubt or negative.
- §2.2.62.1.5.1–.5.9 has **distinct** sample and equipment exemptions; §2.2.62.1.9 is restricted to qualifying biological products, not all medical products.
- §2.2.62.1.11.1–.11.3 distinguishes Cat A/B waste, reasonably low-probability waste, special waste codes and decontaminated waste. SP395 prevents UN3549 for liquid, bio-research and non-disposal contexts.
- Table A Class6.2 candidates (2814/2900/3291/3373/3549) have a **blank** PG (4); no I/II/III. Column (6) SP dependencies are 318/318/565/319/395 respectively. Refer to `special_entry_dependencies.json` for checked source pages and packaging instructions.
- SP319 does not remove ADR obligations until actual P650 packaging and marking requirements are met; this module does not certify packing.
- The indicative Category A pathogen table is non-exhaustive. Three cultures have a discretionary diagnostic/clinical Category B footnote; no organism-name-only classification.
- Air and other transport modes are **not classified**; ADR §2.2.62.1.5.8 Note2 explicitly refers to conditions for air packaging, which does not make ADR a full air-mode rulebook.

## Integration handoff
Use `decision_rules.json` plus `regulatory_register.csv` as auditable metadata, `unsupported_cases.csv` as open gates, `test_results.json` as test evidence, and `HANDOVER.md` for Lead Agent actions. Schema and interface are provisional until Lead Agent adopts a shared convention. No other agent files altered.