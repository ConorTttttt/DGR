"""Provisional ADR 2025 Class 4.1 evidence-scoped evaluator; no UN assignment.

Only transport-specific evidence is consumed. A candidate PG is never a final PG.
Interface is local until Lead Agent approves canonical schema.
"""
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

ADR = 'ADR 2025 ECE/TRANS/352 Vol. I'
MTC = 'ST/SG/AC.10/11/Rev.8 (check Amend.1 separately)'
PATHS = {'combustible_solid', 'metal_powder', 'friction_solid', 'self_reactive',
         'solid_desensitized_explosive', 'polymerizing', 'related_self_reactive'}


def _num(data: Dict[str, Any], key: str):
    v = data.get(key)
    if v is None or isinstance(v, bool):
        return None
    try:
        x = Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None
    return x if x.is_finite() else None


def _out(path: str):
    return {'module': 'ADR25_CLASS41', 'edition': ADR, 'pathway': path,
            'status': 'indeterminate', 'class_candidate': None,
            'pg_candidate': None, 'final_packing_group': None,
            'temperature_control_required': None, 'subdivision': None,
            'type_candidate': None, 'subsidiary_hazard_candidates': [],
            'blockers': [], 'clauses': [], 'notes': [],
            'needs_table_a_and_special_provisions': True,
            'independently_reviewed': False}


