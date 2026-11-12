"""Unit and fixture tests for the non-operational ADR 2025 Table A importer."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ingest_adr2025_table_a.py"
spec = importlib.util.spec_from_file_location("adr2025_table_a", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
FIXTURE = ROOT / "regulations" / "adr" / "2025" / "table_a_review_examples.json"


class TableAImporterTests(unittest.TestCase):
    def test_preserve_leading_zeros_and_exclude_broken_ids(self):
        self.assertEqual(mod.un_number("0004"), "0004")
        self.assertEqual(mod.un_number(" 0012 "), "0012")
        self.assertIsNone(mod.un_number("12"))
        self.assertIsNone(mod.un_number("UN 1203"))

    def test_sp_codes_are_tokenized_without_substring_matches(self):
        self.assertEqual(mod.special_codes("274 640C, 650"), (["274", "640C", "650"], ""))
        self.assertEqual(mod.special_codes(""), ([], ""))
        self.assertEqual(mod.special_codes("-"), ([], ""))
        self.assertEqual(mod.special_codes("SP 188"), (["188"], ""))
        self.assertNotEqual(mod.special_codes("274 garbage")[1], "")

    def test_facing_pages_require_identical_un_and_name(self):
        l = ["0012", "CARTRIDGES FOR WEAPONS, INERT PROJECTILE or CARTRIDGES, SMALL ARMS"] \
            + [""] * 12
        r = [""] * 9 + ["0012", "CARTRIDGES FOR WEAPONS, INERT PROJECTILE or CARTRIDGES, SMALL ARMS"]
        self.assertIsNone(mod.compare_pair(l, r))
        r[9] = "0014"
        self.assertEqual(mod.compare_pair(l, r), "un_number_mismatch")
        r[9] = "0012"
        r[10] = "SOME OTHER ENTRY"
        self.assertEqual(mod.compare_pair(l, r), "description_mismatch")

    def test_corr2_3423_is_guarded_and_audited(self):
        row = {
            "un_number": "3423",
            "raw_columns": {"20": "688"},
            "effective_columns": {"20": "688"},
            "corrigenda_applied": [],
            "corrigenda_already_in_source": [],
        }
        mod.patch_corr2(row)
        self.assertEqual(row["raw_columns"]["20"], "688")
        self.assertEqual(row["effective_columns"]["20"], "668")
        self.assertEqual(row["corrigenda_applied"], ["ECE/TRANS/352/Corr.2:Vol.I:item4"])
        with self.assertRaises(ValueError):
            row["raw_columns"]["20"] = "999"
            mod.patch_corr2(row)

    def test_review_examples_catch_multirow_and_prohibition(self):
        f = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data = f["examples"]
        self.assertEqual(len(data), 7)
        numbers = [x["un_number"] for x in data]
        self.assertEqual(numbers.count("0015"), 3)
        self.assertEqual([x for x in data if x["un_number"] == "0012"][0]["special_provision_codes"], ["364"])
        self.assertTrue([x for x in data if x["un_number"] == "0020"][0]["carriage_prohibited"])
        self.assertEqual(f["clause"], "3.2.1")

    def test_column_mapping_counts(self):
        self.assertEqual(len(mod.COL_L), 14)
        self.assertEqual(len(mod.COL_R), 11)
        self.assertEqual(len(mod.FIELDS_BY_COL), 23)
        self.assertEqual(set(mod.COL_L) | set(mod.COL_R), set(mod.FIELDS_BY_COL))


if __name__ == "__main__":
    unittest.main()
