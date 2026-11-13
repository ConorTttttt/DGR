"""Provisional ADR 2025 Class 9 evidence-to-candidate evaluator (Agent 13).

No CLP/GHS auto-conversion, transport exemption, final UN assignment or final SDS output.
See rules.json and HANDOVER.md. Decimal arithmetic is used at regulatory boundaries.
"""
from decimal import Decimal, InvalidOperation

EDITION = "ADR 2025"
SOURCE = "ECE/TRANS/352, Volume I, English edition (2024)"
MTC = "ST/SG/AC.10/11/Rev.8 (2023) + Amendment 1 (where applicable)"
TABLE_ACLAUSE = "3.2.1 Table A (3a, 3b, 4, 6)"
AQ = ["2.1.3.8", "2.2.9.1.10.3.1", "2.2.9.1.10.4", "2.2.9.1.10.6"]


def num(v, *, zero=False):
    """Return finite Decimal from genuine numeric measurements, excluding bool/text."""
    if isinstance(v, bool) or not isinstance(v, (int, float, Decimal)):
        return None
    try:
        d = Decimal(str(v))
        return d if d.is_finite() and (d >= 0 if zero else d > 0) else None
    except (InvalidOperation, ValueError):
        return None


def signed_num(v):
    """Finite signed numeric measurement (e.g. a legitimate negative flash point)."""
    if isinstance(v, bool) or not isinstance(v, (int, float, Decimal)):
        return None
    try:
        d = Decimal(str(v))
        return d if d.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def result(rule, status="indeterminate", *, clauses=(), missing=(), categories=(), data=None, notes=(), pg=None):
    assert status in ("indeterminate", "criteria_met", "criteria_not_met")
    return {"hazard_class": "9", "status": status, "rule_id": rule,
            "source": {"edition": EDITION, "document": SOURCE, "clauses": list(clauses)},
            "candidate_packing_group": pg, "aquatic_categories": sorted(set(categories)),
            "candidate_data": data or {}, "missing_evidence": sorted(set(missing)),
            "limitations": list(notes), "requires_independent_review": True,
            "is_final_section_14_classification": False}


def m_from_toxicity(v, base):
    """Table 2.2.9.1.10.4.6.4: factor x10 at each inclusive decade boundary."""
    d, b = num(v), Decimal(str(base))
    if d is None or d > b:
        return None
    factor = 1
    while d <= b / 10:
        factor *= 10
        b /= 10
    return factor


def _factor(c, pathway, missing):
    field = "acute_m" if pathway == "acute" else "chronic_m"
    tox = "acute_l_ec50_mg_l" if pathway == "acute" else "chronic_noec_mg_l"
    base = 1 if pathway == "acute" else (Decimal("0.01") if c.get("rapidly_degradable") is True else Decimal("0.1") if c.get("rapidly_degradable") is False else None)
    if base is None:
        missing.add(f"{c.get('id','?')}.rapidly_degradable")
        return None
    expected = m_from_toxicity(c[tox], base) if tox in c else None
    provided = c.get(field)
    provided_ok = type(provided) is int and provided >= 1 and str(provided)[0] == "1" and set(str(provided)[1:]) <= {"0"}
    if provided is not None and not provided_ok:
        missing.add(f"{c.get('id','?')}.{field}_valid")
        return None
    if provided is not None and expected is not None and provided != expected:
        missing.add(f"{c.get('id','?')}.{field}_matches_toxicity")
        return None
    if expected is None and provided is None:
        missing.add(f"{c.get('id','?')}.{field}_or_valid_toxicity")
        return None
    # When based on an attested M factor, requiring documentary provenance is mandatory.
    if expected is None and not c.get("m_factor_evidence_ref"):
        missing.add(f"{c.get('id','?')}.m_factor_evidence_ref")
        return None
    return provided if provided is not None else expected


