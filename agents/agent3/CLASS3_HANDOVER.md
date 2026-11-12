# Agent 3 — ADR 2025 Class 3 audit and extension handover

**Review state:** DRAFT / PROVISIONAL. This branch is stacked on draft PR #2 and targets PR #2; it is not an independently approved or production-ready transport classifier. No final UN entry, subsidiary risk or Table A packing group is asserted. Lead Agent file ownership/schema approval has not been confirmed.

## Scope, source register and boundaries

- Regulatory authority: ADR 2025, **ECE/TRANS/352 Vol. I** (supplied 2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf), Part 1 definition of liquid at **1.2.1**, Chapter **2.2.3**, tests at **2.3.3.1–2.3.3.3** and **2.3.4**; multiple hazards **2.1.3.10**, Table A **3.2**, SPs **3.3**, packing **4.1.1.1–4.1.1.8**.
- Supporting tests: supplied **UN Manual of Tests and Criteria Rev.8, ST/SG/AC.10/11/Rev.8** (2023), Part III **32.2.5, 32.4.2, 32.4.3, 32.5.1 (L.1), 32.5.2 (L.2)**. Supplied Rev.8 **Amendment 1** modifies **32.3.2.1** (liquid desensitized explosives); that amendment does **not** authorise new ADR UN assignments.
- ADR 2025 corrigenda have **not** been compared clause-by-clause; regulatory release is blocked pending version-delta review.
- Evidence-to-decision clauses are recorded in `class3_rule_register.json`. The scope is flammable liquids; it does not derive ADR from CLP/GHS.

## Implemented and source-indexed pathways

1. **ADR 1.2.1 / 2.2.3.1.1:** liquid definition requires measured vapour pressure <=300 kPa at 50 C, non-gaseous at 20 C/101.3 kPa, and verified melting point <=20 C or accepted fluidity test; state uncertainties block.
2. **2.2.3.1.1 and 2.2.3.1.3 table:** closed-cup flash point <=60 C; IBP <=35 C -> calculated Class 3 PG I; IBP >35 C and flash point <23 C -> PG II; IBP >35 C and 23..60 C inclusive -> PG III. **Calculated Class 3 PG is never final Table A PG.**
3. **2.3.3.1.1–2.3.3.1.5 / 2.3.3.2:** approved recorded closed-cup and initial-boiling-point methods and evidence IDs required. Non-equilibrium FP readings in 23±2 C or 60±2 C windows need equilibrium confirmation; inconsistent readings, disputes or dissimilar confirmation are **indeterminate** pending formal 2.3.3.1.5 checking.
4. **2.2.3.1.1 NOTE 1 / UN MTC 32.2.5:** >35 C non-sustained combustion substantiated by negative L.2, ISO 2592 fire point strictly >100 C, or miscible solution water strictly >90% mass; not a global exemption, and not applicable if heated at/above FP.
5. **2.2.3.1.1 NOTE 2 and elevated-temperature text:** diesel/gasoil/light heating oil 60<FP<=100 C -> UN 1202 **candidate**; liquid or molten solid heated at/above FP where FP>60 C -> UN 3256 **candidate** with measured carriage temperature. Entries and special provisions remain external checks.
6. **2.2.3.1.1, 2.2.3.2.3:** liquid desensitized explosive route recognises listed UN Nos. 1204, 2059, 3064, 3343, 3357, 3379 and 3555 as **candidate references only**; unlisted entries blocked as potentially not acceptable for carriage.
7. **2.2.3.1.4 table (a)–(d):** viscous liquids with FP<23 C, validated ISO 2431/UN MTC 32.4.3 flow/jet, six strict FP rows, L.1 solvent separation strictly <3%, receptacles <=450 L, and independently tested absence of Class 6.1/8 criteria for material AND separated solvent may qualify for calculated PG III. Ambiguous initial PG I downgrade blocked.
8. **2.2.3.1.5.1 and .5.2:** viscous-liquid relief for 23<=FP<=60 C when required benign hazard/NC/packaging/test evidence exists; 6 mm jet flow >=60 s OR >=40 s if <=60% Class 3 substances. Environmental substances only obtain a **packaging-specific** relief at <=5 L per single/inner and all referenced general packing requirements. No global "not regulated" output.
9. **2.2.3.1.4 NOTE, .1.6:** NC <=20%, nitrogen <=12.6% dry mass may follow viscosity route; named UN 2059 or Class 1/4.1 dependencies are explicitly blocked when stated thresholds require review. Tested whole-material mixtures supported; untested/inferred constituent mixtures blocked.
10. **2.2.3.2.1–2.2.3.2.3, 2.3.3.3:** peroxide calculated as H2O2 strictly >0.3% -> carriage prohibition candidate; unsafe chemical instability -> conditional carriage blocker; no manufactured approval.
11. **2.2.3.1.1 NOTES 3–4, 2.2.3.1.3, 2.1.3.10:** highly toxic inhalation or specified pesticide routes refer to Class 6.1, and Class 6.1/8/environmental subsidiary hazard candidates are passed as unresolved; no multi-hazard precedence guessed.

