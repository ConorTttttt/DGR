"""Conservative ADR 2025 Class 7 *candidate* assessment; NEVER a UN/PG assignment.

Standalone proposed interface: Lead Agent must approve a shared schema before integration.
The numerical radionuclide registry is deliberately incomplete. All outputs provisional.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json
from pathlib import Path
from typing import Any

DATA = json.loads((Path(__file__).with_name("radionuclides.json")).read_text(encoding="utf-8"))
D = Decimal
TBQ_BQ = D("1000000000000")
ACTIVITY_UNITS = {"Bq": D(1), "kBq": D(1000), "MBq": D(10)**6, "GBq": D(10)**9, "TBq": TBQ_BQ}
MASS_UNITS = {"g": D(1), "kg": D(1000)}
FISSILE_NUCLIDES = {"U-233", "U-235", "Pu-239", "Pu-241"}


def _quantity(obj: Any, units: dict[str, Decimal], name: str) -> Decimal:
    if not isinstance(obj, dict) or obj.get("unit") not in units:
        raise ValueError(f"{name}: quantity with supported unit is required")
    if isinstance(obj.get("value"), (bool, float)):
        raise ValueError(f"{name}: decimal string or integer required, not float")
    try:
        value = D(str(obj["value"]))
    except (KeyError, InvalidOperation, TypeError):
        raise ValueError(f"{name}: invalid decimal") from None
    if not value.is_finite() or value < 0:
        raise ValueError(f"{name}: finite non-negative value required")
    for field in ("source_id", "measured_on", "method"):
        if not isinstance(obj.get(field), str) or not obj[field].strip():
            raise ValueError(f"{name}: evidence field {field} required")
    try:
        date.fromisoformat(obj["measured_on"])
    except ValueError:
        raise ValueError(f"{name}: measured_on must be ISO date") from None
    return value * units[obj["unit"]]


def _out(x: Decimal) -> str:
    return format(x, "f")


def _mixture_limit(fractions: dict[str, Decimal], column: str) -> Decimal:
    """ADR 2.2.7.2.2.4 reciprocal activity-fraction formula."""
    denominator = sum((f / D(DATA["values"][nuclide][column]) for nuclide, f in fractions.items()), D(0))
    if denominator <= 0:
        raise ValueError("invalid mixture denominator")
    return D(1) / denominator


def _fissile(payload: dict, names: set[str]) -> dict:
    if not (names & FISSILE_NUCLIDES):
        return {"state": "NO_FISSILE_NUCLIDES_IDENTIFIED", "ref": "2.2.7.1.3", "requires_review": True}
    fissile = payload.get("fissile", {})
    if not fissile.get("complete_mass_inventory"):
        return {"state": "UNRESOLVED_FISSILE_MASS", "ref": "2.2.7.1.3;2.2.7.2.3.5", "requires_review": True}
    masses = fissile.get("nuclide_masses", {})
    if not isinstance(masses, dict) or not names.intersection(FISSILE_NUCLIDES).issubset(masses):
        return {"state": "UNRESOLVED_FISSILE_MASS", "ref": "2.2.7.1.3", "requires_review": True}
    try:
        total = sum((_quantity(masses[n], MASS_UNITS, f"fissile.{n}") for n in masses), D(0))
    except ValueError as exc:
        return {"state": "INVALID_FISSILE_EVIDENCE", "reason": str(exc), "requires_review": True}
    if total < D("0.25") and fissile.get("no_other_fissile_in_package_or_unpacked_consignment") is True:
        return {"state": "DEFINITION_EXCLUDED_0_25G", "fissile_mass_g": _out(total),
                "ref": "2.2.7.1.3(c),(d) and final condition", "requires_review": True}
    return {"state": "FISSILE_CONTROLS_REQUIRE_REVIEW", "fissile_mass_g": _out(total),
            "potential_exceptions": ["2.2.7.2.3.5(a)-(f);7.5.11 CV33(4.3)"],
            "ref": "2.2.7.2.3.5;2.2.7.2.3.6", "requires_review": True}


def assess_lsa(data: dict, concentration: Decimal, exempt_concentration: Decimal,
               a2_bq: Decimal, fissile_state: str) -> dict:
    """Material-characteristic *candidates*; 4.1.9.2 and CV33 not checked."""
    mat = data.get("material", {})
    phase = mat.get("phase")
    uniform = mat.get("activity_distributed_throughout") is True
    candidates: list[str] = []
    if mat.get("ore_with_naturally_occurring_nuclides") is True:
        candidates.append("LSA-I(i)")
    if (mat.get("unirradiated_natural_depleted_u_or_natural_th_or_compound") is True
            and phase in ("solid", "liquid")):
        candidates.append("LSA-I(ii)")
    # Unlimited A2 route deliberately withheld for curated finite-valued subset.
    if uniform and concentration <= D(30) * exempt_concentration and fissile_state in (
            "NO_FISSILE_NUCLIDES_IDENTIFIED", "DEFINITION_EXCLUDED_0_25G"):
        candidates.append("LSA-I(iv) - fissile exception verification still required")
    if mat.get("tritiated_water") is True and phase == "liquid":
        try:
            tritium_bq_l = _quantity(mat.get("tritium_concentration"),
                                     {"Bq/l": D(1), "TBq/l": TBQ_BQ}, "tritium_concentration")
            if tritium_bq_l <= D("0.8") * TBQ_BQ:
                candidates.append("LSA-II(i)")
        except ValueError:
            pass
    if uniform and phase in ("solid", "gas", "liquid"):
        factor = D("0.00001") if phase == "liquid" else D("0.0001")
        if concentration <= factor * a2_bq:
            candidates.append("LSA-II(ii)")
    if (phase == "solid" and mat.get("powder") is False
            and mat.get("solid_or_binding_distribution_compliant") is True
            and concentration <= D("0.002") * a2_bq):
        candidates.append("LSA-III")
    return {"candidates": candidates, "status": "MATERIAL_ONLY_REQUIRES_PACKAGING_CV33_REVIEW",
            "refs": ["2.2.7.1.3", "2.2.7.2.3.1.2", "2.2.7.2.4.2", "4.1.9.2", "7.5.11 CV33(2)"]}


def assess_sco(data: dict) -> dict:
    """Conservative SCO-I/II surface measurements, both emitter groups required."""
    sco = data.get("sco")
    if not isinstance(sco, dict):
        return {"status": "NOT_ASSESSED", "ref": "2.2.7.2.3.2"}
    if sco.get("solid_object_not_itself_radioactive") is not True or sco.get("area_averaging_verified") is not True:
        return {"status": "INSUFFICIENT_OBJECT_OR_300CM2_EVIDENCE", "ref": "2.2.7.1.3;2.2.7.2.3.2"}
    measures = sco.get("measurements", {})
    bands = {"beta_gamma_low_toxicity_alpha": (D("0.4"), (D(4), D(40000), D(40000)),
                                                 (D(400), D(800000), D(800000))),
             "other_alpha": (D("0.04"), (D("0.4"), D(4000), D(4000)),
                             (D(40), D(80000), D(80000)))}
    observed = {}
    for band in bands:
        m = measures.get(band)
        if not isinstance(m, dict):
            return {"status": "MISSING_MEASUREMENTS", "missing_band": band, "ref": "2.2.7.2.3.2"}
        try:
            observed[band] = tuple(_quantity(m.get(x), {"Bq/cm2": D(1)}, f"sco.{band}.{x}")
                                  for x in ("accessible_nonfixed", "accessible_fixed", "inaccessible_total"))
        except ValueError as exc:
            return {"status": "INVALID_MEASUREMENT", "reason": str(exc)}
    contamination = any(
        observed[band][0] > bands[band][0] or observed[band][1] > bands[band][0]
        or observed[band][2] > bands[band][0] for band in bands)
    if not contamination:
        return {"status": "NOT_CONTAMINATED_AT_DEFINITION_LIMIT", "ref": "2.2.7.1.2;1.7.1.4(g)"}
    if all(all(value <= limit for value, limit in zip(observed[b], bands[b][1])) for b in bands):
        return {"status": "SCO_I_CANDIDATE", "ref": "2.2.7.2.3.2(a);2.2.7.2.4.3", "requires_review": True}
    if all(all(value <= limit for value, limit in zip(observed[b], bands[b][2])) for b in bands):
        return {"status": "SCO_II_CANDIDATE", "ref": "2.2.7.2.3.2(b);2.2.7.2.4.3", "requires_review": True}
    return {"status": "OUTSIDE_SCO_I_II_LIMITS_SCO_III_EXPERT_ONLY",
            "ref": "2.2.7.2.3.2(c);5.1.5.1.2(e)", "requires_review": True}


def assess_package(data: dict, activities: dict[str, Decimal]) -> dict:
    """Independent post-classification *screen*, NOT package approval/UN assignment."""
    pkg = data.get("package")
    if not isinstance(pkg, dict):
        return {"status": "NOT_ASSESSED"}
    out: dict = {"status": "PRELIMINARY_NUMERIC_SCREEN_ONLY", "category": None, "type_a": None,
                 "excepted": None, "approval_checks": ["5.1.5.2.1", "6.4", "4.1.9", "7.5.11 CV33"]}
    try:
        if pkg.get("single_package_contains_all") is True:
            special = pkg.get("special_form_certificate_reviewed") is True
            ratio = sum((activity / (D(DATA["values"][n]["A1" if special else "A2"]) * TBQ_BQ)
                         for n, activity in activities.items()), D(0))
            out["type_a"] = {"activity_ratio": _out(ratio), "within_numeric_limit": ratio <= 1,
                             "special_form_used": special, "ref": "2.2.7.2.4.4",
                             "warning": "Package construction, approvals and other requirements NOT assessed"}
            route = pkg.get("excepted_route")
            multiplier = {"solid_special": ("A1", D("0.001")),
                          "solid_other": ("A2", D("0.001")),
                          "liquid": ("A2", D("0.0001")),
                          "gas_tritium": ("A2", D("0.02")),
                          "gas_special": ("A1", D("0.001")),
                          "gas_other": ("A2", D("0.001"))}.get(route)
            if multiplier and (not route.endswith("special") or special) and (route != "gas_tritium" or set(activities) == {"T(H-3)"}):
                col, factor = multiplier
                excepted_ratio = sum((a / (D(DATA["values"][n][col]) * TBQ_BQ) for n, a in activities.items()), D(0))
                out["excepted"] = {"within_material_activity_limit": excepted_ratio <= factor,
                                   "normalized_ratio": _out(excepted_ratio), "limit_factor": _out(factor),
                                   "ref": "Table 2.2.7.2.4.1.2 column (4)",
                                   "warning": "5 uSv/h surface and other conditions still required"}
        if pkg.get("geometry") == "single_package":
            one_m = _quantity(pkg.get("dose_rate_1m"), {"mSv/h": D(1), "uSv/h": D("0.001")}, "dose_rate_1m")
            surface = _quantity(pkg.get("surface_dose_rate"), {"mSv/h": D(1), "uSv/h": D("0.001")}, "surface_dose_rate")
            raw_ti = one_m * D(100)
            ti = D(0) if raw_ti <= D("0.05") else raw_ti.quantize(D("0.1"), rounding=ROUND_CEILING)
            ti_rank = 0 if ti == 0 else 1 if ti <= 1 else 2
            surface_rank = 0 if surface <= D("0.005") else 1 if surface <= D("0.5") else 2
            rank = max(ti_rank, surface_rank)
            out["category"] = {"transport_index": _out(ti),
                               "provisional_label": ("I-WHITE", "II-YELLOW", "III-YELLOW")[rank],
                               "exclusive_use_review": ti > 10 or surface > D(2),
                               "out_of_standard_surface_limit": surface > D(10),
                               "ref": "5.1.5.3.1;Table 5.1.5.3.4",
                               "warning": "Not for overpack/container/special arrangement/certificate conflicts"}
    except ValueError as exc:
        out["evidence_issue"] = str(exc)
    return out


def classify(data: dict) -> dict:
    """Return no final UN, proper shipping name, PG, package approval or no-DG result."""
    output = {"module": "ADR2025_CLASS7_PROVISIONAL", "edition": "ECE/TRANS/352 Vol.I+Vol.II (2025)",
              "scope": "INDETERMINATE", "refs": ["2.2.7.1.1", "2.2.7.2.2.1", "2.2.7.2.2.4"],
              "final_un_number": None, "packing_group": None, "transport_not_regulated": None,
              "requires_independent_review": True, "issues": []}
    if not isinstance(data, dict) or data.get("complete_radionuclide_inventory") is not True:
        output["issues"].append("A documented complete radionuclide inventory is required")
        return output
    if data.get("single_homogeneous_material") is not True or data.get("mass_excludes_shielding") is not True:
        output["issues"].append("Single homogeneous material and unshielded sample mass evidence required")
        return output
    if data.get("activity_covers_entire_consignment") is not True:
        output["issues"].append("Document that activities represent entire consignment, not only one package or sample")
        return output
    reference_date = data.get("activity_reference_date")
    try:
        date.fromisoformat(reference_date)
    except (TypeError, ValueError):
        output["issues"].append("Explicit ISO activity_reference_date required (decay correction external)")
        return output
    try:
        mass = _quantity(data.get("material_mass"), MASS_UNITS, "material_mass")
        if mass <= 0:
            raise ValueError("material_mass must be positive")
        items = data.get("radionuclides")
        if not isinstance(items, list) or not items:
            raise ValueError("nonempty radionuclides required")
        activities: dict[str, Decimal] = {}
        source_dates = set()
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValueError("radionuclide entry with id required")
            name = item["id"]
            if name not in DATA["values"]:
                raise ValueError(f"{name}: not in independently checked curated register; refer to 2.2.7.2.2.1-2.2.7.2.2.6")
            if name in activities:
                raise ValueError(f"duplicate radionuclide {name}")
            if DATA["values"][name]["notes"] and item.get("table_footnotes_reviewed") is not True:
                raise ValueError(f"{name}: nuclide footnotes/daughter equilibrium require independent evidence review")
            activities[name] = _quantity(item.get("activity"), ACTIVITY_UNITS, name)
            source_dates.add(item["activity"]["measured_on"])
        if source_dates != {reference_date}:
            raise ValueError("All activities must be evidenced on the same activity_reference_date; decay correction requires expert-reviewed preprocessing")
        total = sum(activities.values(), D(0))
        if total <= 0:
            raise ValueError("positive measured radionuclide activity required to establish radioactive inventory")
        fractions = {name: a / total for name, a in activities.items()}
        concentration_limit = _mixture_limit(fractions, "exempt_concentration")
        consignment_limit = _mixture_limit(fractions, "exempt_consignment")
        a1 = _mixture_limit(fractions, "A1") * TBQ_BQ
        a2 = _mixture_limit(fractions, "A2") * TBQ_BQ
        concentration = total / mass
        concentration_exceeds = concentration > concentration_limit
        consignment_exceeds = total > consignment_limit
        output["scope"] = "CLASS7_RADIOACTIVE_MATERIAL_CRITERIA_MET" if (
            concentration_exceeds and consignment_exceeds) else "CLASS7_DEFINITION_NOT_MET_FOR_ASSESSED_MATERIAL"
        output["calculation"] = {"total_activity_Bq": _out(total), "material_mass_g": _out(mass),
            "activity_concentration_Bq_per_g": _out(concentration),
            "exempt_concentration_limit_Bq_per_g": _out(concentration_limit),
            "exempt_consignment_limit_Bq": _out(consignment_limit),
            "A1_Bq": _out(a1), "A2_Bq": _out(a2),
            "concentration_exceeds": concentration_exceeds, "consignment_exceeds": consignment_exceeds,
            "derived": "activity-fraction reciprocal mixture rule; no shielding included",
            "activity_reference_date": reference_date,
            "source_dates": sorted(source_dates | {data["material_mass"]["measured_on"]}),
            "refs": ["2.2.7.1.1", "2.2.7.2.2.1", "2.2.7.2.2.4"]}
        fissile = _fissile(data, set(activities))
        output["fissile"] = fissile
        output["lsa"] = assess_lsa(data, concentration, concentration_limit, a2, fissile["state"])
        output["sco"] = assess_sco(data)
        output["package_screen"] = assess_package(data, activities)
        if data.get("claimed_1_7_1_4_exemption"):
            output["issues"].append("1.7.1.4 exemption claimed; needs separate evidenced legal determination")
        for field, ref in (("special_form_claim", "2.2.7.2.3.3.1;5.1.5.2.1"),
                           ("low_dispersible_claim", "2.2.7.2.3.4.1;5.1.5.2.1")):
            if data.get(field):
                output["issues"].append(f"{field} requires test and competent-authority certificate review ({ref})")
        output["issues"].append("Check Part 1 exemptions; special provisions 290/369; other hazards; Table A; 4.1.9; 5.1.5; 6.4; CV33 before UN/transport conclusions")
    except ValueError as exc:
        output["issues"].append(str(exc))
    return output
