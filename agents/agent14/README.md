# Agent 14 — ADR 2025 cross-class precedence and packing-group reconciliation

**DRAFT — PROVISIONAL, UNVALIDATED, NOT FOR LIVE SDS SECTION 14.** All results are non-publishable. Only Agent14 files are owned; the Agent4 selector and Agent1 importer remain untouched.

## Regulatory scope

Authoritative source: ADR 2025 English ECE/TRANS/352, Volume I, especially clauses 2.1.2, 2.1.3.3–2.1.3.10, 2.1.5.5, 3.2.1 Table A columns (3a),(3b),(4),(5),(6), Chapter 3.3. The source precedence table is PDF page 127 / printed 107. The 198 occupied cells are normalized in precedence_matrix.json, 22 row keys and 18 column keys, including solid/liquid alternatives and pesticide footnote. All matrix cells need independent checking against the rendered source before approval.

## Deliverables

- precedence.py: deterministic Python stdlib gate for full 13-class screening, §2.1.3.5.3 absolute precedence, §2.1.3.10 matrix, PG reconciliation and Table A/SP compatibility.
- precedence_matrix.json: version-pinned, source-located table; no UN-number entries.
- decision_rules.json and regulatory_register.csv: edition, clause, rule IDs, handling and review status.
- unsupported_cases.csv: unverified, exceptional, human and source-dependent conditions.
- source_manifest.json: ADR PDF hash, Corr.1/Corr.2, Vol.II and UN Manual Rev.8/Amend1 dependencies.
- test_precedence.py: synthetic regression tests, including conditional cell boundary, multi-hazard competition, exception, missing evidence, named-vs-generic and row/PG/SP contradictions.
- HANDOVER.md and TEST_RESULTS.md: lead handover and test provenance.

## Local execution

    python -m unittest discover -s agents/agent14 -p 'test_*.py' -v
    python -m py_compile agents/agent14/precedence.py

In Python import evaluate from agents.agent14.precedence (namespace packages supported). Call evaluate(packet, precedence_context, agent4_row_selection); this is a provisional producer/consumer adapter design pending Lead approval.

## Required evidence and units

Input class findings follow Agent0 v0.1.0 draft contract: 13 assessed class records, scoped status, stable candidate IDs, source citations, source-document SHA256, sample identity and evidence IDs. Each class agent must retain its actual test methods, standards, measurement units, numerical results and uncertainty. Agent14 only consumes supported primary/subsidiary and class PG *candidates*. It must not recreate toxicity, flammability or corrosivity thresholds or map CLP/GHS to ADR. For conditional table cells require externally evidenced solid vs liquid transport state; for Class6.1 PG I/II require oral, dermal or inhalation route. Classification negatives are class-scoped, never globally non-dangerous.

## Fail-closed policy

No row: preserve provisional class/PG in trace, but selected UN number and final PG remain null. Any contradiction or missing named-entry/col5/col6 SP/corrigenda evidence blocks and cannot be silently repaired. Absolute-priority classes without numeric PG are not assigned a fictional PG. Named solutions and mixtures require exact §2.1.3.3/2.1.3.4 exception evidence and Agent4 row choice. Waste, articles, environmental-only secondary marking, authority decisions and carriage prohibitions require separate expert paths; larger than five simultaneous matrix candidates block pending review. Outputs always include publishable=false, assignment_permitted=false.

This module is **engineering-only, not independently reviewed and must remain a draft**.
