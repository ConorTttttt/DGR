"""Synthetic-only Agent 14 integration tests. All rows and substances are MOCKS."""
import unittest
from precedence import evaluate, MATRIX, CLASSES


def evidence(i):
    return {"evidence_id":i,"state":"known","field_id":i,"value":True,
            "sample_id":"SYNTHETIC","review_state":"unreviewed",
            "references":[{"source_id":"ADR25_VOL1","clause":"2.1.2.1"}],
            "source_documents":[{"document_id":i,"kind":"test_result",
                                 "locator":"synthetic://"+i,"sha256":"0"*64,
                                 "issuer":"SYNTHETIC_ONLY","authenticated":False}]}


def packet(*items):
    given=dict(items)
    es=[]
    fs=[]
    for c in CLASSES:
        eid="E"+c.replace(".","")
        es.append(evidence(eid))
        pc=c in given
        pg=given.get(c)
        fs.append({"module_id":"synthetic-"+c,"hazard_class":c,
                   "coverage_status":"evaluated",
                   "criteria_status":"criteria_met" if pc else "criteria_not_met",
                   "evidence_ids":[eid],"references":[{"source_id":"ADR25_VOL1",
                   "clause":"2.2.x.1 mock only"}],
                   "primary_class_candidates":([{"candidate_id":"C"+c,"hazard_class":c,
                    "evidence_ids":[eid],"references":[{"source_id":"ADR25_VOL1",
                    "clause":"2.2.x.1 mock only"}]}] if pc else []),
                   "packing_group_candidates":([{"candidate_id":"PG"+c,"value":pg,
                    "evidence_ids":[eid],"references":[{"source_id":"ADR25_VOL1",
                    "clause":"2.2.x.1 mock only"}]}] if pg else []),
                   "subsidiary_risk_candidates":[],"exclusions":[],
                   "unresolved_evidence":[],"expert_decision_ids":[],
                   "rule_ids":["SYNTH-"+c]})
    return {"contract_version":"0.1.0","regulatory_context":{
                "regime":"ADR","edition_id":"ADR-2025-EN",
                "source_set_id":"adr2025-en-provisional-v1",
                "language":"en","evaluation_date":"2026-11-13"},
            "sample_id":"SYNTHETIC","evidence":es,"class_evaluations":fs}


def add(p,name):
    key="E"+name
    p["evidence"].append(evidence(key))
    return key


def context(p,form="LIQ"):
    return {"material_form":{"status":"known","value":form,"evidence_ids":[add(p,"FORM")]},
            "absolute_subtypes":{c:{"status":"does_not_apply",
                                     "evidence_ids":[add(p,"SUB"+c)]}
                                 for c in ("3","4.1","4.2")},
            "toxicity_route":{"status":"known","value":"ORAL",
                              "evidence_ids":[add(p,"ROUTE")]},
            "radioactive_exception":{"status":"does_not_apply",
                                     "evidence_ids":[add(p,"RAD")]},
            "inhalation_corrosive_exception":{"status":"does_not_apply",
                                              "evidence_ids":[add(p,"CARVE")]},
            "pesticide":{"status":"does_not_apply","evidence_ids":[add(p,"PEST")]},
            "oxidizer_explosive_screen":"cleared"}


def selected(cl,pg,labels,sps=""):
    # UN 9999 is an intentionally FICTIONAL unit-test value, NOT a UN assignment.
    return {"selector_status":"table_a_verified","candidate_set_complete":True,
            "named_entry_screening":"complete",
            "selected_row":{"row_id":"MOCK-ROW-NOT-ADR","source_id":"ADR25_VOL1",
                "un_number":"9999","proper_shipping_name":"MOCK ENTRY NOT IN ADR",
                "verification":{"edition":"ADR-2025-EN","identity":True,
                                "column_cells":True,"corrigenda":True},
                "columns":{"3a":cl,"3b":"MOCK","4":pg or "",
                           "5":"+".join(labels),"6":sps},
                "verified_label_classes":labels,"label_cell_verified":True},
            "special_provision_outcomes":[]}


def code(result):
    return result["blocking_issues"][0]["code"] if result["blocking_issues"] else None


class DataTests(unittest.TestCase):
    def test_grid_198_exact_cells(self):
        self.assertEqual(sum(len(r["values"]) for r in MATRIX["rows"].values()),198)
        self.assertEqual(len(MATRIX["rows"]),22)
        self.assertEqual(len(MATRIX["columns"]),18)
        for r in MATRIX["rows"].values():
            self.assertEqual(len(r["values"]),18-r["start"])
            for x in r["values"]:
                if isinstance(x,dict):self.assertEqual(set(x),{"SOL","LIQ"})

    def test_source_edition(self):
        self.assertEqual(MATRIX["edition"],"ADR-2025-EN")
        self.assertEqual(MATRIX["source_pdf_page"],127)


