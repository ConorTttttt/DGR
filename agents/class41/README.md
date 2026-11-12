# Agent 4 — Class 4.1 module, ADR 2025 (PROVISIONAL)

**Safety status:** specialist draft only. **Not regulatory-validated, not independently reviewed, not approved for automatic SDS Section 14 release.** This branch changes only \`agents/class41/\`. It is unrelated to the pre-existing Agent 4 UN-assignment draft PR and does not modify other agents' files.

## Deliverables

| File | Role |
| --- | --- |
| \`class41.py\` | Deterministic, Python-standard-library, single-pathway evaluator |
| \`rules.json\` | Machine-readable register: 36 scoped conditions, exact clause references, units, accepted evidence and downstream dependencies |
| \`test_class41.py\` | Threshold, exception, negative, missingness, temperature, authority and handoff tests |
| \`exceptions.json\` | Explicit unsupported cases, legal exceptions and manual decisions |
| \`HANDOVER.md\` | Lead Agent integration, unresolved decisions, risk register and release protocol |

Run: \`cd agents/class41 && python -m unittest -v test_class41\`.

Local baseline: **10 test methods / 76 scenario checks, passing**, prior to GitHub PR creation. All tests use fabricated input evidence; they are not independent chemical test validation.

## Authority and edition

* **ADR 2025, English, ECE/TRANS/352 Volume I**: 2.1.1.3, 2.1.2, 2.1.3, **2.2.41.1.1–2.2.41.1.21**, **2.2.41.2.1–2.2.41.2.3**, 2.2.41.3, 2.2.41.4, Chapter 3.2 Table A, Chapter 3.3 (especially SP386). The document supplied is \`2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf\` (printed pp. 151–160 for core Class 4.1).
* **ADR 2025, English, ECE/TRANS/352 Volume II**: relevant P520, IBC520, T23 and 7.1.7 temperature-control dependencies; these are *not* implemented as automatic carriage permissions.
* **UN Manual of Tests and Criteria, Revision 8, English, ST/SG/AC.10/11/Rev.8**, Part I explosive test series 1, 2 and 6; Part II 20.4 and test series A–H, including Series H SADT/SAPT; Part III **33.2.4 Test N.1** and 33.3 desensitized explosives.
* **MTC Rev.8 Amendment 1, ST/SG/AC.10/11/Rev.8/Amend.1**: checked changes to 28.4.2.2.2.3, 33.3.1 and Appendix 6 A6.5.1. Revised Appendix 6 calorimetric screening and its autocatalysis caveat are **not** implemented as an automatic exclusion.

The base-repository register also flags ADR 2025 corrigenda. They have **not** been independently reconciled for this module. No claim of complete amendment/corrigendum application is made.

## Seven isolated pathways

1. **\`combustible_solid\`** — non-metal powder/granules/pastes: UN Test N.1, 100 mm burning time under 45 s **or** burning rate over 2.2 mm/s (2.2.41.1.5(a)). PG II candidate only for time under 45 s with flame passing wetted zone; PG III candidate only for time under 45 s with wetted zone stopping flame at least four minutes (2.2.41.1.8(a); MTC 33.2.4). Documented positive experience may support *unnamed organic* flammable solids under 2.2.41.1.4; it does not establish PG.
2. **\`metal_powder\`** — UN Test N.1 ignition and full-sample reaction in **at most 10 minutes**. PG II if time **at most 5 minutes**, PG III if **over 5 and at most 10 minutes** (2.2.41.1.5(b), .8(b)). Metal powders with evidence of Class 4.2 or 4.3 route externally (2.2.41.3 footnotes).
3. **\`friction_solid\`** — special-provision or named-entry analogy only. No fabricated N.1-derived PG (2.2.41.1.5, .8).
4. **\`self_reactive\`** — oxygen-independent, strongly exothermic thermal decomposition, specified competing-class exclusions; heat of decomposition **under 300 J/g** or **50 kg SADT over 75 °C** excludes this pathway. Type A is not accepted; types B–F require accepted type test evidence, exact listed formulation or competent-authority approval; type G is outside self-reactive Class 4.1 provisions (2.2.41.1.9–.17; MTC 20.4.2). **SADT of the actual package offered** at **55 °C or below** triggers temperature control. **No self-reactive packing group.** The 5.1 oxidizing-mixture exception at **5% combustible organics by mass or more** is explicitly routed, not collapsed into a GHS label.
5. **\`solid_desensitized_explosive\`** — solid and desensitized evidence, **must** match a Table A entry. Unlisted solid desensitized explosives are not accepted for carriage (2.2.41.1.18, .2.3). PG and transport conditions are read only from the verified row/provisions; no universal PG.
6. **\`polymerizing\`** — SAPT **at most 75 °C** in offered container and reaction heat **over 300 J/g**, and no other Classes 1–8 criteria (2.2.41.1.20; MTC 20.4.4). Temperature control: packages/IBCs SAPT **at most 50 °C**, tanks **at most 45 °C** (2.2.41.1.21). SP386 gate on competing Classes 1–8. No universal PG.
7. **\`related_self_reactive\`** — must show provisional Class 1 acceptance under series 1/2, Class 1 exemption by series 6, and verified exclusions from self-reactives and Classes 5.1/5.2 (2.2.41.1.19). Table A/PG determination deferred.

Class 4.1 subdivisions F, FO, FT, FC, D, DT, SR1, SR2, PM1 and PM2, and named entries are in 2.2.41.1.2 and 2.2.41.3. **No final UN assignment is made by this module.** Actual composition, physical state, concentration, packaging, named entries, special provisions and Table A row must be reconciled externally.

## Transport-specific evidence input (not CLP/GHS)

The evaluator takes a Python dict with an explicit \`pathway\` and values named in \`rules.json\`. It does **not** infer test results from SDS hazard statements or CLP/GHS classes.

| Path | Mandatory quantitative/test evidence | Additional regulatory gates |
| --- | --- | --- |
| Combustible solid | UN N.1 200 mm screening, full-test time (s) and/or rate (mm/s), wetted zone for PG | Test protocol (MTC 33.2.4.3–.4); organic experience with document provenance if used |
| Metal powder | UN N.1 screening and full length reaction time (minutes) | Actual ignition and 4.2/4.3 competing evidence |
| Self-reactive | Heat of decomposition (J/g, DSC/adiabatic calorimetry), 50 kg SADT (°C), actual package SADT (°C), Part II type A–G report | Class 1/5.1/5.2 findings; formulation/concentration; approval or listed entry; activator, diluent, package, temperatures |
| Polymerizing | SAPT (°C) in offered container, heat of reaction (J/g), container kind | Strong exothermic polymerization; confirmed absence/positive findings for Classes 1–8; SP386 |
| Desensitized explosive | Solid state, desensitization and *exact* Table A listing | Class 1 evidence and conditions of listed entry; any PG only from Table A |
| Friction | Verified fire-through-friction and analogy/SP | Analogy or SP-controlled PG |
| Related self-reactive | UN MTC Part I series 1, 2 and 6 test reports | Negatives for self-reactive, 5.1, 5.2 |

Tests are required in the **commercial/offered form**, at the relevant concentration, packing and stabilizer/diluent conditions. For N.1, the screening exposure/time and 200 mm propagation parameters must be demonstrated according to MTC 33.2.4.3.1. A local bool is a *normalized test conclusion*, not a replacement for underlying test evidence. The Lead Agent must bind every input to actual report IDs, methods, versions, sample/formulation IDs and provenance before production use. Missing evidence is never interpreted as a negative.

For self-reactives, optional sample carriage under 2.2.41.1.15 requires available data showing no more danger than type B, OP2 packing, **up to 10 kg per transport unit**, and adequate control-temperature data. This module emits an *expert-decision gate* only, not transport clearance. Self-reactive dilution also requires compatibility, tested-as-offered concentration, leakage concentration prevention and, for temperature-controlled liquid diluents, boiling point at least 60 °C, flash point at least 5 °C and boiling point at least 50 °C above control temperature (2.2.41.1.16).

## Deterministic response

\`evaluate(evidence)\` returns a mapping with \`status\`, \`class_candidate\`, \`pg_candidate\`, \`final_packing_group=None\`, \`type_candidate\`, \`subdivision\`, \`temperature_control_required\`, \`subsidiary_hazard_candidates\`, \`clauses\`, \`blockers\` and downstream-gate flags. It is a **pathway-scoped** assessment.

Statuses: \`criteria_met\`, \`criteria_not_met\`, \`indeterminate\`, \`not_accepted_for_carriage\`, \`requires_authority\`, \`requires_expert_decision\`, \`external_class_review\`. A positive \`criteria_met\` **may still contain unresolved blockers** and can never alone authorize assignment. \`criteria_not_met\` **does not** mean “not regulated for transport.”

Example:

\`\`\`python
from class41 import evaluate
out = evaluate({
  "pathway":"metal_powder", "test_method":"UN_MTC_N1",
  "screening_propagates_200mm":True, "ignited":True,
  "full_length_reaction_min":5
})
assert out["pg_candidate"] == "II"
assert out["final_packing_group"] is None
\`\`\`

## Release boundaries

* Table A identification and Column (4) PG, listed formulations (2.2.41.4, P520/IBC520/T23), special provisions, transport packaging, control/emergency temperatures, stability and carriage conditions all require **independent lookups and review**.
* Do not assign a final UN number, proper shipping name, label, subsidiary hazard, PG or SDS Section 14 from this module alone.
* Do not infer CLP/GHS equivalence. Do not use absence of evidence as evidence of absence.
* Multi-hazard and named-entry precedence belongs to the Lead Agent and UN-assignment specialist.
* The detailed unhandled/exception cases in \`exceptions.json\` must be resolved before regulatory release.

**Review required** for legal interpretation, source transcription, numeric boundaries, method normalization, schema/interface alignment, amendments/corrigenda, named entries, and real-world report-to-rule traceability.
