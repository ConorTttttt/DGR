# ADR 2025 — regulatory knowledge base (Agent 1)

**Status: foundational structured clause index; not a validated or complete rule set.**  
**Regulation:** Agreement concerning the International Carriage of Dangerous Goods by Road (ADR), 2025 edition, English.  
**Primary source:** ECE/TRANS/352, Volume I, Parts 1–3.  
**Publisher:** United Nations Economic Commission for Europe (UNECE).  
**Applicable from:** 2025-01-01.  
**Edition scope:** historical ADR 2025; do not silently apply as another edition or jurisdiction.

## What is here

| Artifact | Content | Coverage |
|---|---|---|
| [clause_register.csv](clause_register.csv) | Clause-level reference, functional tag, plain-language index, edition/source and verification state | 132 entries: Part 1 = 26; Part 2 = 70; Part 3 = 36 |
| [special_provisions_focus.csv](special_provisions_focus.csv) | Selected SP identifiers, likely effect type and review status | 62 selected SPs, **not** all of 3.3.1 |
| [dgl_table_a_columns.json](dgl_table_a_columns.json) | All 23 distinct column/subcolumn fields of the Table A schema (columns 1–20, split 3a/3b, 7a/7b, 9a/9b), source linkage, and normalization requirements | **Schema only**, no UN-number rows yet |
| [excepted_quantity_codes.csv](excepted_quantity_codes.csv) | The E0–E5 table from 3.5.1.2 | Six codes and quantitative thresholds, subject to other EQ conditions |
| [sources.json](sources.json) | Source URLs, document symbols, applicability, corrigenda and related test manual | English source metadata; corrigenda not reconciled |
| [../../../scripts/validate_adr2025_kb.py](../../../scripts/validate_adr2025_kb.py) | Structural integrity checks | Format and key checks only, not legal verification |

Each row is a **lookup/index record**, not itself a complete legal rule. A label of `clause_spot_checked` indicates that the reference was reviewed against retrieved ADR 2025 clause text for a preliminary mapping, not legal certification. A label of `reference_indexed` indicates a candidate index reference still requiring clause-by-clause validation. Do not turn either state into executable rules without confirming full text, cross-references, footnotes, exceptions and changes.

## The key regulatory decision points

**Part 1 — applicability and exceptions:** 1.1.3.1 to 1.1.3.10 for exemptions; 1.1.3.6 transport category and aggregate quantities; 1.2.1 definitions; 1.6 transitional measures. Transport-unit quantity relief does not automatically make a substance non-dangerous.

**Part 2 — classification and exceptions:** 2.1.2 for named/collective entries; 2.1.3.3 for named-substance mixture caveats; 2.1.3.4 for specified mixtures; 2.1.3.5 and 2.1.3.10 for competing hazards; 2.1.4 for samples; 2.1.5 and 2.1.6 for articles/waste packagings; 2.2 for each class; 2.3 for prescribed tests. A mixture may be outside ADR only if the applicable criteria and rules establish that outcome.

**Part 3 — lookups and conditional requirements:** 3.1.2/3.1.3 govern proper shipping descriptions; Table A at 3.2.1 assigns entry-specific regulatory data; 3.3.1 defines referenced special provisions; Chapter 3.4 applies only to qualifying limited quantities; Chapter 3.5 applies only to qualifying excepted quantities. **Table B is an alphabetical aid, not part of the official legal text.**

**Special provisions are not universally applicable.** For each Table A row, read the actual codes in column (6); then read the corresponding full clauses at 3.3.1, in addition to classification provisions. The selection in `special_provisions_focus.csv` is a priority list, **not** a complete extract and **not** yet linked to UN entries. SP 673 is reserved in ADR 2025 and is therefore not an actionable register entry.

## Source authority and edition notes

Official ADR 2025 catalogue: https://unece.org/adr-2025-files

Official Volume I source PDF: https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf

Official Volume II and English corrigenda are indexed in [sources.json](sources.json). The user-supplied Volume II is relevant to subsequent phases (packing, labelling, vehicle and carriage rules), rather than a substitute for Volume I. The user-supplied `ST/SG/AC.10/11/Rev.8` Manual of Tests and Criteria is a supporting classification-test reference, not the source of ADR-specific overrides. This repository links to sources instead of redistributing the full copyrighted ADR text.

The English ADR 2025 Corrigenda **1 and 2** are listed as separate documents and **have not yet been diffed or applied** to row-level interpretations. The transition provided by 1.6.1.1 may permit use of ADR 2023 until 2025-06-30 in qualifying circumstances; the knowledge base does not currently implement effective-date or transition logic.

## Proposed deterministic classifier dependency graph

```text
source material identity + composition + physical data + tests
  -> Part 1 applicability / scope check
  -> Part 2 class and packing-group evaluation
       -> named-substance mixture rules; absolute precedence; hazard precedence table
  -> Part 3 Table A lookup (one or more entries per UN number)
       -> proper shipping name + classification code
       -> column (6) special provisions
       -> column (7a) limited-quantity or (7b) excepted-quantity logic
  -> Part 4–9 cross-referenced carriage/packing checks (later phase)
  -> SDS section 14 outcome + provenance + unresolved evidence + human review
```

A transport exemption, packaging exemption, and classification as not subject to ADR are separate outcomes and must not be conflated. If classification evidence is incomplete, the engine should explicitly return `insufficient_evidence` or `requires_competent_authority_review`, not default to `not_dangerous`.

## Work still required before operational use

1. **Verify all indexed references and paraphrases** against the full ADR 2025 text, including the 51 spot-checked entries; identify any non-operative heading-only references.
2. **Apply Corr.1 and Corr.2** to affected provisions and log exact changes at row level.
3. **Ingest all Table A UN rows**, retaining the source row/page and multiple entries per UN number. The current schema has **zero UN rows**.
4. **Extract all applicable 3.3.1 special provisions** and link their assignments to UN rows via column (6). The focus list is 62 candidates, not complete.
5. Encode the classes, test thresholds, mixture rules, hazard precedence matrix, transport category and named/collective entry selection as independently reviewed and versioned decision tables.
6. Build golden-case validation fixtures with positive/negative boundaries and expert review of every rule before use for live SDS Section 14 outputs.

## Quality gates

- Preserve raw source and stable clause references (e.g. `2.1.3.5.3`), document symbol, language, edition, publication and amendment.
- Separate rule inputs, conditions, exceptions and effects. Avoid undocumented inference.
- Maintain source provenance for every derived outcome.
- Keep classification exemption, LQ/EQ relief and exemptions from some ADR provisions separate.
- Structural validator success **does not** imply regulatory correctness.
