"""Verification-oriented regression fixtures. Not independent regulatory sign-off."""
import importlib.util
from decimal import Decimal
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "class7.py"
spec = importlib.util.spec_from_file_location("class7_agent11", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def q(value, unit, method="laboratory measurement"):
    return {"value": str(value), "unit": unit, "source_id": "fixture-verified-against-ADR2025",
            "measured_on": "2026-11-13", "method": method}


def sample(nuclide="Co-60", activity="100001", mass="1"):
    return {"complete_radionuclide_inventory": True, "single_homogeneous_material": True,
            "mass_excludes_shielding": True, "activity_covers_entire_consignment": True,
            "activity_reference_date": "2026-11-13", "material_mass": q(mass, "g", "weighed excluding shielding"),
            "radionuclides": [{"id": nuclide, "activity": q(activity, "Bq")}],
            "material": {"phase": "solid", "activity_distributed_throughout": True,
                         "powder": False, "solid_or_binding_distribution_compliant": True}}


def sco_measurements(nf="4", fixed="0", inaccessible="0"):
    def measures(nf, fixed, inaccessible):
        return {"accessible_nonfixed": q(nf, "Bq/cm2"),
                "accessible_fixed": q(fixed, "Bq/cm2"),
                "inaccessible_total": q(inaccessible, "Bq/cm2")}
    return {"solid_object_not_itself_radioactive": True, "area_averaging_verified": True,
            "measurements": {"beta_gamma_low_toxicity_alpha": measures(nf, fixed, inaccessible),
                             "other_alpha": measures("0", "0", "0")}}


class TestClass7Scope(unittest.TestCase):
    def test_positive_co60_both_strictly_exceed(self):
        r = mod.classify(sample())
        self.assertEqual(r["scope"], "CLASS7_RADIOACTIVE_MATERIAL_CRITERIA_MET")
        self.assertEqual(r["calculation"]["exempt_consignment_limit_Bq"], "100000")
        self.assertEqual(r["calculation"]["exempt_concentration_limit_Bq_per_g"], "10")
        self.assertIsNone(r["final_un_number"])
        self.assertIsNone(r["packing_group"])

    def test_consignment_exact_threshold_is_not_exceeded(self):
        r = mod.classify(sample(activity="100000", mass="1"))
        self.assertEqual(r["scope"], "CLASS7_DEFINITION_NOT_MET_FOR_ASSESSED_MATERIAL")
        self.assertTrue(r["calculation"]["concentration_exceeds"])
        self.assertFalse(r["calculation"]["consignment_exceeds"])
        self.assertIsNone(r["transport_not_regulated"])

    def test_concentration_exact_threshold_is_not_exceeded(self):
        r = mod.classify(sample(activity="1000000", mass="100000"))
        self.assertEqual(r["scope"], "CLASS7_DEFINITION_NOT_MET_FOR_ASSESSED_MATERIAL")
        self.assertFalse(r["calculation"]["concentration_exceeds"])

    def test_concentration_below_even_when_total_above(self):
        self.assertEqual(mod.classify(sample(activity="1000001", mass="1000000"))["scope"],
                         "CLASS7_DEFINITION_NOT_MET_FOR_ASSESSED_MATERIAL")

    def test_missing_inventory_indeterminate(self):
        s = sample(); s["complete_radionuclide_inventory"] = False
        self.assertEqual(mod.classify(s)["scope"], "INDETERMINATE")

    def test_unknown_shipment_activity_basis_indeterminate(self):
        s = sample(); s["activity_covers_entire_consignment"] = False
        self.assertEqual(mod.classify(s)["scope"], "INDETERMINATE")

    def test_mixed_source_dates_blocked_without_decay_review(self):
        s = sample(); s["radionuclides"][0]["activity"]["measured_on"] = "2026-11-12"
        self.assertEqual(mod.classify(s)["scope"], "INDETERMINATE")

    def test_unknown_nuclide_indeterminate(self):
        self.assertEqual(mod.classify(sample(nuclide="Es-999"))["scope"], "INDETERMINATE")

    def test_no_unproved_dilution_with_shielding(self):
        s = sample(); s["mass_excludes_shielding"] = False
        self.assertEqual(mod.classify(s)["scope"], "INDETERMINATE")

    def test_missing_source_date_indeterminate(self):
        s = sample(); s["radionuclides"][0]["activity"].pop("measured_on")
        self.assertEqual(mod.classify(s)["scope"], "INDETERMINATE")

    def test_float_rejected_for_exact_boundaries(self):
        s = sample(); s["radionuclides"][0]["activity"]["value"] = 100001.0
        self.assertEqual(mod.classify(s)["scope"], "INDETERMINATE")

    def test_activity_prefix_conversion(self):
        s = sample(); s["radionuclides"][0]["activity"] = q("0.100001", "MBq")
        self.assertEqual(mod.classify(s)["calculation"]["total_activity_Bq"], "100001.000000")

    def test_two_nuclide_harmonic_mixture(self):
        s = sample(activity="1000000", mass="1000")
        s["radionuclides"].append({"id": "I-131", "activity": q("1000000", "Bq")})
        r = mod.classify(s)
        self.assertEqual(r["scope"], "CLASS7_RADIOACTIVE_MATERIAL_CRITERIA_MET")
        self.assertEqual(Decimal(r["calculation"]["exempt_consignment_limit_Bq"]).quantize(Decimal("0.01")),
                         Decimal("181818.18"))
        self.assertEqual(r["calculation"]["source_dates"], ["2026-11-13"])

    def test_no_inferred_daughter_equilibrium(self):
        r = mod.classify(sample(nuclide="Cs-137", activity="10001"))
        self.assertIn("Cs-137", mod.DATA["values"])
        self.assertTrue(mod.DATA["values"]["Cs-137"]["notes"])
        self.assertTrue(r["requires_independent_review"])

    def test_fissile_missing_mass_not_excluded(self):
        r = mod.classify(sample(nuclide="Pu-239", activity="10001"))
        self.assertEqual(r["fissile"]["state"], "UNRESOLVED_FISSILE_MASS")

    def test_fissile_below_quarter_gram_needs_no_other_claim(self):
        s = sample(nuclide="Pu-239", activity="10001")
        s["fissile"] = {"complete_mass_inventory": True,
                        "nuclide_masses": {"Pu-239": q("0.249", "g")},
                        "no_other_fissile_in_package_or_unpacked_consignment": True}
        self.assertEqual(mod.classify(s)["fissile"]["state"], "DEFINITION_EXCLUDED_0_25G")
        s["fissile"]["nuclide_masses"]["Pu-239"] = q("0.25", "g")
        self.assertEqual(mod.classify(s)["fissile"]["state"], "FISSILE_CONTROLS_REQUIRE_REVIEW")

    def test_fissile_below_threshold_without_package_absence_not_excepted(self):
        s = sample(nuclide="Pu-239", activity="10001")
        s["fissile"] = {"complete_mass_inventory": True,
                        "nuclide_masses": {"Pu-239": q("0.1", "g")}}
        self.assertEqual(mod.classify(s)["fissile"]["state"], "FISSILE_CONTROLS_REQUIRE_REVIEW")

    def test_lsa_i_specific_activity_30_times_limit_boundary(self):
        s = sample(activity="300000", mass="1000")
        r = mod.classify(s)
        self.assertTrue(any("LSA-I(iv)" in x for x in r["lsa"]["candidates"]))
        s["material_mass"] = q("999", "g")
        r2 = mod.classify(s)
        self.assertFalse(any("LSA-I(iv)" in x for x in r2["lsa"]["candidates"]))

    def test_lsa_ii_tritium_water_limit(self):
        s = sample(nuclide="T(H-3)", activity="1000000001", mass="1000")
        s["material"].update({"phase": "liquid", "tritiated_water": True,
                              "tritium_concentration": q("0.8", "TBq/l")})
        self.assertIn("LSA-II(i)", mod.classify(s)["lsa"]["candidates"])
        s["material"]["tritium_concentration"] = q("0.8000000001", "TBq/l")
        self.assertNotIn("LSA-II(i)", mod.classify(s)["lsa"]["candidates"])

    def test_sco_definition_exact_boundary_not_contaminated(self):
        s = sample(); s["sco"] = sco_measurements(nf="0.4")
        self.assertEqual(mod.classify(s)["sco"]["status"], "NOT_CONTAMINATED_AT_DEFINITION_LIMIT")

    def test_sco_i_limit_exactly_four(self):
        s = sample(); s["sco"] = sco_measurements(nf="4")
        self.assertEqual(mod.classify(s)["sco"]["status"], "SCO_I_CANDIDATE")

    def test_sco_ii_just_above_sco_i(self):
        s = sample(); s["sco"] = sco_measurements(nf="4.0001")
        self.assertEqual(mod.classify(s)["sco"]["status"], "SCO_II_CANDIDATE")

    def test_sco_ii_upper_boundary(self):
        s = sample(); s["sco"] = sco_measurements(nf="400")
        self.assertEqual(mod.classify(s)["sco"]["status"], "SCO_II_CANDIDATE")
        s["sco"] = sco_measurements(nf="400.0001")
        self.assertEqual(mod.classify(s)["sco"]["status"], "OUTSIDE_SCO_I_II_LIMITS_SCO_III_EXPERT_ONLY")

    def test_sco_missing_other_alpha_data_is_not_negative(self):
        s = sample(); s["sco"] = sco_measurements()
        del s["sco"]["measurements"]["other_alpha"]
        self.assertEqual(mod.classify(s)["sco"]["status"], "MISSING_MEASUREMENTS")

    def test_type_a_numeric_exact_limit_but_not_package_approval(self):
        s = sample(activity="400000000000", mass="1")
        s["package"] = {"single_package_contains_all": True}
        p = mod.classify(s)["package_screen"]
        self.assertTrue(p["type_a"]["within_numeric_limit"])
        self.assertEqual(p["type_a"]["activity_ratio"], "1")
        self.assertEqual(p["status"], "PRELIMINARY_NUMERIC_SCREEN_ONLY")
        s["radionuclides"][0]["activity"] = q("400000000001", "Bq")
        self.assertFalse(mod.classify(s)["package_screen"]["type_a"]["within_numeric_limit"])

    def test_excepted_package_material_limit_numeric_not_final(self):
        s = sample(activity="400000000", mass="1")
        s["package"] = {"single_package_contains_all": True, "excepted_route": "solid_other"}
        p = mod.classify(s)["package_screen"]
        self.assertTrue(p["excepted"]["within_material_activity_limit"])
        s["radionuclides"][0]["activity"] = q("400000001", "Bq")
        self.assertFalse(mod.classify(s)["package_screen"]["excepted"]["within_material_activity_limit"])

    def test_ti_round_up_and_white_exact_boundary(self):
        s = sample(); s["package"] = {"geometry": "single_package",
                                      "dose_rate_1m": q("0.0005", "mSv/h"),
                                      "surface_dose_rate": q("0.005", "mSv/h")}
        p = mod.classify(s)["package_screen"]["category"]
        self.assertEqual(p["transport_index"], "0")
        self.assertEqual(p["provisional_label"], "I-WHITE")
        s["package"]["dose_rate_1m"] = q("0.00051", "mSv/h")
        p = mod.classify(s)["package_screen"]["category"]
        self.assertEqual(p["transport_index"], "0.1")
        self.assertEqual(p["provisional_label"], "II-YELLOW")

    def test_surface_rate_higher_category_wins(self):
        s = sample(); s["package"] = {"geometry": "single_package",
                                      "dose_rate_1m": q("0", "mSv/h"),
                                      "surface_dose_rate": q("0.5001", "mSv/h")}
        self.assertEqual(mod.classify(s)["package_screen"]["category"]["provisional_label"], "III-YELLOW")
        s["package"]["surface_dose_rate"] = q("2.0001", "mSv/h")
        self.assertTrue(mod.classify(s)["package_screen"]["category"]["exclusive_use_review"])

    def test_special_form_claim_does_not_auto_approve(self):
        s = sample(); s["special_form_claim"] = True
        self.assertTrue(any("special_form_claim" in x for x in mod.classify(s)["issues"]))

    def test_no_case_emits_packing_group_or_final_un(self):
        for s in (sample(), sample(activity="1"), sample(nuclide="Unknown-1")):
            r = mod.classify(s)
            self.assertIsNone(r["final_un_number"])
            self.assertIsNone(r["packing_group"])
            self.assertIsNone(r["transport_not_regulated"])


if __name__ == "__main__":
    unittest.main()
