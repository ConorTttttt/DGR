"""Proposed input-model structural/fail-safe tests. NOT regulatory validation."""
import csv, json, unittest
from pathlib import Path
P = Path(__file__).resolve().parents[1]
PATHS = {'1','2','3','4.1','4.2','4.3','5.1','5.2','6.1','6.2','7','8','9'}

def load(n): return json.loads((P/n).read_text(encoding='utf-8'))
def negative_ready(statuses):
    """Conservative pre-review gate ONLY; never emits a legal transport conclusion."""
    return set(statuses)==PATHS and all(v in ('negative_supported','not_applicable_by_clause') for v in statuses.values())

class InputModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=load('input_schema.v0.1.json')
        cls.matrix=load('decision_requirements.v0.1.json')
        with (P/'field_catalog.csv').open(encoding='utf-8',newline='') as f: cls.fields=list(csv.DictReader(f))
    def test_all_thirteen_class_paths(self):
        self.assertEqual({x['pathway_id'] for x in self.matrix['hazard_pathways']},PATHS)
    def test_204_unique_fields(self):
        keys=[r['field_id'] for r in self.fields]
        self.assertEqual(len(keys),204)
        self.assertEqual(len(keys),len(set(keys)))
        self.assertEqual(set(keys),set(self.schema['properties']['data']['properties']))
    def test_candidate_fields_all_defined(self):
        keys={r['field_id'] for r in self.fields}
        for p in self.matrix['hazard_pathways']:
            self.assertTrue(set(p['candidate_evidence_fields']+p['conditional_follow_up_fields']).issubset(keys))
        for p in self.matrix['cross_cutting_decisions']:
            self.assertTrue(set(p['evidence_fields']).issubset(keys))
    def test_every_path_has_adr2025_reference(self):
        for p in self.matrix['hazard_pathways']:
            self.assertTrue(any(r.startswith('ADR2025:') for r in p['regulatory_basis']))
    def test_missing_path_blocks_negative(self):
        self.assertFalse(negative_ready({p:'negative_supported' for p in PATHS if p!='7'}))
        self.assertFalse(negative_ready({'3':'not_assessed','8':'negative_supported'}))
    def test_unresolved_path_blocks_negative(self):
        x={p:'negative_supported' for p in PATHS}
        x['5.2']='unresolved'
        self.assertFalse(negative_ready(x))
    def test_all_resolved_requires_separate_reviewer(self):
        x={p:'negative_supported' for p in PATHS}
        self.assertTrue(negative_ready(x)) # ONLY enters review; not a regulatory determination
        self.assertEqual(self.matrix['final_state_contract']['default'],'UNRESOLVED')
    def test_schema_enforces_known_datum_evidence(self):
        try: from jsonschema import Draft202012Validator
        except ImportError: self.skipTest('pip install jsonschema')
        v=Draft202012Validator(self.schema)
        p={'model_version':'0.1.0-draft','context':{'product_id':'X','mode':'ADR','edition':'2025','effective_date':'2025-01-01'},
            'data':{'physical.flash_point_c':{'state':'known','value':30}},'evidence':[],
            'hazard_screens':[{'pathway_id':'3','status':'not_assessed'}]}
        self.assertTrue(list(v.iter_errors(p)))
        p['data']['physical.flash_point_c']['evidence_ids']=['lab-report']
        self.assertFalse(list(v.iter_errors(p)))
    def test_schema_rejects_unsubstantiated_na(self):
        try: from jsonschema import Draft202012Validator
        except ImportError: self.skipTest('pip install jsonschema')
        v=Draft202012Validator(self.schema)
        p={'model_version':'0.1.0-draft','context':{'product_id':'X','mode':'ADR','edition':'2025','effective_date':'2025-01-01'},
            'data':{'physical.flash_point_c':{'state':'not_applicable','reason':'wrong pathway'}},
            'evidence':[], 'hazard_screens':[{'pathway_id':'3','status':'not_assessed'}]}
        self.assertTrue(list(v.iter_errors(p)))
        p['data']['physical.flash_point_c'].update(non_applicability_clause_ref='ADR2025:2.2.2',evidence_ids=['E1'])
        self.assertFalse(list(v.iter_errors(p)))
    def test_negative_screen_needs_provenance(self):
        try: from jsonschema import Draft202012Validator
        except ImportError: self.skipTest('pip install jsonschema')
        v=Draft202012Validator(self.schema)
        p={'model_version':'0.1.0-draft','context':{'product_id':'X','mode':'ADR','edition':'2025','effective_date':'2025-01-01'},
            'data':{},'evidence':[], 'hazard_screens':[{'pathway_id':'7','status':'negative_supported'}]}
        self.assertTrue(list(v.iter_errors(p)))
        p['hazard_screens'][0].update(evidence_ids=['E1'],clause_refs=['ADR2025:2.2.7'],rationale='Evidence-backed screen')
        self.assertFalse(list(v.iter_errors(p)))
    def test_explicit_relevance_examples(self):
        with (P/'relevance_examples.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows),20)
        self.assertTrue(all(x['missing_effect'] and x['irrelevant_or_deferred_when'] and x['source'] for x in rows))

if __name__=='__main__': unittest.main()
