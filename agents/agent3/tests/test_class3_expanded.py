"""ADR 2025 Class 3 boundary / negative / exception / missing evidence tests.

These check deterministic implementation behaviour, NOT independent legal validation.
"""
import unittest
from adr2025.class3 import evaluate

BASE=dict(
    physical_state='liquid', liquid_definition_basis='melting_point', melting_point_c=-10,
    vapour_pressure_kpa_50c=10, completely_gaseous_at_20c=False,
    liquid_desensitized_explosive=False, flash_point_c=22.9,
    flash_point_method='ISO 2719', flash_point_method_kind='equilibrium',
    flash_point_evidence_id='FP-001', carried_at_or_above_flash_point=False,
    diesel_gasoil_light_heating_oil=False, peroxide_forming=False,
    chemically_unstable=False, material_scope='substance',
    contains_nitrocellulose=False, sustains_combustion=True,
    viscosity_concession_claimed=False, initial_boiling_point_c=70,
    initial_boiling_point_method='ISO 3405', initial_boiling_point_evidence_id='BP-001',
    other_hazards_assessed=True, named_entry_checked=True,
    toxic=False, corrosive=False, environmentally_hazardous=False,
)
def classify(**updates):
    return evaluate({**BASE,**updates})

class TestClass3Expanded(unittest.TestCase):
    def test_flash_and_ibp_boundaries(self):
        for fp,pg in [(-5,'II'),(22.999,'II'),(23,'III'),(35,'III'),(60,'III')]:
            with self.subTest(fp=fp):self.assertEqual(classify(flash_point_c=fp)['candidate_packing_group'],pg)
        for bp,pg in [(35,'I'),(35.001,'II')]:
            with self.subTest(bp=bp):self.assertEqual(classify(initial_boiling_point_c=bp)['candidate_packing_group'],pg)
        self.assertEqual(classify(flash_point_c=60.001)['status'],'criteria_not_met')

    def test_state_criteria_boundaries(self):
        self.assertEqual(classify(vapour_pressure_kpa_50c=300)['status'],'criteria_met')
        self.assertEqual(classify(vapour_pressure_kpa_50c=300.001)['status'],'indeterminate')
        self.assertEqual(classify(melting_point_c=20)['status'],'criteria_met')
        self.assertEqual(classify(melting_point_c=20.01)['status'],'indeterminate')

    def test_invalid_measurements_and_methods_block(self):
        for fp in (None, True, float('nan'), float('inf')):
            with self.subTest(fp=fp):self.assertEqual(classify(flash_point_c=fp)['status'],'indeterminate')
        self.assertEqual(classify(flash_point_method='open cup')['status'],'indeterminate')
        self.assertEqual(classify(initial_boiling_point_method=None)['status'],'indeterminate')

    def test_non_equilibrium_confirmation_windows(self):
        for fp in (21,23,25,58,60,62):
            with self.subTest(fp=fp):
                self.assertEqual(classify(flash_point_c=fp,flash_point_method_kind='non_equilibrium')['status'],'indeterminate')
                self.assertNotEqual(classify(flash_point_c=fp,flash_point_method_kind='non_equilibrium',
                    flash_point_equilibrium_confirmation_c=fp,
                    flash_point_equilibrium_confirmation_id='EQ')['status'],'indeterminate')

    def test_contradictory_flash_results_block(self):
        self.assertEqual(classify(flash_point_measurements=[
            {'value_c':22.9,'evidence_id':'A'},{'value_c':23,'evidence_id':'B'}])['status'],'indeterminate')

    def test_non_sustaining_evidence_and_boundaries(self):
        for fire,status in ((100,'indeterminate'),(100.001,'criteria_not_met')):
            self.assertEqual(classify(flash_point_c=40,sustains_combustion=False,
                non_sustained_combustion_basis='ISO_2592_fire_point',fire_point_c=fire,
                sustained_combustion_evidence_id='ISO')['status'],status)
        for water,status in ((90,'indeterminate'),(90.001,'criteria_not_met')):
            self.assertEqual(classify(flash_point_c=40,sustains_combustion=False,
                non_sustained_combustion_basis='miscible_water_content',miscible_solution=True,
                water_content_mass_percent=water,sustained_combustion_evidence_id='W')['status'],status)
        self.assertEqual(classify(flash_point_c=35,sustains_combustion=False)['status'],'criteria_met')
        self.assertEqual(classify(flash_point_c=40,sustains_combustion=None)['status'],'indeterminate')
        self.assertEqual(classify(flash_point_c=40,sustains_combustion=False,
            non_sustained_combustion_basis='UN_MTC_L2_negative',
            sustained_combustion_test_result='negative',sustained_combustion_evidence_id='L2')['status'],
            'criteria_not_met')

    def test_diesel_and_heated(self):
        self.assertEqual(classify(flash_point_c=100,
            diesel_gasoil_light_heating_oil=True)['candidate_data']['named_un_candidate'],'1202')
        self.assertEqual(classify(flash_point_c=100.001,
            diesel_gasoil_light_heating_oil=True)['status'],'criteria_not_met')
        self.assertEqual(classify(flash_point_c=105,carried_at_or_above_flash_point=True)
            ['candidate_data']['named_un_candidate'],'3256')

    def test_peroxide_and_instability(self):
        self.assertEqual(classify(peroxide_forming=True,peroxide_h2o2_mass_pct=.3,
            peroxide_evidence_id='P')['status'],'criteria_met')
        r=classify(peroxide_forming=True,peroxide_h2o2_mass_pct=.300001,
                   peroxide_evidence_id='P')
        self.assertEqual(r['status'],'indeterminate')
        self.assertIn('carriage_prohibition_candidate',r['candidate_data'])
        self.assertEqual(classify(chemically_unstable=True)['status'],'indeterminate')
        self.assertEqual(classify(chemically_unstable=True,
            stabilization_precautions_documented=True)['status'],'criteria_met')

    def test_desensitized_named_entries(self):
        for un in ('1204','2059','3064','3343','3357','3379','3555'):
            with self.subTest(un=un):
                self.assertEqual(classify(liquid_desensitized_explosive=True,
                    liquid_desensitized_un_number=un)['status'],'criteria_met')
        self.assertEqual(classify(liquid_desensitized_explosive=True,
            liquid_desensitized_un_number='9999')['status'],'indeterminate')

    def test_mixture_and_nitrocellulose(self):
        self.assertEqual(classify(material_scope='untested_mixture')['status'],'indeterminate')
        self.assertEqual(classify(material_scope='whole_tested_mixture',
            mixture_actual_hazard_reviewed=True)['status'],'criteria_met')
        self.assertEqual(classify(contains_nitrocellulose=True,nitrocellulose_mass_pct=20.01,
            nitrocellulose_nitrogen_dry_mass_pct=12.6)
            ['candidate_data']['named_un_candidate'],'2059')
        self.assertEqual(classify(contains_nitrocellulose=True,nitrocellulose_mass_pct=55.01,
            nitrocellulose_nitrogen_dry_mass_pct=12.6)['status'],'indeterminate')

    def test_precedence_and_pg_only_provisional(self):
        r=classify()
        self.assertEqual(r['candidate_data']['calculated_class3_packing_group'],'II')
        self.assertIsNone(r['candidate_data']['table_a_packing_group'])
        self.assertFalse(r['is_final_section_14_classification'])
        self.assertEqual(classify(toxic=True)['status'],'indeterminate')
        self.assertEqual(classify(toxic_by_inhalation_high=True)
            ['candidate_data']['possible_primary_class'],'6.1')
        self.assertEqual(classify(flash_point_c=30,toxic_pesticide=True)
            ['candidate_data']['possible_primary_class'],'6.1')

    def test_viscosity_pg_iii_strict_boundaries(self):
        v=dict(viscosity_concession_claimed=True,solvent_separation_pct=2.99,
               receptacle_capacity_l=450,viscosity_evidence_id='V',
               solvent_separation_evidence_id='L1',
               viscosity_test_method='ISO 2431:1984 / MTC 32.4.3',
               mixture_class61_criteria_met=False,mixture_class8_criteria_met=False,
               separated_solvent_class61_criteria_met=False,
               separated_solvent_class8_criteria_met=False)
        for fp,jet,t,pg in ((18,4,21,'III'),(17,4,21,'II'),
                             (11,4,61,'III'),(10,4,61,'II'),
                             (6,6,21,'III'),(5,6,21,'II'),
                             (0,6,33,'III'),(-1,6,33,'II'),
                             (-4,6,45,'III'),(-5,6,45,'II'),
                             (-40,6,100.001,'III')):
            with self.subTest(fp=fp,jet=jet,t=t):
                self.assertEqual(classify(flash_point_c=fp,
                    viscosity_jet_diameter_mm=jet,viscosity_flow_time_s=t,**v)
                    ['candidate_packing_group'],pg)
        self.assertEqual(classify(initial_boiling_point_c=35,
            viscosity_concession_claimed=True)['status'],'indeterminate')

    def test_viscosity_pg_exclusion(self):
        v=dict(viscosity_concession_claimed=True,flash_point_c=18,
               viscosity_jet_diameter_mm=4,viscosity_flow_time_s=30,
               viscosity_test_method='ISO 2431:1984 / MTC 32.4.3',
               viscosity_evidence_id='V',solvent_separation_evidence_id='L1',
               receptacle_capacity_l=450,
               mixture_class61_criteria_met=False,mixture_class8_criteria_met=False,
               separated_solvent_class61_criteria_met=False,
               separated_solvent_class8_criteria_met=False)
        self.assertEqual(classify(solvent_separation_pct=3,**v)['candidate_packing_group'],'II')

    def test_viscosity_exempt_40_60_and_5_l(self):
        v=dict(viscosity_concession_claimed=True,flash_point_c=23,
               viscosity_jet_diameter_mm=6,
               viscosity_test_method='ISO 2431:1984 / MTC 32.4.3',
               viscosity_evidence_id='V',solvent_separation_evidence_id='L1',
               solvent_separation_pct=2.9,receptacle_capacity_l=450,
               class3_substances_mass_pct=60)
        self.assertEqual(classify(viscosity_flow_time_s=40,**v)['status'],'criteria_not_met')
        self.assertEqual(classify(viscosity_flow_time_s=39.999,**v)['status'],'criteria_met')
        env={**v,'environmentally_hazardous':True,
             'packaging_single_or_combination':True,'packaging_4_1_1_compliant':True}
        self.assertEqual(classify(viscosity_flow_time_s=60,
            net_quantity_per_single_or_inner_l=5,**env)['status'],'criteria_not_met')
        self.assertEqual(classify(viscosity_flow_time_s=60,
            net_quantity_per_single_or_inner_l=5.001,**env)['status'],'indeterminate')

    def test_missing_required_evidence(self):
        for k in ('flash_point_evidence_id','liquid_definition_basis','peroxide_forming',
                  'viscosity_concession_claimed','contains_nitrocellulose',
                  'initial_boiling_point_evidence_id'):
            with self.subTest(k=k):self.assertEqual(classify(**{k:None})['status'],'indeterminate')

if __name__=='__main__':
    unittest.main()
