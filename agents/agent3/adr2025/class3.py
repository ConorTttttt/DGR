"""Provisional ADR 2025 Class 3 evidence evaluator (no final DGL/Section 14 assignment).

All clause citations refer to ECE/TRANS/352, volume I, ADR 2025. The
UN Manual of Tests and Criteria is supporting test-method authority, Rev.8
(ST/SG/AC.10/11/Rev.8) plus Amendment 1. Independent review is required.
"""
from math import isfinite
from .common import blocked, decide

C = '3'
BASE = ['1.2.1 (liquid)', '2.2.3.1.1', '2.3.3.1']
FLASH_METHODS = frozenset({
    'ISO 1516', 'ISO 1523', 'ISO 2719', 'ISO 13736', 'ISO 3679', 'ISO 3680',
    'ASTM D3828-07a', 'ASTM D56-05', 'ASTM D3278-96(2004)e1', 'ASTM D93-08',
    'NF M 07-019', 'NF M 07-011', 'NF T 30-050', 'NF T 66-009',
    'NF M 07-036', 'DIN 51755', 'GOST 12.1.044-84',
    'EN ISO 13736', 'EN ISO 2719 Method B',
})
BOILING_METHODS = frozenset({
    'ISO 3924', 'ISO 4626', 'ISO 3405', 'ASTM D86-07a', 'ASTM D1078-05',
    'EC 440/2008 A.2',
})
LIQUID_DESENSITIZED_ENTRIES = frozenset({'1204','2059','3064','3343','3357','3379','3555'})
# ADR 2.2.3.1.4 table: strict minima, inclusive maxima; flash point STRICTLY above.
VISCOSITY_TABLE = (
    {'jet':4,'t_min':20,'t_max':60,'v_min':20,'v_max':80,'fp_min':17},
    {'jet':4,'t_min':60,'t_max':100,'v_min':80,'v_max':135,'fp_min':10},
    {'jet':6,'t_min':20,'t_max':32,'v_min':135,'v_max':220,'fp_min':5},
    {'jet':6,'t_min':32,'t_max':44,'v_min':220,'v_max':300,'fp_min':-1},
    {'jet':6,'t_min':44,'t_max':100,'v_min':300,'v_max':700,'fp_min':-5},
    {'jet':6,'t_min':100,'t_max':None,'v_min':700,'v_max':None,'fp_min':None},
)

def num(x, low=None, high=None):
    return type(x) in (int,float) and isfinite(x) and (low is None or x>=low) and (high is None or x<=high)

def nonempty(x):
    return isinstance(x,str) and bool(x.strip())

def failure(rule, refs, *fields, note=None, pg=None, data=None):
    return blocked(C, rule, refs, *fields, pg=pg, data=data,
                   notes=([note] if note else []))

def result(status, rule, refs, *, pg=None, data=None, notes=()):
    d=dict(data or {})
    if pg:
        d['calculated_class3_packing_group']=pg
        d['table_a_packing_group']=None
    return decide(C, status, rule, refs, pg=pg, data=d, notes=notes)

