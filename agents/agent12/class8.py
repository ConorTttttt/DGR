"""Agent 12 proposed Class 8 evaluator; ADR 2025, provisional and NOT validated.

Isolated implementation for Lead-controlled integration into PR #2. Does not assign
UN number, final DGL packing group, subsidiary hazard, or overall transport status.
"""
from math import isfinite

ADR = 'ECE/TRANS/352 (Vol. I), ADR 2025'
MTC = 'ST/SG/AC.10/11/Rev.8 (2023), Part III, section 37'
STEEL = {'S235JR+CR', 'S275J2G3+CR', 'ISO 3574', 'UNS G10200', 'SAE 1020'}
ALUMINIUM = {'7075-T6', 'AZ5GU-T6'}
LOSS = {7: 13.5, 14: 26.5, 21: 39.2, 28: 51.5}
INTRUSION = {7: 120, 14: 240, 21: 360, 28: 480}
METHODS = {'OECD_404', 'OECD_435', 'OECD_431', 'OECD_430', 'OECD_439'}


def num(x, zero=True):
    return type(x) in (int, float) and isfinite(x) and (x >= 0 if zero else x > 0)


def result(status, rule, clauses, pg=None, missing=(), notes=(), details=None):
    assert status in ('criteria_met', 'criteria_not_met', 'indeterminate')
    assert pg in (None, 'I', 'II', 'III')
    return {
        'hazard_class': '8', 'status': status, 'rule_id': rule,
        'candidate_packing_group': pg, 'calculated_packing_group': pg,
        'dgl_packing_group': None, 'dgl_entry': None,
        'source': {'edition': 'ADR 2025', 'document': ADR,
                   'clauses': clauses, 'supporting_test_source': MTC},
        'missing_evidence': sorted(set(missing)), 'limitations': list(notes),
        'candidate_data': details or {}, 'requires_named_entry_resolution': True,
        'requires_precedence_review': True, 'requires_independent_review': True,
        'is_final_section_14_classification': False,
    }


def blocked(rule, clauses, *missing, pg=None, notes=(), details=None):
    return result('indeterminate', rule, clauses, pg, missing, notes, details)


def met(rule, clauses, pg, details=None):
    return result('criteria_met', rule, clauses, pg, notes=[
        'Class 8 property/packing-group candidate only: Table A, Chapter 3.3, '
        'other hazards, special precedence and carriage restrictions remain unresolved.'
    ], details=details)


def _human(e):
    h = e.get('human_evidence')
    if not isinstance(h, dict) or h.get('review_complete') is not True or not h.get('evidence_id'):
        return None, 'documented_human_experience_review'
    if h.get('status') not in ('none', 'corrosive', 'non_corrosive', 'conflicting'):
        return None, 'valid_human_conclusion'
    if h['status'] == 'conflicting':
        return None, 'expert_resolution_of_conflicting_human_evidence'
    if h['status'] == 'corrosive' and h.get('candidate_pg') not in (None, 'I', 'II', 'III'):
        return None, 'documented_human_pg_basis'
    return h, None


def _skin(e):
    s = e.get('skin_test')
    if not isinstance(s, dict):
        return None, 'valid_skin_test_or_documented_human_skin_conclusion'
    if s.get('status') == 'not_available':
        return ('unavailable', None), None
    if s.get('status') not in ('corrosive', 'non_corrosive') or s.get('valid') is not True:
        return None, 'valid_skin_study_conclusion'
    if s.get('method') not in METHODS or not s.get('evidence_id'):
        return None, 'documented_OECD_404_435_431_430_439_method_and_study_id'
    if s['method'] == 'OECD_439' and s['status'] != 'non_corrosive':
        return None, 'supported_OECD_439_non_corrosive_only'
    if s['status'] == 'non_corrosive':
        return ('non_corrosive', None), None
    ex, ob = s.get('exposure_minutes'), s.get('observation_minutes')
    # Tier times are accepted from OECD 404 exposure/observation evidence only.
    if s['method'] == 'OECD_404' and num(ex, False) and num(ob, True):
        if ex <= 3 and ob <= 60:
            return ('corrosive', 'I'), None
        if 3 < ex <= 60 and ob <= 20160:
            return ('corrosive', 'II'), None
        if 60 < ex <= 240 and ob <= 20160:
            return ('corrosive', 'III'), None
    tier = s.get('tier_discrimination')
    if tier == 'not_PGI_cannot_distinguish_II_III' and s.get('valid_PGI_exclusion') is True:
        return ('corrosive', 'II'), None
    if tier == 'cannot_distinguish_any' and s.get('no_other_test_indicates_other_pg') is True:
        return ('corrosive', 'I'), None
    return None, 'valid_skin_exposure_observation_or_supported_nondiscriminating_test'


