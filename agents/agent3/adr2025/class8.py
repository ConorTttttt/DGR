"""ADR 2025 Class 8 direct skin and metal corrosion evidence only."""
from .common import decide, blocked, numeric


def evaluate(e):
    cls='8'
    clauses=['2.2.8.1.5.1','2.2.8.1.5.2','2.2.8.1.5.3']
    if e.get('material_scope') not in ('substance','whole_mixture_tested'):
        return blocked(cls,'ADR25-C8-001',clauses,'material_scope',
                       notes=['Mixture bridges and concentration calculation 2.2.8.1.6 excluded.'])
    if e.get('human_experience_reviewed') is not True:
        return blocked(cls,'ADR25-C8-001',clauses,'human_experience_reviewed')
    if e.get('human_evidence_requires_expert_classification') is not False:
        return blocked(cls,'ADR25-C8-001',clauses,'expert_assessment_of_human_evidence')
    if e.get('valid_skin_test_result') not in ('corrosive','non_corrosive'):
        return blocked(cls,'ADR25-C8-001',clauses,'valid_skin_test_result')
    pg=None
    if e['valid_skin_test_result']=='corrosive':
        exposure=e.get('skin_exposure_min')
        observation=e.get('irreversible_damage_observed_after_min')
        if numeric(exposure,allow_zero=True) and numeric(observation,allow_zero=True):
            if exposure<=3 and observation<=60:pg='I'
            elif 3<exposure<=60 and observation<=20160:pg='II'
            elif 60<exposure<=240 and observation<=20160:pg='III'
        if pg is None and e.get('pg_i_excluded_by_valid_test') is True and e.get('ii_iii_indistinguishable') is True:
            pg='II'  # 2.2.8.1.5.2
        if pg is None and e.get('all_pg_indistinguishable') is True and e.get('other_test_resolves_pg') is False:
            pg='I'  # 2.2.8.1.5.2
        if pg is None:
            return blocked(cls,'ADR25-C8-001',clauses,'valid_skin_exposure_observation_or_tier_test',
                           notes=['Skin test identifies corrosion but cannot justify a numeric packing group.'])
    else:
        # ADR 2.2.8.1.5.3(c)(ii): one qualifying metal rate is enough to prove PG III,
        # but both non-qualifying rates are needed to rule out this metal pathway.
        steel=e.get('steel_corrosion_mm_year_55c')
        aluminium=e.get('aluminium_corrosion_mm_year_55c')
        for key,val in [('steel_corrosion_mm_year_55c',steel),('aluminium_corrosion_mm_year_55c',aluminium)]:
            if val is not None and not numeric(val,allow_zero=True):
                return blocked(cls,'ADR25-C8-002',['2.2.8.1.5.3(c)(ii)'],'valid_'+key)
        if (steel is not None and steel>6.25) or (aluminium is not None and aluminium>6.25):
            pg='III'
        elif steel is not None and aluminium is not None:
            return decide(cls,'criteria_not_met','ADR25-C8-002',['2.2.8.1.5.3(c)(ii)'],
                          notes=['Only assessed skin/metal corrosion pathways; evaluate other ADR hazard classes.'])
        else:
            return blocked(cls,'ADR25-C8-002',['2.2.8.1.5.3(c)(ii)'],
                           'metal_corrosion_rates_or_positive_rate_55c')
    notes=['Packing group provisional until named entries, human data, possible other hazards and precedence are reviewed.']
    if e.get('other_hazards_assessed') is not True or e.get('named_entry_checked') is not True:
        return blocked(cls,'ADR25-C8-001',clauses,*[k for k in ('other_hazards_assessed','named_entry_checked') if e.get(k) is not True],pg=pg,notes=notes)
    return decide(cls,'criteria_met','ADR25-C8-001' if e['valid_skin_test_result']=='corrosive' else 'ADR25-C8-002',clauses,pg=pg,notes=notes)