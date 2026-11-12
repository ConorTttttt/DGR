# Agent 4 — ADR 2025 UN-number assignment, draft review contract

**Status:** draft / not independently validated. **Owner:** Agent 4. **Edition:** ADR 2025, ECE/TRANS/352 (Vol.I), English (effective 2025-01-01). **Package version:** 0.1.0.

This workstream proposes a fail-closed UN number / proper-shipping-name selector. It does not calculate transport hazards, packing groups, absolute or matrix precedence, special-provision applicability, or Class 1 criteria. Those remain with Agent 3 and the Agent 1 source catalogue. It never transforms missing data into "not regulated for transport."

## Exact clause register for selection

| Rule | Primary ADR 2025 clauses | Decision | State |
|---|---|---|---|
| AG4-01 | 2.1.1.2; 2.1.2.2–2.1.2.5 | Identify named A and collective B/C/D candidates using class-specific 2.2.x.3 decision trees | gated |
| AG4-02 | 2.1.2.3; 2.1.3.3 | Classification-affecting impurities enter mixture branch | gated |
| AG4-03 | 2.1.2.8; 5.4.1.1.20 | Named entry with newly identified unlisted hazard requires competent-authority route; block without approval | manual |
| AG4-04 | 2.1.3.3(a); 3.1.3.2 | Prefer specifically named solution or mixture entry | gated |
| AG4-05 | 2.1.3.3(b)–(d); 3.1.3.2 | Predominant named ingredient only when every condition is evidenced | gated |
| AG4-06 | 2.1.3.4.1; 2.1.3.4.2 | Named special mixtures incl PCB group require full condition and exclusion checks | delegated predicates |
| AG4-07 | 2.1.3.4.3 | Used articles special route not implemented | blocked |
| AG4-08 | 2.1.3.5.1–2.1.3.5.4; 2.1.3.10 | Multiple-hazard precedence resolved externally by Agent 3 | delegated |
| AG4-09 | 2.1.3.5.5 | Wastes of imprecise composition require specific evidence and exception review | blocked pending review |
| AG4-10 | 2.1.3.6; 2.1.2.5 | Most-specific collective; B before C before D, never D if B/C appropriate | gated |
| AG4-11 | 2.1.3.7 | Potentially explosive oxidizer mixtures require Class 1 carriage gate | gated |
| AG4-12 | 2.1.3.8; 2.1.3.9 | Environmentally hazardous and Basel waste paths not automatically classified | delegated |
| AG4-13 | 3.1.2.1; 3.1.3.2; 3.2.1 | Select exact verified Table A name and applicable SOLUTION/MIXTURE qualifier | gated |
| AG4-14 | 3.1.2.8.1–3.1.2.8.1.2; 3.3.1 SP274/318 | Technical name supplement; subsidiary contributor evidence for SP274 | gated |
| AG4-15 | 1.1.3; 2.1.4–2.1.6 | Exemptions, samples, articles, waste packagings require other modules | not in scope |

## Proposed, **not Lead Agent-approved**, interface

```text
assign({
  edition: "ADR-2025",
  candidateSet: {complete: true, assessmentId: "..."},
  product: {kind: "SUBSTANCE|SOLUTION|MIXTURE", ...verified composition decisions},
  hazard: {evaluation: "complete", evidence: [...], meetsADR: true,
           primaryClass, classificationCode, packingGroup, state,
           subsidiary: [...], multipleHazards, precedenceResolved, precedenceBasis,
           notAccepted: false, ...reviewed special-case decisions},
  entries: [{rowId, un, name, type: "A|B|C|D", class, code, pg,
             state, subsidiary, specialProvisions,
             verified:true, applicable:true, specialProvisionsChecked:true,
             ...named/mixture/decision-tree predicates}],
  technicalNames: [...], subsidiaryTechnicalNameCovered: true|false
}) -> ASSIGNED or BLOCKED
```

An `ASSIGNED` response requires complete independent ADR hazard evidence and a Table A candidate-set completeness attestation. It contains UN number, selected row ID, proper shipping name, class, code, packing group, subsidiary hazards, clause references. `BLOCKED` includes a reason, clause and no assigned classification. A negative Agent 3 hazard finding is **still BLOCKED in Agent 4** for separate Lead Agent handling; no implicit "Not regulated".

## Review evidence and tests

Local reference package contains `assignment.mjs`, `tests.mjs`, `rules.json`, `interface.example.json`, `README.md`, and `HANDOVER.md`. The prototype passed **28/28 synthetic routing unit tests**; neither the official full Table A nor an independent classification review has been performed. Tests are *not* evidence for actual product classifications.

**Source:** [UNECE ADR 2025 Vol I](https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf); [ADR 2025 edition and corrigenda](https://unece.org/adr-2025-files); related repository manifest `regulations/adr/2025/sources.json`. Corr.1 and Corr.2 must be fully reconciled before approval.

## Lead Agent approvals and dependencies

1. Approve shared I/O fields, result taxonomy, evidence IDs and versioning.
2. Agent 1 provides independently checked full Table A/SP candidate catalogue, class-specific collective decision trees, and proof of exhaustive candidate screening (the local prototype currently accepts an external completeness assertion).
3. Agent 3 provides signed hazards, primary-class precedence, prohibited-carriage and waste/environmental-special-case decisions.
4. Independent regulatory reviewer checks all branches, named-mixture exceptions, technical names, corrigenda, and real Table A fixtures.
5. Only after that review should the executable prototype be integrated and enabled for SDS Section 14.

**Change isolation:** This branch touches only `agents/agent4_un_assignment/` and does not modify existing Agent 1 catalogue assets or Agent 3 criteria.
