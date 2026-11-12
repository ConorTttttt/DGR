"""Synthetic-only regression; no real explosive classification or CA approval is asserted."""
import copy
import unittest
from agents.class1_explosives.evaluator import evaluate

CODES = ("1.1A 1.1B 1.1C 1.1D 1.1E 1.1F 1.1G 1.1L "
         "1.2B 1.2C 1.2D 1.2E 1.2F 1.2L "
         "1.3C 1.3G 1.3L 1.4B 1.4C 1.4D 1.4E 1.4F 1.4G 1.4S 1.5D 1.6N").split()

def sample(code="1.1A"):
    series = {"1.5": ["5", "6"], "1.6": ["7"]}.get(code[:3], ["6"])
    return {
        "assessment_id": "synthetic-only", "regime": "ADR", "edition": "2025",
        "product_kind": "substance", "hazard_screen": "confirmed_explosive",
        "evidence": [
            {"id": "ca", "kind": "authority_document", "source_id": "synthetic",
             "locator": "dummy", "sha256": "a"*64, "admissibility": "verified"},
            {"id": "ts", "kind": "test_report", "source_id": "synthetic",
             "locator": "dummy", "sha256": "b"*64, "admissibility": "verified"}
        ],
        "test_series": [
            {"series": s, "result": "recorded", "evidence_id": "ts",
             "assessed_by_expert": True} for s in series
        ],
        "authority": {
            "status": "approved", "decision_id": "SYN-CA", "document_ref": "ca",
            "verification": "externally_verified", "scope_matches": True,
            "approved_code": code, "approved_un_number": "9999",
            "approved_row_id": "SYN-ROW"
        },
        "candidate": {
            "division": code[:3], "group": code[3:], "un_number": "9999",
            "table_a_row_id": "SYN-ROW", "table_a_row_status": "source_verified",
            "entry_is_applicable": True, "n_o_s_or_sample": False,
            "competent_authority_conditions_complete": True
        },
        "special_provisions": [
            {"code": "SYN", "status": "does_not_apply", "evidence_ids": ["ts"]}
        ], "cross_class_flags": []
    }

class Class1Gate(unittest.TestCase):
    def chk(self, r, expected):
        out = evaluate(r)
        self.assertEqual(out["status"], expected)
        self.assertFalse(out["assignment_permitted"])
        self.assertTrue(out["requires_independent_review"])
        self.assertEqual(out["packing_group_candidates"], [])
        return out

    def test_collective_codes_all_divisions_and_group_coverage(self):
        for code in CODES:
            with self.subTest(code=code):
                out = self.chk(sample(code), "criteria_met")
                self.assertEqual(out["primary_class_candidates"][0]["classification_code"], code)
                self.assertIsNone(out["primary_class_candidates"][0]["packing_group"])
        self.assertEqual({x[:3] for x in CODES}, {"1.1","1.2","1.3","1.4","1.5","1.6"})

    def test_named_entry_synthetic_h_j(self):
        for code in ("1.1H", "1.1J"):
            self.chk(sample(code), "criteria_met")  # Source row authenticity is external.
    def test_group_k(self):
        self.chk(sample("1.2K"), "prohibited_for_carriage")
    def test_no_test_and_missing_series5_7(self):
        for code in ("1.1A", "1.5D", "1.6N"):
            r=sample(code); r["test_series"]=[]
            self.chk(r, "indeterminate")
    def test_missing_or_expired_authority(self):
        for state in ("pending", "rejected", "expired", "not_provided"):
            r=sample();r["authority"]["status"]=state
            self.chk(r,"authority_required")
    def test_authority_mismatch(self):
        r=sample();r["authority"]["approved_code"]="1.4S";self.chk(r,"conflict")
        r=sample();r["authority"]["approved_row_id"]="different";self.chk(r,"conflict")
    def test_missing_evidence_not_global_non_dg(self):
        for s,exp in [("not_assessed","indeterminate"),("suspected","authority_required"),("confirmed_no_explosive_properties","authority_required")]:
            r=sample();r["hazard_screen"]=s;self.chk(r,exp)
    def test_verified_exclusion_is_class_scoped(self):
        r=sample();r["hazard_screen"]="excluded_approved"
        out=self.chk(r,"excluded_from_class")
        self.assertFalse(out["primary_class_candidates"])
        self.assertTrue(out["exclusions"])
    def test_sp_and_table_a(self):
        r=sample();r["candidate"]["table_a_row_status"]="provisional";self.chk(r,"indeterminate")
        r=sample();r["special_provisions"][0]["status"]="uncertain";self.chk(r,"indeterminate")
        r=sample();r["special_provisions"][0]["status"]="prohibits";self.chk(r,"prohibited_for_carriage")
    def test_other_nonacceptance(self):
        for x in ("spontaneous_reaction","unduly_sensitive","no_legal_table_a_entry"):
            r=sample();r["cross_class_flags"]=[x];self.chk(r,"prohibited_for_carriage")
    def test_fireworks_analogy(self):
        r=sample("1.4G");r["product_kind"]="pyrotechnic_article"
        r["test_series"]=[];r["cross_class_flags"]=["fireworks_analogy"]
        self.chk(r,"indeterminate")
        r["cross_class_flags"].append("packaging_dependent")
        self.chk(r,"criteria_met")
    def test_un0190(self):
        r=sample();r["candidate"]["n_o_s_or_sample"]=True
        r["candidate"]["competent_authority_conditions_complete"]=False
        self.chk(r,"authority_required")
    def test_other_edition_rejected(self):
        r=sample();r["edition"]="2027"
        with self.assertRaises(ValueError):evaluate(r)

if __name__ == "__main__": unittest.main()