def _mix_summation(e):
    clauses = ["2.2.9.1.10.4.1", "2.2.9.1.10.4.2", "2.2.9.1.10.4.5.1",
               "2.2.9.1.10.4.6.2.2", "2.2.9.1.10.4.6.3.3",
               "2.2.9.1.10.4.6.4", "2.2.9.1.10.4.6.5"]
    missing = set()
    if e.get("whole_mixture_data_available") is not False:
        missing.add("whole_mixture_data_available=False")
    if e.get("bridging_data_available") is not False:
        missing.add("bridging_data_available=False")
    # This is a method-selection gate, not an aquatic threshold. If whole-mixture
    # data or eligible bridging may apply, the lower-priority summation method
    # cannot independently establish a classification.
    method_hierarchy_blocked = bool(missing)
    cs = e.get("constituents")
    if not isinstance(cs, list) or not cs:
        return result("C9-AQ-SUM", clauses=clauses, missing=["constituents"])
    if e.get("composition_complete") is not True:
        missing.add("composition_complete")
    a, c1, c2, pct_sum = Decimal(0), Decimal(0), Decimal(0), Decimal(0)
    unknown = False
    for index, c in enumerate(cs):
        if not isinstance(c, dict):
            missing.add(f"constituents[{index}]")
            continue
        name = str(c.get("id", index))
        pct = num(c.get("concentration_pct"), zero=True)
        if pct is None or pct > 100:
            missing.add(f"{name}.concentration_pct")
            continue
        pct_sum += pct
        if not c.get("evidence_ref") or c.get("category_basis") != "ADR_2025":
            missing.add(f"{name}.ADR_2025_evidence_ref")
            continue
        acute, chronic = c.get("acute_category"), c.get("chronic_category")
        if acute not in (None, "Acute 1") or chronic not in (None, "Chronic 1", "Chronic 2"):
            missing.add(f"{name}.valid_category")
            continue
        # Every declared ingredient is included, including toxic constituents below 0.1%.
        # This is intentionally conservative; negative decisions require complete evidence.
        if acute == "Acute 1":
            m = _factor(c, "acute", missing)
            if m is not None:
                a += pct * m
        if chronic == "Chronic 1":
            m = _factor(c, "chronic", missing)
            if m is not None:
                c1 += pct * m
        elif chronic == "Chronic 2":
            c2 += pct
        if not (c.get("aquatic_evidence_complete") is True):
            unknown = True
        if c.get("unknown_aquatic_data") is True:
            unknown = True
    if pct_sum > 100:
        missing.add("sum_concentrations_must_not_exceed_100_pct")
    if pct_sum < 100 and not (e.get("unlisted_fraction_assessed_nonhazardous") is True and e.get("unlisted_fraction_evidence_ref")):
        unknown = True
        missing.add("unlisted_fraction_aquatic_evidence")
    cats = []
    if a >= 25:
        cats.append("Acute 1")
    if c1 >= 25:
        cats.append("Chronic 1")
    elif 10 * c1 + c2 >= 25:
        cats.append("Chronic 2")
    # Never generate definitive negative where evidence is missing; preserve known positives as provisional.
    valid = not any("valid" in x or "must_not" in x or "matches_toxicity" in x for x in missing)
    status = "indeterminate" if method_hierarchy_blocked else ("criteria_met" if cats and valid else "indeterminate" if (missing or unknown) else "criteria_not_met")
    return result("C9-AQ-SUM", status, clauses=clauses, missing=missing, categories=cats,
                  data={"weighted_acute_1_pct": str(a), "weighted_chronic_1_pct": str(c1),
                        "chronic_2_pct": str(c2), "composition_reported_pct": str(pct_sum),
                        "categories_definitive": not (missing or unknown)},
                  notes=["Missing/unlisted constituent information prevents a definitive category under 2.2.9.1.10.4.6.5"] if (missing or unknown) else [])


