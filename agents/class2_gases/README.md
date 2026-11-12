# Agent 2 — ADR 2025 Class 2 gases (PROVISIONAL)

**Owner:** Class 2 specialist only. **Isolation:** only this directory on branch `agent2/adr2025-class2-gases`. **Review state:** NOT APPROVED; must not drive live SDS Section 14.

## Regulatory baseline

- **ADR 2025, ECE/TRANS/352, English, Volume I:** 2.2.2.1.1–2.2.2.1.7, 2.2.2.2.1–2.2.2.2.2, 2.2.2.3; Chapter 3.2 Table A column 4 and Chapter 3.3 special provisions; Volume II 4.1.4.1 P200.
- **UN Manual of Tests and Criteria**, ST/SG/AC.10/11/Rev.8, Part III, §31 (especially 31.1.3, 31.3, 31.4–31.6), and Rev.8/Amend.1, §31.1.3 and §31.3.3.
- **ISO 10156:2017** is referenced by ADR 2.2.2.1.5 for flammable/oxidizing gases.
- Official texts: [ADR 2025](https://unece.org/adr-2025-files); [UN Manual Rev.8 and Amendment 1](https://unece.org/transport/dangerous-goods/rev8-files).
- Corrigenda 1/2 and the amendment's interaction with ADR's specific aerosol combustion-method wording require independent edition-by-edition reconciliation.

The implementation paraphrases rules and does not reproduce bulk UN copyrighted text.

## Files

| File | Function |
| --- | --- |
| `classify.js` | Pure, dependency-free Class 2 provisional evaluator |
| `classify.test.js` | Synthetic positive/negative/boundary/missing evidence suite |
| `rule_register.json` | 40 exact-clause rule/exception/dependency records |
| `evidence.schema.json` | 34 evidence fields with value types, units, methods and provenance |
| `unsupported_cases.md` | Exclusions, unimplemented routes and review blockers |
| `handover.md` | Lead Agent integration contract and regulatory review plan |
| `test_results.json` | V8 in-session test execution summary (not independent Node CI) |

Run (Node.js with built-in test runner, no npm dependencies):

    node --test agents/class2_gases/classify.test.js

API (CommonJS):

    const { evaluateClass2 } = require("./agents/class2_gases/classify");
    const decision = evaluateClass2(evidenceObject);

Input examples and synthetic evidence construction are in the tests. A numeric or
boolean fact must use an evidence record `{value, unit, method, id}`. All methods,
units, and requiredness gates are documented in `evidence.schema.json`. Schema
validation and full evidence provenance checking must be performed by the Lead
Agent's canonical input layer before invoking this interim evaluator. A literal
`false` with substantiated provenance is not the same as an absent field.

## Decision status policy (temporary, awaiting Lead)

- `class2_group_candidate`: only an ADR Class 2 *hazard group* and sometimes a §2.2.2.3 classification **code candidate** is supported; still requires named-entry identity, Table A row, relevant special provisions and review.
- `blocked_missing_evidence`: necessary evidence is absent or a competing hazard cannot be excluded. NEVER `not regulated`.
- `blocked_unsupported`: unhandled or contradictory evidence, invalid unit or method, impossible/unlisted grouping, or entry-specific route unsupported.
- `not_accepted_for_carriage`: explicit Class 2 prohibition or route prohibition under the cited ADR clause. This is not an overall legal conclusion for other routes.
- `requires_aerosol_route`: chemical-under-pressure formulation presented in an aerosol dispenser; requires reevaluation under the aerosol pathway (§2.2.2.1.7 Note 4).
- `outside_class2_gas_definition_not_non_dg`: both ordinary-gas definition alternatives proved false; **does not** establish that material is not dangerous.
- `outside_class2_special_named_exception`: UN 1052 anhydrous hydrogen fluoride Class 8 caveat; re-route externally.

All outputs include `requires_independent_review=true`,
`final_sds_section14_permitted=false`, `packing_group=null`, `un_number=null`,
`table_a_row_id=null`, trace, sources, blockers and missing evidence.

## Scope of executable pathways

1. **Gas definition** at 50 °C/20 °C, and the transport forms compressed,
   liquefied (high/low pressure), refrigerated, dissolved (restricted named
   entries) and adsorbed (§2.2.2.1.1–.2).
2. **Ordinary-gas group properties** A/O/F/T/TF/TC/TO/TFC/TOC and ADR's
   within-Class-2 precedence. Flammability (`<=13 vol%`, `>=12 percentage
   points`), oxidizing power (`>23.5%`), toxicity (`LC50 <=5000 ppm`),
   human toxicity, and corrosivity; optional mole-fraction harmonic
   computation with component Ti and explicit scientific source.
3. **Aerosols:** groups A/O/F/T/C/CO/FC/TF/TC/TO/TFC/TOC. Extreme threshold
   `>=85%` and `>=30 kJ/g`; no-F threshold `<=1%` and `<20 kJ/g`;
   intermediate cases require an attested UN MTC §31 result. PG I content and
   toxic/pyrophoric propellant prohibitions.
4. **Chemicals under pressure:** A/F/T/C/FC/TF and selected prohibited
   propellants/components, PG I content, concurrent PG II/III toxicity and
   corrosion, and aerosol dispenser rerouting.
5. **Cartridges and other exceptions:** LC50 <200 ppm/pyrophoric small gas
   receptacle restrictions; chemical instability/stabilization, explicit named
   forbidden entries, 3A/3O/3F refrigerated restriction, dissolved-gas
   permitted-name gate.

## Classification code is not a UN assignment

§2.2.2.3 lists ordinary codes `1..3,9` + applicable hazard-group suffix,
**code 4** for dissolved-gas named entries, **code 5** for aerosols and
small gas receptacles, and codes `8A/8F/8T/8C/8TF/8FC` for chemicals under
pressure. The evaluator supplies only a **candidate classification code**,
never a selected UN number. Named entries may invalidate an n.o.s. guess,
and the exact Table A row and SPs are integration-agent responsibilities.

**Packing groups:** Class 2 hazard-property groups (A/F/T/etc.) are not
packing groups I/II/III. This module never creates Class 2 PGs. Class 6.1/8
PG references used for aerosol/chemical **contents** must come from those
class specialists and are not transferred to the Class 2 entry. The final
Table A row's PG column (4) must be checked by the assignment agent.

## Assumptions and blockers

See `unsupported_cases.md`, `handover.md`, and machine register. Do not map
CLP/GHS labels, hazard statements or H-codes directly to a transport group.
Do not silently assign an entry based on an SDS shipping name. No independent
regulatory validation, official Table A normalization, special-provision
verification, external reference test corpus or integration sign-off has occurred.
