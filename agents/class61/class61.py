"""ADR 2025 2.2.61 Class 6.1 candidate engine (Agent 9, provisional).

This does not make final transport assignments, select a UN entry, or resolve precedence.
The caller must verify evidence authenticity and regulatory applicability independently.
"""
from decimal import Decimal, InvalidOperation

PG_ORDER = {'I': 0, 'II': 1, 'III': 2}
SRC = {'edition': 'ADR 2025', 'document': 'ECE/TRANS/352 Vol. I',
       'chapter': '2.2.61', 'independent_validation': 'pending'}
CLAUSES = ['2.2.61.1.3', '2.2.61.1.5', '2.2.61.1.6', '2.2.61.1.7',
           '2.2.61.1.7.1', '2.2.61.1.7.2', '2.2.61.1.7.3',
           '2.2.61.1.8', '2.2.61.1.9.1', '2.2.61.1.9.2-2.2.61.1.9.5',
           '2.2.61.1.10.1', '2.2.61.1.10.2', '2.2.61.1.11',
           '2.2.61.1.12-2.2.61.1.14', '2.2.61.2.1', '2.2.61.2.2',
           '2.1.3.5.3(h)', '2.1.3.10', '3.2.1 Table A', '3.3.1']


def d(value, *, allow_zero=False, maximum=None):
    if isinstance(value, bool) or value is None or not isinstance(value, (int, float, str, Decimal)):
        raise ValueError('invalid finite numeric evidence')
    try:
        out = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('invalid decimal evidence') from exc
    if not out.is_finite() or out < 0 or (not allow_zero and out == 0) or (maximum is not None and out > maximum):
        raise ValueError('out of range numeric evidence')
    return out


def group(value, limits):
    for pg, bound in zip(('I', 'II', 'III'), limits):
        if value <= Decimal(str(bound)):
            return pg
    return None


def verified(item):
    return isinstance(item, dict) and isinstance(item.get('evidence_id'), str) and bool(item['evidence_id'].strip())


def animal_evidence(item, route):
    if not verified(item) or item.get('sample') != 'carried_material' or item.get('observation_days') != 14:
        raise ValueError('missing or invalid study provenance, sample or 14-day observation')
    if route == 'oral' and item.get('species') != 'rat':
        raise ValueError('oral LD50 species mismatch')
    if route == 'dermal' and (item.get('species') != 'rabbit' or item.get('contact_hours') != 24):
        raise ValueError('dermal LD50 requires 24h rabbit skin contact')
    if route in ('dust_mist', 'vapour') and (item.get('species') != 'rat' or item.get('both_sexes') is not True):
        raise ValueError('LC50 study requires rats of both sexes')


def inhalation_value(item, multiplier):
    data = item.get('lc50_by_hours')
    if not isinstance(data, dict):
        raise ValueError('missing 1h/4h LC50 evidence')
    if '1' in data:
        return d(data['1']), '1h', [] if '4' not in data else ['1-hour result used in preference to 4-hour result']
    if '4' in data:
        return d(data['4']) * multiplier, '4h converted to 1h comparator', []
    raise ValueError('only 1h or 4h exposure evidence is supported')


def mixture_ld(item, route):
    if not verified(item) or item.get('composition_complete') is not True:
        raise ValueError('mixture composition and provenance required')
    method = item.get('method')
    comps = item.get('components')
    if not isinstance(comps, list) or not comps or not all(isinstance(x, dict) for x in comps):
        raise ValueError('active constituent list required')
    if method == 'single_active' and len(comps) != 1:
        raise ValueError('single active method requires exactly one active')
    if method not in ('single_active', 'most_hazardous_total', 'reciprocal_sum'):
        raise ValueError('unsupported oral/dermal mixture method')
    vals = []
    for c in comps:
        if not c.get('evidence_id') or not c.get('active') is True:
            raise ValueError('each active constituent needs authenticated toxicity evidence')
        concentration = d(c.get('mass_percent'), maximum=Decimal('100'))
        ld = d(c.get('ld50_mg_kg'))
        if route == 'dermal' and (not c.get('species') or c.get('species') != item.get('dermal_species')):
            raise ValueError('dermal constituent test species must match')
        vals.append((concentration, ld))
    total = sum((c for c, _ in vals), Decimal('0'))
    if total > 100:
        raise ValueError('active mass percentages exceed 100')
    if method == 'single_active':
        return vals[0][1] * 100 / vals[0][0]
    if method == 'most_hazardous_total':
        return min(v for _, v in vals) * 100 / total
    if route == 'dermal' and not item.get('dermal_species'):
        raise ValueError('dermal reciprocal method requires same species')
    return Decimal('100') / sum((c / ld for c, ld in vals), Decimal('0'))