class HazardTests(unittest.TestCase):
    def test_one_hazard_no_row(self):
        r=evaluate(packet(("3","II")))
        self.assertEqual(code(r),"TABLE_A_ROW_MISSING")
        self.assertEqual(r["provisional_precedence"]["class"],"3")
        self.assertIsNone(r["un_number"])

    def test_synthetic_matched_row(self):
        r=evaluate(packet(("3","II")),selection=selected("3","II",["3"]))
        self.assertEqual((r["status"],r["packing_group"]),
                         ("RECONCILED_PROVISIONAL","II"))
        self.assertFalse(r["publishable"])
        self.assertFalse(r["assignment_permitted"])

    def test_all_negative_not_a_global_negative(self):
        self.assertEqual(code(evaluate(packet())),"NO_GLOBAL_NEGATIVE")

    def test_one_missing_class(self):
        p=packet(("3","II"))
        p["class_evaluations"].pop()
        self.assertEqual(code(evaluate(p)),"SCREENING_INCOMPLETE")

    def test_unresolved_evidence(self):
        p=packet(("3","II"))
        p["evidence"][0]["state"]="unknown"
        self.assertEqual(code(evaluate(p)),"SCREENING_INCOMPLETE")

    def test_conflicting_pg_candidates(self):
        p=packet(("3","II"))
        f=next(x for x in p["class_evaluations"] if x["hazard_class"]=="3")
        f["packing_group_candidates"].append({**f["packing_group_candidates"][0],
                                                "value":"III"})
        self.assertEqual(code(evaluate(p)),"SCREENING_INCOMPLETE")

    def test_exact_matrix_3ii_8i(self):
        p=packet(("3","II"),("8","I"))
        r=evaluate(p,context(p),selected("8","I",["3","8"]))
        self.assertEqual((r["primary_class"],r["packing_group"]),("8","I"))
        self.assertEqual(r["subsidiary_classes"],["3"])

    def test_solid_liquid_split(self):
        for form,exp,pg in (("SOL","4.1",None),("LIQ","3","II")):
            with self.subTest(form=form):
                p=packet(("3","II"),("4.1","II"))
                r=evaluate(p,context(p,form))
                self.assertEqual(r["provisional_precedence"]["class"],exp)
                self.assertEqual(r["provisional_precedence"]["packing_group"],pg)

    def test_missing_form(self):
        p=packet(("3","II"),("4.1","II"))
        x=context(p);x.pop("material_form")
        self.assertEqual(code(evaluate(p,x)),"PHYSICAL_FORM_UNKNOWN")

    def test_adr_2_1_3_10_note_1_three_hazards(self):
        p=packet(("3","III"),("6.1","II"),("8","I"))
        r=evaluate(p,context(p))
        self.assertEqual((r["provisional_precedence"]["class"],
                          r["provisional_precedence"]["packing_group"]),("8","I"))

    def test_toxicity_route_missing(self):
        p=packet(("3","II"),("6.1","II"))
        x=context(p);x.pop("toxicity_route")
        self.assertEqual(code(evaluate(p,x)),"TOXICITY_ROUTE_UNRESOLVED")

    def test_pesticide_footnote(self):
        for applies,expected in ((True,"6.1"),(False,"3")):
            p=packet(("3","III"),("6.1","III"))
            x=context(p);x["pesticide"]["status"]="applies" if applies else "does_not_apply"
            r=evaluate(p,x)
            self.assertEqual(r["provisional_precedence"]["class"],expected)

    def test_class1_absolute(self):
        p=packet(("1",None),("3","II"))
        r=evaluate(p,context(p))
        self.assertEqual(r["provisional_precedence"]["class"],"1")
        self.assertEqual(r["trace"][1]["clause"],"2.1.3.5.3(b)")

    def test_class2_absolute(self):
        p=packet(("2",None),("3","II"))
        self.assertEqual(evaluate(p,context(p))["provisional_precedence"]["class"],"2")

    def test_class52_absolute_without_pg(self):
        p=packet(("5.2",None),("3","II"))
        r=evaluate(p,context(p),selected("5.2",None,["3","5.2"]))
        self.assertEqual((r["primary_class"],r["packing_group"]),("5.2",None))

    def test_class7_without_sp290(self):
        p=packet(("7",None),("3","II"))
        self.assertEqual(evaluate(p,context(p))["provisional_precedence"]["class"],"7")

    def test_class7_excepted_sp290(self):
        p=packet(("7",None),("3","II"))
        x=context(p)
        x["radioactive_exception"]={"status":"applies","sp290_verified":True,
             "un3507":False,"evidence_ids":[add(p,"RADSP290")]}
        self.assertEqual(evaluate(p,x)["provisional_precedence"]["class"],"3")

    def test_class7_unverified_sp290(self):
        p=packet(("7",None),("3","II"))
        x=context(p);x["radioactive_exception"]["status"]="applies"
        self.assertEqual(code(evaluate(p,x)),"SP290_UN3507_EXCEPTION_UNVERIFIED")

    def test_6_1_inhalation_pg1_absolute(self):
        p=packet(("6.1","I"),("3","II"))
        x=context(p);x["toxicity_route"]["value"]="INHAL"
        self.assertEqual(evaluate(p,x)["provisional_precedence"]["class"],"6.1")

    def test_6_1_corrosive_exception(self):
        p=packet(("6.1","I"),("8","I"))
        x=context(p);x["toxicity_route"]["value"]="INHAL"
        x["inhalation_corrosive_exception"]["status"]="applies"
        self.assertEqual(evaluate(p,x)["provisional_precedence"]["class"],"8")

    def test_oxidizer_explosive_gate(self):
        p=packet(("5.1","II"),("3","II"))
        x=context(p);x["oxidizer_explosive_screen"]="unknown"
        self.assertEqual(code(evaluate(p,x)),"OXIDIZER_EXPLOSIVE_SCREEN_UNRESOLVED")

    def test_packing_group_blank_cell_contradiction(self):
        p=packet(("8","II"))
        self.assertEqual(code(evaluate(p,selection=selected("8",None,["8"]))),
                         "MATRIX_ROW_PG_CONTRADICTION")

    def test_row_class_conflict(self):
        p=packet(("3","II"))
        self.assertEqual(code(evaluate(p,selection=selected("8","II",["8"]))),
                         "ROW_CLASS_CONTRADICTION")

    def test_row_subsidiary_conflict(self):
        p=packet(("3","II"),("8","I"))
        self.assertEqual(code(evaluate(p,context(p),selected("8","I",["8"]))),
                         "SUBSIDIARY_LABEL_CONTRADICTION")

    def test_sp_missing(self):
        p=packet(("3","II"))
        self.assertEqual(code(evaluate(p,selection=selected("3","II",["3"],"274"))),
                         "SP_CODE_SET_INCOMPLETE")

    def test_sp_known_exact_clause(self):
        p=packet(("3","II"))
        s=selected("3","II",["3"],"274 318")
        eid=add(p,"SPEVID")
        s["special_provision_outcomes"]=[
            {"code":c,"status":"does_not_apply","verified":True,
             "source_clause":"3.3.1 SP"+c,"evidence_ids":[eid]}
            for c in ("274","318")]
        self.assertEqual(evaluate(p,selection=s)["status"],"RECONCILED_PROVISIONAL")

    def test_named_vs_generic_override(self):
        p=packet(("3","II"),("9","II"))
        x=context(p);s=selected("9","II",["9"])
        self.assertEqual(code(evaluate(p,x,s)),"ROW_CLASS_CONTRADICTION")
        eid=add(p,"PCBNAMED")
        s["named_exception"]={"status":"applies","clause":"2.1.3.4.2",
            "target_class":"9","verified":True,"evidence_ids":[eid],
            "subsidiary_classes":[],"reason":"SYNTHETIC ONLY"}
        self.assertEqual(evaluate(p,x,s)["primary_class"],"9")

    def test_named_override_without_evidence(self):
        p=packet(("3","II"),("9","II"))
        x=context(p);s=selected("9","II",["9"])
        s["named_exception"]={"status":"applies","clause":"2.1.3.4.2",
            "target_class":"9","verified":True,"evidence_ids":["MISSING"]}
        self.assertEqual(code(evaluate(p,x,s)),"ROW_CLASS_CONTRADICTION")

    def test_named_candidate_set_incomplete(self):
        p=packet(("3","II"));s=selected("3","II",["3"])
        s["candidate_set_complete"]=False
        self.assertEqual(code(evaluate(p,selection=s)),"UN_SELECTOR_INCOMPLETE")

    def test_row_source_not_verified(self):
        p=packet(("3","II"));s=selected("3","II",["3"])
        s["selected_row"]["verification"]["corrigenda"]=False
        self.assertEqual(code(evaluate(p,selection=s)),"ROW_PROVENANCE_UNVERIFIED")

    def test_edition_other_than_2025(self):
        p=packet(("3","II"));p["regulatory_context"]["edition_id"]="ADR-2027-EN"
        self.assertEqual(code(evaluate(p)),"SCREENING_INCOMPLETE")

    def test_carriage_prohibition_blocks(self):
        p=packet(("3","II"))
        self.assertEqual(code(evaluate(p,{"carriage_prohibited":True})),
                         "REGULATORY_EXCEPTION_HOLD")


if __name__=="__main__":unittest.main(verbosity=2)
