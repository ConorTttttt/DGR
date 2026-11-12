"""Machine-readable contract regression tests. All examples synthetic."""
import copy
import json
import sys
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from orchestrator import route

def apply_patch(target, patch):
    parts=[p.replace("~1","/").replace("~0","~") for p in patch["path"].split("/")[1:]]
    parent=target
    for part in parts[:-1]:
        parent=parent[int(part)] if isinstance(parent,list) else parent[part]
    last=parts[-1]
    if isinstance(parent,list):
        index=int(last)
        if patch["op"]=="remove":
            parent.pop(index)
        elif patch["op"]=="replace":
            parent[index]=patch["value"]
        elif patch["op"]=="add":
            parent.insert(index,patch["value"])
    else:
        if patch["op"]=="remove":
            parent.pop(last)
        else:
            parent[last]=patch["value"]

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((HERE/"integration_cases.json").read_text())
        cls.schema=json.loads((HERE.parent/"schemas/integration_packet.schema.json").read_text())
        cls.out_schema=json.loads((HERE.parent/"schemas/outcome.schema.json").read_text())
        cls.rule_schema=json.loads((HERE.parent/"schemas/rule.schema.json").read_text())
        cls.registry=json.loads((HERE.parent/"reference_registry.json").read_text())
    def test_schemas_valid_draft202012(self):
        for doc in (self.schema,self.out_schema,self.rule_schema):
            Draft202012Validator.check_schema(doc)
    def test_input_and_outcome_structural_validity(self):
        Draft202012Validator(self.schema).validate(self.data["base_packet"])
        for case in self.data["cases"]:
            with self.subTest(case=case["id"]):
                packet=copy.deepcopy(self.data["base_packet"])
                for patch in case["patches"]:
                    apply_patch(packet,patch)
                out=route(packet,schema=self.schema,registry=self.registry)
                Draft202012Validator(self.out_schema).validate(out)
                self.assertEqual(case["expect"],out["state"])
                if case.get("issue"):
                    self.assertIn(case["issue"],[x["code"] for x in out["blocking_issues"]])
                self.assertFalse(out["publishable"])
                self.assertEqual(out,route(packet,schema=self.schema,registry=self.registry))
    def test_every_outcome_nonpublishable(self):
        self.assertEqual(Draft202012Validator(self.out_schema).is_valid({
            "contract_version":"0.1.0","state":"READY_FOR_RELEASE_REVIEW",
            "next_stage":"external_review","publishable":True,
            "blocking_issues":[],"trace":[]}),False)
    def test_canonical_registry_sources_unique(self):
        sources=self.registry["sources"]
        self.assertEqual(len(sources),len({s["source_id"] for s in sources}))
        self.assertEqual("ADR-2025-EN",self.registry["edition_id"])
        self.assertTrue(all(x["legal_rule_approval"]=="not_approved" for x in self.registry["clauses"]))
    def test_no_operational_un_numbers_in_synthetic_tests(self):
        raw=json.dumps(self.data)
        self.assertIn("SYNTHETIC",raw)
        self.assertNotIn('"un_number": "1202"',raw)
if __name__=="__main__":
    unittest.main()
