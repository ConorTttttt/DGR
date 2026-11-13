"""Synthetic deterministic regression tests, not regulatory validation."""
import copy
import unittest
from class61 import evaluate


def oral(value):
    return dict(status='measured', ld50_mg_kg=str(value), sample='carried_material', species='rat', observation_days=14, evidence_id='ORAL-1')

def dermal(value):
    return dict(status='measured', ld50_mg_kg=str(value), sample='carried_material', species='rabbit', contact_hours=24, observation_days=14, evidence_id='DERM-1')

def dust(value, hours=1):
    return dict(status='measured', lc50_by_hours={str(hours):str(value)}, sample='carried_material', species='rat', both_sexes=True, observation_days=14, evidence_id='DUST-1', aerosol_form='dust', specimen_respirable_mass_percent='90.01', aerodynamic_diameter_um=10, likely_respirable_dust_mass_percent=10)

def vapour(value, v, hours=1):
    return dict(status='measured', lc50_by_hours={str(hours):str(value)}, sample='carried_material', species='rat', both_sexes=True, observation_days=14, evidence_id='VAP-1', temperature_c=20, pressure_kpa='101.3', saturated_vapour_ppm_20c=str(v))

def base(state='solid'):
    return dict(material_type='substance', physical_state=state,
                human_experience=dict(reviewed=True, status='none_documented', evidence_id='HUM-REVIEW-1'),
                screen={x:True for x in ('identity_reviewed','named_entry_reviewed','stability_reviewed','prohibitions_reviewed','subsidiary_hazards_reviewed')},
                pesticide=False, tear_gas=False, class8_meets_criteria=False,
                routes={'oral':oral(500), 'dermal':dermal(1500),
                        'dust_mist': (dict(status='excluded', basis='respirable_fraction_below_10_percent', respirable_fraction_mass_percent='9.999', evidence_id='DUST-SCREEN') if state=='solid' else dict(status='excluded', basis='no_mist_on_leakage', mist_likely_on_leakage=False, evidence_id='MIST-SCREEN')),
                        'vapour': (dict(status='excluded', basis='not_liquid', evidence_id='STATE-SCREEN') if state=='solid' else vapour(10000,0))})

def testanimal(deaths, ppm=1000, dilution=None):
    t=dict(rats=10, male=5, female=5, exposure_hours=1, observation_days=14, deaths=deaths, nominal_concentration_ppm=ppm, evidence_id='RATS-1')
    if dilution is not None:t['dilution_air_volumes']=dilution
    return t


def tiers():
    return {'I': {'toxicity':testanimal(0,1000), 'equilibrium':testanimal(0,1000,9)},
            'II':{'toxicity':testanimal(0,3000), 'equilibrium':testanimal(0,3000,0)},
            'III':{'toxicity':testanimal(0,5000), 'saturated_vapour_ppm_20c':0}}


