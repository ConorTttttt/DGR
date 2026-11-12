"""Independent-to-code boundary and safety checks, NOT independent regulatory validation."""
import unittest

from adr2025 import evaluate_class


class EvidenceFixtures:
    C3 = dict(physical_state='liquid', liquid_desensitized_explosive=False,
              diesel_gasoil_light_heating_oil=False, flash_point_c=22.9,
              flash_point_method='ISO 2719', flash_point_method_kind='equilibrium',
              flash_point_evidence_id='fp-001', carried_at_or_above_flash_point=False,
              liquid_definition_basis='melting_point', melting_point_c=-10,
              vapour_pressure_kpa_50c=10, completely_gaseous_at_20c=False,
              initial_boiling_point_c=70, initial_boiling_point_method='ISO 3405',
              initial_boiling_point_evidence_id='bp-001', other_hazards_assessed=True,
              named_entry_checked=True, viscosity_concession_claimed=False,
              sustains_combustion=True, material_scope='substance',
              peroxide_forming=False, chemically_unstable=False,
              contains_nitrocellulose=False, toxic=False, corrosive=False,
              environmentally_hazardous=False)
    C61 = dict(material_scope='substance',human_experience_reviewed=True,
               human_evidence_requires_expert_classification=False,
               exposure_route_evidence_complete=True, class8_priority_checked=True,
               other_hazards_assessed=True,named_entry_checked=True)
    C8 = dict(material_scope='substance', human_experience_reviewed=True,
              human_evidence_requires_expert_classification=False,
              valid_skin_test_result='corrosive',skin_exposure_min=3,
              irreversible_damage_observed_after_min=60,
              other_hazards_assessed=True,named_entry_checked=True)
    C9 = dict(pathway='aquatic',material_scope='substance',
              physical_state='liquid',lowest_valid_aquatic_acute_l_ec50_mg_l=1,
              all_other_hazard_classes_excluded=True,named_entry_checked=True)


def case(base,**kw):return {**base,**kw}


class TestClass3(unittest.TestCase):
    def test_flash_point_boundary_pgs(self):
        for fp,expected in [(-5,'II'), (22.999,'II'), (23,'III'), (35,'III'), (60,'III')]:
            with self.subTest(fp=fp):
                r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=fp))
                self.assertEqual((r['status'],r['candidate_packing_group']),('criteria_met',expected))
    def test_boiling_boundary_pgi(self):
        for b,expected in [(35,'I'),(35.001,'II')]:
            with self.subTest(b=b):
                r=evaluate_class('3',case(EvidenceFixtures.C3,initial_boiling_point_c=b))
                self.assertEqual(r['candidate_packing_group'],expected)
    def test_above_sixty_is_only_pathway_negative(self):
        r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=60.001))
        self.assertEqual(r['status'],'criteria_not_met')
        self.assertFalse(r['is_final_section_14_classification'])
    def test_diesel_exception(self):
        r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=85,diesel_gasoil_light_heating_oil=True))
        self.assertEqual(r['candidate_data']['named_un_candidate'],'1202')
    def test_heated(self):
        r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=100,carried_at_or_above_flash_point=True,carriage_temperature_c=100))
        self.assertEqual(r['candidate_data']['named_un_candidate'],'3256')
    def test_sustained_combustion_exception(self):
        r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=40,sustains_combustion=False,
                                     non_sustained_combustion_basis='UN_MTC_L2_negative',
                                     sustained_combustion_test_result='negative',
                                     sustained_combustion_evidence_id='TEST-SC-001'))
        self.assertEqual(r['rule_id'],'ADR25-C3-005')
        self.assertEqual(r['status'],'criteria_not_met')
    def test_unsubstantiated_non_sustain_cannot_grant_exception(self):
        r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=40,sustains_combustion=False))
        self.assertEqual(r['status'],'indeterminate')

    def test_non_sustain_iso_2592_fire_point_method(self):
        for fire_point,expected in [(100,'indeterminate'),(100.001,'criteria_not_met')]:
            r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=40,
                            sustains_combustion=False,non_sustained_combustion_basis='ISO_2592_fire_point',
                            fire_point_c=fire_point,sustained_combustion_evidence_id='ISO-001'))
            self.assertEqual(r['status'],expected)

    def test_non_sustain_misicible_water_method(self):
        for pct,expected in [(90,'indeterminate'),(90.001,'criteria_not_met')]:
            r=evaluate_class('3',case(EvidenceFixtures.C3,flash_point_c=40,
                            sustains_combustion=False,non_sustained_combustion_basis='miscible_water_content',
                            miscible_solution=True,water_content_mass_percent=pct,
                            sustained_combustion_evidence_id='WATER-001'))
            self.assertEqual(r['status'],expected)

    def test_missing_gates_never_pass(self):
        for k in ('liquid_desensitized_explosive','diesel_gasoil_light_heating_oil','carried_at_or_above_flash_point','named_entry_checked','viscosity_concession_claimed'):
            v=dict(EvidenceFixtures.C3);del v[k]
            with self.subTest(missing=k): self.assertEqual(evaluate_class('3',v)['status'],'indeterminate')
    def test_gas_state_gate(self):
        r=evaluate_class('3',case(EvidenceFixtures.C3,vapour_pressure_kpa_50c=300.001))
        self.assertEqual(r['status'],'indeterminate')
    def test_liquid_definition_boundary(self):
        self.assertEqual(evaluate_class('3',case(EvidenceFixtures.C3,vapour_pressure_kpa_50c=300))['status'],'criteria_met')


