"""ADR 2025 Class 6.1 numeric evidence pathways (pure substance/whole-material data).

No numerical mixing calculations, CLP short-circuits or hazard-precedence resolution.
"""
from .common import decide, blocked, numeric


def _ld_pg(v, thresholds):
    if v <= thresholds[0]: return 'I'
    if v <= thresholds[1]: return 'II'
    if v <= thresholds[2]: return 'III'
    return None


def evaluate(e):
    cls='6.1'
    clauses=['2.2.61.1.6', '2.2.61.1.7', '2.2.61.1.7.1', '2.2.61.1.8']
    if e.get('material_scope') not in ('substance', 'whole_mixture_tested'):
        return blocked(cls, 'ADR25-C61-001', clauses, 'material_scope',
                       notes=['Constituent-based mixture methods in 2.2.61.1.9–1.10 not implemented.'])
    if e.get('human_experience_reviewed') is not True:
        return blocked(cls, 'ADR25-C61-001', clauses, 'human_experience_reviewed',
                       notes=['Human experience must be considered before animal criteria (2.2.61.1.6).'])
    if e.get('human_evidence_requires_expert_classification') is not False:
        return blocked(cls, 'ADR25-C61-001', clauses, 'expert_assessment_of_human_evidence')
    paths=[]
    for name,bounds in [('oral_ld50_mg_kg',(5,50,300)),
                        ('dermal_ld50_mg_kg',(50,200,1000))]:
        v=e.get(name)
        if v is not None:
            if not numeric(v): return blocked(cls,'ADR25-C61-001',clauses,'valid_'+name)
            grade=_ld_pg(v,bounds)
            if grade: paths.append((name,grade))
    dust=e.get('dust_mist_lc50_mg_l')
    if dust is not None:
        if not numeric(dust): return blocked(cls,'ADR25-C61-001',clauses,'valid_dust_mist_lc50_mg_l')
        hours=e.get('dust_mist_exposure_hours')
        if hours not in (1,4):return blocked(cls,'ADR25-C61-001',clauses,'dust_mist_exposure_hours_1_or_4')
        converted=dust * (4 if hours==4 else 1)
        pg=_ld_pg(converted,(0.2,2,4))
        if pg:paths.append(('dust_mist_lc50_mg_l',pg))
    vapor=e.get('vapour_lc50_ppm')
    if vapor is not None:
        if not numeric(vapor):return blocked(cls,'ADR25-C61-002',clauses,'valid_vapour_lc50_ppm')
        hours=e.get('vapour_exposure_hours')
        V=e.get('saturated_vapour_concentration_ppm_20c')
        if hours not in (1,4) or not numeric(V,allow_zero=True):
            return blocked(cls,'ADR25-C61-002',clauses,'vapour_exposure_hours_1_or_4','saturated_vapour_concentration_ppm_20c')
        lc=vapor*(2 if hours==4 else 1)
        if V >= 10*lc and lc <= 1000:pg='I'
        elif V >= lc and lc <= 3000:pg='II'
        elif V >= 0.2*lc and lc <= 5000:pg='III'
        else:pg=None
        if pg:paths.append(('vapour_lc50_ppm',pg))
    if not paths:
        return blocked(cls, 'ADR25-C61-001', clauses, 'affirmative_acute_toxicity_evidence',
                       notes=['No applicable toxicity threshold demonstrated; cannot conclude absence of Class 6.1 without complete evidence.'])
    pg=min((x[1] for x in paths), key={'I':0,'II':1,'III':2}.get)
    if e.get('tear_gas') is True and pg=='III':pg='II'
    notes=['Numerical toxicity packing group candidate; whole-mixture method and named-entry overrides not implemented.',
           'Class 8 special precedence 2.2.61.1.7.2, hazard table 2.1.3.10 and DGL 3.2 must be considered.']
    if pg!='I' and e.get('exposure_route_evidence_complete') is not True:
        return blocked(cls,'ADR25-C61-001',clauses,'exposure_route_evidence_complete',pg=pg,notes=notes)
    if e.get('class8_priority_checked') is not True or e.get('other_hazards_assessed') is not True or e.get('named_entry_checked') is not True:
        return blocked(cls,'ADR25-C61-001',clauses,*[k for k in ('class8_priority_checked','other_hazards_assessed','named_entry_checked') if e.get(k) is not True], pg=pg,notes=notes)
    return decide(cls,'criteria_met','ADR25-C61-001',clauses+['2.2.61.1.7.2'],pg=pg,notes=notes,data={'positive_routes':paths})