def _mix_additivity(e):
    """ADR 2.2.9.1.10.4.5.2: compute toxicity of tested fraction, then sum its categories.

    Constituents must have both validated acute and chronic endpoints for a definitive
    combined assessment; incompatible taxonomic evidence is not approximated.
    """
    clauses = ["2.2.9.1.10.4.5.2(a)", "2.2.9.1.10.4.5.2(b)",
               "2.2.9.1.10.4.5.3", "2.2.9.1.10.4.5.4"]
    raw = e.get("toxicity_constituents")
    if not isinstance(raw, list) or not raw:
        return result("C9-AQ-ADD", clauses=clauses, missing=["toxicity_constituents"])
    if not e.get("taxonomic_endpoint_selection_ref"):
        return result("C9-AQ-ADD", clauses=clauses, missing=["taxonomic_endpoint_selection_ref"])
    acute_c, acute_den, chronic_c, chronic_den = (Decimal(0) for _ in range(4))
    missing = set()
    for i, r in enumerate(raw):
        if not isinstance(r, dict):
            missing.add(f"raw[{i}].record")
            continue
        n = str(r.get("id", i))
        pc = num(r.get("concentration_pct"), zero=True)
        acute = num(r.get("acute_l_ec50_mg_l"))
        chronic = num(r.get("chronic_noec_mg_l"))
        rd = r.get("rapidly_degradable")
        if pc is None or pc > 100 or acute is None or chronic is None or type(rd) is not bool:
            missing.add(f"{n}.complete_acute_and_chronic_endpoint_data")
            continue
        if not r.get("test_evidence_ref"):
            missing.add(f"{n}.test_evidence_ref")
            continue
        acute_c += pc
        acute_den += pc / acute
        chronic_c += pc
        chronic_den += pc / (chronic if rd else Decimal("0.1") * chronic)
    if missing or acute_c <= 0 or chronic_c <= 0 or acute_den <= 0 or chronic_den <= 0:
        return result("C9-AQ-ADD", clauses=clauses, missing=missing or ["nonempty_valid_toxicity_fraction"])
    acute_eq = acute_c / acute_den
    chronic_eq = chronic_c / chronic_den
    if e.get("classified_constituents") is not None and not isinstance(e.get("classified_constituents"), list):
        return result("C9-AQ-ADD", clauses=clauses, missing=["classified_constituents_list"])
    synthetic = {"id": "tested_portion", "concentration_pct": acute_c,
                 "acute_category": "Acute 1" if acute_eq <= 1 else None,
                 "chronic_category": "Chronic 1" if chronic_eq <= Decimal("0.01") else "Chronic 2" if chronic_eq <= Decimal("0.1") else None,
                 "acute_l_ec50_mg_l": acute_eq, "chronic_noec_mg_l": chronic_eq,
                 "rapidly_degradable": True, "category_basis": "ADR_2025",
                 "evidence_ref": e["taxonomic_endpoint_selection_ref"],
                 "aquatic_evidence_complete": True}
    summary_input = dict(e, aquatic_method="summation", constituents=list(e.get("classified_constituents", [])) + [synthetic])
    out = _mix_summation(summary_input)
    out["rule_id"] = "C9-AQ-ADD"
    out["source"]["clauses"] = sorted(set(out["source"]["clauses"] + clauses))
    out["candidate_data"].update({"acute_additive_lec50_mg_l": str(acute_eq),
                                  "chronic_additive_eq_noec_mg_l": str(chronic_eq),
                                  "tested_fraction_pct": str(acute_c)})
    return out


def _whole(e, *, mixture):
    clauses = ["2.2.9.1.10.4.3.3", "2.2.9.1.10.4.3.4"] if mixture else ["2.2.9.1.10.3.1", "Table 2.2.9.1.10.3.1"]
    cats, missing = [], []
    acute = num(e.get("acute_l_ec50_mg_l"))
    chronic = num(e.get("chronic_noec_ecx_mg_l"))
    if acute is not None and acute <= 1:
        cats.append("Acute 1")
    elif acute is None:
        missing.append("acute_l_ec50_mg_l_or_endpoint_clearance")
    if chronic is not None:
        if mixture:
            rd = e.get("all_relevant_ingredients_rapidly_degradable")
            if type(rd) is not bool:
                missing.append("all_relevant_ingredients_rapidly_degradable")
                rd = None
        else:
            rd = e.get("rapidly_degradable")
            if rd is None and e.get("degradation_data_absent") is True:
                rd = False  # Table 2.2.9.1.10.3.1 Note 4: no useful data -> not rapidly degradable
            if type(rd) is not bool:
                missing.append("rapid_degradation_evaluation")
                rd = None
        # A missing RD conclusion cannot be silently interpreted as NRD.
        # Only a documented lack of degradation data invokes the ADR Note 4 default.
        if rd is not None:
            c1, c2 = (Decimal("0.01"), Decimal("0.1")) if rd else (Decimal("0.1"), Decimal("1"))
            if chronic <= c1:
                cats.append("Chronic 1")
            elif chronic <= c2:
                cats.append("Chronic 2")
    elif not mixture and e.get("adequate_chronic_data") is False and acute is not None:
        # Table 2.2.9.1.10.3.1(b)(iii); no-data degradability defaults to NRD (Note 4).
        rd = e.get("rapidly_degradable")
        if rd is None and e.get("degradation_data_absent") is True:
            rd = False
        bcf = num(e.get("bcf"), zero=True)
        lk = e.get("log_kow")
        logkow = Decimal(str(lk)) if type(lk) in (float, int, Decimal) and Decimal(str(lk)).is_finite() else None
        bio = bcf >= 500 if bcf is not None else (logkow >= 4 if logkow is not None and e.get("log_kow_is_appropriate") is True else False)
        if (rd is False or bio) and acute <= 1:
            cats.append("Chronic 1")
        elif (rd is False or bio) and acute <= 10:
            cats.append("Chronic 2")
        if rd is None:
            missing.append("degradability_or_confirmed_absence")
    else:
        missing.append("chronic_noec_ecx_mg_l_or_fallback_assessment")
    if e.get("test_evidence_ref") is None:
        missing.append("test_evidence_ref")
    if not mixture and e.get("algal_data_exception_reviewed") is not True:
        missing.append("algal_data_exception_reviewed")
    if not mixture and e.get("trophic_levels_adequately_assessed") is not True:
        missing.append("trophic_levels_adequately_assessed")
    if mixture and e.get("whole_mixture_test_adequate") is not True:
        missing.append("whole_mixture_test_adequate")
    status = "criteria_met" if cats and not ("test_evidence_ref" in missing or "whole_mixture_test_adequate" in missing) else ("criteria_not_met" if not cats and not missing else "indeterminate")
    return result("C9-AQ-WHOLE", status, clauses=clauses, categories=cats, missing=missing,
                  data={"categories_definitive": not bool(missing)})