class Class61Tests(unittest.TestCase):
    def run_route(self, route, evidence, state='solid', **overrides):
        e = base(state)
        e['routes'][route]=evidence
        e.update(overrides)
        return evaluate(e)

    def test_oral_operator_boundaries(self):
        for v,pg in [('0.01','I'),(5,'I'),('5.00001','II'),(50,'II'),('50.00001','III'),(300,'III'),('300.00001',None)]:
            with self.subTest(v=v):
                r=self.run_route('oral',oral(v))
                self.assertEqual(r['candidate_packing_group'],pg)
    def test_dermal_operator_boundaries(self):
        for v,pg in [(50,'I'),('50.0001','II'),(200,'II'),('200.0001','III'),(1000,'III'),('1000.01',None)]:
            with self.subTest(v=v):
                self.assertEqual(self.run_route('dermal',dermal(v))['candidate_packing_group'],pg)
    def test_dust_operator_boundaries(self):
        for v,pg in [('0.2','I'),('0.20001','II'),(2,'II'),('2.00001','III'),(4,'III'),('4.00001',None)]:
            e=base('solid');e['routes']['dust_mist']=dust(v)
            with self.subTest(v=v):
                self.assertEqual(evaluate(e)['candidate_packing_group'],pg)
    def test_dust_four_hour_conversion(self):
        for v,pg in [('0.05','I'),('0.05001','II'),('0.5','II'),('0.50001','III'),('1','III'),('1.00001',None)]:
            with self.subTest(v=v):
                self.assertEqual(self.run_route('dust_mist',dust(v,4))['candidate_packing_group'],pg)
    def test_dust_one_hour_preferred(self):
        x=dust(0.1);x['lc50_by_hours']['4']='4'
        r=self.run_route('dust_mist',x)
        self.assertEqual(r['candidate_packing_group'],'I')
        self.assertIn('1-hour result',r['route_results']['dust_mist']['notes'][0])
    def test_vapour_boundary_and_volatility(self):
        for lc,V,pg in [('1000','10000','I'),('1000','9999.99','II'),('3000','3000','II'),('3000.01','3000.01','III'),('5000','1000','III'),('5000.001','100000',None),('5000','999.99',None)]:
            with self.subTest(lc=lc,V=V):
                self.assertEqual(self.run_route('vapour',vapour(lc,V),state='liquid')['candidate_packing_group'],pg)
    def test_vapour_4h_conversion(self):
        self.assertEqual(self.run_route('vapour',vapour(500,10000,4),state='liquid')['candidate_packing_group'],'I')
    def test_multi_route_highest_hazard(self):
        e=base();e['routes']['oral']=oral(250);e['routes']['dermal']=dermal(50)
        self.assertEqual(evaluate(e)['candidate_packing_group'],'I')
    def test_missing_route_blocks_lower_pgs(self):
        e=base();e['routes']['oral']=oral(10);del e['routes']['dermal']
        r=evaluate(e)
        self.assertIsNone(r['candidate_packing_group']);self.assertEqual(r['status'],'indeterminate')
    def test_missing_route_cannot_block_known_pgi(self):
        e=base();e['routes']={'oral':oral(5)}
        r=evaluate(e)
        self.assertEqual(r['candidate_packing_group'],'I');self.assertTrue(r['missing_evidence'])
    def test_all_negative_is_scoped_only(self):
        r=evaluate(base());self.assertEqual(r['status'],'criteria_not_met');self.assertFalse(r['assignment_permitted'])
    def test_human_experience_overrides_to_expert(self):
        e=base();e['routes']['oral']=oral(5);e['human_experience']['status']='positive'
        r=evaluate(e);self.assertEqual(r['status'],'indeterminate');self.assertIn('HUMAN_EXPERIENCE_PRIORITY_EXPERT_REVIEW',r['referrals'])
    def test_missing_human_review_blocks_positive_status(self):
        e=base();e['routes']['oral']=oral(5);e['human_experience']['reviewed']=False
        self.assertEqual(evaluate(e)['status'],'indeterminate')
    def test_tear_gas_floor(self):
        e=base();e['routes']['oral']=oral(250);e['tear_gas']=True
        r=evaluate(e);self.assertEqual(r['candidate_packing_group'],'II')
    def test_no_automatic_clp_negative(self):
        e={'material_type':'substance','clp_acute_toxicity':'not_classified'}
        self.assertEqual(evaluate(e)['status'],'indeterminate')
    def test_dust_required_respirable_mass_strict_90(self):
        e=dust(0.2);e['specimen_respirable_mass_percent']=90
        self.assertEqual(self.run_route('dust_mist',e)['route_results']['dust_mist']['status'],'invalid')
    def test_dust_ten_percent_trigger_exclusion(self):
        e=base();e['routes']['dust_mist']['respirable_fraction_mass_percent']=10
        self.assertEqual(evaluate(e)['route_results']['dust_mist']['status'],'invalid')
    def test_invalid_dust_exclusion_no_crash(self):
        e=base();e['routes']['dust_mist']['respirable_fraction_mass_percent']='bogus'
        self.assertEqual(evaluate(e)['status'],'indeterminate')
    def test_mist_form_liquid(self):
        e=base('liquid');m=dust('0.2');m['aerosol_form']='mist';m['mist_likely_on_leakage']=True
        e['routes']['dust_mist']=m
        self.assertEqual(evaluate(e)['candidate_packing_group'],'I')
    def test_mist_mismatch_invalid(self):
        self.assertEqual(self.run_route('dust_mist',dust(0.2),state='liquid')['route_results']['dust_mist']['status'],'invalid')
    def test_class8_dust_pgi_oral_dermal_pgi_ii_gate(self):
        e=base();e['routes']['dust_mist']=dust(0.1);e['routes']['oral']=oral(20);e['class8_meets_criteria']=True
        self.assertIn('C61_DUST_PGI_CLASS8_EXCEPTION_GATE_SATISFIED_PROVISIONALLY',evaluate(e)['referrals'])
    def test_class8_dust_pgi_only_oral_dermal_pgiii_refer(self):
        e=base();e['routes']['dust_mist']=dust(0.1);e['routes']['oral']=oral(250);e['routes']['dermal']=dermal(900);e['class8_meets_criteria']=True
        r=evaluate(e);self.assertEqual(r['status'],'indeterminate');self.assertIn('C61_DUST_PGI_CLASS8_EXCEPTION_REFER_TO_CLASS8',r['referrals'])
    def test_class8_dust_pgi_missing_oral_dermal_escalation(self):
        e=base();e['routes']['dust_mist']=dust(0.1);del e['routes']['dermal'];e['class8_meets_criteria']=True
        self.assertIn('C61_DUST_PGI_CLASS8_EXCEPTION_NEEDS_ORAL_DERMAL_EVIDENCE',evaluate(e)['referrals'])
    def test_pesticide_delegated(self):
        e=base();e['pesticide']=True;e['routes']['oral']=oral(5)
        self.assertIn('PESTICIDE_NAMED_ENTRY_AND_PSN_REVIEW',evaluate(e)['referrals'])
    def test_unreviewed_named_entries_remain_referral(self):
        e=base();e['screen']['named_entry_reviewed']=False;e['routes']['oral']=oral(5)
        self.assertIn('PENDING_NAMED_ENTRY_REVIEWED',evaluate(e)['referrals'])
    def test_mixture_single_active_oral(self):
        e=base();e['material_type']='mixture';e['routes']['oral']=dict(status='derived',method='single_active',components=[dict(mass_percent=20,ld50_mg_kg=10,active=True,evidence_id='COMP-1')],composition_complete=True,evidence_id='FORMULA-1')
        self.assertEqual(evaluate(e)['candidate_packing_group'],'II')
    def test_mixture_reciprocal_oral(self):
        e=base();e['material_type']='mixture';e['routes']['oral']=dict(status='derived',method='reciprocal_sum',components=[dict(mass_percent=10,ld50_mg_kg=10,active=True,evidence_id='A'),dict(mass_percent=10,ld50_mg_kg=100,active=True,evidence_id='B')],composition_complete=True,evidence_id='MIX')
        self.assertEqual(evaluate(e)['candidate_packing_group'],'III')
    def test_mixture_most_hazardous_total(self):
        e=base();e['material_type']='mixture';e['routes']['oral']=dict(status='derived',method='most_hazardous_total',components=[dict(mass_percent=10,ld50_mg_kg=10,active=True,evidence_id='A'),dict(mass_percent=10,ld50_mg_kg=100,active=True,evidence_id='B')],composition_complete=True,evidence_id='MIX')
        self.assertEqual(evaluate(e)['candidate_packing_group'],'II')
    def test_mixture_dermal_species_conflict(self):
        e=base();e['material_type']='mixture';e['routes']['dermal']=dict(status='derived',method='reciprocal_sum',dermal_species='rabbit',components=[dict(mass_percent=20,ld50_mg_kg=100,active=True,evidence_id='A',species='rat')],composition_complete=True,evidence_id='MIX')
        self.assertEqual(evaluate(e)['route_results']['dermal']['status'],'invalid')
    def test_mixture_incomplete_active_blocks(self):
        e=base();e['material_type']='mixture';e['routes']['oral']=dict(status='derived',method='single_active',components=[dict(mass_percent=20,ld50_mg_kg=10,active=True,evidence_id='A')],evidence_id='MIX')
        self.assertEqual(evaluate(e)['route_results']['oral']['status'],'invalid')
    def test_mixture_vapour_r_boundaries(self):
        for p,pg in [('1.013','I'),('0.1013','II'),('0.02026','III'),('0.02025999',None)]:
            with self.subTest(p=p):
                e=base('liquid');e['material_type']='mixture'
                e['routes']['vapour']=dict(status='derived',evidence_id='MIXV',composition_complete=True,components=[dict(mole_fraction=1,lc50_ppm_1h=1000,partial_pressure_kpa_20c=p,evidence_id='A')])
                self.assertEqual(evaluate(e)['candidate_packing_group'],pg)
    def test_mixture_vapour_fraction_invalid(self):
        e=base('liquid');e['material_type']='mixture'
        e['routes']['vapour']=dict(status='derived',evidence_id='MIXV',composition_complete=True,components=[dict(mole_fraction='1.1',lc50_ppm_1h=1000,partial_pressure_kpa_20c=1,evidence_id='A')])
        self.assertEqual(evaluate(e)['route_results']['vapour']['status'],'invalid')
    def test_threshold_tier_boundaries_5_of_10(self):
        for grade in ('I','II','III'):
            with self.subTest(grade=grade):
                e=base('liquid');e['material_type']='mixture';ts=tiers()
                ts[grade]['toxicity']['deaths']=5
                if grade!='III':ts[grade]['equilibrium']['deaths']=5
                else:ts[grade]['saturated_vapour_ppm_20c']=1000
                e['routes']['vapour']=dict(status='threshold_tests',tiers=ts,evidence_id='SERIES')
                self.assertEqual(evaluate(e)['candidate_packing_group'],grade)
    def test_threshold_four_deaths_not_positive(self):
        e=base('liquid');e['material_type']='mixture';ts=tiers()
        ts['I']['toxicity']['deaths']=4;ts['I']['equilibrium']['deaths']=10
        e['routes']['vapour']=dict(status='threshold_tests',tiers=ts,evidence_id='SERIES')
        self.assertEqual(evaluate(e)['route_results']['vapour']['status'],'negative')
    def test_threshold_missing_pgi_tier_invalid(self):
        e=base('liquid');e['material_type']='mixture';ts=tiers();del ts['I']
        e['routes']['vapour']=dict(status='threshold_tests',tiers=ts,evidence_id='SERIES')
        self.assertEqual(evaluate(e)['route_results']['vapour']['status'],'invalid')
    def test_boolean_numeric_rejected(self):
        e=oral(True)
        self.assertEqual(self.run_route('oral',e)['route_results']['oral']['status'],'invalid')
    def test_invalid_methods_do_not_crash(self):
        e=base();e['routes']['oral']={'status':'derived'}
        self.assertEqual(evaluate(e)['status'],'indeterminate')
    def test_never_final_section14(self):
        for e in (base(),base('liquid'),{}):
            r=evaluate(e)
            self.assertFalse(r['assignment_permitted']);self.assertFalse(r['is_final_section_14_classification']);self.assertTrue(r['requires_independent_review'])


if __name__ == '__main__': unittest.main()