def _metal(t, metal):
    """Return (positive/negative/unknown, issue). Negative requires both modes assessed."""
    if not isinstance(t, dict):
        return None, f'documented_{metal}_C1_test'
    grade = t.get('grade')
    if grade not in (STEEL if metal == 'steel' else ALUMINIUM):
        return None, f'approved_{metal}_grade'
    if not t.get('evidence_id') or t.get('method') != 'UN_MTC_REV8_C1':
        return None, f'documented_{metal}_UN_MTC_C1_report'
    if t.get('protocol_confirmed') is not True or t.get('three_positions_tested') is not True:
        return None, f'confirmed_{metal}_C1_protocol_and_exposure_positions'
    if not num(t.get('specimen_sets'), False) or t['specimen_sets'] < 3:
        return None, f'{metal}_at_least_three_specimen_sets'
    if t.get('plate_thickness_mm') != 2 or not num(t.get('solution_volume_l'), False) or t['solution_volume_l'] < 1.5:
        return None, f'{metal}_C1_plate_and_solution_volume'
    lo, hi = t.get('temperature_min_c'), t.get('temperature_max_c')
    if not num(lo) or not num(hi) or lo < 54 or hi > 56 or hi < lo:
        return None, f'{metal}_55C_plus_minus_1C_full_exposure'
    d = t.get('duration_days')
    if d not in LOSS or type(d) is bool or t.get('duration_verified') is not True or \
            not num(t.get('exposure_hours'), False) or abs(t['exposure_hours'] - d * 24) > 1:
        return None, f'{metal}_C1_supported_7_14_21_28_day_duration'
    rate, loss, depth = t.get('rate_mm_year'), t.get('max_mass_loss_pct'), t.get('max_local_intrusion_um')
    if rate is not None and not num(rate):
        return None, f'valid_{metal}_rate_mm_year'
    if loss is not None and not num(loss):
        return None, f'valid_{metal}_mass_loss_pct'
    if depth is not None and not num(depth):
        return None, f'valid_{metal}_intrusion_um'
    if rate is None and loss is None and (depth is None or depth <= INTRUSION[d]):
        return None, f'{metal}_uniform_corrosion_assessment'
    if (rate is not None and rate > 6.25) or (loss is not None and loss > LOSS[d]):
        return True, None
    if depth is not None and depth > INTRUSION[d]:
        if t.get('local_corrosion_assessed') is not True:
            return None, f'{metal}_localised_corrosion_assessment'
        return True, None
    if depth is None or t.get('local_corrosion_assessed') is not True:
        return None, f'{metal}_localised_corrosion_excluded'
    return False, None


def _metals(e):
    tests = e.get('metal_tests', {})
    if not isinstance(tests, dict):
        return blocked('ADR25-C8-MET', ['2.2.8.1.5.3(c)(ii)', 'MTC 37.4.1'], 'metal_tests')
    negatives, missing = 0, []
    for metal in ('steel', 'aluminium'):
        yes, err = _metal(tests.get(metal), metal)
        if yes is True:
            return met('ADR25-C8-MET', ['2.2.8.1.5.3(c)(ii)', 'MTC 37.4.1.4'], 'III',
                       {'qualifying_metal': metal})
        if yes is False:
            negatives += 1
        else:
            missing.append(err)
    if negatives == 2:
        return result('criteria_not_met', 'ADR25-C8-MET', ['2.2.8.1.5.3(c)(ii)'],
                      notes=['Only the independently substantiated skin/metal corrosion pathways are negative; '
                             'not an ADR exemption or evidence that other classes are negative.'])
    return blocked('ADR25-C8-MET', ['2.2.8.1.5.3(c)(ii)', 'MTC 37.4.1'], *missing)


