# ADR 2025 Table A / special provisions — phase 2 handover

**Branch:** `agent1/adr2025-table-a-ingestion`  
**Source edition:** ADR 2025 English; ECE/TRANS/352 (Vol.I), clause 3.2.1 and Chapter 3.3; applies from 1 January 2025.  
**Status:** Table A *structural extraction completed with a passing automated quality gate*; the PDF was retrieved from a mirror reproducing ECE/TRANS/352 Volume I. Independent source equivalence and regulatory accuracy review are **not yet confirmed**. No classification logic is approved.

## Files introduced

- [`scripts/ingest_adr2025_table_a.py`](../../../scripts/ingest_adr2025_table_a.py): deterministic extraction, matching and provenance. Accepts a local Volume I PDF (`--pdf`) or retrieves the official PDF with fallback mirrors (`--download`).
- [`tests/test_adr2025_table_a.py`](../../../tests/test_adr2025_table_a.py): six regression tests including leading-zero UN numbers, name matching, multirow examples, prohibition, SP token parsing and a guarded corrigendum.
- [`scripts/validate_adr2025_table_a_output.py`](../../../scripts/validate_adr2025_table_a_output.py): independent structural verification of the generated rows, their 23 fields, SP links and Corr.2 patch.
- [`table_a_review_examples.json`](table_a_review_examples.json): seven short, source-backed examples illustrating key Table A behaviours; **not** the full dangerous goods list.
- [`corrigenda_impacts.json`](corrigenda_impacts.json): ten item-level impacts of English ECE/TRANS/352/Corr.1 and Corr.2, with the Table A UN 3423 hazard-identification-number correction identified.
- [`.github/workflows/adr2025-table-a.yml`](../../../.github/workflows/adr2025-table-a.yml): unit and structural tests and optional review artifact extraction. No automated public Git commit of full Table A data.
- [`.gitignore`](../../../.gitignore): prevents committing local copy of the source PDF or bulk extracted text.

## Method and data contract

ADR 3.2.1 Table A spans *facing pages*. The left page holds columns (1)–(11) with (3a), (3b), (7a), (7b), (9a) and (9b). The right page holds (12)–(20), followed by repeated (1) and (2) identifiers.

The importer:

1. Confirms the PDF contains the expected ECE/TRANS/352 Volume I identifier and 2025 edition;
2. Identifies the Table A page span and extracts **only** numbered tables, preserving all original raw cell text;
3. Pairs adjacent left/right pages and **rejects** any UN-number or repeated-name mismatch;
4. Emits a unique row ID **per Table A row**, not per UN number;
5. Creates one cross-reference per special-provision code in column (6) and preserves the unevaluated SP text;
6. Retains PDF page indices and source PDF SHA-256 for traceability;
7. Applies the explicit Corr.2 correction to **UN 3423 column (20)**, retaining the original source cell and an audit marker;
8. Produces diagnostic files if any page, row or SP code does not parse; never synthesizes missing values.

Provisional output files (after running the importer locally):

| Filename | Purpose |
|---|---|
| `generated/table_a_rows_provisional.jsonl` | One record per joined Table A row; all 23 raw/effective columns |
| `generated/table_a_sp_links_provisional.csv` | Explicit many-to-many join of Table A row and assigned SP number |
| `generated/table_a_extraction_report.json` | PDF checksum, page coverage, row counts, exceptions and quality-gate result |

Every provisional row contains `classification_rule_status=not_authorized` and `extraction_status=provisional_unreviewed`. Even a passing quality gate is **not** legal certification.

## How to run

```bash
python -m pip install 'PyMuPDF==1.26.4' 'pdfplumber==0.11.7' 'requests==2.32.5'
python -m unittest discover -s tests -p 'test_adr2025_table_a.py' -v
python scripts/ingest_adr2025_table_a.py --self-test
python scripts/ingest_adr2025_table_a.py --pdf /path/to/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf
# or: python scripts/ingest_adr2025_table_a.py --download
```

**Actual extraction evidence:** [GitHub Actions successful run #7](https://github.com/ConorTttttt/DGR/actions/runs/43132198960) produced [review artifact](https://github.com/ConorTttttt/DGR/actions/runs/43132198960/artifacts/13905014131). It extracted **2,939 Table A rows**, **2,347 distinct UN numbers**, **2,506 UN-row/special-provision assignments** representing **331 distinct SP codes**, **126 facing-page pairs**, **zero ambiguous joins**, and **zero unparsed SP tokens**. Corr.2 UN 3423 column (20) was applied once. The source SHA-256 and all counts are retained in [table_a_extraction_manifest.json](table_a_extraction_manifest.json). The source was downloaded from a third-party mirror after the official UNECE endpoint was not accessible from CI; official equivalence should be checked before legal approval.

**Copyright and publication:** UNECE's official ADR 2025 catalogue states © United Nations, 2024, all rights reserved. This DGR repository is public. The repository intentionally **does not publish the entire extracted Table A**. Bulk extraction output is excluded from commits; establish reproduction/redistribution rights before making it public. The source documents are linked, not copied.

## Corrigenda findings

Official English Corr.1 (ECE/TRANS/352/Corr.1) changes 1.9.4 footnote 2's URL (Volume I) and a Volume II row reference to 9.2.4.4.

Official English Corr.2 (ECE/TRANS/352/Corr.2) has five Volume I items:
- 1.2.1: delete a note after the definition of Animal material;
- 1.8.8.1.4: correct cross-reference;
- 2.1.3.10 Note 2: example UN 1921 is **STABILIZED**, not **INHIBITED**;
- **3.2.1 Table A UN 3423 column (20): 688 becomes 668**;
- 3.2.2 Table B: omega-Bromoacetone index Class 6.4 becomes Class 6.1 (Table B is not authoritative).

Corr.2 also contains three Volume II updates, mapped in `corrigenda_impacts.json`. UNECE additionally lists French-only Corr.3; it is not applied to the English text. No 2027 draft regulations are folded into this 2025 edition.

## Acceptance criteria before engine integration

1. **Completed structurally**: a successful full extraction run produced the manifest and both datasets; PDF checksum and download origin are recorded. Independent equivalence to official UNECE PDF remains open.
2. Review all extraction diagnostics; row counts, facing-page matching, all special-provision code tokens and exceptional cells (e.g. `CARRIAGE PROHIBITED`) must be checked.
3. Compare a stratified sample against the **rendered official PDF**, across all classes and multirow UN entries. Current review fixtures are *not* enough.
4. Confirm each assigned SP code has a corresponding text/definition at 3.3.1; digitise and review its regulatory conditions before any executable effects.
5. Verify Corr.1 and Corr.2 impacts; test the UN 3423 correction and complete other affected clause records.
6. Conduct an independent regulatory review, with versioned approvals, before any entry may drive SDS Section 14.

## Sources

- [Official ADR 2025 edition catalogue](https://unece.org/adr-2025-files)
- [UNECE ADR 2025 Volume I PDF](https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf)
- [UNECE Corr.1 PDF](https://shop.un.org/sites/default/files/2024-09/ECE-TRANS-352c1E.pdf)
- [UNECE Corr.2 page](https://unece.org/transport/documents/2025/10/post-session-documents/adr-2025-corrigendum-2)
