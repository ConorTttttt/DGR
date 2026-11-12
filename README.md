# DGR — dangerous goods regulatory knowledge base

This repository is the start of a **traceable, deterministic transport-classification system** for SDS Section 14. Initial regulatory scope: **ADR 2025, English, Parts 1–3**.

## Deliverables

See [ADR 2025 knowledge base](regulations/adr/2025/README.md) for the clause register, special-provision focus register, dangerous-goods-list field schema, source manifest, and status/coverage notes.

## Important boundaries

- This is a regulatory **index**, **not yet an executable classification engine** and **not a complete digitisation of Table A** or all special provisions.
- References point to the official UNECE edition. Summaries are paraphrases, not substitutes for the law.
- Nothing is marked machine-executable until its full text, caveats, cross-references and corrections have been checked.
- Never classify a product as non-dangerous solely from an SDS hazard classification or from an alphabetic index lookup.
- ADR 2025 applies from 1 January 2025; edition metadata and later English corrigenda are tracked independently.

## Suggested integration path

1. Resolve whether transport is within ADR scope and any applicable exemptions (Part 1).
2. Derive class, subsidiary hazards, packing group and most specific entry using Part 2.
3. Retrieve an official Table A row by UN number (Part 3, Chapter 3.2).
4. Resolve every applicable special provision and limited/excepted-quantity condition.
5. Emit a Section 14 result with source references, evidence, assumptions and unresolved issues. A human reviewer signs off safety-critical results.