def _bridge(e):
    b = e.get('bridge')
    clauses = ['2.2.8.1.6.1', '2.2.8.1.6.2']
    if not isinstance(b, dict) or not b.get('evidence_id') or b.get('source_tested_pg') not in ('I', 'II', 'III'):
        return blocked('ADR25-C8-BRIDGE', clauses, 'tested_similar_mixture_and_qualifying_bridge_evidence')
    mode = b.get('type')
    requirements = {
        'dilution': ('diluent_not_class8', 'diluent_no_pg_effect', 'no_increased_corrosion'),
        'batching': ('same_commercial_product', 'same_manufacturer_control', 'no_significant_variation'),
        'concentrated_PGI': ('source_is_PGI', 'only_concentrated'),
        'interpolation': ('identical_ingredients', 'tested_A_and_B_same_pg', 'all_class8_concentrations_intermediate'),
        'substantially_similar': ('same_B_concentration', 'same_A_C_concentration',
                                  'A_C_equivalent_skin_pg', 'A_C_no_effect_on_B'),
    }
    if mode not in requirements:
        return blocked('ADR25-C8-BRIDGE', clauses, 'recognized_ADR_bridging_principle')
    if mode == 'concentrated_PGI' and b['source_tested_pg'] != 'I':
        return blocked('ADR25-C8-BRIDGE', clauses, 'PGI_tested_source_mixture')
    absent = [k for k in requirements[mode] if b.get(k) is not True]
    if absent:
        return blocked('ADR25-C8-BRIDGE', clauses, *absent)
    return met('ADR25-C8-BRIDGE', ['2.2.8.1.6.2(' +
               {'dilution':'a','batching':'b','concentrated_PGI':'c','interpolation':'d',
                'substantially_similar':'e'}[mode] + ')'], b['source_tested_pg'],
               {'bridging_principle': mode, 'evidence_id': b['evidence_id']})


def _calculate(e):
    clauses = ['2.2.8.1.6.3.1', '2.2.8.1.6.3.2', '2.2.8.1.6.3.3',
               '2.2.8.1.6.3.4', 'Figure 2.2.8.1.6.3']
    if e.get('all_ingredients_identified') is not True or not e.get('composition_evidence_id'):
        return blocked('ADR25-C8-CALC', clauses, 'documented_complete_mixture_composition')
    if e.get('specific_limits_checked_against_Table_A_and_SP') is not True:
        return blocked('ADR25-C8-CALC', clauses, 'specific_limit_DGL_and_SP_screen')
    if e.get('specific_limits_present') is not False:
        return blocked('ADR25-C8-CALC', clauses, 'SCL_weighted_formula_case_requires_Lead_review',
                       notes=['Generic GCL calculations only; do not replace SCL by generic values.'])
    ingredients = e.get('ingredients')
    if not isinstance(ingredients, list) or not ingredients:
        return blocked('ADR25-C8-CALC', clauses, 'complete_ingredient_pg_and_concentrations')
    sums = {'I': 0.0, 'II': 0.0, 'III': 0.0}
    total, seen = 0.0, set()
    for i in ingredients:
        if not isinstance(i, dict) or not i.get('id') or i['id'] in seen:
            return blocked('ADR25-C8-CALC', clauses, 'unique_documented_ingredients')
        seen.add(i['id'])
        c, pg = i.get('concentration_pct'), i.get('skin_corrosion_pg')
        if not num(c) or c > 100 or pg not in ('I', 'II', 'III', 'not_class8'):
            return blocked('ADR25-C8-CALC', clauses, 'validated_ingredient_pct_and_skin_corrosion_pg')
        total += c
        if pg != 'not_class8':
            if c < 1 and type(i.get('relevant_below_one_pct')) is not bool:
                return blocked('ADR25-C8-CALC', clauses, f'relevance_below_1pct_for_{i["id"]}')
            if c >= 1 or i['relevant_below_one_pct']:
                sums[pg] += c
    if total > 100.000000001:
        return blocked('ADR25-C8-CALC', clauses, 'composition_total_at_most_100pct')
    if sums['I'] >= 5:
        pg = 'I'
    elif sums['I'] >= 1 or sums['I'] + sums['II'] >= 5:
        pg = 'II'
    elif sum(sums.values()) >= 5:
        pg = 'III'
    else:
        pg = None
    if pg in ('II', 'III', None) and e.get('no_synergistic_corrosion_effect') is not True:
        return blocked('ADR25-C8-CALC', clauses, 'no_synergistic_effects_for_PGII_or_PGIII',
                       pg=pg, details={'included_class8_percent_by_pg': sums})
    if pg:
        return met('ADR25-C8-CALC', clauses, pg, {'included_class8_percent_by_pg': sums})
    return result('criteria_not_met', 'ADR25-C8-CALC', clauses,
                  notes=['Only generic skin-mixture concentration calculation is negative; '
                         'metal corrosion, named entries and other hazards remain unassessed.'],
                  details={'included_class8_percent_by_pg': sums})


