# Agent 0 integration plan, exclusive ownership and review protocol

## Proposed merge order

1. **Source authority (Agent 1).** Review exact ADR 2025 English Parts 1–3 sources, Table A row identities, special provisions and Corr.1/Corr.2. Authenticate original PDF digests independently of supplied-file filenames.
2. **Evidence (Agent 2).** Map the input catalogue to explicit evidence states, test methods, units and a formulation/sample provenance chain; cross-check conditional missingness.
3. **Class modules.** Require class-scoped deterministic outputs for all thirteen ADR classes/divisions, including subsidiary hazard and provisional packing-group candidates. Leave threshold logic with assigned class owners.
4. **Primary hazard precedence (dedicated agent, not Agent 0).** Review absolute cases under ADR 2.1.3.5.3 and remaining cells/notes of 2.1.3.10. Return selected candidate and exact cited basis, or block.
5. **Table A UN assignment (Agent 4).** Prefer named/mixture-specific entries where applicable; screen A/B/C/D entry families, select unique current-edition row ID, cross-check class and PG, and resolve full column (6) SP set.
6. **Rule execution (Agent 5).** Execute only approved, immutable bundles, return evidence-linked deterministic traces; DECIDED is not a release permission.
7. **External independent review.** Regulatory, test-evidence and software reviewers sign off. Source authenticity/corrigenda, authority decisions, rights, audit/rollback and the mode-specific SDS publishing service remain separately gated.

## Exclusive branch/file ownership

| Agent | Existing branch / draft PR | Owned paths |
|---|---|---|
| 0 Lead | agent0/adr2025-integration-contract / new PR | integration/agent0/** and .github/workflows/agent0-integration-contract.yml |
| 1 Source and Table A | agent1/adr2025-table-a-ingestion / #5 | regulations/adr/2025/**, Table A importer/validator and named workflow/tests |
| 2 Evidence | agent2/adr2025-input-model-v0-1 / #3 | engine/input_model/adr2025/** |
| 3 Class drafts | agent3/adr2025-classification-rules / #2 | agents/agent3/** |
| 4 UN assignment | agent4/adr2025-un-assignment-review / #1 | agents/agent4_un_assignment/** |
| 5 Rule execution | agent5/execution-framework / #4 | agent5_execution/** |
| Additional class specialists | to allocate, separate branches | unique agents/<specialist>/<hazard> namespaces, recorded before work |
| Precedence specialist | to allocate | integration/precedence/**, explicitly not Agent 0's namespace |

Agent 0 will not edit other owners' files. Common files such as repository root README and existing shared scripts require a separately assigned coordination PR. Class ownership beyond the five existing PRs remains unassigned, not assumed.

## Review protocol

- **Technical schema review:** all five current agents review I/O field and enum compatibility. Breaking changes get a new contract version and explicit migration adapters.
- **Regulatory review:** a reviewer independent of rule author checks verbatim operative clauses, exceptions, Tables A and precedence, all editorial corrections, notes, named-entry rules and test methods. The Lead index is NOT a substitute for full text.
- **Software review:** a separate reviewer checks reference integrity, deterministic output, unknown and contradictory evidence, precise unit handling, boundary tests, immutable inputs and version pinning.
- **Evidence/security review:** check primary laboratory reports and decisions against physical formulation, samples, source hashes, issuer, approver signature, authority and validity range.
- **Acceptance:** independent real-world golden cases from every relevant class plus combination-hazard, exemption, PG and SP regressions; hold all modules provisional until all gates approve.

## Observed PR status on 12 November 2026

- #1 is a draft UN selection contract; its reference evaluator and 28 synthetic tests are not in that PR.
- #2 is an isolated draft Class 3/6.1/8/9 implementation with 36 reportedly passing local tests; not independently reviewed.
- #3 proposes 204 evidence fields and 13 class pathways, awaiting Lead mapping and corrected-source reconciliation.
- #4 is a draft fail-closed generic evaluator with 17 reported local tests; no signature or legal validation.
- #5 reports structurally validated Table A extraction, 2,939 rows and 331 assigned SP codes. The reported source digest matches the supplied ADR Volume I file; independently authenticated official equivalence, individual rows and legal effects remain pending.

No existing draft PR is ready for production merger on these findings.
