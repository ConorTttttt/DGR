# Lead Agent handover — Agent 2 ADR 2025 Class 2 (PROVISIONAL)

**Branch:** `agent2/adr2025-class2-gases`. Owns only `agents/class2_gases/`.
No shared files or other agents' branches edited. Separate from older Agent 2
input-model draft PR #3. No merger, operational validation or production enablement.

## Deliverables

- `classify.js` — deterministic CommonJS `evaluateClass2(data)` function.
- `classify.test.js` — 50 synthetic tests for positive/negative, inclusive and
  exclusive limits, mixed gases, invalid units, absent evidence, prohibition.
- `test_results.json` — exact GitHub blob SHA and synthetic V8 test record.
- `rule_register.json` — 40 clause-labelled candidate rules and safety gates.
- `evidence.schema.json` — 34 evidence fields, units, accepted methods, source IDs.
- `unsupported_cases.md` — 30 exceptions, limitations and conflicts.
- `README.md` — usage, status contract, references and safety boundaries.

## Regulatory basis

ADR **2025 ECE/TRANS/352 Vol.I English**, §§2.2.2.1.1–2.2.2.1.7,
2.2.2.2.1–2.2.2.2.2, 2.2.2.3; Chapter 3.2 Table A columns 2/3b/4/6;
Chapter 3.3 SP386, Volume II §4.1.4.1 P200 (including paragraph 10(r)).
UN Manual of Tests and Criteria **ST/SG/AC.10/11/Rev.8** Part III §31,
and **Rev.8/Amend.1** §§31.1.3 and 31.3.3. ISO 10156:2017 is invoked by
ADR 2.2.2.1.5. Official references:
https://unece.org/adr-2025-files and
https://unece.org/transport/dangerous-goods/rev8-files.

## Scope and regulatory implementation decisions

1. Class 2 gas definition: vapour pressure >300 kPa at 50 C OR wholly gas
   at 20 C and 101.3 kPa. Compressed, liquefied (critical T >-50 through
   +65 C vs >+65 C), refrigerated liquefied, dissolved, adsorbed category
   conditions. Compressed category allows proven entirely gaseous
   packages at -50 C or critical temperature <=-50 C; adsorbed pressure
   must be strictly <101.3 kPa at 20 C and <300 kPa at 50 C.
2. Ordinary-gas groups A/O/F/T/TF/TC/TO/TFC/TOC. F if ignitable in air
   <=13 volume percent or range >=12 percentage points; O if ISO oxidizing
   power >23.5 percent; T if relevant human hazard or inhalation LC50
   <=5000 ppm. Corrosivity is toxic in Class 2 and yields C subsidiary
   group variants. Harmonic LC50 calculations for gas mixtures require
   complete mole fractions and sourced component Ti.
3. Aerosols: groups A/O/F/T/C/CO/FC/TF/TC/TO/TFC/TOC. F directly at
   >=85 mass percent flammable AND >=30 kJ/g; non-F at <=1 mass percent
   AND heat <20 kJ/g. Other cases need an attested UN MTC Part III §31
   outcome. Toxic/pyrophoric propellant and PG I content prohibition.
4. Chemicals under pressure: groups A/F/T/C/FC/TF, propellant exclusions,
   PG I and combined PG II/III toxicity-corrosivity exclusions, specified
   other-class components prohibited; in aerosol dispenser must reroute.
   Flammable liquid component threshold <=93 C is a distinct §2.2.2.1.7
   criterion, not a general Class 3 threshold.
5. Named exception UN1052 routes to Class 8; prohibited gas entries
   UN2186, 2421, 2455 and special refrigerated/dissolved restrictions
   are candidates for external Table A/identity verification.
6. ADR classification codes: compressed group prefixed 1, liquefied 2,
   refrigerated 3A/3O/3F, dissolved fixed 4, aerosol and small receptacle
   fixed 5, chemicals group prefixed 8, adsorbed group prefixed 9.
   No engine-derived UN number. No Class 2 PG I/II/III; content PG
   from Class 6.1/8 remains separate, and Table A column 4 must be checked.