def evaluate(e):
    if not isinstance(e, dict):
        raise TypeError('evidence must be a dict')
    scope = e.get('material_scope')
    if scope not in ('substance', 'whole_mixture_tested', 'untested_mixture'):
        return blocked('ADR25-C8-SCOPE', ['2.2.8.1.4.4', '2.2.8.1.6.1'], 'material_scope')
    h, err = _human(e)
    if err:
        return blocked('ADR25-C8-HUM', ['2.2.8.1.5.1', '2.2.8.1.5.2'], err)
    if scope == 'untested_mixture':
        if e.get('skin_test') is not None and (
                not isinstance(e['skin_test'], dict) or e['skin_test'].get('status') != 'not_available'):
            return blocked('ADR25-C8-MIX', ['2.2.8.1.6.1'], 'whole_mixture_testing_or_correct_material_scope')
        if h['status'] != 'none':
            return blocked('ADR25-C8-MIX', ['2.2.8.1.5.1', '2.2.8.1.6.1'],
                           'expert_reconciliation_of_human_mixture_evidence')
        if e.get('bridge') is not None:
            return _bridge(e)
        return _calculate(e)
    s, err = _skin(e)
    if err:
        return blocked('ADR25-C8-SKIN', ['2.2.8.1.5.1', '2.2.8.1.5.2'], err)
    state, pg = s
    if h['status'] == 'corrosive' and state == 'non_corrosive':
        return blocked('ADR25-C8-HUM', ['2.2.8.1.5.1', '2.2.8.1.5.2'],
                       'expert_resolution_of_human_vs_skin_test_conflict')
    if h['status'] == 'non_corrosive' and state == 'corrosive':
        return blocked('ADR25-C8-HUM', ['2.2.8.1.5.1', '2.2.8.1.5.2'],
                       'expert_resolution_of_human_vs_skin_test_conflict')
    if h['status'] == 'corrosive':
        human_pg = h.get('candidate_pg')
        if human_pg and pg and human_pg != pg:
            return blocked('ADR25-C8-HUM', ['2.2.8.1.5.1', '2.2.8.1.5.2'],
                           'expert_resolution_of_human_vs_animal_pg_conflict')
        pg = human_pg or pg
        if not pg:
            return blocked('ADR25-C8-HUM', ['2.2.8.1.5.2'], 'human_exposure_tier_or_valid_skin_tier')
        if human_pg and h.get('expert_pg_basis_confirmed') is not True:
            return blocked('ADR25-C8-HUM', ['2.2.8.1.5.2'], 'substantiated_human_pg_basis')
        return met('ADR25-C8-HUM', ['2.2.8.1.5.1', '2.2.8.1.5.2'], pg,
                   {'human_evidence_id': h['evidence_id']})
    if state == 'corrosive':
        return met('ADR25-C8-SKIN', ['2.2.8.1.5.2', '2.2.8.1.5.3',
                   'Table 2.2.8.1.5.3'], pg)
    if state == 'non_corrosive' or (state == 'unavailable' and h['status'] == 'non_corrosive'
                                    and h.get('non_corrosive_basis_confirmed') is True):
        return _metals(e)
    return blocked('ADR25-C8-SKIN', ['2.2.8.1.5.2', '2.2.8.1.5.3'],
                   'documented_skin_noncorrosive_basis_before_metal_pathway')
