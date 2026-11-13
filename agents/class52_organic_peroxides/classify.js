"use strict";
function classify(e) {
  "use strict";
  e=e||{};
  const f=e.formulation||{};
  const r={schema_version:"1.0.0-rc1",assessment_id:e.assessment_id||null,regime:"ADR",edition:"2025 ECE/TRANS/352 English",class:"5.2",rule_id:null,status:"indeterminate",primary_class_candidates:[],subsidiary_risks:[],packing_group_candidates:[],exclusions:[],unresolved_evidence:[],expert_decisions:[],table_a_candidates:[],special_provision_outcomes:[],evidence_refs:e.evidence_refs||[],clause_refs:[],packing_group:null,temperature_control:null,available_oxygen_percent:null,assignment_permitted:false,requires_independent_review:true};
  const end=(status,rule,...clauses)=>{r.status=status;r.rule_id=rule;r.clause_refs=[...new Set(r.clause_refs.concat(clauses))];return r;};
  const need=(id,reason)=>r.unresolved_evidence.push({id,reason,blocks_assignment:true});
  const n=x=>typeof x==="number"&&Number.isFinite(x);
  const dec=x=>{const s=String(x);if(!/^\d+(?:\.\d{1,12})?$/.test(s))throw Error("invalid decimal");const a=s.split(".");return[BigInt(a.join("")),10n**BigInt((a[1]||"").length)];};
  const sum=(a,b)=>[a[0]*b[1]+b[0]*a[1],a[1]*b[1]];
  const mul=(a,b)=>[a[0]*b[0],a[1]*b[1]];
  const divide=(a,b)=>{if(!b[0])throw Error("zero molecular mass");return[a[0]*b[1],a[1]*b[0]];};
  const le=(a,b)=>a[0]*b[1]<=b[0]*a[1];
  if(e.identity_evidence_verified!==true||typeof e.is_organic_peroxide!=="boolean"){need("identity","Verified -O-O- chemical identity or verified negative finding required");return end("indeterminate","OP52-IDENTITY","2.2.52.1.3");}
  if(!e.is_organic_peroxide)return end("not_applicable","OP52-IDENTITY-NEGATIVE","2.2.52.1.3");
  if(e.is_article===true){need("article","UN3545 article-specific pathway not implemented");return end("unsupported","OP52-ARTICLE","2.2.52.3");}
  if(f.current_revision_attested!==true){need("current_formulation","Exact current chemistry and revision required");return end("indeterminate","OP52-FORMULATION","2.2.52.1.7");}
  if(f.changed_since_reference===true){need("reassessment","Changed composition or diluent invalidates prior determination");return end("authority_required","OP52-CHANGED","2.2.52.1.12","20.2.3");}
  if(f.composition_complete===true&&Array.isArray(f.peroxides)&&f.hydrogen_peroxide_mass_percent!==undefined){
    try{
      const h=dec(f.hydrogen_peroxide_mass_percent);let available=[0n,1n],concentrations=[0n,1n];
      if(!le(h,dec(100)))throw Error("H2O2 >100%");
      for(const p of f.peroxides){
        if(!Number.isSafeInteger(p.peroxygen_groups)||p.peroxygen_groups<1)throw Error("peroxygen group count");
        const c=dec(p.concentration_mass_percent),m=dec(p.molecular_mass_g_mol);
        if(!le(c,dec(100)))throw Error("peroxide concentration >100%");
        concentrations=sum(concentrations,c);
        available=sum(available,divide(mul(dec(16*p.peroxygen_groups),c),m));
      }
      if(!le(sum(concentrations,h),dec(100)))throw Error("mass balance >100%");
      r.available_oxygen_percent=Number((Number(available[0])/Number(available[1])).toFixed(10));
      const exempt=(le(h,dec(1))&&le(available,dec(1)))||(!le(h,dec(1))&&le(h,dec(7))&&le(available,dec("0.5")));
      if(exempt){
        if(e.route==="listed"&&e.listing&&e.listing.verified_formulation_match===true&&e.listing.exempt!==true){need("listing_conflict","Verified oxygen exception contradicts claimed dangerous listed formulation");return end("conflict","OP52-OXY-CONFLICT","2.2.52.1.5","2.2.52.4");}
        r.exclusions.push({class:"5.2",basis:"ADR 2.2.52.1.5 oxygen/H2O2 exemption",evidence_ids:r.evidence_refs});
        return end("excluded_from_class","OP52-OXY-EXEMPT","2.2.52.1.5");
      }
    }catch(err){need("composition","Malformed complete composition: "+err.message);return end("conflict","OP52-COMPOSITION","2.2.52.1.5");}
  }else if(e.route!=="listed"&&e.route!=="sample"){need("oxygen_data","Complete peroxide mass percentages, molecular masses, groups and hydrogen peroxide percentage missing");return end("indeterminate","OP52-OXY-MISSING","2.2.52.1.5");}
  if(f.desensitizer_review_complete!==true){need("desensitization","Complete compatibility and spillage evaluation missing");return end("indeterminate","OP52-DILUENT-REVIEW","2.2.52.1.10","2.2.52.1.14");}
  for(const d of f.desensitizers||[]){
    if(d.compatible!==true){need("compatibility","Incompatible or unverified diluent/solid");return end(d.compatible===false?"conflict":"indeterminate","OP52-COMPATIBILITY","2.2.52.1.14");}
    if(d.kind==="A"){if(!n(d.boiling_point_c)){need("A_BP","Type A boiling point missing");return end("indeterminate","OP52-A-MISSING","2.2.52.1.11");}if(d.boiling_point_c<150)return end("conflict","OP52-A-INVALID","2.2.52.1.11");}
    else if(d.kind==="B"){if(!n(d.boiling_point_c)||!n(d.flash_point_c)||!n(e.sadt_50kg_c)){need("B_diluent","Type B boiling point/flashpoint/50kg SADT missing");return end("indeterminate","OP52-B-MISSING","2.2.52.1.11");}if(!(d.boiling_point_c>=60&&d.boiling_point_c<150&&d.flash_point_c>=5&&d.boiling_point_c-e.sadt_50kg_c>=60))return end("conflict","OP52-B-INVALID","2.2.52.1.11");}
    else if(d.kind==="water"){if(e.route!=="sample"&&d.authorized_with_water!==true&&d.authorized_stable_dispersion!==true){need("water","Water desensitization needs listed/authorized wording");return end("authority_required","OP52-WATER","2.2.52.1.13");}}
    else if(d.kind==="other"){need("reassess_other_diluent","Different diluent requires acceptance reassessment");return end("authority_required","OP52-OTHER-DILUENT","2.2.52.1.12");}
    else if(d.kind!=="solid"){need("diluent_kind","Unsupported diluent");return end("unsupported","OP52-DILUENT-KIND","2.2.52.1.10");}
  }
  let type=null,listTemp=null;
  const listed=e.listing||{};
  if(e.route==="listed"){
    if(!["2.2.52.4","IBC520","T23"].includes(listed.source)||listed.verified_formulation_match!==true||listed.source_row_verified!==true||listed.conditions_verified!==true||listed.revision_matches_current!==true){need("official_listing","Exact currently approved formulation/packaging and source row required");return end("indeterminate","OP52-LISTING","2.2.52.1.7","2.2.52.4");}
    if(listed.exempt===true){r.exclusions.push({class:"5.2",basis:"Exact verified listed 'Exempt' formulation; note review pending",evidence_ids:r.evidence_refs});return end("excluded_from_class","OP52-LIST-EXEMPT","2.2.52.4");}
    type=listed.listed_type;listTemp=listed.temperature_control_required;
    if(!["A","B","C","D","E","F"].includes(type)||typeof listTemp!=="boolean"){need("listing_type","Listed type and temperature-control decision required");return end("indeterminate","OP52-LIST-TYPE","2.2.52.1.7");}
  }else if(e.route==="sample"){
    const s=e.sample||{};
    if(s.no_more_dangerous_than_type_b!==true||s.op2_verified!==true||!n(s.kg_per_transport_unit)||s.kg_per_transport_unit<0||s.kg_per_transport_unit>10||s.safe_control_and_phase_separation!==true){need("sample","Must meet all type C sample conditions including OP2 and <=10kg/transport unit");return end("indeterminate","OP52-SAMPLE-GATE","2.2.52.1.9");}
    type="C";
  }else if(e.route==="mixture"){
    const c=e.listed_components||[];
    if(e.all_component_formulations_verified!==true||!c.length||c.some(v=>!["A","B","C","D","E","F"].includes(v.type))){need("mixture_parts","Every component's type/formulation requires verification");return end("indeterminate","OP52-MIX-COMP","2.2.52.1.7");}
    type=c.map(v=>v.type).sort((a,b)=>"ABCDEF".indexOf(a)-"ABCDEF".indexOf(b))[0];
    if(!n(e.sadt_c)||e.sadt_measured_for_current_mixture!==true){need("mixture_sadt","Mixture SADT not determined for current mixture");return end("indeterminate","OP52-MIX-SADT","2.2.52.1.7","20.2.4");}
  }else if(e.route==="unlisted"){
    const p=e.type_evidence||{},t=p.tests||{};
    if(p.complete_for_this_formulation!==true||p.mtc_part_ii_verified!==true||p.provenance_verified!==true){need("A_H_report","Complete applicable MTC series A-H results/waivers required");return end("indeterminate","OP52-TEST-MISSING","20.4.3","21-28");}
    if(typeof t.packaged_detonation!=="boolean"||typeof t.packaged_rapid_deflagration!=="boolean"){need("package_tests","Actual package detonation/rapid-deflagration negative outcomes or waivers required");return end("indeterminate","OP52-PACKAGE-TESTS","20.4.3");}
    if(t.packaged_detonation||t.packaged_rapid_deflagration)type="A";
    else if(t.explosive_properties===true&&t.packaged_thermal_explosion===true)type="B";
    else if(t.explosive_properties===true&&t.packaged_thermal_explosion===false)type="C";
    else if((t.detonation==="partial"&&t.rapid_deflagration===false&&["none","low","medium"].includes(t.confinement_effect))||(t.detonation==="none"&&t.deflagration==="slow"&&["none","low","medium"].includes(t.confinement_effect))||(t.detonation==="none"&&t.deflagration==="none"&&t.confinement_effect==="medium"))type="D";
    else if(t.detonation==="none"&&t.deflagration==="none"&&["none","low"].includes(t.confinement_effect)){
      if(t.cavitated_detonation===false&&["none","low"].includes(t.explosive_power)){
        if(t.confinement_effect==="none"&&t.explosive_power==="none"){
          if(!n(e.sadt_50kg_c)){need("G_sadt","50kg SADT missing to determine F vs G");return end("indeterminate","OP52-G-SADT","20.4.3(g)");}
          if(e.physical_state==="liquid"&&e.is_liquid_mixture===true&&!n(e.g_liquid_diluent_bp_c)){need("G_diluent","Diluent BP missing for liquid mixture");return end("indeterminate","OP52-G-DILUENT","20.4.3(g)");}
          type=e.sadt_50kg_c>=60&&!(e.physical_state==="liquid"&&e.is_liquid_mixture===true&&e.g_liquid_diluent_bp_c<150)?"G":"F";
        }else type="F";
      }else type="E";
    }
    if(!type){need("type_tests","Incomplete/inconsistent A-G classification outcomes");return end("indeterminate","OP52-TYPE-UNRESOLVED","20.4.3");}
    if(e.claimed_type&&e.claimed_type!==type){need("type_conflict","Reported type differs from test-derived candidate");return end("conflict","OP52-TYPE-CONFLICT","20.4.3");}
  }else{need("route","Unknown decision route");return end("unsupported","OP52-ROUTE","2.2.52.1.7");}
  if(type==="A"){need("type_A","Type A forbidden for carriage under Class 5.2");return end("prohibited_for_carriage","OP52-A-PROHIBITED","2.2.52.2","20.4.3(a)");}
  if(type==="G"){r.exclusions.push({class:"5.2",basis:"Type G under MTC 20.4.3(g) is not subject to Class 5.2",evidence_ids:r.evidence_refs});return end("excluded_from_class","OP52-G-EXCLUDED","2.2.52.1.6","20.4.3(g)");}
  if(!["liquid","solid"].includes(e.physical_state)){need("physical_state","Liquid or solid as carried must be established");return end("indeterminate","OP52-STATE","2.2.52.1.7");}
  if(e.route==="listed"&&listed.listed_physical_state!==e.physical_state){need("listed_state","Offered state conflicts with listed state");return end("conflict","OP52-LIST-STATE","2.2.52.1.7");}
  let required;
  if(e.route==="listed"&&!n(e.sadt_c))required=listTemp;
  else{
    if(!n(e.sadt_c)||e.sadt_verified_as_offered!==true){need("package_sadt","Actual formulation/package SADT required");return end("indeterminate","OP52-SADT","2.2.52.1.15","7.1.7.3.6");}
    if(type==="D"&&!["medium","low","none"].includes(e.confinement_effect)){need("D_confinement","Type D medium/low/none E-series result required");return end("indeterminate","OP52-D-CONFINEMENT","2.2.52.1.15","25");}
    required=e.sadt_c<=((type==="B"||type==="C"||(type==="D"&&e.confinement_effect==="medium"))?50:45);
    if(e.route==="listed"&&required!==listTemp){need("temperature_conflict","SADT threshold contradicts listed temperature status");return end("conflict","OP52-TEMP-CONFLICT","2.2.52.1.15","2.2.52.1.16");}
  }
  let ctrl=null,emergency=null,basis="2.2.52.1.15";
  if(required){
    if(e.phase_separation_safe!==true){need("phase","Cannot confirm safe phase stability at carriage temperature");return end("indeterminate","OP52-PHASE","2.2.52.1.16","7.1.7.3.8");}
    if(e.route==="listed"&&n(listed.control_temperature_c)&&n(listed.emergency_temperature_c)){ctrl=listed.control_temperature_c;emergency=listed.emergency_temperature_c;basis="verified listed conditions";}
    else{
      if(!n(e.sadt_c)||!["single","ibc","tank"].includes(e.package_category)){need("temperature_inputs","Need SADT and actual receptacle category");return end("indeterminate","OP52-TEMP-DERIVATION","7.1.7.3.5");}
      if(e.package_category==="tank"){if(e.sadt_c>45){need("tank_table","Table for tanks only prescribes <=45 C SADT");return end("unsupported","OP52-TANK","7.1.7.3.5");}ctrl=e.sadt_c-10;emergency=e.sadt_c-5;}
      else if(e.sadt_c<=20){ctrl=e.sadt_c-20;emergency=e.sadt_c-10;}
      else if(e.sadt_c<=35){ctrl=e.sadt_c-15;emergency=e.sadt_c-10;}
      else{ctrl=e.sadt_c-10;emergency=e.sadt_c-5;}
      basis="7.1.7.3.5";
    }
  }
  r.temperature_control={required,control_temperature_c:ctrl,emergency_temperature_c:emergency,basis};
  const code=required?"P2":"P1";
  const un=(required?3111:3101)+2*"BCDEF".indexOf(type)+(e.physical_state==="solid"?1:0);
  r.primary_class_candidates=[{class:"5.2",classification_code:code,division:null,compatibility_group:null,packing_group:null,organic_peroxide_type:type,evidence_ids:r.evidence_refs,authority_decision_id:e.authority?.decision_id||null,status:"criteria_met"}];
  r.table_a_candidates=[{un_number:String(un),row_id:null,verified:false,final_assignment:false,packing_group_column_4:"blank_in_supplied_ADR_2025_Table_A",basis:"2.2.52.3 proposed generic entry"}];
  r.special_provision_outcomes=(type==="B"?["122","181","274"]:["122","274"]).map(code=>({code,status:"not_evaluated",evidence_ids:[]}));
  if(type==="B")r.subsidiary_risks.push({class:"1",status:"candidate_requires_table_a_integration",evidence_ids:r.evidence_refs});
  for(const h of e.other_transport_hazard_candidates||[])if(h&&h.class)r.subsidiary_risks.push({class:String(h.class),status:"candidate_requires_precedence",evidence_ids:h.evidence_ids||[]});
  r.clause_refs.push("2.2.52.1.15","2.2.52.3","3.2.1","7.1.7.3.5");
  if(e.route==="unlisted"||e.route==="mixture"){
    const a=e.authority||{};
    if(a.approved!==true||a.externally_verified!==true||a.current_formulation_covered!==true||a.conditions_documented!==true){r.expert_decisions.push({decision:"competent_authority_origin",status:"required",basis:"2.2.52.1.8"});return end("authority_required","OP52-AUTHORITY","2.2.52.1.8");}
    if(a.origin_non_adr===true&&a.first_adr_country_recognition_verified!==true){r.expert_decisions.push({decision:"first_adr_country_recognition",status:"required",basis:"2.2.52.1.8"});return end("authority_required","OP52-RECOGNITION","2.2.52.1.8");}
  }
  return end("criteria_met",e.route==="sample"?"OP52-SAMPLE-CANDIDATE":"OP52-CANDIDATE",e.route==="sample"?"2.2.52.1.9":"2.2.52.1.7");
}
module.exports={classify};