7. Never map CLP/GHS labels or an SDS asserted UN number directly to
   ADR class, group, PG or final UN entry.

## API for Lead (temporary; to be formally approved)

`evaluateClass2(input)` consumes:
- `route`: gas, cartridge, aerosol, chemical_under_pressure,
  article or gas_sample (latter two explicitly unsupported);
- `form`: gas transport phase, where applicable;
- `evidence`: field map of `{value, unit, method, id}` with optional
  `authority_reference` for competent-authority equivalent method;
- `components`: optional mixture array with mole fraction, indexed LC50,
  source, evidence ID and corrosivity;
- `preexisting_named_un`: **unverified input hint**, not final assignment.

Returns `status`, `physical_form`, `hazard_group_candidate`,
`classification_code_candidate`, `hazard_candidates`, `negative_findings`,
`missing_evidence`, `blockers`, `exceptions`, `decision_trace`,
`regulatory_references`, `division_hint`, `edition` and `review_status`.
Always `un_number:null`, `table_a_row_id:null`, `packing_group:null`,
`special_provisions_resolved:false`,
`requires_independent_review:true`, `final_sds_section14_permitted:false`.

Temporary statuses:
- `class2_group_candidate` is only a scoped candidate and may be sent
  to the Table A/SP orchestrator after formal Lead mapping.
- `blocked_missing_evidence` and `blocked_unsupported` block progress.
- `not_accepted_for_carriage` is a **route-specific** prohibition.
- `requires_aerosol_route` must rerun the appropriate aerosol pathway.
- `outside_class2_gas_definition_not_non_dg` does not imply non-dangerous.
- `outside_class2_special_named_exception` requires another class agent.

Every status currently **blocks final SDS Section 14 issuance**.

## Lead integration dependencies and approval requests

1. Canonical multi-agent schema/status mapping, including Class 2 group,
   proposed primary Class 2 candidate, corrosive/oxidizing/flammable
   subsidiary risk candidates, unresolved fields and expert decisions.
2. Table A row ID resolver, specific-vs-n.o.s. matcher, gas-mixture named
   entry override, all relevant SPs, P200 and acceptance/filling constraints.
3. Class 6.1 and 8 content PG assessments for aerosols and chemicals
   under pressure, without transposing those PG values to Class 2.
4. Cross-class hazard precedence under shared orchestration (only Class 2
   group precedence is handled here).
5. Review English ADR Corrigenda 1/2 and exact effective edition.
   Critically, MTC Rev.8 Amendment 1 changes §31.1.3 and expands §31.3.3
   heat-of-combustion methods, while ADR 2025 §2.2.2.1.6(c) names specific
   methods. An independent reviewer must settle applicability.
6. Review authority recognized alternatives to ISO 10156, negative
   human-experience evidence, mixture Ti sources and stability cases.
7. Plan independent benchmark with real laboratory evidence and
   regulator-reviewed named entries; synthetic tests alone are insufficient.
8. Agree reviewer and branch ownership before any integration merge.

## Test execution and required review

**50/50** synthetic tests passed by evaluating the *exact GitHub-fetched*
JS classifier and test contents in an isolated V8 environment using
minimal Node-style test/assert shims. See `test_results.json` for SHAs.
This is **not** an actual Node CLI run, GitHub Actions CI or independent
validation. Reviewer should run:

    node --test agents/class2_gases/classify.test.js

Then independently check each of 40 register rules against rendered official
ADR pages, check Corr.1/Corr.2 and MTC Amendment 1 deltas, audit the 30
unsupported cases, and obtain signed regulatory sign-off before enabling.

## Next work, in order

Approve Lead schema; reconcile source editions/corrigenda; encode full
MTC §31 aerosol test raw measurements; implement articles/non-pressurized
samples and complete cartridge P200 gate; integrate Table A/SP rows; run
external real-substance reference corpus; complete independent review.

**Release gate:** NO claim of legally validated ADR classification until all
external evidence, Table A/SP, integration and independent review are complete.