def _bridge(e):
    # Bridging requires a verified reference classification and evidenced facts, not a blind CLP inheritance.
    checks = {"dilution": ["diluent_equal_or_lower_aquatic_hazard", "diluent_no_effect_on_other_ingredients"],
              "batching": ["same_commercial_product", "same_manufacturer_control", "no_significant_variation"],
              "concentration": ["reference_acute_or_chronic1", "relevant_severe_ingredients_concentrated"],
              "interpolation": ["identical_ingredients", "identical_active_ingredients", "intermediate_active_concentrations", "references_same_category"],
              "similar": ["common_ingredient_concentration_equal", "substitutes_equal_concentration", "substitutes_equivalent_aquatic_hazard", "no_effect_on_common_ingredient"]}
    kind = e.get("bridging_principle")
    clauses = ["2.2.9.1.10.4.4.1"]
    cite = {"dilution": "2.2.9.1.10.4.4.2", "batching": "2.2.9.1.10.4.4.3", "concentration": "2.2.9.1.10.4.4.4", "interpolation": "2.2.9.1.10.4.4.5", "similar": "2.2.9.1.10.4.4.6"}
    if kind not in checks:
        return result("C9-AQ-BRIDGE", clauses=clauses, missing=["supported_bridging_principle"])
    clauses.append(cite[kind])
    missing = [k for k in checks[kind] if e.get(k) is not True]
    if e.get("reference_category_basis") != "ADR_2025" or not e.get("reference_evidence_ref"):
        missing.append("ADR_2025_reference_evidence")
    cats = e.get("reference_categories")
    if not isinstance(cats, list) or any(c not in ("Acute 1", "Chronic 1", "Chronic 2") for c in cats):
        missing.append("valid_reference_categories")
        cats = []
    return result("C9-AQ-BRIDGE", "criteria_met" if cats and not missing else "indeterminate",
                  clauses=clauses, missing=missing, categories=cats,
                  notes=["Bridging assumptions require independent scientific review; category not a final transport assignment"])


