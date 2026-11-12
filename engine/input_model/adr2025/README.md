# Agent 2 — ADR 2025 input model, draft v0.1

**Status:** Proposed input contract and catalogue. **NOT executable classification logic; NOT independently validated; do not automatically produce Section 14 classifications.** Agent 2 owns only this directory; Lead Agent approval required before adoption.

## Deliverables

- [field_catalog.csv](field_catalog.csv): **204 field IDs**, units/value types and candidate regulatory references covering identity, composition, shipment context, physical properties, all hazard classes, special provisions, radioactive and infectious material, batteries, environmental hazards and SDS 14.1–14.7.
- [input_schema.v0.1.json](input_schema.v0.1.json): JSON Schema 2020-12 evidence-aware input wrapper, with per-field `known`, `unknown`, `not_measured`, `conflicting`, `not_applicable`; provenance mandatory for known/irrelevant claims.
- [decision_requirements.v0.1.json](decision_requirements.v0.1.json): **13 ADR class/division pathways** (1, 2, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 7, 8, 9) plus 10 cross-cutting decisions.
- [relevance_examples.csv](relevance_examples.csv): examples of what missing evidence blocks, versus inputs that may be deferred/excluded in a specific verified pathway.
- [tests/test_input_model.py](tests/test_input_model.py): structure, provenance, explicit no-default-negative tests.
- [handover.md](handover.md): 8-part handover, status, limitations and dependencies.

## Core safety and interface policy

1. **Unknown ≠ false ≠ not applicable.** A blank or untested field never means “not regulated for transport.” A claim of `not_applicable` requires an applicable clause, supporting evidence and a written reason.
2. **Conditional missingness.** A datum needed by an active Class 3 flammability or PG determination can block that determination. The same datum need not block a distinct Class 7 activity calculation. The matrix lists *candidate and conditional alternatives*, NOT a blanket AND-list and not codified regulatory thresholds.
3. **Three independent decisions:** whether dangerous under relevant criteria, which UN entry/class/PG/subsidiary risk applies, and whether an exemption or carriage condition is available. Quantity relief does not make a substance intrinsically non-dangerous.
4. **Evidence bound to formulation and method.** Record source identifier, test conditions, date, edition, sample and review status. CLP/GHS classification is a screening hint only, not a transport conclusion.
5. **Separate transport-mode outputs.** ADR findings are not automatically transferable to RID, ADN, IMDG or ICAO TI. Record marine pollutants (IMDG) and aquatic hazard (ADR) separately; IMO bulk in SDS 14.7 only when actually relevant.
6. **Competent authority decisions are inputs:** especially explosives, unlisted self-reactives, unlisted organic peroxides and certain radioactive pathways. Capture approval scope, constraints and validity rather than synthesizing them.
7. **Conservative project gate:** any unassessed or conflicting relevant class path, missing required special provision/named-entry decision, or unreconciled corrigendum precludes an automatic overall **NOT_DANGEROUS_GOODS** conclusion. This is an engineering decision requiring Lead approval, not verbatim ADR law.

## Authoritative source manifest

| Source and exact edition | Relevance | Status |
|---|---|---|
| [ADR 2025 Volume I](https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf), **ECE/TRANS/352 (Vol.I)**, 1 Jan 2025 | Parts 1–3; §§1.1.2–1.1.4, 2.1, 2.2.1–2.2.9, 2.3, 3.1–3.5 | Clause references used, all decision logic pending exact cross-ref review |
| [ADR 2025 Volume II](https://unece.org/transport/documents/2025/01/standards/adr-2025-volume-2), **ECE/TRANS/352 (Vol.II)** | Parts 4–9 (packing/consignment/operation) | User-provided, not fully audited |
| [Manual of Tests and Criteria](https://unece.org/transport/dangerous-goods/rev8-files), **ST/SG/AC.10/11/Rev.8** (2023) | Parts I–III, §38.3 | User-provided, test relevance checked at index level |
| [MTC Rev.8 Amendment 1](https://unece.org/transport/dangerous-goods/rev8-files), **ST/SG/AC.10/11/Rev.8/Amend.1** (2025) | New/modified tests | Not reconciled |
| [ADR 2025 corrections](https://unece.org/adr-2025-files), **ECE/TRANS/352/Corr.1 and Corr.2 (English)** | 2025 consolidated corrections | Not reconciled |
| [EU Regulation 2020/878](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32020R0878), Annex II **§14.1–14.7** | SDS output expectations | EU source only; territorial application must be checked |

This catalogue supplements, but does not overwrite, the existing Agent 1 register `regulations/adr/2025/clause_register.csv` which is currently an index, not a rule set.

## Required Lead Agent integration

Confirm canonical product, datum, evidence, decision, regulatory provenance and modal output types; determine which fields the Lead schema already defines; agree exact edition/corrigenda handling, authority lookup, units, quality thresholds, and whether these class screens are the accepted global-completeness interface.

Run tests: `python -m unittest discover -s engine/input_model/adr2025/tests -v`.

**No regulatory tests or classification outcomes have been independently validated.**
