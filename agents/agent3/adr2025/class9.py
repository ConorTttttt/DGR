"""ADR 2025 Class 9 scoped aquatic and elevated-temperature pathways.

Does not classify batteries, miscellaneous articles, aquatic mixtures, M factors or special provisions.
"""
from math import isfinite
from .common import decide, blocked, numeric


def aquatic(e):
    cls='9'
    clauses=['2.2.9.1.10.3.1','Table 2.2.9.1.10.3.1','2.2.9.1.10.6']
    if e.get('material_scope')!='substance':
        return blocked(cls,'ADR25-C9-AQ-001',clauses,'substance_scope',
                       notes=['Mixture criteria in 2.2.9.1.10.4, including M factors and incomplete ingredients, not implemented.'])
    acute=e.get('lowest_valid_aquatic_acute_l_ec50_mg_l')
    chronic=e.get('lowest_valid_chronic_noec_ecx_mg_l')
    categories=[]
    if acute is not None:
        if not numeric(acute):return blocked(cls,'ADR25-C9-AQ-001',clauses,'valid_aquatic_acute_data')
        if acute<=1:categories.append('Acute 1')
    if chronic is not None:
        if not numeric(chronic):return blocked(cls,'ADR25-C9-AQ-001',clauses,'valid_chronic_aquatic_data')
        rd=e.get('rapidly_degradable')
        if type(rd) is bool:
            c1=0.01 if rd else 0.1
            c2=0.1 if rd else 1.0
            if chronic<=c1:categories.append('Chronic 1')
            elif chronic<=c2:categories.append('Chronic 2')
        else:
            return blocked(cls,'ADR25-C9-AQ-001',clauses,'rapidly_degradable',
                           notes=['Adequate chronic data require rapid degradation status to distinguish Chronic 1/2.'])
    elif e.get('chronic_data_adequate') is False and acute is not None:
        # ADR Table 2.2.9.1.10.3.1(b)(iii): acute value in range + NRD and/or BCF / logKow.
        rd=e.get('rapidly_degradable')
        bcf=e.get('bcf')
        logkow=e.get('log_kow')
        if type(rd) is bool and (bcf is None or numeric(bcf,allow_zero=True)) and (logkow is None or (type(logkow) in (int,float) and isfinite(logkow))):
            bioacc=(bcf>=500 if bcf is not None else logkow>=4 if logkow is not None else False)
            if (not rd or bioacc) and acute <=1:categories.append('Chronic 1')
            elif (not rd or bioacc) and acute<=10:categories.append('Chronic 2')
        else:
            return blocked(cls,'ADR25-C9-AQ-001',clauses,'degradability_and_bioaccumulation_assessment')
    if not categories:
        return blocked(cls,'ADR25-C9-AQ-001',clauses,'complete_aquatic_hazard_evidence',
                       notes=['No demonstrated positive category is not a negative transport determination.'])
    notes=['Acute 1 / Chronic 1 / Chronic 2 identifies environmental hazard, not necessarily Class 9 as primary class.',
           'Algal-data judgement, relevant species, metals, M factors, special provisions and Chapter 3.2 require review.']
    if e.get('all_other_hazard_classes_excluded') is not True or e.get('named_entry_checked') is not True:
        return blocked(cls,'ADR25-C9-AQ-001',clauses,*[k for k in ('all_other_hazard_classes_excluded','named_entry_checked') if e.get(k) is not True],notes=notes,data={'aquatic_categories':sorted(set(categories))})
    if e.get('physical_state') not in ('liquid','solid'):
        return blocked(cls,'ADR25-C9-AQ-001',clauses,'physical_state',notes=notes)
    return decide(cls,'criteria_met','ADR25-C9-AQ-001',clauses,pg='III',notes=notes,
                  data={'aquatic_categories':sorted(set(categories)),
                        'candidate_un': '3082' if e['physical_state']=='liquid' else '3077'})


def elevated_temperature(e):
    cls='9'; clauses=['2.2.9.1.13','2.2.9.3']
    form=e.get('physical_state')
    temp=e.get('carriage_temperature_c')
    if form not in ('solid','liquid') or not numeric(temp,allow_zero=True):
        return blocked(cls,'ADR25-C9-TEMP-001',clauses,'physical_state_and_carriage_temperature_c')
    if form=='liquid' and temp>=100:
        if 'flash_point_c' not in e:
            return blocked(cls,'ADR25-C9-TEMP-001',clauses,'flash_point_c_or_verified_no_flash_point')
        fp=e['flash_point_c']
        if fp is not None and (type(fp) not in (int,float) or temp>=fp):
            return blocked(cls,'ADR25-C9-TEMP-001',clauses,'class3_heated_flammable_liquid_assessment')
        code='M9'; un='3257'
    elif form=='solid' and temp>=240:
        code='M10'; un='3258'
    else:
        return decide(cls,'criteria_not_met','ADR25-C9-TEMP-001',clauses,
                      notes=['Only elevated-temperature Class 9 pathway excluded; other hazards remain.'])
    if e.get('all_other_hazard_classes_excluded') is not True or e.get('named_entry_checked') is not True:
        return blocked(cls,'ADR25-C9-TEMP-001',clauses,*[k for k in ('all_other_hazard_classes_excluded','named_entry_checked') if e.get(k) is not True],
                       data={'candidate_code':code,'candidate_un':un},
                       notes=['Class 9 elevated-temperature entries apply only where no other class criterion is met.'])
    return decide(cls,'criteria_met','ADR25-C9-TEMP-001',clauses,
                  data={'candidate_code':code,'candidate_un':un},
                  notes=['Packing group, if any, must be checked in DGL column (4).'])


def evaluate(e):
    if e.get('pathway')=='aquatic':return aquatic(e)
    if e.get('pathway')=='elevated_temperature':return elevated_temperature(e)
    return blocked('9','ADR25-C9-GATE',['2.2.9.1.1','2.2.9.1.2'],'supported_pathway',
                   notes=['Batteries, PCB, asbestos, special entries and other Class 9 pathways not implemented.'])