class TestClass61(unittest.TestCase):
    def test_oral_boundaries(self):
        for dose,pg in [(5,'I'),(5.001,'II'),(50,'II'),(50.001,'III'),(300,'III')]:
            with self.subTest(dose=dose):
                r=evaluate_class('6.1',case(EvidenceFixtures.C61,oral_ld50_mg_kg=dose))
                self.assertEqual(r['candidate_packing_group'],pg)
    def test_dermal_boundaries(self):
        for dose,pg in [(50,'I'),(200,'II'),(1000,'III')]:
            with self.subTest(dose=dose):
                self.assertEqual(evaluate_class('6.1',case(EvidenceFixtures.C61,dermal_ld50_mg_kg=dose))['candidate_packing_group'],pg)
    def test_dust_mist_4h_to_1h(self):
        r=evaluate_class('6.1',case(EvidenceFixtures.C61,dust_mist_lc50_mg_l=0.05,dust_mist_exposure_hours=4))
        self.assertEqual(r['candidate_packing_group'],'I')
    def test_vapour_saturation_and_conversion(self):
        r=evaluate_class('6.1',case(EvidenceFixtures.C61,vapour_lc50_ppm=400, vapour_exposure_hours=4,
                                    saturated_vapour_concentration_ppm_20c=1600))
        self.assertEqual(r['candidate_packing_group'],'II')
    def test_route_priority(self):
        r=evaluate_class('6.1',case(EvidenceFixtures.C61,oral_ld50_mg_kg=200,dermal_ld50_mg_kg=50))
        self.assertEqual(r['candidate_packing_group'],'I')
    def test_incomplete_data_blocks(self):
        self.assertEqual(evaluate_class('6.1',case(EvidenceFixtures.C61,oral_ld50_mg_kg=200,
            exposure_route_evidence_complete=False))['status'],'indeterminate')
        self.assertEqual(evaluate_class('6.1',case(EvidenceFixtures.C61,oral_ld50_mg_kg=400))['status'],'indeterminate')
    def test_human_experience_needs_explicit_clearance(self):
        data=case(EvidenceFixtures.C61,oral_ld50_mg_kg=10)
        del data['human_evidence_requires_expert_classification']
        self.assertEqual(evaluate_class('6.1',data)['status'],'indeterminate')

    def test_constituent_mixture_blocks(self):
        self.assertEqual(evaluate_class('6.1',case(EvidenceFixtures.C61,material_scope='untested_mixture',oral_ld50_mg_kg=1))['status'],'indeterminate')


