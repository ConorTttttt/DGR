"use strict";
/** Provisional ADR 2025 Class 4.2 candidate-only module. Do not use for legal SDS release. */
function evaluateClass42(e) {
  const r={schema_version:"1.0.0-rc1",assessment_id:e?.assessment_id||"",regime:"ADR",
    edition:"2025 ECE/TRANS/352",class:"4.2",rule_id:"ADR25-42-PENDING",status:"indeterminate",
    primary_class_candidates:[],subsidiary_risks:[],packing_group_candidates:[],
    exclusions:[],unresolved_evidence:[],expert_decisions:[],table_a_candidates:[],
    special_provision_outcomes:[],evidence_refs:[],clause_refs:[],assignment_permitted:false,
    requires_independent_review:true,final_un_number:null,final_packing_group:null,
    notes:["Class-scoped result only; never a final UN, PG or SDS 14 classification."]};
  const fail=(status,id,reason,clauses=[])=>{
    r.status=status;r.clause_refs.push(...clauses);
    r.unresolved_evidence.push({id,reason,blocks_assignment:true});return r;
  };
  const good=x=>typeof x==="number"&&Number.isFinite(x);
  const yes=(pg,rule,refs)=>{
    r.status="criteria_met";r.rule_id=rule;r.clause_refs.push(...refs);
    r.primary_class_candidates.push({class:"4.2",classification_code:null,division:null,
      compatibility_group:null,packing_group:pg,evidence_ids:[e.evidence_id],
      authority_decision_id:null,status:"criteria_met"});
    r.packing_group_candidates.push({value:pg,evidence_ids:[e.evidence_id],provisional:true});
    return r;
  };
  const no=(rule,refs)=>{
    r.status="criteria_not_met";r.rule_id=rule;r.clause_refs.push(...refs);
    r.notes.push("Negative only for this tested pathway, never globally not dangerous.");
    if(e.named_entry_un)return fail("indeterminate","named_entry_declassification","Named entry needs ADR 2.2.42.1.7 review.",["2.2.42.1.7"]);
    if(e.more_severe_experience===true)return fail("conflict","experience","More severe experience overrides a lenient N.O.S. finding.",["2.2.42.1.4"]);
    return r;
  };
  const exempt=(note,limit)=>{
    r.status="excluded_from_class";r.rule_id="ADR25-42-N4-PACKAGE-EXEMPTION";
    r.clause_refs.push(note,"MTC 33.4.6.4.2");
    r.exclusions.push({class:"4.2",legal_basis:note,scope:"verified formulation and individual package volume only",
      maximum_package_litres:limit,evidence_ids:[e.evidence_id]});
    if(e.named_entry_un||e.more_severe_experience===true)
      return fail("indeterminate","named_entry_or_experience_review","Package exemption needs further named-entry/experience review.",["2.2.42.1.4","2.2.42.1.7"]);
    return r;
  };
  if(!e||typeof e!=="object"||Array.isArray(e))return fail("indeterminate","input","Evidence object required.");
  const methods={pyrophoric_solid:"N.2",pyrophoric_liquid:"N.3",self_heating:"N.4"};
  if(!methods[e.pathway])return fail("unsupported","pathway","Unknown 4.2 pathway.");
  if(!["solid","liquid"].includes(e.physical_state))
    return fail("indeterminate","physical_state","Verified physical state required.");
  if((e.pathway==="pyrophoric_solid"&&e.physical_state!=="solid")||
     (e.pathway==="pyrophoric_liquid"&&e.physical_state!=="liquid"))
    return fail("conflict","state_mismatch","Pyrophoric N.2/N.3 sample physical state mismatches pathway.");
  if(e.is_article===true)return fail("unsupported","article","Article classification needs named-entry and special-provision assessment.",["2.2.42.1.2"]);
  if(e.pathway==="self_heating"&&e.physical_state==="liquid")
    return fail("unsupported","N4_liquid_sample","N.4 powder/granular cube protocol is not directly validated for liquid samples; obtain qualified alternate evidence or named-entry decision.",["MTC 33.4.6.3","2.2.42.1.4"]);
  for(const key of ["assessment_id","evidence_id","report_id","sample_id"])
    if(typeof e[key]!=="string"||!e[key].trim())return fail("indeterminate",key,"Missing unique report and sample provenance.");
  r.evidence_refs.push(e.evidence_id);
  if(e.named_entry_un!==undefined){
    if(typeof e.named_entry_un!=="string"||!/^\d{4}$/.test(e.named_entry_un)||e.named_entry_verified!==true)
      return fail("indeterminate","named_entry","Exact named Table A row confirmation required.",["3.2.1"]);
    r.unresolved_evidence.push({id:"table_a_named_entry",reason:"Integrator must resolve Table A row, all SPs and named-entry priority.",blocks_assignment:true});
    if(e.named_entry_un==="3255"){r.status="prohibited_for_carriage";r.rule_id="ADR25-42-3255";
      r.clause_refs.push("2.2.42.2");return r;}
    if(e.named_entry_un==="3127"&&e.physical_state==="solid"&&e.oxidizing_confirmed===true){
      if(e.class1_requirements_met===true)return fail("authority_required","UN3127_class1_route","Only competent Class 1 review can resolve exception.",["2.2.42.2","2.1.3.7"]);
      if(e.class1_requirements_met===false){r.status="prohibited_for_carriage";r.rule_id="ADR25-42-3127";r.clause_refs.push("2.2.42.2");return r;}
      return fail("authority_required","UN3127_class1_unknown","Class 1 exception unverified.",["2.2.42.2"]);
    }
  }
  if(e.conflicting_reports===true)return fail("conflict","reports","Contradictory test reports require reconciliation.");
  if(e.shipment_formulation_verified!==true)
    return fail(e.shipment_formulation_verified===false?"unsupported":"indeterminate","formulation",
      "Evidence must represent actual shipped product, concentrations and diluents.",["2.2.42.1.6"]);
  if(typeof e.is_mixture!=="boolean"||(e.is_mixture&&e.mixture_composition_verified!==true))
    return fail("indeterminate","mixture","Mixture status and actual tested formulation required.",["2.2.42.1.1","2.2.42.1.6","2.1.3"]);
  if(e.report_scope_verified!==true||e.protocol_conformant!==true||e.test_method!==methods[e.pathway])
    return fail("indeterminate","test_quality","Verified method, sample scope and MTC procedure required.",["2.2.42.1.4","MTC 33.4"]);
  if(e.pathway==="pyrophoric_solid"&&e.sample_form!=="powdery")
    return fail("unsupported","N2_form","N.2 pouring method is for powdery solid samples.",["MTC 33.4.4.3"]);
  if(e.pathway==="self_heating"&&!["powder","granular"].includes(e.sample_form))
    return fail("unsupported","N4_form","N.4 method specifies powder/granular material in commercial form.",["MTC 33.4.6.3"]);
  if(e.pathway==="self_heating")r.unresolved_evidence.push({
    id:"N4_scaleup_exceptions",reason:"ADR 2.2.42.1.5(c): 27 m³ / 50°C general exclusion; ADR 2.2.42.1.8(b): 450 L / 50°C PG-II exclusion. Cannot derive these from N.4 cubes; external qualified review required.",blocks_assignment:true});
  if(e.competing_evidence!==undefined){
    if(!Array.isArray(e.competing_evidence)||e.competing_evidence.some(x=>!x||
      !["1","3","4.1","4.3","5.1","6.1","8"].includes(x.class)||typeof x.evidence_id!=="string"||
      !x.evidence_id||x.verified!==true))
      return fail("indeterminate","competing_evidence","Separate ADR evidence needed before competing-risk referral.",["2.1.3.10"]);
    r.subsidiary_risks=e.competing_evidence.map(x=>({class:x.class,evidence_ids:[x.evidence_id],status:"indeterminate"}));
    if(r.subsidiary_risks.length)r.unresolved_evidence.push({id:"precedence",reason:"Lead agent must resolve primary/subsidiary hazard precedence.",blocks_assignment:true});
  }
  if(e.organometallic===true)r.unresolved_evidence.push({id:"organometallic_2_3_5",reason:"Separate ADR 2.3.5 N.1–N.5 flowchart and Table A selection required.",blocks_assignment:true});
  if(e.more_severe_experience===true)r.unresolved_evidence.push({id:"experience",reason:"Stricter experience-based assignment requires external review.",blocks_assignment:true});
  if(e.pathway==="pyrophoric_solid"){
    if(!Array.isArray(e.trials)||e.trials.length<1||e.trials.length>6)
      return fail("indeterminate","N2_trials","Six negative trials or an earlier positive required.",["MTC 33.4.4.3"]);
    for(const [i,t] of e.trials.entries()){
      if(!t||!good(t.quantity_ml)||t.quantity_ml<1||t.quantity_ml>2||
        t.drop_about_1m_verified!==true||t.noncombustible_surface_verified!==true||
        typeof t.ignites_during_fall!=="boolean"||
        !(t.ignition_seconds===null||(good(t.ignition_seconds)&&t.ignition_seconds>=0)))
        return fail("indeterminate","N2_trial_"+i,"Invalid N.2 trial, 1–2 ml, height or ignition time.",["MTC 33.4.4.3"]);
      if(t.ignites_during_fall||(t.ignition_seconds!==null&&t.ignition_seconds<=300))
        return yes("I","ADR25-42-N2-POS",["2.2.42.1.5(a)","2.2.42.1.8(a)","MTC 33.4.4.4"]);
      if(t.observed_full_5min!==true)return fail("indeterminate","N2_time_"+i,"Negative requires full five-minute observation.");
    }
    if(e.trials.length<6)return fail("indeterminate","N2_six","Six complete negatives required.",["MTC 33.4.4.3"]);
    return no("ADR25-42-N2-NEG",["MTC 33.4.4.4"]);
  }
  if(e.pathway==="pyrophoric_liquid"){
    const evaluateStage=(trials,stage,expected)=>{
      if(!Array.isArray(trials)||trials.length<1||trials.length>expected)return {bad:"count"};
      for(let i=0;i<trials.length;i++){
        const t=trials[i];
        if(!t||!(t.ignition_seconds===null||(good(t.ignition_seconds)&&t.ignition_seconds>=0))||
           (stage==="filter"&&!(t.charring_seconds===null||(good(t.charring_seconds)&&t.charring_seconds>=0))))
          return {bad:"time_"+i};
        if(stage==="carrier"&&t.inert_carrier_verified!==true)return {bad:"carrier_"+i};
        if(stage==="filter"&&(!good(t.temperature_c)||t.temperature_c<23||t.temperature_c>27||
          !good(t.humidity_pct)||t.humidity_pct<45||t.humidity_pct>55||
          t.fresh_dry_indented_whatman3_verified!==true))return {bad:"filter_conditions_"+i};
        if((t.ignition_seconds!==null&&t.ignition_seconds<=300)||
          (stage==="filter"&&t.charring_seconds!==null&&t.charring_seconds<=300))return {positive:true};
        if(t.observed_full_5min!==true)return {bad:"observation_"+i};
      }
      return {positive:false,complete:trials.length===expected};
    };
    const c=evaluateStage(e.carrier_trials,"carrier",6);
    if(c.bad)return fail("indeterminate","N3_carrier_"+c.bad,"N.3 carrier trial missing or invalid.",["MTC 33.4.5.3.1"]);
    if(c.positive){
      if(Array.isArray(e.filter_trials)&&e.filter_trials.length)return fail("conflict","N3_sequence","Second stage after positive first stage is unsupported.",["MTC 33.4.5.3.1"]);
      return yes("I","ADR25-42-N3-CARRIER",["2.2.42.1.5(b)(i)","2.2.42.1.8(a)","MTC 33.4.5.4"]);
    }
    if(!c.complete)return fail("indeterminate","N3_six","Six negative carrier trials required.",["MTC 33.4.5.3.1"]);
    const f=evaluateStage(e.filter_trials,"filter",3);
    if(f.bad)return fail("indeterminate","N3_filter_"+f.bad,"N.3 filter trial missing or invalid.",["MTC 33.4.5.3.2"]);
    if(f.positive)return yes("I","ADR25-42-N3-FILTER",["2.2.42.1.5(b)(ii)","2.2.42.1.8(a)","MTC 33.4.5.4"]);
    if(!f.complete)return fail("indeterminate","N3_three","Three negative filter trials required.",["MTC 33.4.5.3.2"]);
    return no("ADR25-42-N3-NEG",["MTC 33.4.5.4"]);
  }
  if(!Array.isArray(e.runs))return fail("indeterminate","N4_runs","N.4 thermal cube data required.");
  const recorded={};
  for(const [i,t] of e.runs.entries()){
    if(!t||![25,100].includes(t.cube_mm)||![100,120,140].includes(t.setpoint_c)||
      (t.cube_mm===25&&t.setpoint_c!==140)||!good(t.oven_actual_c)||
      Math.abs(t.oven_actual_c-t.setpoint_c)>2||typeof t.spontaneous_ignition!=="boolean"||
      t.continuous_record_verified!==true)
      return fail("indeterminate","N4_run_"+i,"Cube size, setpoint, ±2°C oven accuracy and continuous thermometry required.",["MTC 33.4.6.2"]);
    if(!t.spontaneous_ignition&&!good(t.max_sample_c))
      return fail("indeterminate","N4_temperature_"+i,"Measured maximum required when ignition absent.",["MTC 33.4.6.4.1"]);
    const actual=t.spontaneous_ignition||(t.max_sample_c>t.oven_actual_c+60);
    const nominal=t.spontaneous_ignition||(t.max_sample_c>t.setpoint_c+60);
    if(actual!==nominal)return fail("conflict","N4_actual_vs_nominal_"+i,
      "ADR 200/180/160°C nominal and N.4 actual oven+60°C thresholds disagree; review.",["2.2.42.1.5(c)","MTC 33.4.6.4.1"]);
    if(actual&&t.event_within_24h!==true)return fail("indeterminate","N4_positive_time_"+i,"Positive N.4 event must occur within 24 h.");
    if(!actual&&t.observed_full_24h!==true)return fail("indeterminate","N4_negative_time_"+i,"Negative N.4 requires 24 h.");
    const key=t.cube_mm+"@"+t.setpoint_c;
    if(key in recorded && recorded[key]!==actual)return fail("conflict","N4_repeat_"+key,"Conflicting repeated N.4 runs.");
    recorded[key]=actual;
  }
  const get=key=>key in recorded?recorded[key]:null;
  const a=get("100@140"),b=get("25@140"),c=get("100@120"),d=get("100@100");
  if(a===false&&(b===true||c===true||d===true))return fail("conflict","N4_temperature_or_cube_inversion","Low-temperature or 25 mm positive conflicts with 100 mm negative @140°C; qualified review required.",["MTC 33.4.6.4.1"]);
  if(a===false)return no("ADR25-42-N4-NEG",["2.2.42.1.5(c)","MTC 33.4.6.4.2(a)"]);
  if(a!==true&&b!==true)return fail("indeterminate","N4_large_140","100 mm positive at 140°C, or 25 mm positive, required.");
  if(b===true)return yes("II","ADR25-42-N4-PGII",["2.2.42.1.8(b)","MTC 33.4.6.4.3"]);
  if(b!==false)return fail("indeterminate","N4_small_140","25 mm @140°C needed to distinguish PG II/III.");
  if(!good(e.package_volume_l)||e.package_volume_l<=0)
    return fail("indeterminate","package_volume_l","Individual package volume required for PG III/exemption.",["2.2.42.1.5(c) Notes 1-2"]);
  if(c===false&&d===true)return fail("conflict","N4_lowtemp_inversion","100°C positive but 120°C negative must be reviewed.");
  if(e.package_volume_l<=450){
    if(c===false)return exempt("2.2.42.1.5(c) Note 1",3000);
    if(d===false)return exempt("2.2.42.1.5(c) Note 2",450);
    if(d===true)return yes("III","ADR25-42-N4-PGIII",["2.2.42.1.8(c)","MTC 33.4.6.4.4(c)"]);
    return fail("indeterminate","N4_low100","Need 100 mm @100°C or negative 120°C for <=450 L.");
  }
  if(e.package_volume_l<=3000){
    if(c===false)return exempt("2.2.42.1.5(c) Note 1",3000);
    if(c===true)return yes("III","ADR25-42-N4-PGIII",["2.2.42.1.8(c)","MTC 33.4.6.4.4(b)"]);
    return fail("indeterminate","N4_low120","Need 100 mm @120°C for >450 L through 3 m³.");
  }
  return yes("III","ADR25-42-N4-PGIII",["2.2.42.1.8(c)","MTC 33.4.6.4.4(a)"]);
}
module.exports={evaluateClass42};
