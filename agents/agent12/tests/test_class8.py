"""Boundary and failure-mode tests only; independent regulatory review outstanding."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('agent12_class8', Path(__file__).resolve().parents[1] / 'class8.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
evaluate = mod.evaluate


def base(**overrides):
    p = dict(material_scope='substance', physical_state='liquid',
             human_evidence=dict(status='none', review_complete=True, evidence_id='HUM-REVIEW-1'),
             skin_test=dict(status='corrosive', valid=True, method='OECD_404',
                            evidence_id='STUDY-1', exposure_minutes=3, observation_minutes=60))
    p.update(overrides)
    return p


def negative_skin():
    return dict(status='non_corrosive', valid=True, method='OECD_439', evidence_id='SKIN-439-1')


def metal(metal, **overrides):
    d = dict(method='UN_MTC_REV8_C1', evidence_id='C1-REPORT-'+metal,
             grade='S235JR+CR' if metal == 'steel' else '7075-T6',
             protocol_confirmed=True, three_positions_tested=True, specimen_sets=3,
             plate_thickness_mm=2, solution_volume_l=1.5,
             temperature_min_c=54, temperature_max_c=56,
             duration_days=7, exposure_hours=168, duration_verified=True,
             rate_mm_year=6.25, max_local_intrusion_um=120, local_corrosion_assessed=True)
    d.update(overrides)
    return d


def mixture(ingredients, **kw):
    p=base(material_scope='untested_mixture', skin_test=dict(status='not_available'),
                ingredients=ingredients, all_ingredients_identified=True,
                composition_evidence_id='COMP-1',
                specific_limits_checked_against_Table_A_and_SP=True,
                specific_limits_present=False, no_synergistic_corrosion_effect=True)
    p.update(kw)
    return p


def ingredient(i, pg, pct, **kw):
    return dict(id=i, skin_corrosion_pg=pg, concentration_pct=pct, **kw)


class Class8Cases(unittest.TestCase):
    def test_skin_tiers_exact_boundaries(self):
        for ex, ob, pg in [(0.1, 60, 'I'), (3, 60, 'I'),
                           (3.0001, 20160, 'II'), (60, 20160, 'II'),
                           (60.0001, 20160, 'III'), (240, 20160, 'III')]:
            with self.subTest(ex=ex, ob=ob):
                r=evaluate(base(skin_test={**base()['skin_test'],
                       'exposure_minutes':ex, 'observation_minutes':ob}))
                self.assertEqual((r['status'],r['calculated_packing_group']),('criteria_met',pg))
    def test_observation_boundaries_fail_closed(self):
        for ex, ob in [(3,60.001), (60,20160.001),(240,20160.001),(240.001,100),
                       (3,-1), (0,60)]:
            with self.subTest(ex=ex, ob=ob):
                s={**base()['skin_test'],'exposure_minutes':ex,'observation_minutes':ob}
                self.assertEqual(evaluate(base(skin_test=s))['status'],'indeterminate')
    def test_missing_study_detail(self):
        for field in ('method','evidence_id','valid','observation_minutes'):
            s=base()['skin_test'].copy(); s.pop(field)
            with self.subTest(field=field):
                self.assertEqual(evaluate(base(skin_test=s))['status'],'indeterminate')
    def test_non_tiering_fallback(self):
        s=dict(status='corrosive', valid=True, method='OECD_431', evidence_id='431-VALID',
               tier_discrimination='not_PGI_cannot_distinguish_II_III', valid_PGI_exclusion=True)
        self.assertEqual(evaluate(base(skin_test=s))['calculated_packing_group'],'II')
        s=dict(status='corrosive', valid=True, method='OECD_435', evidence_id='435-VALID',
               tier_discrimination='cannot_distinguish_any', no_other_test_indicates_other_pg=True)
        self.assertEqual(evaluate(base(skin_test=s))['calculated_packing_group'],'I')
        s.pop('no_other_test_indicates_other_pg')
        self.assertEqual(evaluate(base(skin_test=s))['status'],'indeterminate')
    def test_oecd439_cannot_label_corrosive(self):
        s=base()['skin_test'].copy(); s['method']='OECD_439'
        self.assertEqual(evaluate(base(skin_test=s))['status'],'indeterminate')
    def test_human_requires_documented_review(self):
        self.assertEqual(evaluate(base(human_evidence={}))['status'],'indeterminate')
        self.assertEqual(evaluate(base(human_evidence=dict(status='conflicting',
                  review_complete=True,evidence_id='HUM-X')))['status'],'indeterminate')
    def test_human_and_skin_disagreement(self):
        for status in ('corrosive','non_corrosive'):
            h=dict(status=status,review_complete=True,evidence_id='HUM-EXPERT',
                   candidate_pg='II' if status=='corrosive' else None,
                   expert_pg_basis_confirmed=True)
            skin=negative_skin() if status=='corrosive' else base()['skin_test']
            self.assertEqual(evaluate(base(human_evidence=h,skin_test=skin))['status'],'indeterminate')
    def test_conflicting_human_and_animal_pg(self):
        h=dict(status='corrosive', review_complete=True, evidence_id='HUM-2',
               candidate_pg='II', expert_pg_basis_confirmed=True)
        self.assertEqual(evaluate(base(human_evidence=h))['status'],'indeterminate')
    def test_human_positive_without_tier_needs_tier(self):
        h=dict(status='corrosive',review_complete=True,evidence_id='HUM-3')
        self.assertEqual(evaluate(base(human_evidence=h,skin_test=dict(status='not_available')))['status'],'indeterminate')
    def test_metal_rate_and_mixed_results(self):
        steel=metal('steel', rate_mm_year=6.25001)
        for tests in ({'steel':steel},
                      {'steel':metal('steel'),'aluminium':metal('aluminium',rate_mm_year=6.25001)}):
            r=evaluate(base(skin_test=negative_skin(), metal_tests=tests))
            self.assertEqual((r['status'],r['calculated_packing_group']),('criteria_met','III'))
        both={'steel':metal('steel'), 'aluminium':metal('aluminium')}
        self.assertEqual(evaluate(base(skin_test=negative_skin(),metal_tests=both))['status'],'criteria_not_met')
        self.assertEqual(evaluate(base(skin_test=negative_skin(),metal_tests={'steel':metal('steel')}))['status'],'indeterminate')
    def test_metal_thresholds_and_local_attack(self):
        self.assertEqual(evaluate(base(skin_test=negative_skin(),metal_tests={'steel':
               metal('steel',rate_mm_year=6.25,max_local_intrusion_um=120.001)}))['calculated_packing_group'],'III')
        self.assertEqual(evaluate(base(skin_test=negative_skin(),metal_tests={'aluminium':
               metal('aluminium',rate_mm_year=None,max_mass_loss_pct=13.501)}))['calculated_packing_group'],'III')
        self.assertEqual(evaluate(base(skin_test=negative_skin(),metal_tests={'aluminium':
               metal('aluminium',rate_mm_year=None,max_mass_loss_pct=13.5)}))['status'],'indeterminate')
    def test_only_localised_corrosion_can_prove_positive(self):
        local=metal('aluminium',rate_mm_year=None,max_local_intrusion_um=120.001)
        r=evaluate(base(skin_test=negative_skin(),metal_tests={'aluminium':local}))
        self.assertEqual((r['status'],r['calculated_packing_group']),('criteria_met','III'))
        local['local_corrosion_assessed']=False
        self.assertEqual(evaluate(base(skin_test=negative_skin(),metal_tests={'aluminium':local}))['status'],'indeterminate')

    def test_metal_physical_state_scope(self):
        st=metal('steel',rate_mm_year=6.251)
        self.assertEqual(evaluate(base(skin_test=negative_skin(),physical_state='solid',
           metal_tests={'steel':st}))['status'],'indeterminate')
        r=evaluate(base(skin_test=negative_skin(),physical_state='solid',
          may_become_liquid_during_carriage=True,metal_tests={'steel':st}))
        self.assertEqual(r['calculated_packing_group'],'III')
        self.assertEqual(evaluate(base(skin_test=negative_skin(),physical_state='gas',
          metal_tests={'steel':st}))['status'],'indeterminate')

    def test_metal_conditions_boundaries(self):
        for kw in [dict(temperature_min_c=53.99), dict(temperature_max_c=56.01),
                   dict(solution_volume_l=1.49), dict(specimen_sets=2),
                   dict(plate_thickness_mm=1.9), dict(duration_days=8),
                   dict(grade='other'), dict(protocol_confirmed=False),
                   dict(local_corrosion_assessed=False, rate_mm_year=6.25)]:
            with self.subTest(kw=kw):
                r=evaluate(base(skin_test=negative_skin(),metal_tests={'steel':metal('steel',**kw)}))
                self.assertEqual(r['status'],'indeterminate')
    def test_mixture_generic_flow_boundaries(self):
        cases=[([ingredient('I','I',5)],'I'),
               ([ingredient('I','I',1)],'II'),
               ([ingredient('I','I',4.999)],'II'),
               ([ingredient('II','II',5)],'II'),
               ([ingredient('I','I',0.9,relevant_below_one_pct=True),
                 ingredient('II','II',4.1)],'II'),
               ([ingredient('III','III',5)],'III'),
               ([ingredient('III','III',4.999)],None)]
        for ing,pg in cases:
            with self.subTest(ing=ing):
                r=evaluate(mixture(ing))
                self.assertEqual((r['status'],r['calculated_packing_group']),
                     (('criteria_met' if pg else 'criteria_not_met'),pg))
    def test_mixture_synergy_guard_only_ii_iii(self):
        self.assertEqual(evaluate(mixture([ingredient('I','I',5)],
                                   no_synergistic_corrosion_effect=False))['status'],'criteria_met')
        self.assertEqual(evaluate(mixture([ingredient('II','II',5)],
                                   no_synergistic_corrosion_effect=False))['status'],'indeterminate')
    def test_mixture_gates(self):
        p=mixture([ingredient('III','III',5)]);p['specific_limits_present']=True
        self.assertEqual(evaluate(p)['status'],'indeterminate')
        p=mixture([ingredient('III','III',0.8)])
        self.assertEqual(evaluate(p)['status'],'indeterminate')
        p=mixture([ingredient('III','III',5)]);p['specific_limits_checked_against_Table_A_and_SP']=False
        self.assertEqual(evaluate(p)['status'],'indeterminate')
    def test_bridging_five_principles_and_missing_conditions(self):
        conditions={
            'dilution': ('diluent_not_class8','diluent_no_pg_effect','no_increased_corrosion'),
            'batching': ('same_commercial_product','same_manufacturer_control','no_significant_variation'),
            'concentrated_PGI': ('source_is_PGI','only_concentrated'),
            'interpolation': ('identical_ingredients','tested_A_and_B_same_pg','all_class8_concentrations_intermediate'),
            'substantially_similar': ('same_B_concentration','same_A_C_concentration','A_C_equivalent_skin_pg','A_C_no_effect_on_B')}
        for mode, req in conditions.items():
            pg='I' if mode=='concentrated_PGI' else 'II'
            b=dict(type=mode,evidence_id='BRIDGE-'+mode,source_tested_pg=pg,**{x:True for x in req})
            with self.subTest(mode=mode):
                self.assertEqual(evaluate(base(material_scope='untested_mixture',
                 skin_test=dict(status='not_available'), bridge=b))['calculated_packing_group'],pg)
                b.pop(req[0])
                self.assertEqual(evaluate(base(material_scope='untested_mixture',
                 skin_test=dict(status='not_available'), bridge=b))['status'],'indeterminate')
    def test_never_final_dgl_pg(self):
        r=evaluate(base())
        self.assertIsNone(r['dgl_packing_group'])
        self.assertTrue(r['requires_precedence_review'])
        self.assertTrue(r['requires_independent_review'])
        self.assertFalse(r['is_final_section_14_classification'])
        self.assertEqual(evaluate({})['status'],'indeterminate')


if __name__=='__main__': unittest.main()
