# Agent 8 — ADR 2025 Class 5.2 organic peroxides (PROVISIONAL)

Deterministic **candidate-only** evaluator for organic peroxide formulations and evidence under ADR 2025. Uses Lead Agent draft response schema `1.0.0-rc1`; `assignment_permitted:false`, `requires_independent_review:true`, and `packing_group:null` are invariants. Missing evidence is **never** a negative finding. CLP/GHS are not used to assign transport classes.

## Inputs and API
`const {classify}=require('./classify.js'); classify(evidence);`

Require verified structural identity; current formulation/revision; peroxide component mass % plus molecular mass (g/mol), peroxygen group count and hydrogen peroxide mass % (for available-oxygen exclusion); full desensitizer compatibility/spillage review. Routes: `listed` (exact official 2.2.52.4/IBC520/T23 source row and formulation), `unlisted` (complete applicable MTC A–H report and authority), `mixture` (verified components, actual measured mixture SADT and authority), and `sample` (2.2.52.1.9 sample evidence/OP2/<=10kg/thermal conditions). Add state liquid/solid, package-specific SADT °C, 50 kg SADT when needed, confinement category, package category and phase-separation evidence. See test_cases.json for synthetic examples.

Threshold handling: oxygen uses **exact decimal fractions**; SADT <=50 and <=45 C as applicable; Type A prohibited, Type G Class 5.2-only exclusion. Diluent A boiling >=150 C; B boiling >=60 and <150 C, flash >=5 C and boiling >= SADT(50kg)+60 C; water only under approved wording or sample exception. Control/emergency temperatures derive from ADR 7.1.7.3.5 where not listed.

ADR §2.2.52.3 permits Type B–F liquid/solid generic references UN 3101–3120. The relevant ADR 2025 Table A column (4) is **blank**, hence no PG, but exact `row_id` remains `null` and final UN assignment is **not** made. Type B class-1 subsidiary is candidate only. Article UN3545 is unsupported. SP 122,181,274 and P520/IBC520/T23 require external checks.

**Run tests:** `node --test agents/class52_organic_peroxides/classify.test.js`. Synthetic inline V8 test report in test_results.json; Node CLI/CI and independent regulatory review are pending. Source SHA256 metadata in sources.json. See HANDOVER.md and exceptions.json.

## Refinement to the decision gates
Complete composition must contain an organic peroxide component; A/B diluents must be verified organic liquids. IBC520 and T23 listing paths must match IBC/tank receptacles and verified type. Compatible other-diluent addition must be distinguished from replacement of type A/B requiring re-assessment. Under §2.2.52.1.7, a verified mixture of listed components may be evaluated under the most dangerous component's carriage conditions with measured SADT without inventing a blanket competent-authority approval; significantly different new mixtures require independent new-classification/approval review.

## Evidence schema
See `evidence.schema.json` (JSON Schema draft 2020-12). It deliberately accepts absent evidence fields because the deterministic evaluator must return a blocking status rather than misinterpret a schema rejection as a negative danger finding. `x-positive-evidence-gates` names the required values for a supported positive route. Boiling/SADT gap is compared using exact signed decimal fractions; no floating-point threshold tolerance is added.
