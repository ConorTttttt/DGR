"""Regression and boundary tests for provisional ADR 2025 Class 4.1 module."""
import unittest
from class41 import evaluate


def nonmetal(**overrides):
    base = dict(pathway='combustible_solid', test_method='UN_MTC_N1', screening_propagates_200mm=True, burning_time_100mm_s=40, burning_rate_mm_s=2.5, wetted_zone='passes')
    base.update(overrides)
    return base


def metal(**overrides):
    base = dict(pathway='metal_powder', test_method='UN_MTC_N1', screening_propagates_200mm=True, ignited=True)
    base.update(overrides)
    return base


def sr(**overrides):
    base = dict(pathway='self_reactive', class1_explosive=False,
                class5_1_oxidizer=False, class5_2_organic_peroxide=False,
                heat_of_decomposition_j_g=300, sadt_50kg_c=75,
                sadt_offered_package_c=55,
                decomposes_strongly_exothermically_without_oxygen=True,
                self_reactive_type='D', type_evidence='MTC_part_II_test_report',
                competent_authority_approval_verified=True)
    base.update(overrides)
    return base


def pm(**overrides):
    base = dict(pathway='polymerizing', other_classes_1_to_8='cleared',
                sapt_c=75, heat_of_reaction_j_g=301,
                polymerizes_exothermically_without_stabilization=True,
                container_kind='packaging', sapt_applies_to_offered_form_and_container=True)
    base.update(overrides)
    return base


