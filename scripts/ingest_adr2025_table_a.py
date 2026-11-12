#!/usr/bin/env python3
"""Extract ADR 2025 Table A into provenance-bearing, non-executable review data.

Requires the official ECE/TRANS/352 Volume I PDF. Table A is printed over
facing pages: left page columns 1-11, right page columns 12-20, with repeated
UN numbers and descriptions. NO row is accepted unless the pair matches.

All rows are PROVISIONAL. This is not a legal-validation or classification tool.

Usage:
  python scripts/ingest_adr2025_table_a.py --pdf /path/to/volume1.pdf
  python scripts/ingest_adr2025_table_a.py --download
  python scripts/ingest_adr2025_table_a.py --self-test
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

SOURCE_URL = "https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf"
SOURCE_LANDING = "https://unece.org/transport/documents/2025/01/standards/adr-2025-volume-1"
# Network fallback is the same UN publication hosted by third parties,
# NOT a substitute legal authority; actual download origin is retained.
MIRRORS = [
    "https://www.euraca.eu/media/ewof3ibp/adr-2025-vol-i.pdf",
    "https://www.idgca.org/doc/ADR_2025_vol_1_e.pdf",
]
CORR2_URL = "https://unece.org/transport/documents/2025/10/post-session-documents/adr-2025-corrigendum-2"
COL_L = ("1","2","3a","3b","4","5","6","7a","7b","8","9a","9b","10","11")
COL_R = ("12","13","14","15","16","17","18","19","20","1","2")
DGL_KEYS = (
    "un_number", "proper_shipping_name_description", "hazard_class",
    "classification_code", "packing_group", "labels", "special_provisions",
    "limited_quantities", "excepted_quantities", "packing_instructions",
    "special_packing_provisions", "mixed_packing_provisions",
    "portable_tank_bulk_container_instructions",
    "portable_tank_bulk_container_special_provisions", "adr_tank_code",
    "adr_tank_special_provisions", "tank_vehicle",
    "transport_category_tunnel_restriction_code",
    "packages_transport_provisions", "bulk_transport_provisions",
    "loading_unloading_handling_provisions", "carriage_operation_provisions",
    "hazard_identification_number",
)
FIELDS_BY_COL = dict(zip(
    ("1","2","3a","3b","4","5","6","7a","7b","8","9a","9b","10","11",
     "12","13","14","15","16","17","18","19","20"), DGL_KEYS,
))
assert len(FIELDS_BY_COL) == 23
RE_NUMBER = re.compile(r"^\d{4}$")
RE_SP = re.compile(r"(?<!\w)(?:SP\s*)?(\d{1,3}[A-Z]?)(?!\w)")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "regulations" / "adr" / "2025" / "generated"
PDF_CACHE = ROOT / ".cache" / "adr2025-vol1.pdf"
TABLE_KW = "DANGEROUS GOODS LIST"


def cleaned(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\u00ad", "")).strip()


def simple(value: object) -> str:
    # Compare repeated names without PDF's line wrapping, punctuation or case.
    return re.sub(r"[^a-z0-9]+", "", cleaned(value).lower())


def un_number(value: object) -> str | None:
    s = cleaned(value).replace(" ", "")
    return s if RE_NUMBER.fullmatch(s) else None


def special_codes(value: object) -> tuple[list[str], str]:
    text = cleaned(value).upper()
    if not text or text in {"-", "—"}:
        return [], ""
    codes = RE_SP.findall(text)
    residual = RE_SP.sub(" ", text)
    residual = re.sub(r"[\s,;/\-—]+", "", residual)
    return codes, residual


def identify_numbered_table(table: list[list[object]]) -> tuple[str, list[list[str]]] | None:
    """Return side and data rows after the printed column-number header."""
    for i, row in enumerate(table):
        h = {re.sub(r"\s+", "", cleaned(x)).lower() for x in row}
        side = None
        if {"(1)", "(2)", "(3a)", "(3b)"}.issubset(h):
            side = "left"
            expect = len(COL_L)
        elif {"(12)", "(13)", "(20)"}.issubset(h):
            side = "right"
            expect = len(COL_R)
        if side is None:
            continue
        if len(row) != expect:
            continue
        data = []
        for r in table[i + 1:]:
            values = [cleaned(x) for x in r]
            if len(values) != expect:
                continue
            anchor = values[0] if side == "left" else values[-2]
            if un_number(anchor):
                data.append(values)
        return side, data
    return None


def read_page_table(page, index: int) -> tuple[str, list[list[str]]] | None:
    # PDF is digitally typeset with rules. Prefer strict lines, then a more
    # permissive strategy, without ever guessing or reordering columns.
    for strategy in ("lines", "lines_strict"):
        settings = {
            "vertical_strategy": strategy,
            "horizontal_strategy": strategy,
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "intersection_tolerance": 4,
        }
        for table in page.extract_tables(table_settings=settings):
            result = identify_numbered_table(table)
            if result and result[1]:
                return result
    return None


def compare_pair(left: list[str], right: list[str]) -> str | None:
    if len(left) != len(COL_L) or len(right) != len(COL_R):
        return "column_count_mismatch"
    if not un_number(left[0]) or not un_number(right[-2]):
        return "un_number_not_four_digits"
    if left[0] != right[-2]:
        return "un_number_mismatch"
    if not simple(left[1]) or simple(left[1]) != simple(right[-1]):
        return "description_mismatch"
    return None


def patch_corr2(row: dict) -> None:
    """Apply only the explicit English corrigendum to Table A UN 3423 col 20.

    ECE/TRANS/352/Corr.2, Volume I, item 4: 688 -> 668.
    Preserve unchanged PDF cell in 'raw_columns'. Do not silently rewrite
    other fields or infer an effective date for this editorial corrigendum.
    """
    if row["un_number"] != "3423":
        return
    raw = row["raw_columns"]["20"]
    if raw == "688":
        row["effective_columns"]["20"] = "668"
        row["corrigenda_applied"].append("ECE/TRANS/352/Corr.2:Vol.I:item4")
    elif raw == "668":
        row["corrigenda_already_in_source"].append("ECE/TRANS/352/Corr.2:Vol.I:item4")
    else:
        raise ValueError(f"UN 3423 unexpected col(20) {raw!r}; must inspect source")


def validate_pdf(pdf_path: Path):
    import fitz
    document = fitz.open(pdf_path)
    cover = " ".join(document[i].get_text() for i in range(min(4, len(document))))
    compact = re.sub(r"\s+", "", cover).upper()
    if "ECE/TRANS/352" not in compact or "2025" not in cover or "VOL.I" not in compact:
        raise ValueError("Not independently identified as ECE/TRANS/352 (Vol.I), ADR 2025")
    if not 500 <= len(document) <= 1000:
        raise ValueError(f"Unexpected Volume I page count: {len(document)}")
    return document


def fetch_pdf(target: Path) -> str:
    import requests
    target.parent.mkdir(parents=True, exist_ok=True)
    urls = [SOURCE_URL, *MIRRORS]
    failures = []
    for url in urls:
        try:
            response = requests.get(url, timeout=(20, 180),
                                    headers={"User-Agent": "DGR-Regulatory-KB/0.1 (+public research)"},
                                    stream=True)
            response.raise_for_status()
            with target.open("wb") as dst:
                for b in response.iter_content(1024 * 1024):
                    if b:
                        dst.write(b)
            if target.stat().st_size < 7_000_000:
                raise ValueError("Downloaded PDF unexpectedly small")
            doc = validate_pdf(target)
            doc.close()
            return url
        except Exception as err:
            failures.append(f"{url}: {type(err).__name__}: {err}")
            target.unlink(missing_ok=True)
    raise RuntimeError("No usable Volume I PDF:\n" + "\n".join(failures))


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compile_table(pdf_path: Path, retrieved_from: str, output_dir: Path) -> dict:
    import pdfplumber
    doc = validate_pdf(pdf_path)
    pdf_sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    text_per_page = [p.get_text("text") for p in doc]
    boundaries = [i for i, t in enumerate(text_per_page)
                  if re.search(r"\bTABLE A\s+DANGEROUS GOODS LIST\b", t[:700].upper()) and i > 100]
    if not boundaries:
        raise RuntimeError("Cannot identify Table A start")
    start = boundaries[0]
    end = next((i for i in range(start + 1, len(doc))
                if "CHAPTER 3.3" in text_per_page[i].upper()), len(doc))
    doc.close()

    indexed_pages: list[dict] = []
    diagnostics: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index in range(start, end):
            page = pdf.pages[page_index]
            found = read_page_table(page, page_index)
            if not found:
                if "UN" in text_per_page[page_index].upper() and "NO" in text_per_page[page_index].upper():
                    diagnostics.append({"issue": "table_not_detected", "pdf_page": page_index + 1})
                continue
            side, rows = found
            indexed_pages.append({"pdf_page": page_index + 1, "side": side, "rows": rows})

    matched: list[tuple[dict, dict]] = []
    n = 0
    while n < len(indexed_pages):
        p = indexed_pages[n]
        if p["side"] != "left":
            diagnostics.append({"issue": "orphan_right_page", "pdf_page": p["pdf_page"]})
            n += 1
            continue
        if n + 1 >= len(indexed_pages) or indexed_pages[n + 1]["side"] != "right":
            diagnostics.append({"issue": "unpaired_left_page", "pdf_page": p["pdf_page"]})
            n += 1
            continue
        q = indexed_pages[n + 1]
        if q["pdf_page"] != p["pdf_page"] + 1:
            diagnostics.append({"issue": "nonconsecutive_facing_pages",
                                "left_page": p["pdf_page"], "right_page": q["pdf_page"]})
        matched.append((p, q))
        n += 2

    rows: list[dict] = []
    links: list[dict] = []
    sp_oddities = []
    for left_page, right_page in matched:
        ls, rs = left_page["rows"], right_page["rows"]
        if len(ls) != len(rs):
            diagnostics.append({"issue": "different_row_count",
                                "left_page": left_page["pdf_page"],
                                "right_page": right_page["pdf_page"],
                                "left_count": len(ls), "right_count": len(rs)})
            continue
        for row_i, (l, r) in enumerate(zip(ls, rs), start=1):
            issue = compare_pair(l, r)
            if issue:
                diagnostics.append({
                    "issue": issue, "left_page": left_page["pdf_page"],
                    "right_page": right_page["pdf_page"], "page_row": row_i,
                    "left_un": l[0], "right_un": r[-2],
                    "left_desc": l[1], "right_desc": r[-1],
                })
                continue
            raw = dict(zip(COL_L, l))
            raw.update(zip(COL_R, r))  # repeated (1)/(2) verified
            codes, residue = special_codes(raw.get("6", ""))
            if residue:
                sp_oddities.append({
                    "pdf_page": left_page["pdf_page"], "un_number": l[0],
                    "raw": raw["6"], "unparsed_remainder": residue
                })
            row_id = f"ADR25-TA-{len(rows)+1:06d}"
            item = {
                "row_id": row_id, "regulation": "ADR", "edition": "2025",
                "document": "ECE/TRANS/352 (Vol.I)", "clause_ref": "3.2.1",
                "source_url": SOURCE_URL, "retrieved_from": retrieved_from,
                "source_pdf_sha256": pdf_sha,
                "left_pdf_page_1_based": left_page["pdf_page"],
                "right_pdf_page_1_based": right_page["pdf_page"],
                "page_row_1_based": row_i, "un_number": l[0],
                "name_and_description": l[1], "raw_columns": raw,
                "effective_columns": dict(raw),
                "special_provision_codes": codes,
                "special_provision_parse_unresolved": bool(residue),
                "carriage_prohibited_indication": any(
                    "CARRIAGE PROHIBITED" in v.upper() for v in raw.values()),
                "corrigenda_applied": [],
                "corrigenda_already_in_source": [],
                "extraction_status": "provisional_unreviewed",
                "classification_rule_status": "not_authorized",
            }
            patch_corr2(item)
            rows.append(item)
            for sp in codes:
                links.append({
                    "row_id": row_id, "un_number": l[0],
                    "special_provision": sp, "clause_ref": "3.3.1",
                    "table_a_column": "6",
                    "left_pdf_page_1_based": left_page["pdf_page"],
                    "source_url": SOURCE_URL,
                    "condition_status": "not_evaluated",
                })
    pages = Counter(x["side"] for x in indexed_pages)
    report = {
        "schema_version": "1.0.0", "regulation": "ADR", "edition": "2025",
        "source_document": "ECE/TRANS/352 (Vol.I)", "source_url": SOURCE_URL,
        "download_origin": retrieved_from, "source_pdf_sha256": pdf_sha,
        "source_pdf_pages": len(text_per_page),
        "table_a_page_range_1_based": [start + 1, end],
        "detected_left_pages": pages["left"],
        "detected_right_pages": pages["right"],
        "matched_page_pairs": len(matched),
        "rows_extracted": len(rows),
        "unique_un_numbers": len(set(x["un_number"] for x in rows)),
        "sp_links_extracted": len(links),
        "unparsed_sp_codes": len(sp_oddities),
        "un3423_rows": len([r for r in rows if r["un_number"] == "3423"]),
        "corr2_3423_applied": sum(bool(r["corrigenda_applied"]) for r in rows),
        "diagnostics": diagnostics,
        "sp_parse_diagnostics": sp_oddities,
        "automated_quality_gate_pass": (
            len(rows) >= 2500
            and len(matched) >= 80
            and not diagnostics
            and not sp_oddities
            and any(r["un_number"] == "3423" for r in rows)
        ),
        "independent_legal_review": "not_performed",
        "classification_use_permitted": False,
        "note": "Passing automated gates does NOT validate legal or source correctness.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out_rows = output_dir / "table_a_rows_provisional.jsonl"
    with out_rows.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    out_links = output_dir / "table_a_sp_links_provisional.csv"
    fields = ("row_id", "un_number", "special_provision", "clause_ref",
              "table_a_column", "left_pdf_page_1_based", "source_url", "condition_status")
    with out_links.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(links)
    save_json(output_dir / "table_a_extraction_report.json", report)
    return report


def self_test() -> None:
    left = ["0015", "AMMUNITION, SMOKE containing corrosive substances",
            "1","1.2G","","1 +8","","0","E0","P130","","MP23","",""]
    right = ["","","","1 (B)","","","","","","0015",
             "AMMUNITION, SMOKE  containing   corrosive substances"]
    assert compare_pair(left, right) is None
    right[-2] = "0016"
    assert compare_pair(left, right) == "un_number_mismatch"
    right[-2] = "0015"
    right[-1] = "AMMUNITION, SMOKE containing toxic substances"
    assert compare_pair(left, right) == "description_mismatch"
    assert special_codes("274 640C, 650") == (["274", "640C", "650"], "")
    assert special_codes("") == ([], "")
    item = {"un_number":"3423","raw_columns":{"20":"688"},
            "effective_columns":{"20":"688"}, "corrigenda_applied":[],
            "corrigenda_already_in_source":[]}
    patch_corr2(item)
    assert item["raw_columns"]["20"] == "688"
    assert item["effective_columns"]["20"] == "668"
    try:
        patch_corr2({"un_number":"3423","raw_columns":{"20":"699"},
                    "effective_columns":{"20":"699"}, "corrigenda_applied":[],
                    "corrigenda_already_in_source":[]})
    except ValueError:
        pass
    else:
        raise AssertionError("Corrigendum must refuse unexpected original values")
    print("synthetic extraction unit tests PASS (NOT a legal validation)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=None)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if bool(args.pdf) == bool(args.download):
        parser.error("Choose exactly one of --pdf or --download")
    if args.download:
        path = PDF_CACHE
        origin = fetch_pdf(path)
    else:
        path = args.pdf
        origin = "operator_supplied_file"
    result = compile_table(path, origin, args.out)
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ("diagnostics", "sp_parse_diagnostics")}, indent=2))
    if not result["automated_quality_gate_pass"]:
        print(f"WARNING: automated extraction incomplete or ambiguous: "
              f"{len(result['diagnostics'])} structural diagnostics, "
              f"{result['unparsed_sp_codes']} SP parsing diagnostics", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