def _flash_point(e):
    refs=['2.2.3.1.1', '2.3.3.1.1–2.3.3.1.5']
    if not num(e.get('flash_point_c')):
        return None, failure('ADR25-C3-EVID-FP',refs,'flash_point_c')
    if e.get('flash_point_method') not in FLASH_METHODS:
        return None, failure('ADR25-C3-EVID-FP',refs,'approved_closed_cup_flash_point_method')
    if not nonempty(e.get('flash_point_evidence_id')):
        return None, failure('ADR25-C3-EVID-FP',refs,'flash_point_evidence_id')
    kind=e.get('flash_point_method_kind')
    if kind not in ('equilibrium','non_equilibrium'):
        return None, failure('ADR25-C3-EVID-FP',refs,'flash_point_method_kind')
    fp=e['flash_point_c']
    if kind=='non_equilibrium' and (21 <= fp <=25 or 58<=fp<=62):
        if not num(e.get('flash_point_equilibrium_confirmation_c')) or not nonempty(e.get('flash_point_equilibrium_confirmation_id')):
            return None, failure('ADR25-C3-EVID-FP', ['2.3.3.1.4'],
                                 'equilibrium_confirmation_near_23_or_60_c')
        # Do not silently choose one of contradictory results.
        if fp != e['flash_point_equilibrium_confirmation_c']:
            return None, failure('ADR25-C3-EVID-FP',['2.3.3.1.4','2.3.3.1.5'],
                                 'adjudicated_flash_point_c',
                                 note='Equilibrium confirmation differs from non-equilibrium result; select documented governing result.')
    measurements=e.get('flash_point_measurements')
    if measurements is not None:
        if not isinstance(measurements,list) or not measurements:
            return None, failure('ADR25-C3-EVID-FP',refs,'valid_flash_point_measurements')
        values=[]
        for m in measurements:
            if not isinstance(m,dict) or not num(m.get('value_c')) or not nonempty(m.get('evidence_id')):
                return None, failure('ADR25-C3-EVID-FP',refs,'documented_flash_point_measurements')
            values.append(m['value_c'])
        if any(v != fp for v in values):
            # ADR §2.3.3.1.5 is a dispute-specific two-stage check-test protocol.
            # No generic low-value or caller-booleans may silently override conflict.
            return None, failure('ADR25-C3-EVID-FP',['2.3.3.1.5'],
                                 'flash_point_dispute_check_tests_and_expert_resolution',
                                 note='Contradictory flash points require independently assessed check-test evidence.')
    return fp, None

def _liquid_state(e, *, molten_heated=False):
    refs=['1.2.1 (liquid)','2.2.3.1.1','2.3.4']
    if molten_heated and e.get('physical_state')=='molten_solid':
        return None
    if e.get('physical_state')!='liquid':
        return failure('ADR25-C3-STATE',refs,'liquid_state_under_ADR_1.2.1')
    if not num(e.get('vapour_pressure_kpa_50c'),0,300):
        return failure('ADR25-C3-STATE',refs,'vapour_pressure_kpa_50c_0_to_300')
    if type(e.get('completely_gaseous_at_20c')) is not bool:
        return failure('ADR25-C3-STATE',refs,'completely_gaseous_at_20c')
    if e['completely_gaseous_at_20c']:
        return failure('ADR25-C3-STATE',refs,'class2_physical_state_review')
    basis=e.get('liquid_definition_basis')
    if basis=='melting_point':
        if not num(e.get('melting_point_c')):
            return failure('ADR25-C3-STATE',refs,'melting_point_c')
        if e['melting_point_c']>20:
            return failure('ADR25-C3-STATE',refs,'ASTM_D4359_or_2.3.4_fluidity_test')
    elif basis in ('ASTM D4359-90','ADR 2.3.4'):
        if e.get('liquid_definition_test_passed') is not True:
            return failure('ADR25-C3-STATE',refs,'positive_liquid_definition_test')
    else:
        return failure('ADR25-C3-STATE',refs,'liquid_definition_basis')
    return None

def _restrictions(e):
    refs=['2.2.3.2.1','2.2.3.2.2','2.3.3.3','3.3 SP386']
    if type(e.get('peroxide_forming')) is not bool:
        return failure('ADR25-C3-RESTRICT',refs,'peroxide_forming_assessment')
    if e['peroxide_forming']:
        if not num(e.get('peroxide_h2o2_mass_pct'),0,100) or not nonempty(e.get('peroxide_evidence_id')):
            return failure('ADR25-C3-RESTRICT',refs,'peroxide_h2o2_mass_pct_and_test_evidence')
        if e['peroxide_h2o2_mass_pct']>0.3:
            return failure('ADR25-C3-RESTRICT',['2.2.3.2.1'], 'not_accepted_for_carriage',
                           data={'carriage_prohibition_candidate':'peroxide_H2O2_equivalent_above_0.3_percent'},
                           note='Carriage prohibited by ADR 2.2.3.2.1; do not issue transport classification.')
    if type(e.get('chemically_unstable')) is not bool:
        return failure('ADR25-C3-RESTRICT',refs,'chemical_stability_assessment')
    if e['chemically_unstable'] and e.get('stabilization_precautions_documented') is not True:
        return failure('ADR25-C3-RESTRICT',['2.2.3.2.2','3.3 SP386'],
                       'documented_precautions_preventing_dangerous_reaction',
                       note='Chemically unstable Class 3 may not be accepted unless adequate precautions proven.')
    return None