class Class41Test(unittest.TestCase):
    def check(self, e, status, pg=None, temp=None):
        result = evaluate(e)
        self.assertEqual(result['status'], status, result)
        self.assertEqual(result['pg_candidate'], pg, result)
        self.assertEqual(result['final_packing_group'], None)
        self.assertFalse(result['independently_reviewed'])
        if temp is not None:
            self.assertEqual(result['temperature_control_required'], temp, result)
        return result

    def test_nonmetal_boundaries(self):
        cases = [
            (dict(burning_time_100mm_s=44.999), 'criteria_met', 'II'),
            (dict(wetted_zone='stops_at_least_4min'), 'criteria_met', 'III'),
            (dict(burning_time_100mm_s=45, burning_rate_mm_s=2.2), 'criteria_not_met', None),
            (dict(burning_time_100mm_s=46, burning_rate_mm_s=2.21), 'criteria_met', None),
            (dict(burning_time_100mm_s=45, burning_rate_mm_s=2.21), 'criteria_met', None),
            (dict(burning_time_100mm_s=46, burning_rate_mm_s=2.2), 'criteria_not_met', None),
            (dict(wetted_zone='unknown'), 'criteria_met', None),
            (dict(burning_time_100mm_s=None, burning_rate_mm_s=None), 'indeterminate', None),
            (dict(burning_time_100mm_s=-1), 'indeterminate', None),
            (dict(screening_propagates_200mm=False), 'criteria_not_met', None),
            (dict(test_method='GHS_category_1'), 'indeterminate', None),
            (dict(burning_time_100mm_s=None, burning_rate_mm_s=2.21), 'criteria_met', None),
            (dict(burning_time_100mm_s=55, burning_rate_mm_s=None), 'indeterminate', None),
        ]
        for overrides, stat, pg in cases:
            with self.subTest(overrides=overrides):
                v=nonmetal();v.update(overrides)
                self.check(v,stat,pg)

    def test_metal_boundaries(self):
        cases = [(0,'criteria_met','II'), (5,'criteria_met','II'),
                 (5.0001,'criteria_met','III'), (10,'criteria_met','III'),
                 (10.0001,'criteria_not_met',None),
                 (None,'indeterminate',None), (-2,'indeterminate',None)]
        for minutes,status,pg in cases:
            with self.subTest(minutes=minutes):
                self.check(metal(full_length_reaction_min=minutes),status,pg)
        self.check(dict(metal(full_length_reaction_min=5), ignited=False), 'criteria_not_met')

    def test_documented_experience_friction(self):
        self.check(dict(pathway='combustible_solid', organic=True,
                        evidence_basis='documented_experience', documented_experience_positive=True), 'criteria_met')
        self.check(dict(pathway='friction_solid', friction_fire_hazard_confirmed=True,
                        analogy_or_special_provision_verified=True), 'criteria_met')
        self.check(dict(pathway='friction_solid', friction_fire_hazard_confirmed=True), 'indeterminate')

    def test_selfreactive_boundaries(self):
        for param,value,status,temp in [
            ('heat_of_decomposition_j_g',299.999,'criteria_not_met',None),
            ('heat_of_decomposition_j_g',300,'criteria_met',True),
            ('sadt_50kg_c',75.01,'criteria_not_met',None),
            ('sadt_50kg_c',75,'criteria_met',True),
            ('sadt_offered_package_c',55,'criteria_met',True),
            ('sadt_offered_package_c',55.01,'criteria_met',False),
            ('sadt_offered_package_c',None,'indeterminate',None),
            ('self_reactive_type','A','not_accepted_for_carriage',None),
            ('self_reactive_type','G','criteria_not_met',None),
            ('self_reactive_type',None,'indeterminate',None),
        ]:
            with self.subTest(param=param,value=value):
                self.check(sr(**{param:value}),status,temp=temp)
        self.check(sr(competent_authority_approval_verified=False),'requires_authority')
        self.check(sr(class1_explosive=True),'criteria_not_met')
        self.check(sr(class5_2_organic_peroxide=True),'criteria_not_met')
        self.check(sr(class5_1_oxidizer=True, combustible_organic_mass_pct=4.99,is_mixture=True),'criteria_not_met')
        self.check(sr(class5_1_oxidizer=True, combustible_organic_mass_pct=5,is_mixture=True),'criteria_met',temp=True)
        self.check(sr(class5_1_oxidizer=None),'indeterminate')
        self.check(sr(class5_1_oxidizer=True),'indeterminate')
        self.check(sr(activator_changes_properties=True),'indeterminate')
        self.check(sr(activator_changes_properties=True,reassessed_formulation=True),'criteria_met',temp=True)

    def test_selfreactive_diluent(self):
        base=dict(diluent_used=True,liquid_diluent=True,diluent_compatible=True,
                  tested_as_shipped_with_diluent=True,
                  diluent_no_dangerous_concentration_on_leakage=True,
                  diluent_boiling_point_c=100,diluent_flash_point_c=5,control_temperature_c=50)
        self.check(sr(**base),'criteria_met',temp=True)
        self.check(sr(**dict(base,diluent_boiling_point_c=99.9)),'not_accepted_for_carriage')
        self.check(sr(**dict(base,diluent_flash_point_c=4.999)),'not_accepted_for_carriage')
        self.check(sr(**dict(base,diluent_compatible=False)),'indeterminate')

    def test_selfreactive_sample(self):
        base=dict(sample_for_further_testing=True,sample_no_more_dangerous_than_type_B=True,
                  sample_packing_method='OP2',sample_quantity_kg=10,
                  sample_temperature_conditions_adequate=True)
        self.check(sr(**base),'requires_expert_decision')
        self.check(sr(**dict(base,sample_quantity_kg=10.001)),'indeterminate')

    def test_polymer_boundaries(self):
        for change,status,temp in [
            ({'sapt_c':75},'criteria_met',False),
            ({'sapt_c':75.001},'criteria_not_met',None),
            ({'heat_of_reaction_j_g':300},'criteria_not_met',None),
            ({'heat_of_reaction_j_g':300.001},'criteria_met',False),
            ({'sapt_c':50},'criteria_met',True),
            ({'sapt_c':50.001},'criteria_met',False),
            ({'container_kind':'tank','sapt_c':45},'criteria_met',True),
            ({'container_kind':'tank','sapt_c':45.01},'criteria_met',False),
            ({'container_kind':'IBC','sapt_c':50},'criteria_met',True),
            ({'other_classes_1_to_8':'meets'},'external_class_review',None),
            ({'other_classes_1_to_8':'unknown'},'indeterminate',None),
            ({'sapt_applies_to_offered_form_and_container':False},'indeterminate',None),
        ]:
            with self.subTest(change=change):
                self.check(pm(**change),status,temp=temp)

    def test_desensitized_and_related(self):
        self.check(dict(pathway='solid_desensitized_explosive',physical_state='solid',
                        desensitized_to_suppress_explosive_properties=True,
                        exact_table_a_entry_verified=True),'criteria_met')
        self.check(dict(pathway='solid_desensitized_explosive',physical_state='solid',
                        desensitized_to_suppress_explosive_properties=True,
                        exact_table_a_entry_verified=False),'not_accepted_for_carriage')
        self.check(dict(pathway='solid_desensitized_explosive',physical_state='solid',
                        desensitized_to_suppress_explosive_properties=True),'indeterminate')
        keys=dict(series_1_2_provisionally_class1=True,series_6_exempted_class1=True,
                  not_self_reactive=True,not_class_5_1=True,not_class_5_2=True)
        self.check(dict(pathway='related_self_reactive',**keys),'criteria_met')
        self.check(dict(pathway='related_self_reactive',**dict(keys,not_class_5_2=False)),'indeterminate')

    def test_vetoes_and_non_regulated_safety(self):
        self.check(pm(dangerous_instability=True,prevented_during_carriage=False),'not_accepted_for_carriage')
        self.check(pm(dangerous_instability=True),'indeterminate')
        self.check(nonmetal(phosphorus_sulphide_not_free_from_yellow_white_phosphorus=True),'not_accepted_for_carriage')
        self.check(nonmetal(inorganic_flammable_molten=True),'not_accepted_for_carriage')
        self.check(nonmetal(flammable_solid_oxidizing_un3097=True),'not_accepted_for_carriage')
        for x in [nonmetal(screening_propagates_200mm=False),pm(sapt_c=76)]:
            r=self.check(x,'criteria_not_met')
            self.assertIsNone(r['class_candidate'])
            self.assertTrue(any('NOT a transport non-dangerous' in n for n in r['notes']))
        with self.assertRaises(ValueError):evaluate({'pathway':'GHS_flammable_solid'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
