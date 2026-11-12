# Agent 3 — ADR 2025 preliminary classification rules

**Development status: NOT independently reviewed or validated; NOT a complete SDS Section 14 classifier.**

This Agent 3 workstream implements narrowly scoped deterministic evidence-to-candidate rules for ADR Classes **3**, **6.1**, **8** and **9**. It produces pathway assessments, never a final overall transport classification, and **cannot output "Not regulated for transport"**. The code assumes all supplied measurements are already quality-checked by a competent evaluator. Unsupported evidence, mixture methods, and classification precedence are surfaced as blockers.

## Regulatory baseline

- Regulatory edition: **ADR 2025**, applicable from 1 January 2025.
- Document: **ECE/TRANS/352 (Vol. I)**, Parts 2–3, [UNECE official PDF](https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf); [UNECE ADR 2025 portal and corrigenda](https://unece.org/adr-2025-files).
- Chapters: 2.2.3 (Class 3), 2.2.61 (Class 6.1), 2.2.8 (Class 8), 2.2.9 (Class 9); 2.1.3.10 (hazard precedence); 3.2 (named entries) and 3.3 (special provisions) are not implemented in this module.
- Supporting test procedures: UN Manual of Tests and Criteria, Rev. 8, **ST/SG/AC.10/11/Rev.8** (2023), including §32.2.5 (sustained combustibility) and §37 (metal corrosion). These testing procedures do not replace ADR transport classification criteria.
- **Corrigendum review needed**: UNECE lists ECE/TRANS/352/Corr.1 and Corr.2. Individual reviewed rule source clauses are edition-pinned to 2025, but corrigenda impact assessment and independent legal QA remain a release gate.

## Temporary interface pending Lead Agent schema

```python
from adr2025 import evaluate_class

result = evaluate_class("3", {
    "physical_state": "liquid", "flash_point_c": 22.9,
    "initial_boiling_point_c": 70.0,
    "vapour_pressure_kpa_50c": 10.0,
    "completely_gaseous_at_20c": False,
    "liquid_desensitized_explosive": False,
    "diesel_gasoil_light_heating_oil": False,
    "carried_at_or_above_flash_point": False,
    "other_hazards_assessed": True,
    "named_entry_checked": True,
    "viscosity_concessions_assessed": True,
})
# result['status'] == 'criteria_met'
# result['candidate_packing_group'] == 'II'
# result['is_final_section_14_classification'] == False
```

Output keys: `hazard_class`, `status`, `candidate_packing_group`, `rule_id`, `source` (`edition`, `document`, `url`, `clauses`), `missing_evidence`, `limitations`, `candidate_data`, `requires_independent_review`, `is_final_section_14_classification`.

`status`: `criteria_met` = evidence satisfies *the explicitly implemented pathway*, not necessarily primary hazard; `criteria_not_met` = that pathway is demonstrated not to apply, **not** an overall exemption; `indeterminate` = missing evidence, other class, exception, named listing or unimplemented pathway requires further assessment. Candidate UN numbers must be resolved against the 2025 Dangerous Goods List before use. `candidate_packing_group` is never sufficient by itself to publish Section 14.

Input object currently uses simple evidence keys. Named-entry, other-hazard, and human-evidence booleans are *attestations only*, not auditable evidence records; production must require substantiation, provenance and sign-off through the Lead Agent interface. This temporary interface MUST be adapted rather than allowed to become the de facto shared schema.

## Modules and boundaries

| Module | Implemented | Deliberately omitted (returns `indeterminate` when needed) |
|---|---|---|
| `class3` | Standard closed-cup flash point and initial boiling point PG; high-temperature Class 3 candidate; evidenced non-sustained combustion; named diesel exception | Viscosity concessions calculations, mixed hazard precedence, pesticides, Table A/Table 3.3 resolutions, physical-state ambiguities |
| `class61` | Whole-material oral/dermal LD50; dust/mist LC50; vapour LC50 with concentration `V`; time corrections; route PG priority | Untested-mixture formulas, expert human experience, inhalation-form nuance, DGL, precedence resolution |
| `class8` | Human-review gate; direct skin exposure/observation and known-tier-test fallbacks; steel/aluminium metal corrosion at 55°C | Constituent-mixture bridging/concentration methods, validation of raw studies, DGL, precedence |
| `class9` | Selected aquatic acute/chronic *substance* cut-offs and elevated-temperature material branch; provisional UN 3077/3082/3257/3258 candidates | M-factors and mixture aquatic summation, batteries and articles, all other Class 9 entries, DGL special provisions |

Check `rules_catalog.json` for machine-readable clauses, required evidence, thresholds, exceptions and blockers. Read `HANDOVER.md` for regulatory limitations and integration needs.

## Tests

```sh
cd agent3_adr2025
PYTHONPATH=. python -m unittest discover -v -s tests
```

The suite checks input absence, threshold boundaries, PG candidate outcomes, unsupported mixtures, safety gates and `criteria_not_met` semantics. Passing tests establish **software behaviour against selected examples**, **not** a verified regulatory implementation. Review must check legal interpretation against authoritative full text and positive/negative expert benchmark cases, then record sign-off separately.