def _nitrocellulose(e, fp):
    if e.get('contains_nitrocellulose') is not True:
        if e.get('contains_nitrocellulose') is False:
            return None
        return failure('ADR25-C3-NITRO',['2.2.3.1.4 NOTE','2.2.3.1.5.1'],
                       'contains_nitrocellulose')
    pct=e.get('nitrocellulose_mass_pct'); nitrogen=e.get('nitrocellulose_nitrogen_dry_mass_pct')
    if not num(pct,0,100) or not num(nitrogen,0,100):
        return failure('ADR25-C3-NITRO',['2.2.3.1.4 NOTE'],
                       'nitrocellulose_mass_pct_and_nitrogen_dry_mass_pct')
    if fp>=23 and pct>20:
        return failure('ADR25-C3-NITRO',['2.2.3.1.4 NOTE','2.2.3.1.6'],
                       'nitrocellulose_mixture_named_entry_review',
                       note='The named nitrocellulose routing in 2.2.3.1.4 NOTE applies to mixtures with flash point below 23 C; do not extrapolate.')
    if pct>55 or nitrogen>12.6:
        return failure('ADR25-C3-NITRO',['2.2.3.1.4 NOTE'],
                       'class1_or_class4.1_nitrocellulose_classification',
                       data={'possible_classes':['1','4.1']},
                       note='Nitrocellulose mixture requires Class 1/Class 4.1 and Table A review.')
    if pct>20:
        return failure('ADR25-C3-NITRO',['2.2.3.1.4 NOTE'],
                       'UN2059_table_A_and_special_provisions',
                       data={'named_un_candidate':'2059'},
                       note='20% < nitrocellulose <=55% routes to named UN 2059; no PG assigned here.')
    return None

def _viscosity_pg3(e, fp):
    refs=['2.2.3.1.4','UN MTC Rev.8 Part III 32.4.2','32.4.3','32.5.1']
    for k in ('solvent_separation_pct','receptacle_capacity_l','viscosity_flow_time_s'):
        if not num(e.get(k),0):
            return None, failure('ADR25-C3-VISC-PG',refs,k)
    if not nonempty(e.get('viscosity_evidence_id')) or not nonempty(e.get('solvent_separation_evidence_id')):
        return None, failure('ADR25-C3-VISC-PG',refs,'viscosity_and_solvent_test_evidence_ids')
    if e.get('viscosity_test_method')!='ISO 2431:1984 / MTC 32.4.3':
        return None, failure('ADR25-C3-VISC-PG',refs,'ISO_2431_1984_23c_test_method')
    if e.get('viscosity_jet_diameter_mm') not in (4,6):
        return None, failure('ADR25-C3-VISC-PG',refs,'jet_diameter_4_or_6_mm')
    for key in ('mixture_class61_criteria_met','mixture_class8_criteria_met',
                'separated_solvent_class61_criteria_met','separated_solvent_class8_criteria_met'):
        if type(e.get(key)) is not bool:
            return None, failure('ADR25-C3-VISC-PG',refs,key)
    row=next((r for r in VISCOSITY_TABLE if
              e['viscosity_jet_diameter_mm']==r['jet'] and
              e['viscosity_flow_time_s']>r['t_min'] and
              (r['t_max'] is None or e['viscosity_flow_time_s']<=r['t_max']) and
              (r['fp_min'] is None or fp>r['fp_min'])),None)
    granted=(row is not None and e['solvent_separation_pct']<3 and
             e['receptacle_capacity_l']<=450 and
             not any(e[k] for k in ('mixture_class61_criteria_met','mixture_class8_criteria_met',
                                    'separated_solvent_class61_criteria_met','separated_solvent_class8_criteria_met')))
    return granted, None

