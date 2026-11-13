"""Boundary, negative, unknown-evidence and entry-gate tests (not regulatory validation)."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from class9 import evaluate, m_from_toxicity


def c(id, pct, acute=None, chronic=None, am=None, cm=None, **kw):
    row = dict(id=id, concentration_pct=pct, acute_category=acute,
               chronic_category=chronic, acute_m=am, chronic_m=cm,
               category_basis="ADR_2025", evidence_ref="LAB:" + id,
               aquatic_evidence_complete=True,
               m_factor_evidence_ref="CERT:" + id,
               rapidly_degradable=False)
    row.update(kw)
    return row


def mix(rows, **extra):
    s = sum(i["concentration_pct"] for i in rows)
    d = dict(pathway="aquatic", material_scope="mixture", aquatic_method="summation",
             whole_mixture_data_available=False, bridging_data_available=False,
             composition_complete=True, constituents=rows,
             unlisted_fraction_assessed_nonhazardous=True,
             unlisted_fraction_evidence_ref="COMPOSITION-REVIEW-001")
    if s == 100:
        d.pop("unlisted_fraction_assessed_nonhazardous")
        d.pop("unlisted_fraction_evidence_ref")
    d.update(extra)
    return d


class SummationTests(unittest.TestCase):
    def test_acute_25_exact_and_below(self):
        for p, status in [(25, "criteria_met"), (24.999, "criteria_not_met")]:
            with self.subTest(p=p):
                self.assertEqual(evaluate(mix([c("A", p, acute="Acute 1", am=1)]))["status"], status)

    def test_m_factor_boundary_toxicities(self):
        for value, m in [(1, 1), (0.10001, 1), (0.1, 10), (0.01, 100), (0.001, 1000)]:
            self.assertEqual(m_from_toxicity(value, 1), m)
        for value, m in [(0.1, 1), (0.01, 10), (0.001, 100)]:
            self.assertEqual(m_from_toxicity(value, 0.1), m)
        self.assertEqual(m_from_toxicity(0.01, 0.01), 1)
        self.assertEqual(m_from_toxicity(0.001, 0.01), 10)

    def test_acute_m_factor_weighting(self):
        r = evaluate(mix([c("A", 2.5, acute="Acute 1", am=10)]))
        self.assertEqual(r["status"], "criteria_met")
        self.assertIn("Acute 1", r["aquatic_categories"])

    def test_toxicity_derived_m_factor(self):
        r = evaluate(mix([c("A", 2.5, acute="Acute 1", am=None, acute_l_ec50_mg_l=0.1)]))
        self.assertIn("Acute 1", r["aquatic_categories"])

    def test_conflicting_m_data_blocks(self):
        r = evaluate(mix([c("A", 3, acute="Acute 1", am=1, acute_l_ec50_mg_l=.1)]))
        self.assertEqual(r["status"], "indeterminate")
        self.assertIsNone(r["candidate_packing_group"])

    def test_missing_m_does_not_fabricate_result(self):
        r = evaluate(mix([c("A", 30, acute="Acute 1", am=None, m_factor_evidence_ref=None)]))
        self.assertEqual(r["status"], "indeterminate")

    def test_chronic1_chronic2_25pct_and_factor10(self):
        a = evaluate(mix([c("C1", 25, chronic="Chronic 1", cm=1)]))
        b = evaluate(mix([c("C1", 2.5, chronic="Chronic 1", cm=1)]))
        self.assertIn("Chronic 1", a["aquatic_categories"])
        self.assertIn("Chronic 2", b["aquatic_categories"])
        self.assertNotIn("Chronic 1", b["aquatic_categories"])

    def test_chronic2_25pct_exact(self):
        r = evaluate(mix([c("C2", 25, chronic="Chronic 2")]))
        self.assertIn("Chronic 2", r["aquatic_categories"])

    def test_chronic2_combination_and_boundary(self):
        r = evaluate(mix([c("C1", 1, chronic="Chronic 1", cm=1), c("C2", 15, chronic="Chronic 2")]))
        self.assertIn("Chronic 2", r["aquatic_categories"])
        r = evaluate(mix([c("C1", 1, chronic="Chronic 1", cm=1), c("C2", 14.99, chronic="Chronic 2")]))
        self.assertNotIn("Chronic 2", r["aquatic_categories"])

    def test_unknown_relevant_constituent_prohibits_negative(self):
        r = evaluate(mix([c("U", 98, aquatic_evidence_complete=False)]))
        self.assertEqual(r["status"], "indeterminate")
        self.assertFalse(r["candidate_data"]["categories_definitive"])

    def test_unknown_constituent_preserves_known_positive_but_nondefinitive(self):
        r = evaluate(mix([c("A", 3, acute="Acute 1", am=10), c("U", 97, aquatic_evidence_complete=False)]))
        self.assertEqual(r["status"], "criteria_met")
        self.assertFalse(r["candidate_data"]["categories_definitive"])

    def test_unlisted_fraction_requires_documentary_nonhazard_review(self):
        r = evaluate(mix([c("A", 1)], unlisted_fraction_assessed_nonhazardous=False))
        self.assertEqual(r["status"], "indeterminate")
        r2 = evaluate(mix([c("A", 1)]))
        self.assertEqual(r2["status"], "criteria_not_met")

    def test_fraction_over_100_rejected(self):
        r = evaluate(mix([c("A", 70), c("B", 40)]))
        self.assertEqual(r["status"], "indeterminate")

    def test_unknown_or_clp_only_basis_fails(self):
        r = evaluate(mix([c("A", 50, acute="Acute 1", am=1, category_basis="CLP")]))
        self.assertEqual(r["status"], "indeterminate")

    def test_small_but_highly_toxic_not_ignored(self):
        r = evaluate(mix([c("A", .025, acute="Acute 1", am=1000)]))
        self.assertEqual(r["status"], "criteria_met")

    def test_missing_whole_test_and_bridge_hierarchy_blocks(self):
        r = evaluate(mix([c("A", 25, acute="Acute 1", am=1)], whole_mixture_data_available=None))
        self.assertFalse(r["candidate_data"]["categories_definitive"])


class WholeAndBridgingTests(unittest.TestCase):
    def base(self, **kw):
        x = dict(pathway="aquatic", material_scope="mixture", aquatic_method="whole_tested",
                 whole_mixture_test_adequate=True, test_evidence_ref="WHOLE-TEST-1",
                 acute_l_ec50_mg_l=2, chronic_noec_ecx_mg_l=2)
        x.update(kw)
        return x

    def test_whole_tested_negative_only_when_complete(self):
        self.assertEqual(evaluate(self.base())["status"], "criteria_not_met")
        x = self.base(); x.pop("chronic_noec_ecx_mg_l")
        self.assertEqual(evaluate(x)["status"], "indeterminate")

    def test_whole_tested_chronic_rapid_threshold(self):
        r = evaluate(self.base(chronic_noec_ecx_mg_l=0.1, all_relevant_ingredients_rapidly_degradable=True))
        self.assertIn("Chronic 2", r["aquatic_categories"])
        r = evaluate(self.base(chronic_noec_ecx_mg_l=0.100001, all_relevant_ingredients_rapidly_degradable=True))
        self.assertNotIn("Chronic 2", r["aquatic_categories"])

    def test_substance_chronic_nrd_0_1_and_rd_0_01(self):
        d = dict(pathway="aquatic", material_scope="substance", acute_l_ec50_mg_l=2,
                 chronic_noec_ecx_mg_l=0.1, test_evidence_ref="LAB", algal_data_exception_reviewed=True)
        self.assertIn("Chronic 1", evaluate(dict(d, rapidly_degradable=False))["aquatic_categories"])
        self.assertIn("Chronic 2", evaluate(dict(d, rapidly_degradable=True))["aquatic_categories"])

    def test_substance_bcf_fallback_and_default_nrd(self):
        d = dict(pathway="aquatic", material_scope="substance", acute_l_ec50_mg_l=5,
                 adequate_chronic_data=False, rapidly_degradable=True, bcf=500,
                 test_evidence_ref="LAB", algal_data_exception_reviewed=True)
        self.assertIn("Chronic 2", evaluate(d)["aquatic_categories"])
        d.pop("rapidly_degradable"); d.pop("bcf"); d["degradation_data_absent"] = True
        self.assertIn("Chronic 2", evaluate(d)["aquatic_categories"])

    def test_substance_negative_requires_trophic_coverage(self):
        d = dict(pathway="aquatic", material_scope="substance", acute_l_ec50_mg_l=10,
            chronic_noec_ecx_mg_l=10, rapidly_degradable=False,
            test_evidence_ref="LAB", algal_data_exception_reviewed=True)
        self.assertEqual(evaluate(d)["status"], "indeterminate")
        self.assertEqual(evaluate(dict(d, trophic_levels_adequately_assessed=True))["status"], "criteria_not_met")

    def test_bridging_requires_verified_references_and_conditions(self):
        d = dict(pathway="aquatic", material_scope="mixture", aquatic_method="bridging",
                 bridging_principle="dilution", diluent_equal_or_lower_aquatic_hazard=True,
                 diluent_no_effect_on_other_ingredients=True, reference_category_basis="ADR_2025",
                 reference_evidence_ref="MIX-TEST", reference_categories=["Acute 1"])
        self.assertEqual(evaluate(d)["status"], "criteria_met")
        d["diluent_no_effect_on_other_ingredients"] = None
        self.assertEqual(evaluate(d)["status"], "indeterminate")

    def test_additivity_requires_tested_fraction_and_taxonomic_evidence(self):
        d = self.base(aquatic_method="additivity")
        self.assertEqual(evaluate(d)["status"], "indeterminate")
        d["toxicity_constituents"] = [dict(id="A", concentration_pct=25,
            acute_l_ec50_mg_l=0.5, chronic_noec_mg_l=2,
            rapidly_degradable=True, test_evidence_ref="TEST-A")]
        d["classified_constituents"] = []
        d["taxonomic_endpoint_selection_ref"] = "TAXA-1"
        d["unlisted_fraction_assessed_nonhazardous"] = True
        d["unlisted_fraction_evidence_ref"] = "REVIEW-R"
        r = evaluate(d)
        self.assertEqual(r["status"], "criteria_met")
        self.assertIn("Acute 1", r["aquatic_categories"])
        self.assertEqual(r["candidate_data"]["acute_additive_lec50_mg_l"], "0.5")
        self.assertEqual(r["candidate_data"]["tested_fraction_pct"], "25")

    def test_chronic_additivity_nrd_adjustment(self):
        d = self.base(aquatic_method="additivity", taxonomic_endpoint_selection_ref="TAXA-2",
            toxicity_constituents=[dict(id="NRD", concentration_pct=25,
                acute_l_ec50_mg_l=2, chronic_noec_mg_l=0.1,
                rapidly_degradable=False, test_evidence_ref="NRD-TEST")],
            classified_constituents=[], unlisted_fraction_assessed_nonhazardous=True,
            unlisted_fraction_evidence_ref="R")
        r = evaluate(d)
        self.assertEqual(r["status"], "criteria_met")
        self.assertIn("Chronic 1", r["aquatic_categories"])
        self.assertEqual(r["candidate_data"]["chronic_additive_eq_noec_mg_l"], "0.01")

    def test_additivity_invalid_taxon_and_missing_data_blocks(self):
        d = self.base(aquatic_method="additivity", toxicity_constituents=[
            dict(id="A", concentration_pct=25, acute_l_ec50_mg_l=0.3,
                 chronic_noec_mg_l=0.01, rapidly_degradable=True, test_evidence_ref="A")])
        self.assertEqual(evaluate(d)["status"], "indeterminate")
        d["taxonomic_endpoint_selection_ref"] = "TAXA-1"
        d["toxicity_constituents"][0].pop("chronic_noec_mg_l")
        self.assertEqual(evaluate(d)["status"], "indeterminate")


class TransportAndOtherTests(unittest.TestCase):
    def aq(self, **kw):
        d = dict(pathway="aquatic", material_scope="mixture", aquatic_method="whole_tested",
                 acute_l_ec50_mg_l=.5, chronic_noec_ecx_mg_l=2,
                 whole_mixture_test_adequate=True, test_evidence_ref="M-1",
                 physical_state="liquid", other_class_or_class9_entry_applies=False,
                 cross_class_review_ref="AGENT2-1", named_entry_review_ref="AGENT1-1")
        d.update(kw)
        return d

    def test_aquatic_primary_requires_verified_table_a_pg(self):
        r = evaluate(self.aq())
        self.assertEqual(r["status"], "criteria_met")
        self.assertEqual(r["candidate_data"]["candidate_un"], "3082")
        self.assertIsNone(r["candidate_packing_group"])
        row = dict(edition="ADR 2025", un="3082", **{"class": "9"},
                   classification_code="M6", packing_group="III", evidence_ref="TABLE-A-VERIFIED")
        r = evaluate(self.aq(verified_table_a_row=row))
        self.assertEqual(r["candidate_packing_group"], "III")

    def test_wrong_row_cannot_resolve_pg(self):
        row = dict(edition="ADR 2025", un="3077", **{"class": "9"},
                   classification_code="M7", packing_group="III", evidence_ref="X")
        self.assertIsNone(evaluate(self.aq(verified_table_a_row=row))["candidate_packing_group"])

    def test_aquatic_additional_hazard_no_primary_pg(self):
        r = evaluate(self.aq(other_class_or_class9_entry_applies=True))
        self.assertEqual(r["candidate_data"]["environmental_role"], "additional_to_other_class_or_class9_entry")
        self.assertNotIn("candidate_un", r["candidate_data"])

    def test_solid_un_candidate(self):
        self.assertEqual(evaluate(self.aq(physical_state="solid"))["candidate_data"]["candidate_un"], "3077")

    def test_temp_thresholds_and_flash_point(self):
        base = dict(pathway="elevated_temperature", other_classes_excluded_review_ref="PRECEDENCE",
                    named_entry_review_ref="DGL")
        self.assertEqual(evaluate(dict(base, physical_state="liquid", carriage_temperature_c=99.999))["status"], "criteria_not_met")
        r = evaluate(dict(base, physical_state="liquid", carriage_temperature_c=100, flash_point_c=101))
        self.assertEqual((r["status"], r["candidate_data"]["candidate_un"]), ("criteria_met", "3257"))
        self.assertEqual(evaluate(dict(base, physical_state="liquid", carriage_temperature_c=100, flash_point_c=100))["status"], "indeterminate")
        self.assertEqual(evaluate(dict(base, physical_state="solid", carriage_temperature_c=239.999))["status"], "criteria_not_met")
        self.assertEqual(evaluate(dict(base, physical_state="solid", carriage_temperature_c=240))["candidate_data"]["candidate_un"], "3258")

    def test_pcb_cutoff_applies_only_to_mixtures(self):
        a = dict(pathway="subclass", subclass="pcb_pct", identity_evidence_ref="PCB-ID", material_scope="mixture", pcb_pct_mg_kg=50)
        self.assertEqual(evaluate(a)["status"], "criteria_not_met")
        self.assertEqual(evaluate(dict(a, pcb_pct_mg_kg=50.0001))["status"], "criteria_met")
        self.assertEqual(evaluate(dict(a, material_scope="article"))["status"], "criteria_met")

    def test_polymer_vapour_55_boundary(self):
        d = dict(pathway="subclass", subclass="polymer_vapour", identity_evidence_ref="POLY",
                 polymer_contains_flammable_liquid=True, contained_flammable_liquid_flash_point_c=55)
        self.assertEqual(evaluate(d)["status"], "criteria_met")
        self.assertEqual(evaluate(dict(d, contained_flammable_liquid_flash_point_c=55.001))["status"], "criteria_not_met")

    def test_battery_38_3_and_sp_gate(self):
        d = dict(pathway="subclass", subclass="battery", identity_evidence_ref="BAT-ID",
                 battery_chemistry="lithium_ion", configuration="alone",
                 tested_cell_and_battery_type_38_3=True, vent_or_rupture_protection=True,
                 external_short_circuit_protection=True, reverse_current_protection_if_applicable=True,
                 quality_management_programme=True, test_summary_available=True,
                 sp188_230_310_376_400_and_other_applicability_review_ref="SP-REVIEW")
        r = evaluate(d)
        self.assertEqual(r["status"], "criteria_met")
        self.assertEqual(r["candidate_data"]["candidate_un"], "3480")
        self.assertIsNone(r["candidate_packing_group"])
        self.assertEqual(evaluate(dict(d, tested_cell_and_battery_type_38_3=False))["status"], "indeterminate")

    def test_sodium_definition_and_entry(self):
        d = dict(pathway="subclass", subclass="battery", identity_evidence_ref="NA-ID",
                 battery_chemistry="sodium_ion", configuration="contained",
                 tested_cell_and_battery_type_38_3=True, vent_or_rupture_protection=True,
                 external_short_circuit_protection=True, reverse_current_protection_if_applicable=True,
                 quality_management_programme=True, test_summary_available=True,
                 sp188_230_310_376_400_and_other_applicability_review_ref="SP-REVIEW")
        self.assertEqual(evaluate(d)["status"], "indeterminate")
        r = evaluate(dict(d, organic_electrolyte_no_metallic_sodium_verified=True))
        self.assertEqual(r["candidate_data"]["candidate_un"], "3552")
        self.assertEqual(r["status"], "criteria_met")

    def test_no_catchall_for_missing_and_unsupported(self):
        for d in ({}, {"pathway": "subclass", "subclass": "unknown"}, {"pathway": "aquatic"}):
            r = evaluate(d)
            self.assertEqual(r["status"], "indeterminate")
            self.assertIsNone(r["candidate_packing_group"])
            self.assertFalse(r["is_final_section_14_classification"])

    def test_asbestos_gmo_m11_scope(self):
        self.assertEqual(evaluate(dict(pathway="subclass", subclass="asbestos", identity_evidence_ref="A", asbestos_type="amphibole"))["status"], "criteria_met")
        self.assertEqual(evaluate(dict(pathway="subclass", subclass="gmo", identity_evidence_ref="G"))["status"], "indeterminate")
        self.assertEqual(evaluate(dict(pathway="subclass", subclass="m11_entry", identity_evidence_ref="M"))["status"], "indeterminate")


if __name__ == "__main__":
    unittest.main()
