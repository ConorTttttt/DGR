#!/usr/bin/env python3
"""Structural checks for the ADR 2025 regulatory index.

This tests the dataset's schema and referential integrity; it does NOT validate
the legal accuracy of clause interpretations or implement classification rules.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "regulations" / "adr" / "2025"


def csv_rows(filename: str) -> list[dict[str, str]]:
    with (BASE / filename).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check() -> None:
    sources = json.loads((BASE / "sources.json").read_text(encoding="utf-8"))
    dgl = json.loads((BASE / "dgl_table_a_columns.json").read_text(encoding="utf-8"))
    clauses = csv_rows("clause_register.csv")
    provisions = csv_rows("special_provisions_focus.csv")
    eq_codes = csv_rows("excepted_quantity_codes.csv")

    require(sources["edition"] == "2025", "Incorrect edition in source manifest")
    require(sources["effective_from"] == "2025-01-01", "Unexpected applicability date")
    source_ids = {item["id"] for item in sources["primary_sources"] + sources["related_sources"]}
    require("adr2025_vol1_en" in source_ids, "Missing authoritative Volume I reference")
    require(len(clauses) == 132, "Clause index row count changed: review test baselines")
    require(len(provisions) == 62, "SP focus index row count changed: review test baselines")
    require(len(eq_codes) == 6, "E0–E5 code table must have six records")

    refs = set()
    ids = set()
    parts = {"1": 0, "2": 0, "3": 0}
    for record in clauses:
        ref = record["clause_ref"]
        require(re.fullmatch(r"[123](?:\.\d+)+", ref) is not None,
                f"Invalid or out-of-scope clause ref: {ref}")
        require(ref not in refs, f"Duplicate clause ref: {ref}")
        require(record["register_id"] not in ids, "Duplicate clause record ID")
        refs.add(ref)
        ids.add(record["register_id"])
        part = ref.partition(".")[0]
        parts[part] += 1
        require(record["part"] == part, f"Wrong part for clause {ref}")
        require(record["edition"] == "2025", f"Wrong edition for clause {ref}")
        require(record["source_id"] == "adr2025_vol1_en", "Wrong primary source")
        require(record["source_url"].startswith("https://unece.org/"), "Missing official source link")
        require(record["machine_rule_state"] == "not_encoded",
                "Do not mark as executable without reviewed tests")
    require(parts == {"1": 26, "2": 70, "3": 36}, f"Unexpected part coverage: {parts}")

    sp_numbers = set()
    for record in provisions:
        code = record["sp_code"]
        require(re.fullmatch(r"\d+", code) is not None, f"Bad SP code: {code}")
        require(code not in sp_numbers, f"Duplicate SP: {code}")
        sp_numbers.add(code)
        require(record["clause_ref"] == "3.3.1", f"Incorrect SP clause: {code}")
        require(record["dgl_un_number_binding"] == "not_ingested",
                "SP/UN binding status is invalid")
    require("673" not in sp_numbers, "SP 673 is reserved in this edition")

    columns = dgl["columns"]
    observed = [c["column"] for c in columns]
    expected = [
        "1", "2", "3a", "3b", "4", "5", "6", "7a", "7b",
        "8", "9a", "9b", "10", "11", "12", "13", "14", "15",
        "16", "17", "18", "19", "20"
    ]
    require(observed == expected, "Missing or reordered Table A columns")
    require(dgl["column_count"] == len(expected), "Wrong Table A subcolumn count")
    require(dgl["ingestion_status"] == "field_schema_only_no_un_rows_ingested",
            "Do not claim UN rows ingested without actual Table A data")

    eq_expected = {
        "E0": ("", "", "false"),
        "E1": ("30", "1000", "true"),
        "E2": ("30", "500", "true"),
        "E3": ("30", "300", "true"),
        "E4": ("1", "500", "true"),
        "E5": ("1", "300", "true"),
    }
    eq_by_code = {row["code"]: row for row in eq_codes}
    require(set(eq_by_code) == set(eq_expected), "EQ code set differs from 3.5.1.2")
    for code, (inner, outer, permitted) in eq_expected.items():
        row = eq_by_code[code]
        require(row["net_max_inner_g_or_ml"] == inner, f"Wrong inner limit: {code}")
        require(row["net_max_outer_g_or_ml"] == outer, f"Wrong outer limit: {code}")
        require(row["excepted_quantity_permitted"] == permitted,
                f"Wrong EQ eligibility: {code}")
        require(row["clause_ref"] == "3.5.1.2", f"Wrong source clause: {code}")

    print(f"ADR 2025 KB structural checks PASS: {len(clauses)} clauses, "
          f"{len(provisions)} focused SPs, {len(columns)} DGL subcolumns, "
          f"{len(eq_codes)} EQ codes.")
    print("Regulatory review, full UN table ingestion, and corrigenda reconciliation remain open.")


if __name__ == "__main__":
    try:
        check()
    except (AssertionError, KeyError, ValueError, OSError) as exc:
        print(f"ADR 2025 KB structural checks FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
