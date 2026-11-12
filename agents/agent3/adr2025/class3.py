"""ADR 2025 Class 3 preliminary criteria and standard packing-group calculation.

Deliberately excludes the viscosity concessions, mixtures precedence and DGL lookup.
"""
from .common import blocked, decide, numeric


def evaluate(e):
    c='3'
    rule='ADR25-C3-001'
    clauses=['2.2.3.1.1', '2.2.3.1.3']
    if e.get('physical_state') not in ('liquid', 'molten_solid'):
        return blocked(c, rule, clauses, 'physical_state (liquid or molten_solid)')
    if e.get('liquid_desensitized_explosive') is True:
        return decide(c, 'criteria_met', 'ADR25-C3-004', ['2.2.3.1.1'],
                      notes=['Specific liquid-desensitized explosive entry, restrictions and packing group must be checked in Table A 3.2.'])
    if e.get('liquid_desensitized_explosive') is not False:
        return blocked(c, rule, clauses, 'liquid_desensitized_explosive')
    fp=e.get('flash_point_c')
    if not numeric(fp, allow_zero=True) and not (type(fp) in (int, float) and fp < 0):
        return blocked(c, rule, clauses, 'measured_closed_cup_flash_point_c')
    if e.get('diesel_gasoil_light_heating_oil') is True and 60 < fp <= 100:
        return decide(c, 'criteria_met', 'ADR25-C3-003', ['2.2.3.1.1 NOTE 2'],
                      data={'named_un_candidate': '1202'},
                      notes=['UN 1202 entry, special provisions and packing group must be checked against DGL.'])
    if e.get('diesel_gasoil_light_heating_oil') is not False:
        return blocked(c, rule, clauses, 'diesel_gasoil_light_heating_oil',
                       notes=['Named diesel/gasoil/heating-oil exception may apply.'])
    heated=e.get('carried_at_or_above_flash_point')
    if heated not in (True,False) or type(heated) is not bool:
        return blocked(c, rule, clauses, 'carried_at_or_above_flash_point')
    if fp > 60:
        if heated:
            return decide(c, 'criteria_met', 'ADR25-C3-002', ['2.2.3.1.1'],
                          data={'named_un_candidate': '3256'},
                          notes=['Applies to heated liquids/molten solids; verify UN 3256 and packing group in Table A.'])
        return decide(c, 'criteria_not_met', rule, ['2.2.3.1.1'],
                      notes=['Only standard Class 3 flammability criterion excluded; other ADR classes still require assessment.'])
    if fp > 35 and e.get('sustains_combustion') is False and not heated:
        if e.get('sustained_combustion_test_method') != 'UN_MTC_32.2.5' or not e.get('sustained_combustion_evidence_id'):
            return blocked(c, 'ADR25-C3-005', ['2.2.3.1.1 NOTE 1'],
                           'documented_sustained_combustion_test_UN_MTC_32.2.5')
        return decide(c, 'criteria_not_met', 'ADR25-C3-005',
                      ['2.2.3.1.1 NOTE 1'],
                      notes=['Requires evidenced non-sustained-combustion determination according to MTC 32.2.5. Other classes remain open.'])
    if e['physical_state'] != 'liquid':
        return blocked(c, rule, clauses, 'liquid_state_under_ADR_1.2.1',
                       notes=['Molten solids require separate heated carriage / Table A handling.'])
    if not numeric(e.get('vapour_pressure_kpa_50c'), allow_zero=True):
        return blocked(c, rule, clauses, 'vapour_pressure_kpa_50c')
    if type(e.get('completely_gaseous_at_20c')) is not bool:
        return blocked(c, rule, clauses, 'completely_gaseous_at_20c')
    if e['vapour_pressure_kpa_50c'] > 300 or e['completely_gaseous_at_20c']:
        return blocked(c, rule, clauses, 'Class 2 gas-state evaluation',
                       notes=['Class 3 liquid conditions not established; refer to Class 2.'])
    if not numeric(e.get('initial_boiling_point_c'), allow_zero=True) and not (type(e.get('initial_boiling_point_c')) in (int,float) and e['initial_boiling_point_c'] < 0):
        return blocked(c, rule, clauses, 'measured_initial_boiling_point_c')
    ibp=e['initial_boiling_point_c']
    pg='I' if ibp <= 35 else 'II' if fp < 23 else 'III'
    notes=['Packing group applies to standard Class 3 flammable liquid criteria only.',
           'Named entries, viscosity exceptions (2.2.3.1.4–1.5.2), other hazards, DGL and precedence 2.1.3.10 remain to be checked.']
    if e.get('other_hazards_assessed') is not True:
        return blocked(c, rule, clauses, 'other_hazards_assessed', pg=pg, notes=notes)
    if e.get('named_entry_checked') is not True:
        return blocked(c, rule, clauses, 'named_entry_checked', pg=pg, notes=notes)
    if e.get('viscosity_concessions_assessed') is not True:
        return blocked(c, rule, clauses, 'viscosity_concessions_assessed', pg=pg, notes=notes)
    return decide(c, 'criteria_met', rule, clauses, pg=pg, notes=notes)