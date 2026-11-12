"use strict";
/* ADR 2025 ECE/TRANS/352 Vol.I: PROVISIONAL Class 2 evaluator.
   No final UN, Table A row, packing group, or SDS Section 14 decision. */
function state() { return {missing:new Set(), blockers:[], trace:[], clauses:new Set(), flags:[], hazards:new Set(), override:null}; }
function clause(s,id,why) {s.clauses.add("ADR2025:"+id);if(why)s.trace.push({clause:id,decision:why});}
function read(d,k,unit,methods,s) {
  const x=(d.evidence||{})[k];if(x==null)return undefined;
  if(!x||typeof x!=="object"||!x.id||!x.method||!Object.hasOwn(x,"value")){s.blockers.push("invalid_evidence:"+k);return undefined;}
  if(x.unit!==unit){s.blockers.push("unit:"+k+":expected_"+unit);return undefined;}
  if(methods&&!methods.includes(x.method)){s.blockers.push("method:"+k+":"+x.method);return undefined;}
  if(x.method==="AUTHORITY_EQUIVALENT"&&!x.authority_reference){s.blockers.push("authority_reference_required:"+k);return undefined;}
  if(unit==="boolean"?typeof x.value!=="boolean":unit==="category"?typeof x.value!=="string":typeof x.value!=="number"||!Number.isFinite(x.value)){
    s.blockers.push("type:"+k);return undefined;
  }
  return x.value;
}
function need(s,...keys){keys.forEach(x=>s.missing.add("evidence."+x));}
function mixture(d,s,corrosiveOnly) {
  if(d.components===undefined)return undefined;
  if(!Array.isArray(d.components)||!d.components.length){s.blockers.push("components_required");return undefined;}
  let fsum=0,den=0;
  for(const [i,c] of d.components.entries()) {
    if(!c||!Number.isFinite(c.mole_fraction)||c.mole_fraction<0||c.mole_fraction>1||
       !Number.isFinite(c.toxicity_index_ppm)||c.toxicity_index_ppm<=0||!c.evidence_id||
       !["P200","SCIENTIFIC_LITERATURE","ANALOGUE","TEST"].includes(c.toxicity_index_source)){
      s.blockers.push("invalid_mixture_component:"+i);return undefined;
    }
    if(corrosiveOnly&&typeof c.corrosive!=="boolean"){s.blockers.push("missing_component_corrosivity:"+i);return undefined;}
    fsum+=c.mole_fraction;
    if(!corrosiveOnly||c.corrosive)den+=c.mole_fraction/c.toxicity_index_ppm;
  }
  if(Math.abs(fsum-1)>1e-6){s.blockers.push("mole_fraction_sum_not_one");return undefined;}
  return den===0?Infinity:1/den;
}
function gasDefinition(d,s){
  clause(s,"2.2.2.1.1","gas if pressure at 50 C >300 kPa OR fully gaseous at 20 C and 101.3 kPa");
  const p=read(d,"vapour_pressure_50_kpa","kPa",null,s);
  const v=read(d,"fully_gaseous_20c_101_3kpa","boolean",null,s);
  if(p!==undefined&&p<0)s.blockers.push("negative_pressure");
  if(p!==undefined&&p>300||v===true)return true;
  if(p!==undefined&&p<=300&&v===false)return false;
  if(p===undefined)need(s,"vapour_pressure_50_kpa");
  if(v===undefined)need(s,"fully_gaseous_20c_101_3kpa");
  return null;
}
function physical(d,s){
  clause(s,"2.2.2.1.2","Class 2 physical state at conditions of carriage");
  const f=d.form;
  if(f==="compressed"||f==="liquefied"){
    const t=read(d,"critical_temperature_c","degC",null,s);
    if(f==="compressed"){
      const g=read(d,"entirely_gaseous_at_minus50","boolean",null,s);
      if(g===true||(t!==undefined&&t<=-50&&g!==false))return {name:f,code_prefix:"1"};
      if(g===false)s.blockers.push("not_entirely_gaseous_at_minus50");
      else {
        if(t===undefined)need(s,"critical_temperature_c");
        need(s,"entirely_gaseous_at_minus50");
      }
      return null;
    }
    if(t===undefined){need(s,"critical_temperature_c");return null;}
    const part=read(d,"partially_liquid_above_minus50","boolean",null,s);
    if(part===undefined)need(s,"partially_liquid_above_minus50");
    if(t<=-50)s.blockers.push("liquefied_requires_temp_gt_minus50");
    if(part===false)s.blockers.push("not_partially_liquid");
    if(t<=-50||part!==true)return null;
    return {name:f,subtype:t<=65?"high_pressure":"low_pressure",code_prefix:"2"};
  }
  if(f==="refrigerated_liquefied"){
    const x=read(d,"partially_liquid_due_to_low_temperature","boolean",null,s);
    if(x===undefined)need(s,"partially_liquid_due_to_low_temperature");
    if(x===false)s.blockers.push("refrigerated_liquid_unsubstantiated");
    return x===true?{name:f,code_prefix:"3"}:null;
  }
  if(f==="dissolved"){
    const x=read(d,"dissolved_in_liquid_solvent_under_pressure","boolean",null,s);
    if(x===undefined)need(s,"dissolved_in_liquid_solvent_under_pressure");
    if(x===false)s.blockers.push("dissolved_unsubstantiated");
    if(!["1001","1043","2073","3318"].includes(String(d.preexisting_named_un||"")))s.blockers.push("dissolved_requires_permitted_named_entry");
    s.flags.push("SP642_UN1043_check");
    return x===true?{name:f,code_prefix:"4"}:null;
  }
  if(f==="adsorbed"){
    const a=read(d,"adsorbed_on_solid_porous_material","boolean",null,s);
    const p20=read(d,"internal_pressure_20_kpa","kPa",null,s);
    const p50=read(d,"internal_pressure_50_kpa","kPa",null,s);
    if(a===undefined)need(s,"adsorbed_on_solid_porous_material");
    if(p20===undefined)need(s,"internal_pressure_20_kpa");
    if(p50===undefined)need(s,"internal_pressure_50_kpa");
    if(a===false||p20!==undefined&&p20>=101.3||p50!==undefined&&p50>=300)s.blockers.push("adsorbed_category_limits_failed");
    return a===true&&p20<101.3&&p50<300?{name:f,code_prefix:"9"}:null;
  }
  if(f==="cartridge")return {name:f,code_prefix:null};
  s.blockers.push("unsupported_transport_form:"+String(f));
  return null;
}
function gasProperties(d,s){
  clause(s,"2.2.2.1.3","Class 2 T > F > O/A precedence and combinations");
  clause(s,"2.2.2.1.5","gas hazard criteria; test and calculation methods");
  const ISO=["ISO_10156_2017","AUTHORITY_EQUIVALENT"];
  const l=read(d,"lowest_ignitable_concentration_vol_pct","vol_pct",ISO,s);
  const w=read(d,"flammable_range_percentage_points","percentage_points",ISO,s);
  if(l!==undefined&&(l<0||l>100)||w!==undefined&&(w<0||w>100))s.blockers.push("invalid_flammability_percent");
  const F=l!==undefined&&l<=13||w!==undefined&&w>=12?true:l!==undefined&&w!==undefined?false:null;
  if(F===null){if(l===undefined)need(s,"lowest_ignitable_concentration_vol_pct");if(w===undefined)need(s,"flammable_range_percentage_points");}
  const ox=read(d,"oxidizing_power_pct","percent",ISO,s);
  if(ox!==undefined&&(ox<0||ox>100))s.blockers.push("invalid_oxidizing_percent");
  const O=ox===undefined?null:ox>23.5;
  if(O===null)need(s,"oxidizing_power_pct");
  const h=read(d,"known_toxic_to_humans","boolean",["HUMAN_EXPERIENCE","EVALUATED_LITERATURE"],s);
  const hc=read(d,"known_corrosive_to_humans","boolean",["HUMAN_EXPERIENCE","EVALUATED_LITERATURE"],s);
  const measured=read(d,"inhalation_lc50_ppm","ppm",["ADR_2.2.61.1","P200_MIXTURE_CALC"],s);
  const mix=d.components!==undefined?mixture(d,s,false):undefined;
  const LC=measured===undefined?mix:measured;
  if(LC!==undefined&&LC<=0)s.blockers.push("invalid_lc50");
  const T=h===true||hc===true||LC!==undefined&&LC<=5000?true:h===false&&hc===false&&LC!==undefined&&LC>5000?false:null;
  if(T===null){if(h===undefined)need(s,"known_toxic_to_humans");if(hc===undefined)need(s,"known_corrosive_to_humans");if(LC===undefined)need(s,"inhalation_lc50_ppm_or_components");}
  const humanC=read(d,"human_skin_eye_mucosal_destruction","boolean",["HUMAN_EXPERIENCE","EVALUATED_LITERATURE"],s);
  const sole=read(d,"toxic_solely_due_to_corrosivity","boolean",["HUMAN_EXPERIENCE","EVALUATED_LITERATURE"],s);
  const mixC=d.components!==undefined?mixture(d,s,true):undefined;
  const C=humanC===true||sole===true&&T===true||mixC!==undefined&&mixC<=5000?true:
    humanC===false&&sole===false&&(d.components===undefined||mixC>5000)?false:null;
  if(C===null){if(humanC===undefined)need(s,"human_skin_eye_mucosal_destruction");if(sole===undefined)need(s,"toxic_solely_due_to_corrosivity");}
  if(C===true&&T===false)s.blockers.push("corrosive_gas_requires_toxic_group");
  let group=null;
  const A=read(d,"dilutes_or_replaces_atmospheric_oxygen","boolean",["PHYSICAL_ASSESSMENT","EVALUATED_LITERATURE"],s);
  if([F,O,T,C].every(x=>x!==null)&&!(C&&T===false)){
    if(T)group=F?(C?"TFC":"TF"):O?(C?"TOC":"TO"):(C?"TC":"T");
    else if(F)group="F";
    else if(O)group="O";
    else if(A===true)group="A";
    else if(A===false)s.blockers.push("no_asphyxiant_or_other_hazard_group");
    else need(s,"dilutes_or_replaces_atmospheric_oxygen");
  }
  for(const [k,v] of Object.entries({flammable:F,oxidizing:O,toxic:T,corrosive:C,asphyxiant:A}))if(v===true)s.hazards.add(k);
  if(group)clause(s,"2.2.2.1.3","group candidate "+group);
  return {group,lc50:LC};
}
function restrictions(d,s){
  clause(s,"2.2.2.2.1","unstable gases and precautions/P200(10)(r)");
  const u=read(d,"chemically_unstable","boolean",["STABILITY_ASSESSMENT","EVALUATED_LITERATURE"],s);
  if(u===undefined)need(s,"chemically_unstable");
  if(u===true){
    const p=read(d,"decomposition_precautions_satisfactory","boolean",["DOCUMENTED_PACKING_CONTROL","COMPETENT_AUTHORITY"],s);
    const r=read(d,"p200_10_r_applicable_and_satisfied","boolean",["P200_RECORD","COMPETENT_AUTHORITY"],s);
    if(p!==true&&r!==true){
      if(p===false&&r===false)s.override="not_accepted_for_carriage";
      else{if(p===undefined)need(s,"decomposition_precautions_satisfactory");if(r===undefined)need(s,"p200_10_r_applicable_and_satisfied");}
    }
    s.flags.push("SP386_P200_10_r_review");
  }
  if(["2186","2421","2455"].includes(String(d.preexisting_named_un||""))){
    clause(s,"2.2.2.2.2","explicit excluded named gas");
    s.override="not_accepted_for_carriage";
  }
}
function pressurized(d,s,chemical) {
  clause(s,chemical?"2.2.2.1.7":"2.2.2.1.6","entry-specific composition and group rules");
  const t=read(d,"propellant_toxic_gas","boolean",["ADR_CLASS2_ASSESSMENT"],s);
  const py=read(d,"propellant_pyrophoric_P200","boolean",["P200_TABLE2_NOTE_C"],s);
  const ox=chemical?read(d,"propellant_oxidizing_gas","boolean",["ISO_10156_2017"],s):false;
  const tp=read(d,"contents_nonpropellant_toxic_pg","category",["ADR_CLASS61_ASSESSMENT"],s);
  const cp=read(d,"contents_nonpropellant_corrosive_pg","category",["ADR_CLASS8_ASSESSMENT"],s);
  if(t===undefined)need(s,"propellant_toxic_gas");
  if(py===undefined)need(s,"propellant_pyrophoric_P200");
  if(chemical&&ox===undefined)need(s,"propellant_oxidizing_gas");
  if(tp===undefined)need(s,"contents_nonpropellant_toxic_pg");
  if(cp===undefined)need(s,"contents_nonpropellant_corrosive_pg");
  if(tp!==undefined&&!["none","I","II","III"].includes(tp))s.blockers.push("invalid_toxic_content_pg");
  if(cp!==undefined&&!["none","I","II","III"].includes(cp))s.blockers.push("invalid_corrosive_content_pg");
  if(t===true||py===true||ox===true||tp==="I"||cp==="I"||
    chemical&&["II","III"].includes(tp)&&["II","III"].includes(cp)){
    s.override="not_accepted_for_carriage";
    clause(s,chemical?"2.2.2.1.7 Notes 1-3":"2.2.2.2.2","entry route not accepted");
  }
  const T=tp==="II"||tp==="III", C=cp==="II"||cp==="III";
  let F=null,O=false;
  if(chemical){
    F=read(d,"contents_eligible_flam_form","boolean",["CLASS2_2.2.2.1.7b_EVALUATION"],s);
    if(F===undefined)need(s,"contents_eligible_flam_form");
    const prohibited=read(d,"prohibited_other_class_component","boolean",["COMPONENT_TRANSPORT_ASSESSMENT"],s);
    if(prohibited===undefined)need(s,"prohibited_other_class_component");
    if(prohibited===true)s.override="not_accepted_for_carriage";
  }else{
    O=read(d,"aerosol_contains_oxidizing_gas","boolean",["ISO_10156_2017"],s);
    if(O===undefined)need(s,"aerosol_contains_oxidizing_gas");
    const mass=read(d,"aerosol_flammable_mass_pct","mass_pct",["COMPOSITION_ASSESSMENT"],s);
    const heat=read(d,"aerosol_heat_combustion_kj_g","kJ/g",["ASTM_D240","ISO_FDIS_13943_1999","NFPA_30B"],s);
    if(mass===undefined)need(s,"aerosol_flammable_mass_pct");
    if(heat===undefined)need(s,"aerosol_heat_combustion_kj_g");
    if(mass!==undefined&&(mass<0||mass>100)||heat!==undefined&&heat<0)s.blockers.push("invalid_aerosol_mass_or_heat");
    if(mass!==undefined&&heat!==undefined){
      if(mass>=85&&heat>=30)F=true;
      else if(mass<=1&&heat<20)F=false;
    }
    if(F===null){
      const mtc=read(d,"mtc31_aerosol_result","category",["MTC_REV8_SECTION31"],s);
      if(mtc==="flammable"||mtc==="extremely_flammable")F=true;
      else if(mtc==="non_flammable")F=false;
      else if(mtc===undefined)need(s,"mtc31_aerosol_result");
      else s.blockers.push("unrecognized_mtc31_result");
      s.flags.push("MTC_Rev8_Amend1_section31_reconciliation");
    }
  }
  for(const [k,v] of Object.entries({flammable:F,oxidizing:O,toxic:T,corrosive:C}))if(v===true)s.hazards.add(k);
  if(F===null||F===undefined||O===undefined||tp===undefined||cp===undefined)return null;
  if(chemical){
    if(!F&&!T&&!C)return "A";
    if(F&&!T&&!C)return "F";
    if(!F&&T&&!C)return "T";
    if(!F&&!T&&C)return "C";
    if(F&&!T&&C)return "FC";
    if(F&&T&&!C)return "TF";
  }else{
    const combos={"0000":"A","1000":"F","0100":"O","0010":"T","0001":"C",
      "0101":"CO","1001":"FC","1010":"TF","0011":"TC","0110":"TO","1011":"TFC","0111":"TOC"};
    const k=[F,O,T,C].map(x=>x?"1":"0").join("");
    if(combos[k])return combos[k];
  }
  s.blockers.push("unlisted_property_combination_requires_review");
  return null;
}
function evaluateClass2(data) {
  const d=data&&typeof data==="object"?data:{},s=state();
  let form=null,group=null,lc50=null;
  if(d.route==="gas"||d.route==="cartridge"){
    const gas=gasDefinition(d,s);
    if(gas===false)s.override="outside_class2_gas_definition_not_non_dg";
    if(gas===true){
      form=physical({...d,form:d.route==="cartridge"?"cartridge":d.form},s);
      restrictions(d,s);
      const hz=gasProperties(d,s);group=hz.group;lc50=hz.lc50;
      if(d.route==="cartridge"){
        clause(s,"2.2.2.2.2","small gas receptacle LC50 <200 ppm and pyrophoric prohibition");
        const py=read(d,"propellant_pyrophoric_P200","boolean",["P200_TABLE2_NOTE_C"],s);
        if(py===undefined)need(s,"propellant_pyrophoric_P200");
        if(lc50===undefined)need(s,"inhalation_lc50_ppm_or_components");
        if(py===true||lc50!==null&&lc50!==undefined&&lc50<200)s.override="not_accepted_for_carriage";
        s.flags.push("UN2037_named_row_check");
      }
      if(d.form==="refrigerated_liquefied"&&group&&!["A","O","F"].includes(group)){
        s.override="not_accepted_for_carriage";clause(s,"2.2.2.2.2","refrigerated liquid limited to 3A/3O/3F");
      }
    }
  }else if(d.route==="aerosol"||d.route==="chemical_under_pressure"){
    const chemical=d.route==="chemical_under_pressure";
    group=pressurized(d,s,chemical);
    form={name:d.route,code_prefix:null};
    s.flags.push(chemical?"UN3500_3505_Table_A_gate":"UN1950_Table_A_gate");
  }else if(d.route==="article"||d.route==="gas_sample"){
    clause(s,"2.2.2.1.2","special article/sample routes");
    s.blockers.push("article_or_sample_entry_not_implemented");
  }else s.blockers.push("unsupported_route");
  if(String(d.preexisting_named_un||"")==="1052"){
    s.override="outside_class2_special_named_exception";
    clause(s,"2.2.2.1.1 Note 1","UN1052 anhydrous hydrogen fluoride belongs to Class 8");
  }
  if(d.preexisting_named_un)s.flags.push("Table_A_named_entry_verification_required");
  let status=s.override|| (s.blockers.length?"blocked_unsupported":s.missing.size||!form||!group?"blocked_missing_evidence":"class2_group_candidate");
  return {module:"adr2025_class2",edition:"ADR2025 ECE/TRANS/352 Vol.I English",
    review_status:"PROVISIONAL",status,route:d.route||null,physical_form:form,
    hazard_group_candidate:group,classification_code_candidate:status==="class2_group_candidate"&&form.code_prefix?form.code_prefix+group:null,
    hazard_candidates:[...s.hazards].sort(),division_hint:group?(group.includes("T")?"2.3":group.includes("F")?"2.1":"2.2"):null,
    packing_group:null,un_number:null,table_a_row_id:null,special_provisions_resolved:false,
    missing_evidence:[...s.missing].sort(),blockers:s.blockers,exceptions:s.flags,decision_trace:s.trace,
    regulatory_references:[...s.clauses].sort(),requires_independent_review:true,final_sds_section14_permitted:false};
}
module.exports={evaluateClass2,mixture};