def aquatic(e):
    if e.get("material_scope") not in ("substance", "mixture"):
        return result("C9-AQ-GATE", clauses=AQ, missing=["material_scope"])
    if e.get("material_scope") == "substance":
        hazard = _whole(e, mixture=False)
    else:
        method = e.get("aquatic_method")
        if method == "whole_tested":
            hazard = _whole(e, mixture=True)
        elif method == "bridging":
            hazard = _bridge(e)
        elif method == "summation":
            hazard = _mix_summation(e)
        elif method == "additivity":
            hazard = _mix_additivity(e)
        else:
            return result("C9-AQ-GATE", clauses=["2.2.9.1.10.4.2", "2.2.9.1.10.4.5.2"],
                          missing=["supported_aquatic_method"])
    # Transport class/entry is a separate, cross-class/Chapter 3.2 decision.
    data = dict(hazard["candidate_data"])
    data["environmental_hazard_status"] = hazard["status"]
    other = e.get("other_class_or_class9_entry_applies")
    if hazard["status"] == "criteria_met":
        if other is True:
            data["environmental_role"] = "additional_to_other_class_or_class9_entry"
        elif other is False and e.get("cross_class_review_ref") and e.get("named_entry_review_ref"):
            form = e.get("physical_state")
            if form in ("solid", "liquid"):
                un, code = ("3077", "M7") if form == "solid" else ("3082", "M6")
                data.update({"environmental_role": "primary_class9_candidate", "candidate_un": un, "candidate_code": code})
                row = e.get("verified_table_a_row")
                if (isinstance(row, dict) and row.get("edition") == EDITION and row.get("un") == un
                        and row.get("class") == "9" and row.get("classification_code") == code
                        and row.get("packing_group") == "III" and row.get("evidence_ref")):
                    hazard["candidate_packing_group"] = "III"
                    data["packing_group_basis"] = "2.2.9.1.10.6 + verified 3.2.1 Table A row"
                else:
                    data["packing_group_pending"] = "verified_ADR_2025_Table_A_row"
            else:
                data["environmental_role"] = "primary_candidate_pending_physical_state"
        else:
            data["environmental_role"] = "pending_cross_class_and_named_entry_review"
    hazard["candidate_data"] = data
    hazard["source"]["clauses"] = sorted(set(hazard["source"]["clauses"] + AQ + ([TABLE_ACLAUSE] if hazard["candidate_packing_group"] else [])))
    return hazard


def elevated(e):
    clauses = ["2.2.9.1.13", "2.2.9.3", TABLE_ACLAUSE]
    state = e.get("physical_state")
    t = num(e.get("carriage_temperature_c"), zero=True)
    if state not in ("solid", "liquid") or t is None:
        return result("C9-TEMP", clauses=clauses, missing=["physical_state_and_carriage_temperature_c"])
    if (state == "liquid" and t < 100) or (state == "solid" and t < 240):
        return result("C9-TEMP", "criteria_not_met", clauses=clauses,
                      notes=["Only elevated-temperature criterion excluded"])
    if state == "liquid":
        fp = signed_num(e.get("flash_point_c"))
        if fp is None and e.get("flash_point_absent_evidence_ref") is None:
            return result("C9-TEMP", clauses=clauses, missing=["flash_point_c_or_verified_absence"])
        if fp is not None and t >= fp:
            return result("C9-TEMP", clauses=clauses + ["2.2.3.1.1"],
                          missing=["class3_heated_liquid_precedence_review"],
                          data={"candidate_other_class": "3"})
    code, un = ("M9", "3257") if state == "liquid" else ("M10", "3258")
    data = {"candidate_code": code, "candidate_un": un}
    if not (e.get("other_classes_excluded_review_ref") and e.get("named_entry_review_ref")):
        return result("C9-TEMP", clauses=clauses, missing=[k for k in ("other_classes_excluded_review_ref", "named_entry_review_ref") if not e.get(k)], data=data)
    return result("C9-TEMP", "criteria_met", clauses=clauses, data=data,
                  notes=["Provisional Class 9 criterion; packing group requires verified Table A row"])


