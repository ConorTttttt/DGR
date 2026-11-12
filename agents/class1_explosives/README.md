# Agent 1 — ADR 2025 Class 1 explosives
Status: draft / regulatory review required. Version 1.0.0-rc1. Isolated from PR #5's existing Table A importer. NO experimental thresholds or autonomous competent-authority approvals.

Primary normative source: ADR 2025 ECE/TRANS/352 Vol.I §§2.2.1.1.1–2.2.1.1.9, 2.2.1.2.1–2.2.1.2.2, 2.2.1.3, 2.1.3.7, 2.3.0–2.3.1, 3.2.1 and 3.3.1. Supporting source: UN MTC ST/SG/AC.10/11/Rev.8 Part I and Rev.8/Amend.1 affecting Part I Sections 11, 12 and 18.

The module is a **scope/document-consistency gate**, NOT an algorithm that runs/derives explosive testing or selects a legal UN number. One requested candidate code is tested against documented test-series evidence, signed-and-externally-verified competent-authority decision, exact source-verified Table A row and all assigned SP outcomes. A positive result is Class1 criteria_met candidate only: assignment_permitted=false and independent review always required. User-controlled 'verified' flags cannot substitute for an authentic external verifier. Do not merge into a production classifier until independent regulatory approval.

## Pathways
- All six divisions 1.1–1.6 and 13 compatibility group labels A,B,C,D,E,F,G,H,J,K,L,N,S, ADR §§2.2.1.1.5/.6. Collective-entry combinations from §2.2.1.3 in pathways.json; H/J named-entry pathways need exact verified Table A lookup; K never permitted (§2.2.1.2.2).
- Division + group = classification code. **Class1 has NO packing group I/II/III.**
- Suspected explosive → Manual of Tests and Criteria Part I evidence; absent tests/authority gate = blocker (§2.2.1.1.2).
- New explosive n.o.s., UN0190 sample and certain SP authorization cases require country-of-origin competent-authority classification and approved carriage conditions (§2.2.1.1.3). A competent authority confirming Class1 assigns classification in writing (§2.2.1.1.9).
- Fireworks default analogy requires competent-authority agreement, qualifying table and package constraints (§2.2.1.1.7.2–.7.5); ordinary fireworks require series 6 data.
- Class1 exclusion needs test/definition basis and authority approval (§2.2.1.1.8.1), after which other classes still require screening.
- Unduly sensitive, spontaneously reacting or unlisted explosives are not accepted (§2.2.1.2.1); Group K not accepted (§2.2.1.2.2).
- Explosive oxidizing mixtures from §2.1.3.7 route into Class1. Wet/desensitized Class3/4.1 and predominant Class5.2 routes come from §2.2.1.1.1 Note 2; none may be silently declared non-DG.

## Input/Output
Input contract is proposed Lead class_request.schema.json. Output fields include schema_version, assessment_id, edition, class=1, status, class candidates, subsidiary risks, PG candidates (ALWAYS []), exclusions, unresolved evidence, expert decisions, TableA row_id + four-digit UN, SP outcomes, evidence and clause refs, assignment_permitted=false. See Lead contract branch. No claims of validated real-product classifications.

## Limitations
The full default fireworks decision table, all named-entry combinations, external trust/signature verification, nationally valid authority recognitions, tested criterion details, complete SP effects, precedence for other classes and full MTC amendment delta review are NOT implemented. The supplied synthetic tests demonstrate software handling only. Real-world classification is blocked pending independent authority, data, packaging and legal review.