def mixture_vapour(item):
    if not verified(item) or item.get('composition_complete') is not True:
        raise ValueError('complete liquid mixture and LC50 provenance required')
    components = item.get('components')
    if not isinstance(components, list) or not components:
        raise ValueError('missing vapour mixture components')
    denominator = Decimal('0')
    ratio = Decimal('0')
    f_total = Decimal('0')
    p_total = Decimal('0')
    for c in components:
        if not isinstance(c, dict) or not c.get('evidence_id'):
            raise ValueError('unverified mixture component')
        f = d(c.get('mole_fraction'))
        lc = d(c.get('lc50_ppm_1h'))
        p = d(c.get('partial_pressure_kpa_20c'), allow_zero=True, maximum=Decimal('101.3'))
        f_total += f
        p_total += p
        denominator += f / lc
        ratio += (p * Decimal('1000000') / Decimal('101.3')) / lc
    if f_total > 1 or p_total > Decimal('101.3'):
        raise ValueError('nonphysical mole-fraction or partial-pressure sum')
    lc_mix = 1 / denominator
    if ratio >= 10 and lc_mix <= 1000:
        return 'I', {'mixture_lc50_ppm': str(lc_mix), 'R': str(ratio)}
    if ratio >= 1 and lc_mix <= 3000:
        return 'II', {'mixture_lc50_ppm': str(lc_mix), 'R': str(ratio)}
    if ratio >= Decimal('0.2') and lc_mix <= 5000:
        return 'III', {'mixture_lc50_ppm': str(lc_mix), 'R': str(ratio)}
    return None, {'mixture_lc50_ppm': str(lc_mix), 'R': str(ratio)}


def deaths(test):
    if not verified(test) or test.get('rats') != 10 or test.get('male') != 5 or test.get('female') != 5 or test.get('exposure_hours') != 1 or test.get('observation_days') != 14:
        raise ValueError('threshold tests must document 10 rats (5+5), 1h, 14d')
    n = test.get('deaths')
    if type(n) is not int or n < 0 or n > 10:
        raise ValueError('invalid deaths count')
    return n >= 5


def threshold_vapour(item):
    if not verified(item):
        raise ValueError('threshold series provenance required')
    tests = item.get('tiers')
    if not isinstance(tests, dict):
        raise ValueError('PG I/II/III evidence tiers required')
    for pg in ('I', 'II', 'III'):
        tier = tests.get(pg)
        if not isinstance(tier, dict):
            raise ValueError('unexcluded higher group or missing tier '+pg)
        a = tier.get('toxicity')
        if not isinstance(a, dict) or a.get('nominal_concentration_ppm') != {'I': 1000, 'II': 3000, 'III': 5000}[pg]:
            raise ValueError('incorrect tier test concentration')
        a_pass = deaths(a)
        if pg in ('I', 'II'):
            b = tier.get('equilibrium')
            if not isinstance(b, dict) or b.get('dilution_air_volumes') != {'I': 9, 'II': 0}[pg]:
                raise ValueError('incorrect equilibrium testing atmosphere')
            b_pass = deaths(b)
        else:
            b_pass = d(tier.get('saturated_vapour_ppm_20c'), allow_zero=True) >= 1000
        if a_pass and b_pass:
            return pg, {'threshold_tier': pg}
        # A single failed criterion excludes this group; absent lower tiers remain unresolved.
    return None, {'threshold_tier': None}


