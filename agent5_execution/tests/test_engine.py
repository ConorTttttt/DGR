"""Behavioral unit tests using nonregulatory synthetic examples only."""
import copy
import json
from pathlib import Path
import unittest

from engine import canonical_sha256, evaluate, parse_bundle_json, ContractError

ROOT = Path(__file__).parents[1]
BUNDLE = json.loads((ROOT / 'examples/synthetic_bundle.json').read_text())
REQUEST = json.loads((ROOT / 'examples/synthetic_request.json').read_text())
CITE = {"source_id": "TEST-NON-AUTHORITY", "clause": "TEST.2"}


def positive_rule(rule_id="TEST-POSITIVE", fact="mock_positive_case", value=True,
                  field="transport_status", effect="regulated"):
    return {
        "rule_id": rule_id,
        "when": {"op": "eq", "fact": fact, "expected": {"type": "boolean", "value": value}},
        "citations": [CITE], "effects": [{"field": field, "value": effect}],
    }


def fact(value=True):
    return {"type": "boolean", "value": value, "evidence": [{"ref": "REPORT-1", "locator": "page 1"}]}


class EngineTests(unittest.TestCase):
    def run_engine(self, bundle=None, request=None, test=True):
        return evaluate(bundle if bundle is not None else copy.deepcopy(BUNDLE),
                        request if request is not None else copy.deepcopy(REQUEST),
                        allow_test_rules=test)

    def test_explicit_negative_requires_fixture_opt_in(self):
        self.assertEqual(self.run_engine()["decision_status"], "DECIDED")
        self.assertEqual(self.run_engine()["transport_status"], "not_regulated_for_transport")
        self.assertEqual(self.run_engine(test=False)["decision_status"], "BLOCKED")
        self.assertEqual(self.run_engine(test=False)["issues"][0]["code"], "TEST_RULES_DISABLED")

    def test_missing_fact_is_not_not_regulated(self):
        req = copy.deepcopy(REQUEST); req['facts'] = {}
        result = self.run_engine(request=req)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertEqual(result['section14'], {})
        self.assertIn('MISSING_FACT', {x['code'] for x in result['issues']})

    def test_no_match_is_not_not_regulated(self):
        req = copy.deepcopy(REQUEST); req['facts']['mock_negative_case']['value'] = False
        result = self.run_engine(request=req)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertIsNone(result['transport_status'])

    def test_no_evidence_is_unknown(self):
        req = copy.deepcopy(REQUEST); req['facts']['mock_negative_case']['evidence'] = []
        result = self.run_engine(request=req)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertIn('MISSING_EVIDENCE', {x['code'] for x in result['issues']})

    def test_unknown_rule_blocks_even_if_negative_matched(self):
        bundle = copy.deepcopy(BUNDLE)
        bundle['rules'].append(positive_rule())
        result = self.run_engine(bundle=bundle)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertEqual(result['section14'], {})
        self.assertEqual(result['provisional_effects']['transport_status'], 'not_regulated_for_transport')

    def test_conflicting_decisions_block(self):
        bundle = copy.deepcopy(BUNDLE); bundle['rules'].append(positive_rule())
        req = copy.deepcopy(REQUEST); req['facts']['mock_positive_case'] = fact()
        result = self.run_engine(bundle, req)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertIn('CONFLICTING_RULE_EFFECTS', {x['code'] for x in result['issues']})

    def test_regulated_completeness_comes_from_bundle(self):
        bundle = copy.deepcopy(BUNDLE); bundle['rules'] = [positive_rule()]
        req = copy.deepcopy(REQUEST); req['facts'] = {'mock_positive_case': fact()}
        result = self.run_engine(bundle, req)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertIn('INCOMPLETE_REGULATED_OUTPUT', {x['code'] for x in result['issues']})
        fields = [('un_number', 'UN-TEST'), ('proper_shipping_name', 'SYNTHETIC NAME'),
                  ('transport_hazard_class', 'SYNTHETIC CLASS')]
        for i, (field, value) in enumerate(fields):
            bundle['rules'].append(positive_rule(f'FIELD-{i}', field=field, effect=value))
        result = self.run_engine(bundle, req)
        self.assertEqual(result['decision_status'], 'DECIDED')
        self.assertEqual(result['section14']['proper_shipping_name'], 'SYNTHETIC NAME')
        self.assertEqual(len(result['field_citations']['un_number']), 1)

    def test_no_implicit_negative_without_status(self):
        bundle = copy.deepcopy(BUNDLE); bundle['rules'] = [positive_rule(field='un_number', effect='FAKE')]
        req = copy.deepcopy(REQUEST); req['facts'] = {'mock_positive_case': fact()}
        result = self.run_engine(bundle, req)
        self.assertEqual(result['decision_status'], 'INDETERMINATE')
        self.assertIn('NO_EXPLICIT_TRANSPORT_STATUS', {x['code'] for x in result['issues']})

    def test_unapproved_bundle_blocked(self):
        bundle = copy.deepcopy(BUNDLE); bundle['approval']['status'] = 'draft'
        result = self.run_engine(bundle)
        self.assertEqual(result['issues'][0]['code'], 'UNAPPROVED_BUNDLE')

    def test_missing_citation_blocked(self):
        bundle = copy.deepcopy(BUNDLE); bundle['rules'][0]['citations'] = []
        self.assertEqual(self.run_engine(bundle)['issues'][0]['code'], 'MISSING_PROVENANCE')

    def test_date_and_version_pinning(self):
        req = copy.deepcopy(REQUEST); req['on_date'] = '2030-01-01'
        self.assertEqual(self.run_engine(request=req)['issues'][0]['code'], 'OUTSIDE_EFFECTIVE_DATES')
        req = copy.deepcopy(REQUEST); req['bundle_version'] = '9.0.0'
        self.assertEqual(self.run_engine(request=req)['issues'][0]['code'], 'BUNDLE_PIN_MISMATCH')

    def test_disallowed_predicate_fails_closed(self):
        bundle = copy.deepcopy(BUNDLE); bundle['rules'][0]['when']['op'] = 'execute_code'
        self.assertEqual(self.run_engine(bundle)['issues'][0]['code'], 'INVALID_PREDICATE')

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ContractError) as caught:
            parse_bundle_json('{"bundle_id":"a", "bundle_id":"b"}')
        self.assertEqual(caught.exception.code, 'DUPLICATE_JSON_KEY')

    def test_deterministic_reordering(self):
        bundle = copy.deepcopy(BUNDLE)
        bundle['rules'].append(positive_rule('TEST-FALSE', fact='mock_negative_case', value=False))
        first = self.run_engine(bundle)
        bundle['rules'].reverse()
        second = self.run_engine(bundle)
        self.assertEqual(first['decision_status'], second['decision_status'])
        self.assertEqual(first['trace'], second['trace'])
        self.assertNotEqual(first['bundle_sha256'], second['bundle_sha256'])
        self.assertEqual(canonical_sha256({'a': 1, 'b': 2}), canonical_sha256({'b': 2, 'a': 1}))

    def test_exact_decimal_threshold(self):
        bundle = copy.deepcopy(BUNDLE)
        bundle['rules'][0]['when'] = {
            'op': 'gte', 'fact': 'mass', 'expected': {'type': 'decimal', 'value': '0.10'}}
        req = copy.deepcopy(REQUEST); req['facts'] = {
            'mass': {'type': 'decimal', 'value': '0.1000000000000000000001',
                     'evidence': [{'ref': 'REPORT', 'locator': 'lab result'}]}}
        self.assertEqual(self.run_engine(bundle, req)['decision_status'], 'DECIDED')

    def test_negative_rule_requires_scope_attestation(self):
        bundle = copy.deepcopy(BUNDLE); bundle['rules'][0].pop('exhaustive_scope')
        self.assertEqual(self.run_engine(bundle)['issues'][0]['code'], 'NON_REGULATED_NOT_JUSTIFIED')

    def test_source_edition_mismatch(self):
        bundle = copy.deepcopy(BUNDLE); bundle['sources'][0]['edition'] = 'unrelated edition'
        self.assertEqual(self.run_engine(bundle)['issues'][0]['code'], 'EDITION_MISMATCH')


if __name__ == '__main__':
    unittest.main()