def _viscosity_exemption(e, fp):
    refs=['2.2.3.1.5.1','2.2.3.1.5.2','UN MTC Rev.8 32.4.3','32.5.1']
    for k in ('toxic','corrosive','environmentally_hazardous'):
        if type(e.get(k)) is not bool:
            return None, failure('ADR25-C3-VISC-EXEMPT',refs,k)
    for k in ('solvent_separation_pct','receptacle_capacity_l',
              'viscosity_flow_time_s','class3_substances_mass_pct'):
        if not num(e.get(k),0,100 if k in ('solvent_separation_pct','class3_substances_mass_pct') else None):
            return None, failure('ADR25-C3-VISC-EXEMPT',refs,k)
    if not nonempty(e.get('solvent_separation_evidence_id')) or not nonempty(e.get('viscosity_evidence_id')):
        return None, failure('ADR25-C3-VISC-EXEMPT',refs,'solvent_separation_and_viscosity_test_ids')
    if e.get('viscosity_test_method')!='ISO 2431:1984 / MTC 32.4.3' or e.get('viscosity_jet_diameter_mm') != 6:
        return None, failure('ADR25-C3-VISC-EXEMPT',refs,'ISO_2431_1984_6_mm_jet')
    passes=(not e['toxic'] and not e['corrosive'] and e['receptacle_capacity_l']<=450 and
            e['solvent_separation_pct']<3 and
            (e['viscosity_flow_time_s']>=60 or
             (e['viscosity_flow_time_s']>=40 and e['class3_substances_mass_pct']<=60)))
    if not passes:
        return False, None
    if not e['environmentally_hazardous']:
        return 'ADR_exemption_2.2.3.1.5.1',None
    for k in ('packaging_single_or_combination', 'packaging_4_1_1_compliant'):
        if type(e.get(k)) is not bool:
            return None, failure('ADR25-C3-VISC-EXEMPT',['2.2.3.1.5.2'],k)
    if not num(e.get('net_quantity_per_single_or_inner_l'),0):
        return None, failure('ADR25-C3-VISC-EXEMPT',['2.2.3.1.5.2'],'net_quantity_per_single_or_inner_l')
    if e['packaging_single_or_combination'] and e['packaging_4_1_1_compliant'] and e['net_quantity_per_single_or_inner_l']<=5:
        return 'conditional_packaging_exemption_2.2.3.1.5.2', None
    return False,None

def _non_sustaining(e, fp):
    if fp<=35:
        return False,None
    refs=['2.2.3.1.1 NOTE 1','UN MTC Rev.8 32.2.5']
    sustain=e.get('sustains_combustion')
    if type(sustain) is not bool:
        return None, failure('ADR25-C3-COMBUST',refs,'sustains_combustion_or_approved_non_sustain_evidence')
    if sustain:
        return False,None
    if not nonempty(e.get('sustained_combustion_evidence_id')):
        return None, failure('ADR25-C3-COMBUST',refs,'sustained_combustion_evidence_id')
    basis=e.get('non_sustained_combustion_basis')
    proven=(basis=='UN_MTC_L2_negative' and e.get('sustained_combustion_test_result')=='negative') or (
        basis=='ISO_2592_fire_point' and num(e.get('fire_point_c')) and e['fire_point_c']>100) or (
        basis=='miscible_water_content' and e.get('miscible_solution') is True and
        num(e.get('water_content_mass_percent'),0,100) and e['water_content_mass_percent']>90)
    if not proven:
        return None, failure('ADR25-C3-COMBUST',refs,'negative_L2_or_ISO2592_over100_or_miscible_water_over90pct')
    return True,None