class TestClass8(unittest.TestCase):
    def test_skin_boundaries(self):
        for exposure,obs,pg in [(3,60,'I'),(3.001,20160,'II'),(60,20160,'II'),(60.001,20160,'III'),(240,20160,'III')]:
            with self.subTest(exposure=exposure,obs=obs):
                self.assertEqual(evaluate_class('8',case(EvidenceFixtures.C8,skin_exposure_min=exposure,
                    irreversible_damage_observed_after_min=obs))['candidate_packing_group'],pg)
    def test_human_evidence_needs_explicit_clearance(self):
        data=case(EvidenceFixtures.C8)
        del data['human_evidence_requires_expert_classification']
        self.assertEqual(evaluate_class('8',data)['status'],'indeterminate')

    def test_skin_missing_timing_blocks(self):
        self.assertEqual(evaluate_class('8',case(EvidenceFixtures.C8,skin_exposure_min=241))['status'],'indeterminate')
    def test_steel_metal_threshold(self):
        metal=case(EvidenceFixtures.C8,valid_skin_test_result='non_corrosive',steel_corrosion_mm_year_55c=6.251)
        self.assertEqual(evaluate_class('8',metal)['candidate_packing_group'],'III')
    def test_both_metals_not_exceed(self):
        metal=case(EvidenceFixtures.C8,valid_skin_test_result='non_corrosive',steel_corrosion_mm_year_55c=6.25,
                   aluminium_corrosion_mm_year_55c=6.25)
        self.assertEqual(evaluate_class('8',metal)['status'],'criteria_not_met')
    def test_missing_second_metal_blocks_negative(self):
        metal=case(EvidenceFixtures.C8,valid_skin_test_result='non_corrosive',steel_corrosion_mm_year_55c=6.25)
        self.assertEqual(evaluate_class('8',metal)['status'],'indeterminate')


class TestClass9(unittest.TestCase):
    def test_aquatic_acute_boundary(self):
        r=evaluate_class('9',EvidenceFixtures.C9)
        self.assertEqual((r['status'],r['candidate_data']['candidate_un'],r['candidate_packing_group']),
                         ('criteria_met','3082','III'))
    def test_aquatic_solid(self):
        self.assertEqual(evaluate_class('9',case(EvidenceFixtures.C9,physical_state='solid'))['candidate_data']['candidate_un'],'3077')
    def test_chronic_nonrapid_threshold(self):
        r=evaluate_class('9',case(EvidenceFixtures.C9,lowest_valid_aquatic_acute_l_ec50_mg_l=12,
                                  lowest_valid_chronic_noec_ecx_mg_l=0.1,rapidly_degradable=False))
        self.assertIn('Chronic 1',r['candidate_data']['aquatic_categories'])
    def test_mixture_unimplemented(self):
        self.assertEqual(evaluate_class('9',case(EvidenceFixtures.C9,material_scope='mixture'))['status'],'indeterminate')
    def test_other_classes_not_excluded(self):
        self.assertEqual(evaluate_class('9',case(EvidenceFixtures.C9,all_other_hazard_classes_excluded=False))['status'],'indeterminate')
    def test_elevated_temp(self):
        base={'pathway':'elevated_temperature','all_other_hazard_classes_excluded':True,'named_entry_checked':True}
        for form,temp,fp,un in [('liquid',100,200,'3257'),('solid',240,None,'3258')]:
            with self.subTest(form=form):
                r=evaluate_class('9',case(base,physical_state=form,carriage_temperature_c=temp,flash_point_c=fp))
                self.assertEqual(r['candidate_data']['candidate_un'],un)
    def test_temp_liquid_above_fp_blocks(self):
        r=evaluate_class('9',dict(pathway='elevated_temperature',physical_state='liquid',carriage_temperature_c=110,
                                  flash_point_c=100,all_other_hazard_classes_excluded=True,named_entry_checked=True))
        self.assertEqual(r['status'],'indeterminate')
    def test_batteries_block(self):
        self.assertEqual(evaluate_class('9',{'pathway':'lithium_battery'})['status'],'indeterminate')


class TestGlobalSafety(unittest.TestCase):
    def test_missing_inputs_all_classes_block(self):
        for cls in ['3','6.1','8','9']:
            with self.subTest(cls=cls): self.assertEqual(evaluate_class(cls,{})['status'],'indeterminate')
    def test_never_global_not_regulated(self):
        for cls,evidence in [('3',EvidenceFixtures.C3),('6.1',case(EvidenceFixtures.C61,oral_ld50_mg_kg=300)),
                             ('8',EvidenceFixtures.C8),('9',EvidenceFixtures.C9)]:
            result=evaluate_class(cls,evidence)
            self.assertTrue(result['requires_independent_review'])
            self.assertFalse(result['is_final_section_14_classification'])
            self.assertNotIn('not_regulated',str(result).lower())
            self.assertEqual(result['source']['edition'],'ADR 2025')


if __name__=='__main__': unittest.main()