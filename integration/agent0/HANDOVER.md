# Agent 0 detailed handover — ADR 2025 SDS Section 14

**Prepared:** 2026-11-12. **Pull request:** https://github.com/ConorTttttt/DGR/pull/6 (DRAFT).
**Branch:** agent0/adr2025-integration-contract. **Schema/interface:** 0.1.0, Lead technical baseline, regulatory approval NOT obtained.

## 1. Deliverables

- Canonical schemas: schemas/integration_packet.schema.json, schemas/rule.schema.json, schemas/outcome.schema.json.
- Edition/source/clause registry: reference_registry.json, with exact document identifiers, URLs and user-supplied source hashes.
- Executable fail-closed orchestration protocol: orchestrator.py. Returns stage readiness only, never publishable Section 14 classification.
- Machine-readable cases and tests: tests/integration_cases.json and tests/test_contract.py.
- Contributor contract, branch/path ownership, integration dependency plan, decision log, regulatory release checklist, and isolated CI workflow.

## 2. Regulatory sources used

ADR 2025 English, ECE/TRANS/352 Vol.I (Parts 1–3) and Vol.II (Parts 4–9); especially 1.1.3, 2.1.1.1–2.1.1.2, 2.1.2.1–2.1.2.2, 2.1.3.3, 2.1.3.5.3–2.1.3.5.4, 2.1.3.10, 3.1.2, 3.2.1, 3.3.1, 3.4 and 3.5. Supporting test documents: ST/SG/AC.10/11/Rev.8 and Rev.8/Amend.1. English ECE/TRANS/352/Corr.1 and Corr.2 registered, but legal deltas remain pending review. Source URLs and fingerprints are in reference_registry.json; no source document is redistributed.

Local ADR Volume I SHA-256 abb98cdaeadc2cbda6642e5123e38635a2ab23cd610776fb375fe8c76a130f65 matches Agent 1's extraction manifest. This is file-digest correspondence, not independent authentication of the official publisher.

## 3. Rules and decisions

No hazardous-material numerical classification rule was created. Stage policies require 13 class/division evaluation records; known or documented negative evidence; explicitly cited exception bases; unique primary-candidate IDs; separately resolved precedence; named-entry and Table A row screening; selected row PG consistency; and full special provision resolution before external release review.

Status BLOCKED forbids further automatic assignment. READY_FOR_PRECEDENCE authorizes precedence evaluation only. READY_FOR_ASSIGNMENT authorizes Agent 4 assignment search. READY_FOR_SPECIAL_PROVISIONS authorizes SP resolution. READY_FOR_RELEASE_REVIEW allows external regulatory/software review only. Every output has publishable=false, regardless of review metadata.

Negative class evidence cannot create global no-dangerous-goods conclusions. The all-class negative branch additionally requires independently reviewed exhaustive screening and named-entry checks, and STILL cannot publish a Section 14 negative statement from this router.

## 4. Tests performed

GitHub Actions contract job PASS: https://github.com/ConorTttttt/DGR/actions/runs/43327085050 .
Test methods: 5/5 pass; machine-readable cases within one method: 23/23 pass. Covers positive stage routing, all-class negative review, missing/unmeasured evidence, invalid schemas, duplicate candidate screening, incorrect precedence, unsupported PG, contradictory SP, rejected review and immutable non-publishability. JSON Schema Draft 2020-12 schema checks and Python compilation also pass. These are purely synthetic software tests, not boundary tests of real hazard criteria and not independent regulatory validation.

## 5. Exceptions and unresolved cases

- Every transport quantity/carriage exemption is deliberately separated from intrinsic hazard findings.
- No 2.1.3.10 precedence matrix values, class thresholds, Article/competent authority technical decisions, or modal transfer rules are implemented.
- Source authenticity, official corrigenda and amendment reconciliation, table row legal audit and SP effects are incomplete.
- Agent 4's evaluator and 28 synthetic unit tests were external to PR #1; they are not merged or integrated.
- No credible signature/authority verification or production SDS publishing gate exists.
- A limited source reference index is NOT a complete substantive clause register; Agent 1 must extend/verify it.

## 6. Coordination and assumptions needing approval

- Agents 1–5 must approve the new adapter interfaces and the treatment of not_applicable, explicit negative, class coverage and multiple hazard precedence.
- Assign unique repositories/branches for all remaining hazard-class owners and the precedence specialist.
- A trusted external review system must establish authority/evidence authentication, immutable versioning, signature controls, time validity and audit logs.
- Determine whether class-path completeness should use mandatory all-13 review, or an independently approved conditional relevance matrix. The current conservative all-13 gate is a project choice, not a verbatim ADR obligation.
- Agree release and Section 14 formatting requirements mode-by-mode.

## 7. Lead integration follow-up

1. Hold PR #6 in draft until the schema review is complete.
2. Request proposed adapters and object-mapping fixtures from Agents 1–5, without direct edits to their namespaces.
3. Collect independent source authentication and Corr.1/Corr.2 + MTC Amend.1 legal reconciliation.
4. Add expert-approved real-world golden classifications, threshold boundary cases and independently coded precedence tests.
5. Complete security/release attestations before any production classification or SDS output.

## 8. Current approval state

**Technical CI: PASS.** **Regulatory review: NOT PERFORMED.** **Source authenticity: PENDING.** **Corrigenda integration: PENDING.** **Class-module integration: PENDING.** **Production SDS authorization: BLOCKED.**