def evaluate(e):
    if not isinstance(e,dict):
        return failure('ADR25-C3-INPUT',BASE,'evidence_dictionary')
    if e.get('physical_state') not in ('liquid','molten_solid'):
        return failure('ADR25-C3-STATE',BASE,'physical_state_liquid_or_molten_solid')
    if type(e.get('liquid_desensitized_explosive')) is not bool:
        return failure('ADR25-C3-DESENS',['2.2.3.1.1','2.2.3.2.3'], 'liquid_desensitized_explosive')
    if e['liquid_desensitized_explosive']:
        if e['physical_state'] != 'liquid':
            return failure('ADR25-C3-DESENS',['2.2.3.1.1'], 'homogeneous_liquid_state')
        un=str(e.get('liquid_desensitized_un_number',''))
        if un not in LIQUID_DESENSITIZED_ENTRIES:
            return failure('ADR25-C3-DESENS',['2.2.3.1.1','2.2.3.2.3'],
                           'approved_table_A_liquid_desensitized_entry',
                           data={'carriage_prohibition_candidate':'unlisted_liquid_desensitized_explosive'},
                           note='Only specified Table A entries; otherwise Class 3 carriage prohibited.')
        return result('criteria_met','ADR25-C3-DESENS',['2.2.3.1.1','2.2.3.2.3'],
                      data={'named_un_candidate':un,'table_a_required':True},
                      notes=['Liquid desensitized explosives require Table A/competent-authority and restrictions review.'])
    fp,err=_flash_point(e)
    if err: return err
    if type(e.get('carried_at_or_above_flash_point')) is not bool:
        return failure('ADR25-C3-HEATED',['2.2.3.1.1'], 'carried_at_or_above_flash_point')
    heated=e['carried_at_or_above_flash_point']
    if heated and (not num(e.get('carriage_temperature_c')) or e['carriage_temperature_c']<fp):
        return failure('ADR25-C3-HEATED',['2.2.3.1.1'],
                       'carriage_temperature_c_at_or_above_flash_point')
    if type(e.get('diesel_gasoil_light_heating_oil')) is not bool:
        return failure('ADR25-C3-DIESEL',['2.2.3.1.1 NOTE 2'], 'diesel_gasoil_light_heating_oil')
    state_err=_liquid_state(e, molten_heated=(heated and fp>60))
    if state_err: return state_err
    restrict=_restrictions(e)
    if restrict: return restrict
    if fp>60 and e['diesel_gasoil_light_heating_oil'] and fp<=100:
        return result('criteria_met','ADR25-C3-DIESEL',['2.2.3.1.1 NOTE 2'],
                      data={'named_un_candidate':'1202','table_a_required':True},
                      notes=['Named diesel/gasoil/light-heating-oil exception; Table A PG not resolved.'])
    if fp>60 and heated:
        return result('criteria_met','ADR25-C3-HEATED',['2.2.3.1.1'],
                      data={'named_un_candidate':'3256','table_a_required':True},
                      notes=['Heated carriage at/above flash point; entry/PG subject to Table A.'])
    if fp>60:
        return result('criteria_not_met','ADR25-C3-BASE',['2.2.3.1.1'],
                      notes=['Only the ordinary Class 3 flammability pathway is negative; check other classes and named entries.'])
    if e.get('material_scope') not in ('substance','whole_tested_mixture'):
        return failure('ADR25-C3-MIX',['2.2.3.1.6','2.2.3.1.7','2.1.3'],
                       'substance_or_whole_tested_mixture')
    if e['material_scope']=='whole_tested_mixture' and e.get('mixture_actual_hazard_reviewed') is not True:
        return failure('ADR25-C3-MIX',['2.2.3.1.6','2.1.3'],
                       'actual_mixture_hazards_and_named_entry_review')
    nc_err=_nitrocellulose(e,fp)
    if nc_err: return nc_err
    if e.get('toxic_by_inhalation_high') is True or (fp>=23 and e.get('toxic_pesticide') is True):
        return failure('ADR25-C3-PRECEDENCE',['2.2.3.1.1 NOTE 3','2.2.3.1.1 NOTE 4'],
                       'Class_6.1_primary_hazard_and_entry_review',
                       data={'possible_primary_class':'6.1'},
                       note='Class 6.1 priority is reviewed before any viscosity concession.')
    non_sustain,err=_non_sustaining(e,fp)
    if err: return err
    if non_sustain and not heated:
        return result('criteria_not_met','ADR25-C3-COMBUST',['2.2.3.1.1 NOTE 1','UN MTC Rev.8 32.2.5'],
                      notes=['Evidenced non-sustained combustion is only a Class 3 criterion exclusion.'])
    if type(e.get('viscosity_concession_claimed')) is not bool:
        return failure('ADR25-C3-VISC-CLAIM',['2.2.3.1.4','2.2.3.1.5.1'],
                       'viscosity_concession_claimed')
    if not num(e.get('initial_boiling_point_c')):
        return failure('ADR25-C3-PG',['2.2.3.1.3','2.3.3.2'], 'initial_boiling_point_c')
    if e.get('initial_boiling_point_method') not in BOILING_METHODS or not nonempty(e.get('initial_boiling_point_evidence_id')):
        return failure('ADR25-C3-PG',['2.3.3.2'], 'approved_initial_boiling_point_method_and_evidence_id')
    ibp=e['initial_boiling_point_c']
    basepg='I' if ibp<=35 else ('II' if fp<23 else 'III')
    candidate=basepg
    if e['viscosity_concession_claimed'] and fp<23:
        if basepg=='I':
            return failure('ADR25-C3-VISC-PG',['2.2.3.1.3','2.2.3.1.4'],
                           'regulatory_review_of_PG_I_viscosity_concession',pg=basepg,
                           note='Do not downgrade a PG I liquid without independent regulatory determination.')
        granted,err=_viscosity_pg3(e,fp)
        if err:return err
        if granted:candidate='III'
    if e['viscosity_concession_claimed'] and fp>=23:
        exempt,err=_viscosity_exemption(e,fp)
        if err:return err
        if exempt:
            return result('criteria_not_met','ADR25-C3-VISC-EXEMPT',
                          ['2.2.3.1.5.1','2.2.3.1.5.2'],
                          data={'concession':exempt,'calculated_class3_packing_group':basepg,
                                'table_a_packing_group':None},
                          notes=['Exemption applies only under stated substance and packaging conditions; no global Section 14 decision.'])
    pg_refs=['2.2.3.1.3','2.3.3.1','2.3.3.2']
    if candidate!=basepg:pg_refs+=['2.2.3.1.4','UN MTC Rev.8 32.4.3','32.5.1']
    data={'subsidiary_hazard_candidates':[],'table_a_required':True}
    for flag,name in [('toxic','6.1'),('corrosive','8'),('environmentally_hazardous','environmental')]:
        if e.get(flag) is True:data['subsidiary_hazard_candidates'].append(name)
    if e.get('toxic_by_inhalation_high') is True or (fp>=23 and e.get('toxic_pesticide') is True):
        return failure('ADR25-C3-PRECEDENCE',['2.2.3.1.1 NOTE 3','2.2.3.1.1 NOTE 4','2.1.3.10'],
                       'Class_6.1_primary_hazard_and_entry_review',pg=candidate,
                       data={**data,'possible_primary_class':'6.1'},
                       note='ADR explicitly refers highly toxic inhalation liquids and specified pesticides to Class 6.1.')
    if e.get('other_hazards_assessed') is not True or e.get('named_entry_checked') is not True:
        return failure('ADR25-C3-PRECEDENCE',['2.2.3.1.3','2.1.3.10','3.2','3.3'],
                       'other_hazards_and_named_entry_attested',pg=candidate,data=data,
                       note='Class 3 intrinsic PG only; actual classification/PG requires Table A and precedence.')
    if data['subsidiary_hazard_candidates']:
        return failure('ADR25-C3-PRECEDENCE',['2.2.3.1.3','2.1.3.10'],
                       'multi_hazard_precedence_review',pg=candidate,data=data)
    return result('criteria_met','ADR25-C3-BASE',pg_refs,pg=candidate,data=data,
                  notes=['Calculated Class 3 PG is provisional and distinct from Table A PG.'])