def subclass(e):
    kind = e.get("subclass")
    clauses = {"asbestos": ["2.2.9.1.4", "2.2.9.3"],
               "pcb_pct": ["2.2.9.1.5", "2.2.9.3"],
               "polymer_vapour": ["2.2.9.1.6", "2.2.9.3"],
               "battery": ["2.2.9.1.7.1", "2.2.9.1.7.2", "2.2.9.2", "2.2.9.3", "MTC Rev.8 38.3"],
               "life_saving": ["2.2.9.1.8", "2.2.9.3", "3.3 SP 235/296"],
               "gmo": ["2.2.9.1.11", "2.2.9.3"],
               "m11_entry": ["2.2.9.1.14", "2.2.9.3", TABLE_ACLAUSE]}
    if kind not in clauses:
        return result("C9-SUBCLASS", clauses=["2.2.9.1.1", "2.2.9.1.2", "2.2.9.3"],
                      missing=["specific_supported_subclass"], notes=["Class 9 cannot be inferred from missing classification data"])
    cite, data, missing = clauses[kind], {"subclass": kind}, []
    if not e.get("identity_evidence_ref"):
        missing.append("identity_evidence_ref")
    if kind == "asbestos":
        if e.get("asbestos_type") not in ("amphibole", "chrysotile"):
            missing.append("asbestos_type")
        data.update({"candidate_code": "M1", "named_entry_and_special_provision_review_required": True})
    elif kind == "pcb_pct":
        if e.get("material_scope") == "mixture":
            v = num(e.get("pcb_pct_mg_kg"), zero=True)
            if v is None:
                missing.append("pcb_pct_mg_kg")
            elif v <= 50 and not missing:
                return result("C9-PCB", "criteria_not_met", clauses=cite, notes=["Only PCB/PCT mixture Class 9 pathway; other classes unaffected"])
        elif e.get("material_scope") not in ("substance", "article"):
            missing.append("material_scope")
        data["candidate_code"] = "M2"
    elif kind == "polymer_vapour":
        fp = signed_num(e.get("contained_flammable_liquid_flash_point_c"))
        if e.get("polymer_contains_flammable_liquid") is not True or fp is None:
            missing.append("verified_polymer_and_flash_point")
        elif fp > 55 and not missing:
            return result("C9-POLYMER", "criteria_not_met", clauses=cite, notes=["Other Class 9 pathways unaffected"])
        data["candidate_code"] = "M3"
    elif kind == "battery":
        b, config = e.get("battery_chemistry"), e.get("configuration")
        choices = {("lithium_metal", "alone"): "3090", ("lithium_metal", "packed"): "3091", ("lithium_metal", "contained"): "3091",
                   ("lithium_ion", "alone"): "3480", ("lithium_ion", "packed"): "3481", ("lithium_ion", "contained"): "3481",
                   ("sodium_ion", "alone"): "3551", ("sodium_ion", "packed"): "3552", ("sodium_ion", "contained"): "3552"}
        if (b, config) in choices:
            data.update({"candidate_code": "M4", "candidate_un": choices[b, config]})
        else:
            missing.append("supported_battery_chemistry_configuration")
        mandatory = ["tested_cell_and_battery_type_38_3", "vent_or_rupture_protection", "external_short_circuit_protection",
                     "reverse_current_protection_if_applicable", "quality_management_programme"]
        if not (b == "lithium_ion" or b == "lithium_metal") or e.get("button_cells_installed") is not True:
            mandatory.append("test_summary_available")
        for k in mandatory:
            if e.get(k) is not True:
                missing.append(k)
        if not e.get("sp188_230_310_376_400_and_other_applicability_review_ref"):
            missing.append("special_provision_assessment")
        if b == "sodium_ion" and e.get("organic_electrolyte_no_metallic_sodium_verified") is not True:
            missing.append("sodium_ion_definition")
        data["special_provision_gate"] = "SP188/230/310/376/387/389/400/636/670 as applicable"
        data["carriage_prohibition_check"] = "2.2.9.2"
    elif kind == "life_saving":
        data.update({"candidate_code": "M5", "required_sp": ["235", "296"]})
        missing.append("verified_special_provision_235_or_296")
    elif kind == "gmo":
        data["candidate_code"] = "M8"
        if e.get("toxic_and_infectious_classes_excluded") is not True or e.get("ecological_modification_potential") is not True:
            missing.append("GMO_criteria_and_class6_2_review")
        if not e.get("competent_authority_authorization_exceptions_review_ref"):
            missing.append("GMO_authorization_and_exemption_review")
    else:
        data.update({"candidate_code": "M11", "entry_only": True})
        if not e.get("listed_2_2_9_3_entry_ref"):
            missing.append("listed_2_2_9_3_entry_ref")
        if not e.get("verified_table_a_row"):
            missing.append("verified_table_a_row")
    return result("C9-SUBCLASS", "criteria_met" if not missing else "indeterminate", clauses=cite,
                  missing=missing, data=data,
                  notes=["No final UN entry, carriage permission, special provision outcome or packing group is inferred"])


def evaluate(e):
    if not isinstance(e, dict):
        return result("C9-GATE", missing=["evidence_object"])
    return {"aquatic": aquatic, "elevated_temperature": elevated,
            "subclass": subclass}.get(e.get("pathway"), lambda _: result("C9-GATE", clauses=["2.2.9.1.2"], missing=["pathway"]))(e)
