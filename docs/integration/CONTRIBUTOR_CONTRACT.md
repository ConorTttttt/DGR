# ADR 2025 contributor contract — Lead Agent, v1.0.0-rc1
Status: DESIGN APPROVED BY LEAD FOR REVIEW ONLY. No independent regulatory approval, no production enablement.

## Edition and provenance
ADR 2025 English ECE/TRANS/352 Vol. I/II, Corr.1 and Corr.2 tracked as separate source layers. UN MTC Rev.8 and Amend.1 are supporting test-method sources. Pin immutable source hashes and clause IDs; never silently upgrade an edition or infer ADR from CLP/GHS. The matching source set and schema remain a draft until independent verification.

## Canonical module response
Every class evaluator MUST return schema_version, assessment_id, regime, edition, class, rule_id, status, primary_class_candidates, subsidiary_risks, packing_group_candidates, exclusions, unresolved_evidence, expert_decisions, table_a_candidates, special_provision_outcomes, evidence_refs, clause_refs, assignment_permitted=false, requires_independent_review=true.

Primary candidates: class, classification_code, division, compatibility_group, packing_group, evidence_ids, authority_decision_id, status. Subsidiary risks: class, evidence_ids, status. PG candidates: value I/II/III and evidence. Exclusions: class-scoped legal basis, competent-authority decision and evidence. Table A: exact importer row_id plus four-digit UN. Special provisions: code and applies/does_not_apply/prohibits/requires_authority/uncertain/not_evaluated plus evidence. Unresolved evidence: id, reason, blocks_assignment. Authority: unique decision, approval status and *externally verified* trust attestation.

Class1 MUST have packing_group=null and packing_group_candidates=[]. Division and compatibility group are distinct from PG. Every response is class-scoped, never an SDS final answer.

## Decision status taxonomy
- criteria_met: hazard-scoped candidate, not a direct UN assignment.
- criteria_not_met: continue other-class screening; not globally 'not regulated'.
- excluded_from_class: documented exclusion from that class only; screen others.
- not_applicable: documented irrelevance; not a negative finding without evidence.
- indeterminate, authority_required, conflict, unsupported: mandatory blocker.
- prohibited_for_carriage: mandatory carriage blocker, never 'not regulated'.

Assignment review can occur only after ALL relevant class screens close, precedence/mixture and subsidiary hazards resolve, applicable authority documents are authenticated, candidate-set completeness is attested, exact Table A row is verified and all assigned SP outcomes are resolved. A class-module status alone NEVER unlocks assignment. SDS publication additionally requires independent regulatory, security and release sign-off; software DECIDED != legal approval. Exhaustive explicit review is mandatory for 'not regulated for transport'.

## File ownership
Agent 0: contracts/v1/, docs/integration/, tests/integration/, and .github/workflows/adr2025-contract-ownership.yml only. Branch protection must require ownership CI after merging.
New Agent 1 Class1: agents/class1_explosives/ only.
Existing PR #5 Table A owner: regulations/adr/2025/table_a_* and its existing importer/validator paths.
PR #3 Agent 2: engine/input_model/adr2025/.
PR #2 Agent 3: agents/agent3/.
PR #1 Agent 4: agents/agent4_un_assignment/.
PR #4 Agent 5: agent5_execution/.
Reject PRs editing paths outside ownership; schema changes require Lead adapter PR. Never let two agents edit the same file.

## Contributor acceptance and handover
Require rule id, exact clause/edition, evidence IDs, null/unknown handling, exception predicates, effect, independent synthetic tests, limitations, status, version and reviewer. Provide blocked/uncertain, contradictory, authority missing/expired, leading-zero UN, multirow, SP and no-Class1-PG tests. Public repository: no bulk copyrighted Table A/SP reproduction without rights clearance. Merge remains disabled until independent source, regulatory, security and integration review.
