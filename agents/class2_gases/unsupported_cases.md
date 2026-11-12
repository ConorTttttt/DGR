# Unsupported-case, exception and conflict register — Class 2 ADR 2025

All statuses below are **provisional**. This document records executable safety gates and
what cannot yet be decided; it is not a permit to ship, nor a declaration of non-dangerous goods.

| ID | Case and controlling reference | Current behaviour | Required closure |
| --- | --- | --- | --- |
| U01 | Named gas, mixture, or article entry differs from generic characteristics (§2.2.2.1.4; Chapter 3.2 Table A) | Annotates Table A named-entry gate; no UN number assigned | Official row matching plus n.o.s. rereouting |
| U02 | Full list of gas collective entries and subrow choices (§2.2.2.3) | Classification code candidate only | Agent for Table A/DGL entry selection |
| U03 | Class 2 material also presents independent class hazards (§2.1.3; Table A) | Hazard candidates only, no cross-class precedence | Shared precedence and independent integration approval |
| U04 | ADR 2025 official English Corr.1 and Corr.2 | Not fully reconciled in rule text | Edition registry and per-clause delta signoff |
| U05 | UN MTC Rev.8/Amend.1 §31.1.3 deletes second sentence of flammable components; §31.3.3 adds published literature, calculation or suitable calorimetry. ADR §2.2.2.1.6(c) still expressly lists particular methods | ADR methods retained in evaluator; MTC test report allowed only as externally attested result | Regulatory interpretation and applicability date approval |
| U06 | Full spray and foam aerosol test pathways (MTC Rev.8 §31.3–§31.6, Figures 31.1–31.3) | Qualified aggregate test outcome accepted; raw ignition distance/enclosed space/foam measurements not algorithmically adjudicated | Add audited decision trees and method-condition checks |
| U07 | ISO 10156:2017 mixtures and calculations; authority-approved comparable methods (§2.2.2.1.5) | Accepts ISO-derived conclusions; equivalent method requires authority reference | Validate underlying calculation, origin authority and evidence |
| U08 | Toxic mixture analogue selection when Ti unavailable (P200; §2.2.2.1.5) | Numerically computes only if every Ti and mole fraction is attested; no invented substitutions | Expert-sourced P200/literature/analogue and scientific review |
| U09 | Human toxicity and corrosivity knowledge (§2.2.2.1.5) | Requires sourced boolean attestations, treats missing as unresolved | Independent literature and toxicology review |
| U10 | Oxygen displacement by a gas with negative F/O/T (§2.2.2.1.5) | Explicit physical attestation needed for group A | Expert evidence if atypical gas |
| U11 | Mixture with combined gas F and O / T and C, special combinations (§2.2.2.1.3) | Applies within-Class-2 group precedence only, blocks unlisted aerosol/chemical combinations | Lead/hazard-precedence expert check |
| U12 | Gas stability, polymerization, special provision 386 and P200(10)(r) (§2.2.2.2.1; 3.3; 4.1.4.1) | Prohibition if both allowed safety alternatives are documented false; missing blocks | Verified packing/stabilization record and official SP text |
| U13 | UN 2186, UN 2421, UN 2455 (§2.2.2.2.2) | Explicit not-accepted gate when supplied *preexisting* named UN identity matches | External named-entry verification; do not infer identity from CLP/GHS |
| U14 | Refrigerated liquefied gas outside 3A/3O/3F (§2.2.2.2.2) | Not-accepted outcome with group candidate | Verify Table A identity and constraints |
| U15 | Dissolved gases (§2.2.2.2.2; §2.2.2.3): only listed named entries 1001, 1043, 2073, 3318; UN1043 SP642 | Blocks absent/unpermitted named-entry hint; fixed code 4 only | Named identity + SP642 + Table A review |
| U16 | Gas cartridges §2.2.2.2.2; P200 pyrophoric; LC50 <200 ppm | Prohibition gate and fixed code 5 only; no full filling-condition check | UN2037, P200, construction and capacity validation |
| U17 | Other gas-containing articles under codes 6A/6F/6T (§2.2.2.1.2(6); §2.2.2.3) | `blocked_unsupported` | Implement article-specific identity, classification, equipment, pressure and SP gates |
| U18 | Non-pressurized gas samples, codes 7F/7T/7TF (§2.2.2.1.2(7); §2.2.2.3) | `blocked_unsupported` | Dedicated sample module |
| U19 | Aerosol hazards including O+F (no corresponding group in §2.2.2.1.6 list) | `blocked_unsupported`, no invented combination | Regulatory subject-matter interpretation |
| U20 | Chemicals under pressure with Class 1, 3 desensitized explosive, selected Class 4, 5, 6.2, 7 components (§2.2.2.1.7 Note 3) | Requires external boolean component assessment; true leads not-accepted | Specialist class evidence and ingredient-level assessor signoff |
| U21 | Chemicals under pressure in aerosol dispensers (§2.2.2.1.7 Note 4) | Explicit `requires_aerosol_route` | Reevaluate entire contents through aerosol route |
| U22 | Aerosol/chemical contents PG I or combined Class 6.1 and 8 PG II/III (§2.2.2.1.6/7 Notes) | Prohibits specified routes; never sets Class 2 PG | Independent Class 6.1 and 8 content PG determinations |
| U23 | Exact MTC aerosol test result evidence `mtc31_aerosol_result` | Accepts a documented result at high level, no laboratory test-report verification | Trace physical report, aerosol form and test conditioning |
| U24 | Mixed-gas phase properties and material impurities (§2.2.2.1.1 Note 2) | Evaluates received properties, does not compute phase from composition | Require representative full mixture and stability |
| U25 | All applicable special provisions, P200 fill pressure, cylinders, tanks, exemptions and carriage limits (Parts 1,3–9) | Unresolved and clearly reported | Lead integration with DGL/SP and transport constraints |
| U26 | Packing group for Class 2 §2.2.2.1.3 vs Chapter 3.2 Table A column (4) | Always null, even when contents PG II/III drives aerosol/chemical hazard | Table A row binding and reviewer confirmation |
| U27 | CLP/GHS-derived “gases under pressure”, H codes, SDS declared UN number | Not accepted as independent ADR evidence | Transport-specific test/identity evidence |
| U28 | Engine input schema not yet formally Lead-approved; `not_applicable`, uncertainty intervals, evidential conflicts, threshold measurement error | Missing/invalid mostly blocks; no interval propagation or expert decision attestation | Lead schema, confidence model, conflict resolution |
| U29 | Different method/calculation for ISO 10156 flammability (volume basis) and oxidizing power | Numeric conclusions required; does not calculate ISO algorithm from mixture formula | Verified ISO library or lab report |
| U30 | Cross-jurisdiction IMDG/ICAO divisions 2.1, 2.2, 2.3 (§2.2.2.1.3 Note 1) | `division_hint` only, not final ADR SDS classification | Mode-specific rule ownership |

## Non-negotiable safety contract

- Missing evidence, missing Table A match, and missing special provisions do **not** mean `not regulated`.
- Explicit negative class-property tests are retained as evidence; they do not cancel independent positive criteria.
- `not_accepted_for_carriage` is route- and ADR-2025-specific; assess permitted alternatives independently.
- Any output containing a candidate code or group remains **not** a final UN, PG or SDS Section 14 answer.
- This module must not be treated as independently validated. Do not merge into production until reviewed.
