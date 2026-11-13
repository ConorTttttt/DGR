# Agent 13 — ADR 2025 Class 9 specialist (provisional)

This is a **separate, unvalidated** Class 9 specialist workstream. It audits PR #2 (`agents/agent3/adr2025/class9.py`) without changing Agent 3-owned files. Integration into PR #2 requires Lead Agent permission and a versioned shared schema. **Do not use for a final SDS Section 14, UN assignment, dangerous-goods exemption, or carriage authorization.**

## Run

```sh
cd agents/agent13
python -m unittest discover -s tests -v
```

Inputs are dictionaries to `class9.evaluate(e)`, with `pathway` set to `aquatic`, `elevated_temperature`, or `subclass`. Results use Agent 3's provisional field vocabulary plus `aquatic_categories`; `criteria_not_met` is strictly scoped to a completed pathway, never a global transport finding. `indeterminate` means evidence or regulatory dependencies are missing. Every result is review-required; `candidate_packing_group` defaults to `None`.

## Supported Class 9 pathways

- **Aquatic hazard (M6/M7):** Substance and whole-mixture acute/chronic cut-offs, limited substance chronic-data fallback, mixture summation including per-endpoint M-factors, additive toxicity fraction (acute L(E)C50 and chronic EqNOEC), five evidence-attested bridging rules. Mixture process is hierarchy-gated. Unknown relevant ingredient data precludes a **definitive** negative, although a confirmed positive contribution remains a provisional category. Aquatic hazard is **separate** from primary Class 9 or additional environmental descriptor, per 2.1.3.8.
- **Primary aquatic Class 9 candidate:** UN 3077 (solid) or 3082 (liquid) only as entry *candidates* when an attested cross-class review and a named-entry review are supplied. PG III requires the environmental criterion **and** an external, evidenced, matching ADR 2025 Table A row for the same UN/code; the module does not itself certify DGL rows.
- **Elevated temperature (M9/M10):** ≥100°C liquid **below flashpoint** (if it has one), or ≥240°C solid. Class 3 at-or-above-FP situations remain blocked. No PG inferred.
- **Other:** Asbestos M1; PCB/PCT M2 (mixture-only 50 mg/kg exclusion); flammable-vapour polymers M3 (55°C threshold); lithium and sodium ion batteries M4 with type test, design and QMP/test-summary gates; life-saving appliances M5 as SP-dependent; GM organisms M8 as authority/class-gated; M11 named-entry-only. All remain subject to listed-entry and special-provision checking; none is a catch-all.

## Evidence and conventions

- Regulatory references: ADR 2025 **ECE/TRANS/352 Vol I**, §§2.1.3.8, 2.2.9, 3.2, 3.3, supplied English PDF, plus **UN MTC Rev.8** Part III §38.3/§38.3.5 and Rev.8 **Amend.1** (2025) for modified battery testing rules. ADR 2025 is the pinned regulatory baseline; the 2025 MTC amendment must be reconciled for temporal applicability by the Lead.
- Aquatic toxicity measurements in **mg/L**, concentrations in **mass %**, PCB/PCT in **mg/kg**, temperature in **°C**. All numeric inputs are finite; boolean or string substitutes are invalid. Classifier evidence must have traceable report identifiers.
- Acute fish **OECD 203** (96h LC50), crustacea **OECD 202** (48h EC50), algae **OECD 201** (72/96h ErC50); chronic fish **OECD 210**, crustacea **OECD 211**, algae **OECD 201** or valid equivalents (§2.2.9.1.10.2.3–.4). Degradation **OECD 301/306**, log Kow **OECD 107/117**, experimental BCF preference per §2.2.9.1.10.2.5–.6. Where source test details are missing, do not fabricate a surrogate.
- **No automatic CLP-to-ADR conversion.** ADR §2.2.9.1.10.5 has a conditional fallback when directly relevant data are not available; it requires a separate, independently specified source-based rule and is intentionally not enabled here.
- The `verified_table_a_row` object is an **external attestation**, not a trusted lookup. It must contain `{ "edition":"ADR 2025", "un":"3082", "class":"9", "classification_code":"M6", "packing_group":"III", "evidence_ref":"<verified row record>" }` (or matching solid 3077/M7). Its authenticity must be checked by Agent 1/Lead before production.

## File index

`class9.py` deterministic evaluator; `rules.json` clause/rule/evidence register; `tests/test_class9.py` software behaviour tests; `UNSUPPORTED.md` exceptions, evidence limits and dependency register; `HANDOVER.md` Lead integration/review handover.