def evaluate(e):
    """Return class-scoped outcomes, never a final class/UN/packing group assignment."""
    routes = {}
    missing = []
    flags = []
    candidates = []
    result = dict(hazard_class='6.1', status='indeterminate', candidate_packing_group=None,
                  route_results=routes, missing_evidence=missing, referrals=flags,
                  source=SRC, clauses=CLAUSES, assignment_permitted=False,
                  requires_independent_review=True, is_final_section_14_classification=False)
    if not isinstance(e, dict) or e.get('material_type') not in ('substance', 'mixture'):
        missing.append('valid_material_type')
        return result
    state = e.get('physical_state')
    if state not in ('solid', 'liquid'):
        missing.append('verified_physical_state')
    human = e.get('human_experience')
    if not isinstance(human, dict) or human.get('reviewed') is not True or not verified(human):
        missing.append('documented_human_experience_review')
    elif human.get('status') != 'none_documented':
        flags.append('HUMAN_EXPERIENCE_PRIORITY_EXPERT_REVIEW')
    screen = e.get('screen') or {}
    if not isinstance(screen, dict): screen = {}
    for key in ('identity_reviewed', 'named_entry_reviewed', 'stability_reviewed', 'prohibitions_reviewed', 'subsidiary_hazards_reviewed'):
        if screen.get(key) is not True:
            flags.append('PENDING_'+key.upper())
    if e.get('pesticide') is True:
        flags.append('PESTICIDE_NAMED_ENTRY_AND_PSN_REVIEW')
    if e.get('tear_gas') is None:
        flags.append('TEAR_GAS_IDENTITY_UNVERIFIED')

    evidence = e.get('routes') or {}
    if not isinstance(evidence, dict): evidence = {}
    for route in ('oral', 'dermal', 'dust_mist', 'vapour'):
        item = evidence.get(route)
        if item is None:
            routes[route] = {'status': 'missing'}
            missing.append(route+'_evidence_or_supported_exclusion')
            continue
        if not isinstance(item, dict):
            routes[route] = {'status': 'invalid'}
            missing.append('valid_'+route+'_evidence')
            continue
        kind = item.get('status')
        if kind == 'excluded':
            basis = item.get('basis')
            try:
                allowed = ((route == 'dust_mist' and state == 'solid' and basis == 'respirable_fraction_below_10_percent' and
                        d(item.get('respirable_fraction_mass_percent'), allow_zero=True, maximum=Decimal('100')) < 10)
                       or (route == 'dust_mist' and state == 'liquid' and basis == 'no_mist_on_leakage' and item.get('mist_likely_on_leakage') is False)
                       or (route == 'vapour' and state == 'solid' and basis == 'not_liquid'))
            except (ValueError, TypeError, InvalidOperation):
                allowed = False
            if allowed and verified(item):
                routes[route] = {'status': 'excluded', 'basis': basis}
            else:
                routes[route] = {'status': 'invalid'}
                missing.append('substantiated_'+route+'_exclusion')
            continue
        try:
            if kind == 'measured':
                animal_evidence(item, route)
                if route in ('oral', 'dermal'):
                    ld = d(item.get('ld50_mg_kg'))
                    pg = group(ld, (5, 50, 300) if route == 'oral' else (50, 200, 1000))
                    info = {'study_ld50_mg_kg': str(ld)}
                elif route == 'dust_mist':
                    if item.get('aerosol_form') not in ('dust', 'mist'):
                        raise ValueError('dust vs mist distinction required')
                    if (item.get('aerosol_form') == 'dust' and state != 'solid') or (item.get('aerosol_form') == 'mist' and state != 'liquid'):
                        raise ValueError('aerosol form must match physical state')
                    if d(item.get('specimen_respirable_mass_percent'), maximum=Decimal('100')) <= 90:
                        raise ValueError('more than 90 percent respirable test specimen required')
                    if d(item.get('aerodynamic_diameter_um'), maximum=Decimal('10')) > 10:
                        raise ValueError('invalid particle size')
                    if state == 'solid' and d(item.get('likely_respirable_dust_mass_percent'), allow_zero=True, maximum=Decimal('100')) < 10:
                        flags.append('DUST_TEST_NOT_MANDATORY_BUT_RESULT_USED')
                    if state == 'liquid' and item.get('mist_likely_on_leakage') is not True:
                        raise ValueError('mist likelihood evidence missing')
                    lc, time, notes = inhalation_value(item, Decimal('4'))
                    pg = group(lc, ('0.2', '2', '4'))
                    info = {'lc50_1h_equivalent_mg_l': str(lc), 'time_basis': time, 'notes': notes}
                else:
                    if state != 'liquid' or item.get('temperature_c') != 20 or d(item.get('pressure_kpa')) != Decimal('101.3'):
                        raise ValueError('vapour criteria: liquid at 20C/101.3kPa')
                    lc, time, notes = inhalation_value(item, Decimal('2'))
                    V = d(item.get('saturated_vapour_ppm_20c'), allow_zero=True)
                    pg = ('I' if V >= 10*lc and lc <= 1000 else
                          'II' if V >= lc and lc <= 3000 else
                          'III' if V >= Decimal('0.2')*lc and lc <= 5000 else None)
                    info = {'lc50_1h_equivalent_ppm': str(lc), 'V_ppm_20c': str(V), 'time_basis': time, 'notes': notes}
            elif kind == 'derived' and e['material_type'] == 'mixture':
                if route in ('oral', 'dermal'):
                    ld = mixture_ld(item, route)
                    pg = group(ld, (5,50,300) if route == 'oral' else (50,200,1000))
                    info = {'derived_ld50_mg_kg': str(ld), 'method': item['method']}
                elif route == 'vapour' and state == 'liquid':
                    pg, info = mixture_vapour(item)
                else:
                    raise ValueError('unsupported mixture derivation for this route')
            elif kind == 'threshold_tests' and route == 'vapour' and e['material_type'] == 'mixture' and state == 'liquid':
                pg, info = threshold_vapour(item)
            else:
                raise ValueError('unsupported route evidence method')
            routes[route] = {'status': 'positive' if pg else 'negative', 'candidate_packing_group': pg, **info}
            if pg:
                candidates.append((route, pg))
        except (ValueError, InvalidOperation, ZeroDivisionError, KeyError, TypeError) as exc:
            routes[route] = {'status': 'invalid', 'reason': str(exc)}
            missing.append('valid_'+route+'_evidence')

    if e.get('class8_meets_criteria') is not False:
        flags.append('CLASS8_PRECEDENCE_REFERRAL')
    if any(route == 'dust_mist' and pg == 'I' for route, pg in candidates) and e.get('class8_meets_criteria') is True:
        other = [routes[x].get('candidate_packing_group') for x in ('oral','dermal') if routes.get(x, {}).get('status') in ('positive','negative')]
        if any(pg in ('I','II') for pg in other):
            flags.append('C61_DUST_PGI_CLASS8_EXCEPTION_GATE_SATISFIED_PROVISIONALLY')
        elif len(other) == 2:
            flags.append('C61_DUST_PGI_CLASS8_EXCEPTION_REFER_TO_CLASS8')
        else:
            flags.append('C61_DUST_PGI_CLASS8_EXCEPTION_NEEDS_ORAL_DERMAL_EVIDENCE')
            missing.append('class8_dust_pgi_oral_dermal_screen')
    if not candidates:
        if not missing and len(routes) == 4 and all(r.get('status') in ('negative','excluded') for r in routes.values()) and not flags:
            result['status'] = 'criteria_not_met'
        return result
    best = min((pg for _, pg in candidates), key=lambda x: PG_ORDER[x])
    if best == 'III' and e.get('tear_gas') is True:
        best = 'II'
        flags.append('TEAR_GAS_PGII_FLOOR')
    # Lower-priority grade is not established while a more severe, applicable route is unassessed.
    unresolved = any(v.get('status') in ('missing','invalid') for v in routes.values())
    if best == 'I' or not unresolved:
        result['candidate_packing_group'] = best
    if not isinstance(human, dict) or not verified(human) or human.get('reviewed') is not True or human.get('status') != 'none_documented':
        result['status'] = 'indeterminate'
    elif result['candidate_packing_group'] is None:
        result['status'] = 'indeterminate'
    elif 'C61_DUST_PGI_CLASS8_EXCEPTION_REFER_TO_CLASS8' in flags or 'C61_DUST_PGI_CLASS8_EXCEPTION_NEEDS_ORAL_DERMAL_EVIDENCE' in flags:
        result['status'] = 'indeterminate'
    else:
        result['status'] = 'criteria_met'
    return result