def evaluate(evidence: Dict[str, Any]):
    """Classify a single explicitly selected Class 4.1 pathway; never global DG status."""
    if not isinstance(evidence, dict):
        raise TypeError('evidence must be a mapping')
    path = evidence.get('pathway')
    if path not in PATHS:
        raise ValueError('pathway must be one of: ' + ', '.join(sorted(PATHS)))
    r = _out(path)
    def missing(*fields):
        r['blockers'].extend('missing_or_invalid:' + x for x in fields)
        return r
    def positive(*clauses):
        r['status'] = 'criteria_met'; r['class_candidate'] = '4.1'
        r['clauses'].extend(clauses)
        return r
    def negative(*clauses):
        r['status'] = 'criteria_not_met'; r['clauses'].extend(clauses)
        r['notes'].append('Pathway-only negative; NOT a transport non-dangerous finding.')
        return r
    def refuse(reason, *clauses):
        r['status'] = 'not_accepted_for_carriage'; r['blockers'].append(reason)
        r['clauses'].extend(clauses)
        return r

    # Subsidiary/competing hazards require independently verified ADR-class evidence;
    # multiple-hazard precedence remains outside this specialist module.
    competing = evidence.get('competing_transport_hazard_classes')
    if competing is not None:
        if not isinstance(competing, list) or any(x not in ('4.2', '4.3', '5.1', '6.1', '8') for x in competing):
            return missing('competing_transport_hazard_classes')
        if competing and evidence.get('competing_class_evidence_verified') is not True:
            return missing('competing_class_evidence_verified')
        r['subsidiary_hazard_candidates'] = sorted(set(competing))
        if path == 'metal_powder' and any(x in ('4.2', '4.3') for x in competing):
            r['status'] = 'external_class_review'
            r['clauses'].append('2.2.41.3 footnotes (a)-(c)')
            r['blockers'].append('metal powder Class 4.2/4.3 candidate: resolve precedence externally')
            return r

    # A Class 4.1 chemical instability veto precedes positive class/PG results.
    if evidence.get('dangerous_instability') is True:
        safe = evidence.get('prevented_during_carriage')
        if safe is False:
            return refuse('dangerous_decomposition_or_polymerization_not_prevented', '2.2.41.2.1')
        if safe is not True:
            return missing('prevented_during_carriage')
    if evidence.get('phosphorus_sulphide_not_free_from_yellow_white_phosphorus') is True:
        return refuse('phosphorus_sulphide_impurity', '2.2.41.2.3')
    if evidence.get('inorganic_flammable_molten') is True:
        if evidence.get('verified_un2448_sulphur_molten') is not True:
            return refuse('inorganic_molten_not_verified_exception', '2.2.41.2.3')
        r['status'] = 'requires_expert_decision'
        r['blockers'].append('UN2448 named-entry exception; verify Table A conditions')
        r['clauses'].append('2.2.41.2.3')
        return r
    if evidence.get('flammable_solid_oxidizing_un3097') is True:
        if evidence.get('verified_class1_requirements') is not True:
            return refuse('un3097_class1_requirements_unverified', '2.2.41.2.2')
        r['status'] = 'external_class_review'
        r['blockers'].append('UN3097 Class 1 requirements route; integrator to resolve')
        r['clauses'].extend(['2.2.41.2.2', '2.1.3.7'])
        return r

    if path in ('combustible_solid', 'metal_powder'):
        r['clauses'].extend(['2.2.41.1.3', '2.2.41.1.4', '2.2.41.1.5',
                             '2.2.41.1.8', 'MTC III 33.2.4'])
        if evidence.get('test_method') != 'UN_MTC_N1':
            if path == 'combustible_solid' and evidence.get('organic') is True and evidence.get('documented_experience_positive') is True and evidence.get('evidence_basis') == 'documented_experience':
                positive('2.2.41.1.4')
                r['blockers'].append('PG needs N.1 results, analogy or Table A verification')
                return r
            return missing('test_method:UN_MTC_N1')
        screening = evidence.get('screening_propagates_200mm')
        if screening is False:
            if any(evidence.get(k) is not None for k in
                   ('burning_time_100mm_s', 'burning_rate_mm_s', 'full_length_reaction_min')):
                return missing('contradictory_negative_screening_and_full_test')
            return negative('MTC III 33.2.4.3.1')
        if screening is not True:
            return missing('screening_propagates_200mm')
        if path == 'metal_powder':
            if evidence.get('ignited') is not True:
                return missing('ignited_or_contradictory_screening')
            minutes = _num(evidence, 'full_length_reaction_min')
            if minutes is None or minutes < 0:
                return missing('full_length_reaction_min')
            if minutes > 10:
                return negative('2.2.41.1.5(b)')
            positive('2.2.41.1.5(b)', '2.2.41.1.8(b)')
            r['pg_candidate'] = 'II' if minutes <= 5 else 'III'
            return r
        seconds = _num(evidence, 'burning_time_100mm_s')
        rate = _num(evidence, 'burning_rate_mm_s')
        if seconds is None and rate is None:
            return missing('burning_time_100mm_s|burning_rate_mm_s')
        if (seconds is not None and seconds < 0) or (rate is not None and rate < 0):
            return missing('nonnegative_N1_burning_measurements')
        if (seconds is not None and seconds < 45) or (rate is not None and rate > Decimal('2.2')):
            positive('2.2.41.1.5(a)', '2.2.41.1.8(a)')
            if seconds is None or seconds >= 45:
                r['blockers'].append('PG requires measured burning time under 45 s and wetted-zone behaviour')
                return r
            wet = evidence.get('wetted_zone')
            if wet == 'passes':
                r['pg_candidate'] = 'II'
            elif wet == 'stops_at_least_4min':
                r['pg_candidate'] = 'III'
            else:
                r['blockers'].append('wetted_zone:passes|stops_at_least_4min')
            return r
        if seconds is not None and rate is not None:
            return negative('2.2.41.1.5(a)', 'MTC III 33.2.4.4.1')
        return missing('both_N1_burning_measurements_for_negative_conclusion')

    if path == 'friction_solid':
        r['clauses'].extend(['2.2.41.1.3', '2.2.41.1.5', '2.2.41.1.8'])
        if evidence.get('analogy_or_special_provision_verified') is not True:
            return missing('analogy_or_special_provision_verified')
        if evidence.get('friction_fire_hazard_confirmed') is not True:
            return missing('friction_fire_hazard_confirmed')
        positive('2.2.41.1.5')
        r['blockers'].append('PG by verified analogy or applicable special provision, never N.1 default')
        return r

    if path == 'solid_desensitized_explosive':
        r['clauses'].extend(['2.2.41.1.18', '2.2.41.2.3', 'MTC III 33.3'])
        if evidence.get('physical_state') != 'solid' or evidence.get('desensitized_to_suppress_explosive_properties') is not True:
            return missing('solid_state_and_desensitization_evidence')
        row = evidence.get('exact_table_a_entry_verified')
        if row is False:
            return refuse('solid_desensitized_explosive_not_in_Table_A', '2.2.41.2.3')
        if row is not True:
            return missing('exact_table_a_entry_verified')
        positive('2.2.41.1.18')
        r['blockers'].append('PG/subsidiary hazard/conditions must come from exact Table A row and provisions')
        return r

    if path == 'related_self_reactive':
        r['clauses'].append('2.2.41.1.19')
        needed = ('series_1_2_provisionally_class1', 'series_6_exempted_class1',
                  'not_self_reactive', 'not_class_5_1', 'not_class_5_2')
        if any(evidence.get(k) is not True for k in needed):
            return missing(*[k for k in needed if evidence.get(k) is not True])
        positive('2.2.41.1.19')
        r['blockers'].append('Entry and PG, if any, must be verified against Table A')
        return r

    if path == 'polymerizing':
        r['clauses'].extend(['2.2.41.1.20', '2.2.41.1.21', 'MTC II 20.4.4'])
        classes = evidence.get('other_classes_1_to_8')
        if classes == 'meets':
            r['status'] = 'external_class_review'
            r['blockers'].append('other ADR Class 1-8 criterion; inspect special provision 386')
            r['clauses'].append('3.3.1 SP386')
            return r
        sapt, heat = _num(evidence, 'sapt_c'), _num(evidence, 'heat_of_reaction_j_g')
        if sapt is None or heat is None:
            return missing(*[k for k, v in [('sapt_c', sapt), ('heat_of_reaction_j_g', heat)] if v is None])
        if sapt > 75 or heat <= 300:
            return negative('2.2.41.1.20(a)-(b)')
        if classes != 'cleared':
            return missing('other_classes_1_to_8:cleared')
        if evidence.get('polymerizes_exothermically_without_stabilization') is not True:
            return missing('polymerizes_exothermically_without_stabilization')
        packaging = evidence.get('container_kind')
        if packaging not in ('packaging', 'IBC', 'tank'):
            return missing('container_kind:packaging|IBC|tank')
        if evidence.get('sapt_applies_to_offered_form_and_container') is not True:
            return missing('sapt_applies_to_offered_form_and_container')
        positive('2.2.41.1.20')
        r['subdivision'] = 'PM2' if sapt <= (45 if packaging == 'tank' else 50) else 'PM1'
        r['temperature_control_required'] = (r['subdivision'] == 'PM2')
        r['notes'].append('No numeric PG rule for polymerizing substances: defer to Table A')
        return r

    if path == 'self_reactive':
        r['clauses'].extend(['2.2.41.1.9', '2.2.41.1.11', '2.2.41.1.12',
                             '2.2.41.1.13', '2.2.41.1.17', 'MTC II 20.4.2'])
        exclusion_flags = ('class1_explosive', 'class5_1_oxidizer', 'class5_2_organic_peroxide')
        absent = [x for x in exclusion_flags if not isinstance(evidence.get(x), bool)]
        if absent:
            return missing(*absent)
        if evidence.get('class1_explosive') is True or evidence.get('class5_2_organic_peroxide') is True:
            return negative('2.2.41.1.9(a),(c)')
        ox = evidence.get('class5_1_oxidizer')
        if ox is True:
            pct = _num(evidence, 'combustible_organic_mass_pct')
            if pct is None:
                return missing('combustible_organic_mass_pct_for_oxidizing_mixture_exception')
            if not isinstance(evidence.get('is_mixture'), bool):
                return missing('is_mixture')
            if not (evidence.get('is_mixture') is True and pct >= 5):
                return negative('2.2.41.1.9(b)')
            r['notes'].append('5.1 oxidizing-mixture >=5% combustible organic exception: route type B-F vs G with integrator')
        if evidence.get('sample_for_further_testing') is True:
            sample_kg = _num(evidence, 'sample_quantity_per_transport_unit_kg')
            conditions = (evidence.get('sample_no_more_dangerous_than_type_B') is True
                          and evidence.get('sample_packing_method') == 'OP2'
                          and sample_kg is not None and 0 <= sample_kg <= 10
                          and evidence.get('sample_temperature_conditions_adequate') is True)
            if not conditions:
                return missing('sample_type_C_exception_conditions_2.2.41.1.15')
            r['status'] = 'requires_expert_decision'
            r['type_candidate'] = 'C_sample_provision'
            r['clauses'].append('2.2.41.1.15')
            r['blockers'].append('sample type C entry and carriage conditions require independent ADR verification')
            return r
        heat, sadt = _num(evidence, 'heat_of_decomposition_j_g'), _num(evidence, 'sadt_50kg_c')
        if (heat is not None and heat < 300) or (sadt is not None and sadt > 75):
            return negative('2.2.41.1.9(d),(e)')
        if heat is None or sadt is None:
            return missing(*[k for k,v in [('heat_of_decomposition_j_g',heat),('sadt_50kg_c',sadt)] if v is None])
        if evidence.get('decomposes_strongly_exothermically_without_oxygen') is not True:
            return missing('decomposes_strongly_exothermically_without_oxygen')
        typ = evidence.get('self_reactive_type')
        if typ not in ('A','B','C','D','E','F','G'):
            return missing('self_reactive_type_proven_by_Part_II')
        if evidence.get('type_evidence') not in ('MTC_part_II_test_report', 'verified_ADR_list_or_authority_approval'):
            return missing('type_evidence')
        r['type_candidate'] = typ
        if typ == 'A':
            return refuse('type_A_not_accepted', '2.2.41.2.3')
        if typ == 'G':
            return negative('2.2.41.1.11', 'MTC II 20.4.2(g)')
        sadt_offered = _num(evidence, 'sadt_offered_package_c')
        if sadt_offered is None:
            return missing('sadt_offered_package_c_for_temperature_control')
        r['temperature_control_required'] = sadt_offered <= 55
        r['subdivision'] = 'SR2' if sadt_offered <= 55 else 'SR1'
        if evidence.get('exact_listed_formulation_verified') is not True and evidence.get('competent_authority_approval_verified') is not True:
            r['status'] = 'requires_authority'
            r['blockers'].append('unlisted formulation requires competent authority approval and test report')
            return r
        if evidence.get('activator_changes_properties') is True and evidence.get('reassessed_formulation') is not True:
            return missing('reassessed_formulation_per_2.2.41.1.14')
        if evidence.get('diluent_used') is True:
            for k in ('diluent_compatible', 'tested_as_shipped_with_diluent',
                      'diluent_no_dangerous_concentration_on_leakage'):
                if evidence.get(k) is not True:
                    return missing(k + ':2.2.41.1.16')
            if evidence.get('liquid_diluent') is True and r['temperature_control_required']:
                bp = _num(evidence, 'diluent_boiling_point_c')
                fp = _num(evidence, 'diluent_flash_point_c')
                ct = _num(evidence, 'control_temperature_c')
                if bp is None or fp is None or ct is None:
                    return missing('diluent_boiling_point_c|diluent_flash_point_c|control_temperature_c')
                if bp < 60 or fp < 5 or bp < ct + 50:
                    return refuse('temperature_controlled_diluent_thresholds_failed', '2.2.41.1.16')
        positive('2.2.41.1.11', '2.2.41.1.17')
        r['notes'].append('Self-reactive types B-F use type/packaging method, NOT a packing group')
        return r
    raise AssertionError('unreachable')
