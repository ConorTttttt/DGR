#!/usr/bin/env python3
"""Independent structural checks for PROVISIONAL ADR 2025 Table A output.

No legal correctness claim is made by a passing result.
"""
from __future__ import annotations
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "regulations" / "adr" / "2025" / "generated"
EXPECTED_COLUMNS = {
    "1","2","3a","3b","4","5","6","7a","7b","8","9a","9b","10","11",
    "12","13","14","15","16","17","18","19","20"
}


def main(folder: Path = OUTPUT) -> int:
    rows = [json.loads(l) for l in (folder / "table_a_rows_provisional.jsonl").open(encoding="utf-8")]
    with (folder / "table_a_sp_links_provisional.csv").open(newline="",encoding="utf-8") as fd:
        links = list(csv.DictReader(fd))
    report = json.loads((folder / "table_a_extraction_report.json").read_text(encoding="utf-8"))
    assert len(rows) == report["rows_extracted"], "Rows differ from report"
    assert len(links) == report["sp_links_extracted"], "Links differ from report"
    assert not report["diagnostics"], "Ambiguous page or row joins exist"
    assert not report["sp_parse_diagnostics"], "Unparsed special provision code exists"
    assert report["automated_quality_gate_pass"], "Automated source extraction gate failed"
    assert len(rows) >= 2500, "Unexpectedly low Table A coverage"
    assert len(report["source_pdf_sha256"]) == 64, "Missing source PDF digest"

    keys = [r["row_id"] for r in rows]
    assert len(set(keys)) == len(rows), "Duplicate Table A row IDs"
    by_id = {r["row_id"]:r for r in rows}
    sp_count = 0
    for r in rows:
        assert re.fullmatch(r"\d{4}", r["un_number"]), "UN numbers must retain 4 digits"
        assert set(r["raw_columns"]) == EXPECTED_COLUMNS, "Lost a raw Table A column"
        assert set(r["effective_columns"]) == EXPECTED_COLUMNS, "Lost a corrected column"
        assert r["raw_columns"]["1"] == r["un_number"]
        assert r["raw_columns"]["2"] == r["name_and_description"]
        assert r["extraction_status"] == "provisional_unreviewed"
        assert r["classification_rule_status"] == "not_authorized"
        assert r["left_pdf_page_1_based"] + 1 == r["right_pdf_page_1_based"]
        assert not r["special_provision_parse_unresolved"]
        sp_count += len(r["special_provision_codes"])
    assert sp_count == len(links), "SP links not exhaustive"

    linked = Counter()
    for x in links:
        r = by_id[x["row_id"]]
        assert x["un_number"] == r["un_number"], "SP join UN mismatch"
        assert x["special_provision"] in r["special_provision_codes"], "Unknown SP assignment"
        assert x["clause_ref"] == "3.3.1"
        assert x["condition_status"] == "not_evaluated"
        linked[x["row_id"],x["special_provision"]] += 1
    expected = Counter((r["row_id"], sp) for r in rows for sp in r["special_provision_codes"])
    assert linked == expected, "SP links do not match all row assignments"

    corrected = [r for r in rows if r["un_number"] == "3423"]
    assert len(corrected) == 1, "Unexpected UN 3423 row count"
    c = corrected[0]
    assert c["raw_columns"]["20"] in {"688","668"}
    assert c["effective_columns"]["20"] == "668", "Corr.2 not applied"
    assert c["corrigenda_applied"] or c["corrigenda_already_in_source"]

    # Baselines aid regression detection; they are observations of this PDF,
    # not independent legal certification or universal edition expectations.
    print(json.dumps({
        "rows": len(rows),
        "distinct_un_numbers":len({r["un_number"] for r in rows}),
        "duplicate_un_groups": sum(v > 1 for v in Counter(r["un_number"] for r in rows).values()),
        "special_provision_links":len(links),
        "distinct_sp_codes": len({x["special_provision"] for x in links}),
        "carriage_prohibited_indications":sum(r["carriage_prohibited_indication"] for r in rows),
        "source_pdf_sha256":report["source_pdf_sha256"],
        "quality":"STRUCTURE_ONLY_PASS_NO_LEGAL_APPROVAL"
    },indent=2))
    return 0


if __name__=="__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv)>1 else OUTPUT))