## Input conventions and API

The existing temporary Agent 3 `evaluate_class('3', evidence)` output is retained. It returns `criteria_met`, `criteria_not_met` (pathway only), or `indeterminate`, a rule ID and ADR clause citations, `missing_evidence`, provisional `candidate_packing_group`, `candidate_data`, and `requires_independent_review=True`. This is **not** Lead-approved schema. Important new measured inputs are `flash_point_c` (C), `initial_boiling_point_c` (C), `vapour_pressure_kpa_50c` (kPa at 50 C), `carriage_temperature_c` (C), `viscosity_flow_time_s` (s at 23 C), `viscosity_jet_diameter_mm` (mm), `solvent_separation_pct` (% of height), `receptacle_capacity_l` (L), `net_quantity_per_single_or_inner_l` (L), `peroxide_h2o2_mass_pct` (% mass) and nitrocellulose/nitrogen content (%). IDs and method identifiers document evidence. A boolean review attestation without an auditable evidence record is **not production proof**.

## Unsupported-case and exception register

| Issue | Current deterministic disposition | Required decision/owner |
|---|---|---|
| Full 2.2.3.3 generic/n.o.s. entry selection, Table A PG, special provisions, named diesel and UN 2059 handling | Candidate only / `indeterminate` where unresolved | Lead/entry agent, Chapter 3.2–3.3 register |
| Multi-hazard precedence, F/FT/FC/FTC code, toxic inhalation, pesticide and aquatic-hazard interactions | Block or emit candidate hazard; do not select primary class | Integration/precedence Agent |
| Non-Newtonian variable-shear extrapolation to near-zero-rate apparent viscosity per 2.2.3.1.4 footnote | Not implemented; viscosity route blocked | Agent 3/approved viscosity test specialist |
| Viscosity concession for PG I starting point | Blocks downgrade | Independent ADR reviewer |
| Detailed ADR 2.3.3.1.5 consignor/dispute check-test decision, differing FP results | Block all disagreement, not resolved by unverified boolean | Competent evidence reviewer |
| Complete method-range validation of ISO/ASTM standards and method applicability to viscous products | Enumerated accepted method names, but full method validity not proven | Laboratory/evidence agent |
| Full nitrocellulose mixtures, instability stabilizers, SP386, packaging/temperature provisions | Conditional candidate or blocker | Named-entry/packing agent |
| Class 3 articles, F3, named mixtures not assessed as whole material, cross-regime IMDG/IATA | Not implemented | Lead and relevant mode agents |
| Lead schema, review signatures, ADR corrigenda 1/2 applicability | Missing | Lead/regulatory QA |

## Tests and reproducibility

- Developmental local Class 3 suite: **31 test methods passed** with extensive boundary subcases using the tested evaluator before minor final defensive guards were added. This verifies software logic only.
- Submitted `tests/test_class3_expanded.py`: **15 unittest methods** covering threshold values, named exceptions, toxicity priority, disputed FP evidence, full viscosity rows, 40/60s and 5-L thresholds, restrictions and missing evidence.
- Legacy `tests/test_classes.py` Class 3 fixtures updated to the stricter documented measurement input contract while retaining non-Class-3 tests.
- **GitHub CI run is not yet established**, the submitted branch head is not independently benchmarked, and the new test file has not been verified as a GitHub workflow success. Do not claim a passing repository CI suite from these local results.

## Requested Lead Agent decisions before merge

Approve ownership and reviewed input schema / evidence attestations; supply Table A row ID, definitive named-entry + SP checks and precedence API; set priority rules for blockers vs possible positive candidates; arrange independent regulatory review of all table boundaries, concession interactions and corrigenda; add golden certified material cases and CI contract. Until then, this work is a **draft, non-validated module**, not approved for publishing SDS Section 14 classifications.
