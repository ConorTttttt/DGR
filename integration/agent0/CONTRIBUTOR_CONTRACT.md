# Agent 0 contributor contract — technical interface v0.1.0

**State:** Lead-owned DRAFT engineering contract. No rule is legally certified. Each owner works only in their allocated namespace; breaking changes to canonical types require an Agent 0 coordination PR and new versioned adapter tests.

## Required hazard-class module output

1. Return one class_evaluation per ADR class or division using schemas/integration_packet.schema.json. Include hazard_class, module_id, coverage_status, criteria_status, rule IDs, exact clauses, evidence IDs and limitations.
2. Separate primary_class_candidates, subsidiary_risk_candidates, packing_group_candidates, exclusions and unresolved_evidence. Candidate IDs must remain stable and unique. No class specialist may invent final UN numbers, proper shipping names or PGs.
3. Distinguish criteria_met, criteria_not_met, exception_applies, indeterminate; likewise evaluated, not_applicable, incomplete and not_assessed. A class-scoped negative is NOT a globally negative transport decision.
4. Evidence must include state, sample identity, actual primary document URI/locator and SHA-256, applicable test standard/method and units, regulatory citations, and review status. Unknown, conflicting or unmeasured facts must not become false. A documented not_applicable finding requires its own rationale, clause and support.
5. Include all applicable exceptions, named-entry and special-provision dependencies, subsidiary hazard pathways, human/competent authority decisions, and exact edition metadata. Register every unsupported case and boundary condition.
6. Tests must include positives, negatives, missing evidence, threshold boundaries, conflicts and exceptions. State clearly whether they are synthetic or independently reviewed actual regulatory cases.
7. Changes to another agent's files require prior agreement. Produce a draft PR and complete handover. Independent legal validation must occur before claims of regulatory correctness.

## Deterministic rule envelope

schemas/rule.schema.json specifies rule_id, version, owner, regime, edition_id, rule_kind, when, if_unknown, effects, references and review_status. Comparisons use explicit typed operands; decimal values are base-10 strings and measurement units are explicit. Unknown input must propagate indeterminate, not false. Implementation of actual ADR thresholds belongs to the class specialists, not Agent 0.

## Status routing

| Router status | Allowed action | Assignment and publication |
|---|---|---|
| BLOCKED | Resolve invalid data, conflict, missing evidence or expertise | Assignment prohibited; never publish |
| READY_FOR_PRECEDENCE | Dedicated precedence agent evaluates competing hazards | UN assignment prohibited |
| READY_FOR_ASSIGNMENT | Agent 4 screens named entries and actual Table A rows | May attempt assignment; cannot publish |
| READY_FOR_SPECIAL_PROVISIONS | Resolve all applicable column (6) codes under 3.3.1 | Cannot finalize assignment |
| READY_FOR_RELEASE_REVIEW | Independent regulatory, technical, security and source review | Router still returns publishable=false |

These labels are engineering gate outputs, not regulatory terminology. Even approved metadata is not a trusted electronic signature. No Section 14 results or global not-regulated decision are emitted by Agent 0.

## Explicit PR adapter actions

- PR #5, Agent 1: supply source-authenticated Table A per-row identifiers, candidate-set completeness evidence, all row-linked special provisions and exact corrigenda impacts.
- PR #3, Agent 2: adapt known/unknown/not_measured/conflicting/not_applicable fields and evidence provenance; preserve explicit measured negatives without converting missingness.
- PR #2, Agent 3: map criteria_met/criteria_not_met/indeterminate into class_evaluation, retain test and exception references; class PG is only a candidate. Do not erase limitations.
- PR #1, Agent 4: return row ID, Table A edition, name, classification code, PG check, named-entry screening, SP status and any competent-authority blocker.
- PR #4, Agent 5: accept a reviewed immutable rule bundle and enforce this outer release gate; its DECIDED result means computation complete, not legal approval.

## Scope notes

ADR classification and carriage relief are distinct: exemptions under 1.1.3 and LQ/EQ under Chapters 3.4/3.5 cannot silently erase class candidates. Mode-specific ADR results cannot directly certify RID, IMDG or ICAO TI results. No CLP/GHS-to-transport default classification is permitted.
