# Agent 0 — ADR 2025 canonical integration contract (draft)

**Technical interface version:** 0.1.0. **Scope:** ADR 2025 English, ECE/TRANS/352 Parts 1–9, initially Parts 1–3. **Regulatory validation:** NOT performed. No live Section 14 output may be published on the basis of these files.

The Lead Agent owns the canonical envelope and integration gate, **not hazard thresholds**. All paths are confined to `integration/agent0/`; no upstream agent files were modified. The accompanying workflow name is unique to Agent 0.

## Contracts

- `schemas/integration_packet.schema.json`: evidence, class results, primary/subsidiary candidates, PG candidates, exclusions, unresolved evidence, authority decisions, Table A row and SP outcomes.
- `schemas/rule.schema.json`: exact-source-cited declarative rules with 3-valued missingness semantics; an envelope, not approved numerical rules.
- `schemas/outcome.schema.json`: fail-closed deterministic stage routing; `publishable` is always false.
- `reference_registry.json`: document SHA-256 fingerprints from user-supplied PDFs and a non-exhaustive, cross-cutting exact-clause register.
- `orchestrator.py`: checks integration readiness without inventing class thresholds or UN entries.
- `tests/`: synthetic routing/negative/missingness/precedence/SP/Table A tests; no real product classifications.

## Architectural decisions

- Class criteria, primary/subsidiary candidates and PG are **separate proposals**. All PGs require matching the selected Table A row before downstream release review. Never infer an entry from a class candidate.
- Class-module `criteria_not_met` is a **class-scoped negative**, never 'not dangerous goods'. A missing, unmeasured or conflicting field is **not** negative. A documented `not_applicable` state demands rationale and cited evidence.
- Exemptions under Part 1 and LQ/EQ under Parts 3.4/3.5 remain separate carriage-relief assessments. They never silently erase hazard classification.
- Agent 0 DOES NOT implement 2.1.3.5 or 2.1.3.10 precedence values; a dedicated precedence owner must supply an independently reviewed selection. Equally, named entry/UN row resolution belongs to Agent 4 and Table A/SP text to Agent 1.
- The execution-layer `DECIDED` flag in PR #4 means logical completion only; it never supersedes regulatory-source, Table A, expert and release gates.
- No direct mapping from CLP/GHS classification is allowed.

See `CONTRIBUTOR_CONTRACT.md`, `INTEGRATION_PLAN.md`, `RELEASE_CHECKLIST.md` and `DECISION_LOG.md`.
