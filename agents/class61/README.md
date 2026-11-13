# Agent 9 — Class 6.1 (toxic substances), ADR 2025

**PROVISIONAL / UNREVIEWED.** This is an independently scoped audit-and-extension of the draft Class 6.1 prototype in [PR #2](https://github.com/ConorTttttt/DGR/pull/2). It does **not** change `agents/agent3/*`, and it never emits a final UN number, proper shipping name, primary transport class, classification code, packing group or SDS Section 14 determination.

## Source and scope

* Primary: ADR 2025 ECE/TRANS/352 Vol. I, §§2.2.61.1.1–2.2.61.3, 2.1.3.5.3(h), 2.1.3.10, 3.2.1 and 3.3.1, English (source SHA in `sources.json`). Effective 1 January 2025.
* Supporting documents supplied: UN Manual of Tests and Criteria Rev.8 and Amendment 1 (both fingerprinted); they do **not** replace ADR Class 6.1 acute-toxicity criteria. ADR 2025 Corr.1/Corr.2 and SP/entry-by-entry review remain **unresolved**.
* Source-grounded requirements: `rule_register.json` (27 records). Known blockers: `exceptions.json` (26 records). Detailed Lead handover: `HANDOVER.md`.

## Pure candidate evaluator

```python
from class61 import evaluate

r = evaluate({
    'material_type': 'substance', 'physical_state': 'solid',
    'human_experience': {'reviewed': True, 'status': 'none_documented', 'evidence_id': 'HUM-001'},
    'screen': {'identity_reviewed': True, 'named_entry_reviewed': True,
               'stability_reviewed': True, 'prohibitions_reviewed': True,
               'subsidiary_hazards_reviewed': True},
    'tear_gas': False, 'pesticide': False, 'class8_meets_criteria': False,
    'routes': {
       'oral': {'status': 'measured', 'ld50_mg_kg': '5',
                'sample': 'carried_material', 'species': 'rat',
                'observation_days': 14, 'evidence_id': 'TOX-LAB-01'},
    },
})
# r['status'] == 'criteria_met', r['candidate_packing_group'] == 'I'
# r['missing_evidence'] still records missing dermal / inhalation routes.
# r['assignment_permitted'] is ALWAYS False.
```

Evidence values are strictly decimal: inputs may be numbers or decimal strings, not booleans, NaN or infinities. Oral/dermal LD50 in mg/kg; dust/mist LC50 in mg/L; vapour LC50 and V in ml/m³ (ppm); partial pressure in kPa at 20°C and standard atmospheric pressure; dermal contact 24h; animal follow-up 14d; inhalation 1h or 4h. A one-hour result takes precedence over four-hour interpolation; four-hour conversions are ×4 for dust/mist, ×2 for vapour.

Use `routes` with `status: measured | derived | threshold_tests | excluded`. Every measured/derived/threshold-series route requires a nonempty `evidence_id`. `measured` requires the carried material, animal species and observation conditions specified by §2.2.61.1.3. `derived` is supported only for oral/dermal mixture routes under §2.2.61.1.10.1/.2, and vapour mixture routes under §2.2.61.1.9.1. `threshold_tests` is supported only for liquid-vapour mixtures under §§2.2.61.1.9.2–.5 with tier-specific animal and volatility evidence. Aerosol mixtures require a whole-material study; no unsupported calculation of LC50 is performed.

An `excluded` dust/mist route requires substantiated respirable mass fraction <10% for solids or no mist likely on leakage for liquids. A non-liquid vapour route may be excluded with physical state evidence. Oral or dermal routes cannot simply be marked 'not applicable' based on absent data. **An intrinsic PG II/III candidate is withheld if an unassessed route might establish PG I or II.** A positive PG I observation can be reported as a candidate despite incomplete lower-priority routes, but it still cannot be used as a final transport assignment.

## Human priority, precedence and identity

Human experience must be specifically reviewed. Human observations other than `none_documented` are sent to a competent evaluator instead of applying an automatic animal-data override. If Class 8 applies, the special dust/mist PG I plus oral/dermal eligibility test of §2.2.61.1.7.2 is surfaced, but no Class 6.1/8 primary selection is made. Pesticide active substance, physical state and subsidiary hazards must be used by the named-entry/PSN agent. Tear gases have a PG II minimum for otherwise PG III toxicity. All outputs include reference-clause and version flags and permanently set `assignment_permitted=False`.

**CLP/GHS:** ADR §2.2.61.1.14 contains a permissive non-pesticide CLP exception, but project policy forbids automatically deriving transport classification from CLP/GHS; it is deliberately not automated here.

## Tests and unresolved release gates

```bash
cd agents/class61
python -m unittest -v test_class61.py
```

Local verification: 38 Python `unittest` test groups passed, zero failures (`test_results.json`). These are synthetic rule tests **not independently reviewed legal interpretations**, not CI results, not validated laboratory data and not an approved Section 14 classifier. The tests do not prove authenticity or uncertainty handling of lab results. No autonomous treatment of named entries, Table A Col. 4, special provisions, prohibitions, Class 8 precedence or exceptional waste/artifact methods is permitted. See `HANDOVER.md` for integration decision points.
