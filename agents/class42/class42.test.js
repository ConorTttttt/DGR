"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {evaluateClass42:evaluate}=require("./class42.js");

function base(pathway="self_heating", physical_state="solid",test_method="N.4",sample_form="powder"){
 return {assessment_id:"case",evidence_id:"e",report_id:"report",sample_id:"sample",pathway,
 physical_state,test_method,sample_form,shipment_formulation_verified:true,is_mixture:false,
 protocol_conformant:true,report_scope_verified:true};
}
const solid=()=>({...base("pyrophoric_solid","solid","N.2","powdery"),trials:Array.from({length:6},negativeSolid)});
const liquid=()=>({...base("pyrophoric_liquid","liquid","N.3"),carrier_trials:Array.from({length:6},negativeCarrier),filter_trials:Array.from({length:3},negativeFilter)});
const heat=()=>({...base(),runs:[run(100,140,true),run(25,140,false)],package_volume_l:450});
function negativeSolid(){return {quantity_ml:1.5,drop_about_1m_verified:true,noncombustible_surface_verified:true,ignites_during_fall:false,ignition_seconds:null,observed_full_5min:true};}
function negativeCarrier(){return {inert_carrier_verified:true,ignition_seconds:null,observed_full_5min:true};}
function negativeFilter(){return {ignition_seconds:null,charring_seconds:null,temperature_c:25,humidity_pct:50,fresh_dry_indented_whatman3_verified:true,observed_full_5min:true};}
function run(cube_mm,setpoint_c,positive){return {cube_mm,setpoint_c,oven_actual_c:setpoint_c,
 spontaneous_ignition:false,max_sample_c:setpoint_c+(positive?61:60),
 continuous_record_verified:true,event_within_24h:positive,observed_full_24h:!positive};}
function check(name,input,status,pg){
 test(name,()=>{
  const a=evaluate(input);
  assert.equal(a.status,status);
  assert.equal(a.packing_group_candidates[0]?.value,pg);
  assert.equal(a.final_un_number,null);
  assert.equal(a.final_packing_group,null);
  assert.equal(a.assignment_permitted,false);
  assert.equal(a.requires_independent_review,true);
  assert.equal(a.class,"4.2");
  if(["indeterminate","conflict","unsupported","authority_required"].includes(status))
    assert.ok(a.unresolved_evidence.some(x=>x.blocks_assignment));
 });
}
// N.2, strict/closed 300-second boundary, six replicates, evidence quality
check("N2 six negatives",solid(),"criteria_not_met");
check("N2 ignition during fall",{...solid(),trials:[{...negativeSolid(),ignites_during_fall:true}]},"criteria_met","I");
check("N2 exactly 300 seconds",{...solid(),trials:[{...negativeSolid(),ignition_seconds:300}]},"criteria_met","I");
check("N2 just over 300 seconds",{...solid(),trials:Array.from({length:6},()=>({...negativeSolid(),ignition_seconds:300.001}))},"criteria_not_met");
check("N2 five negatives insufficient",{...solid(),trials:Array.from({length:5},negativeSolid)},"indeterminate");
check("N2 1 ml valid",{...solid(),trials:[{...negativeSolid(),quantity_ml:1,ignition_seconds:100}]},"criteria_met","I");
check("N2 2 ml valid",{...solid(),trials:[{...negativeSolid(),quantity_ml:2,ignition_seconds:100}]},"criteria_met","I");
check("N2 below 1 ml blocked",{...solid(),trials:[{...negativeSolid(),quantity_ml:0.99,ignition_seconds:100}]},"indeterminate");
check("N2 beyond 2 ml blocked",{...solid(),trials:[{...negativeSolid(),quantity_ml:2.01,ignition_seconds:100}]},"indeterminate");
check("N2 unsupported solid form",{...solid(),sample_form:"lump"},"unsupported");

// N.3, two-stage negative closure and positive-by-charring
check("N3 both stages negative",liquid(),"criteria_not_met");
check("N3 first carrier ignites at 300 s",{...liquid(),carrier_trials:[{...negativeCarrier(),ignition_seconds:300}],filter_trials:[]},"criteria_met","I");
check("N3 carrier positive after 300 is negative",{...liquid(),carrier_trials:Array.from({length:6},()=>({...negativeCarrier(),ignition_seconds:300.001}))},"criteria_not_met");
check("N3 filter chars exactly 300 s",{...liquid(),filter_trials:[{...negativeFilter(),charring_seconds:300}]},"criteria_met","I");
check("N3 three filter negatives needed",{...liquid(),filter_trials:Array.from({length:2},negativeFilter)},"indeterminate");
check("N3 six carrier negatives needed",{...liquid(),carrier_trials:Array.from({length:5},negativeCarrier)},"indeterminate");
check("N3 lower temp 23 valid",{...liquid(),filter_trials:[{...negativeFilter(),temperature_c:23,charring_seconds:1}]},"criteria_met","I");
check("N3 upper temp 27 valid",{...liquid(),filter_trials:[{...negativeFilter(),temperature_c:27,charring_seconds:1}]},"criteria_met","I");
check("N3 temperature outside tolerance",{...liquid(),filter_trials:[{...negativeFilter(),temperature_c:27.001,charring_seconds:1}]},"indeterminate");
check("N3 lower RH 45 valid",{...liquid(),filter_trials:[{...negativeFilter(),humidity_pct:45,charring_seconds:1}]},"criteria_met","I");
check("N3 upper RH 55 valid",{...liquid(),filter_trials:[{...negativeFilter(),humidity_pct:55,charring_seconds:1}]},"criteria_met","I");
check("N3 humidity outside tolerance",{...liquid(),filter_trials:[{...negativeFilter(),humidity_pct:44.999,charring_seconds:1}]},"indeterminate");
check("N3 filter stage after carrier positive blocked",{...liquid(),carrier_trials:[{...negativeCarrier(),ignition_seconds:1}]},"conflict");

// N.4 140/120/100, 200/180/160 °C strict thresholds; 450 and 3000 L inclusive
check("N4 25 mm at 140 positive PGII",{...heat(),runs:[run(25,140,true)]},"criteria_met","II");
check("N4 25 mm exact 200 negative",{...heat(),runs:[run(100,140,true),run(25,140,false)],package_volume_l:400},"indeterminate");
check("N4 100 mm exactly 200 negative",{...heat(),runs:[run(100,140,false)]},"criteria_not_met");
check("N4 100 mm over 200 positive",{...heat(),runs:[run(100,140,true),run(25,140,false)],package_volume_l:3000.01},"criteria_met","III");
check("N4 <=450L negative 100C threshold 160",{...heat(),runs:[...heat().runs,run(100,100,false)]},"excluded_from_class");
check("N4 <=450L positive 100C >160",{...heat(),runs:[...heat().runs,run(100,100,true)]},"criteria_met","III");
check("N4 450L positive 120C and negative 100C exempt",{...heat(),runs:[...heat().runs,run(100,120,true),run(100,100,false)]},"excluded_from_class");
check("N4 450.001L needs 120C",{...heat(),package_volume_l:450.001},"indeterminate");
check("N4 >450L negative 120C threshold 180",{...heat(),package_volume_l:450.001,runs:[...heat().runs,run(100,120,false)]},"excluded_from_class");
check("N4 >450L positive 120C >180",{...heat(),package_volume_l:450.001,runs:[...heat().runs,run(100,120,true)]},"criteria_met","III");
check("N4 3000L negative 120C exempt",{...heat(),package_volume_l:3000,runs:[...heat().runs,run(100,120,false)]},"excluded_from_class");
check("N4 3000.001L PGIII without low-temp test",{...heat(),package_volume_l:3000.001},"criteria_met","III");
check("N4 missing package volume",{...heat(),package_volume_l:undefined},"indeterminate");
check("N4 140C oven 142C valid",{...heat(),runs:[run(100,140,false),{...run(25,140,false),oven_actual_c:142,max_sample_c:202}]},"indeterminate");
check("N4 140C oven >142 rejected",{...heat(),runs:[{...run(100,140,true),oven_actual_c:142.001}]},"indeterminate");
check("N4 nominal/actual temperature conflict",{...heat(),runs:[{...run(100,140,false),oven_actual_c:139,max_sample_c:200}]},"conflict");
check("N4 duplicated contradictory runs",{...heat(),runs:[run(100,140,true),run(100,140,false)]},"conflict");
check("N4 contradictory cube sizes",{...heat(),runs:[run(100,140,false),run(25,140,true)]},"conflict");
check("N4 missing continuous recorder",{...heat(),runs:[{...run(100,140,false),continuous_record_verified:false}]},"indeterminate");

// Gatekeeping and cross-class referrals
check("No CLP shortcut",{...solid(),test_method:"CLP_GHS"},"indeterminate");
check("Invalid physical state",{...liquid(),physical_state:"solid"},"conflict");
check("Mixture composition required",{...solid(),is_mixture:true},"indeterminate");
check("Mixture verified",{...solid(),is_mixture:true,mixture_composition_verified:true},"criteria_not_met");
check("Nonrepresentative formulation",{...solid(),shipment_formulation_verified:false},"unsupported");
check("Missing report attestation",{...solid(),report_scope_verified:false},"indeterminate");
check("Conflicting reports",{...solid(),conflicting_reports:true},"conflict");
check("Named entry not verified",{...solid(),named_entry_un:"3255"},"indeterminate");
check("UN 3255 confirmed is prohibited",{...solid(),named_entry_un:"3255",named_entry_verified:true},"prohibited_for_carriage");
check("UN 3127 confirmed prohibited unless Class1",{...heat(),named_entry_un:"3127",named_entry_verified:true,oxidizing_confirmed:true,class1_requirements_met:false},"prohibited_for_carriage");
check("UN 3127 Class1 exemption referred",{...heat(),named_entry_un:"3127",named_entry_verified:true,oxidizing_confirmed:true,class1_requirements_met:true},"authority_required");
check("Negative N2 cannot override named entry",{...solid(),named_entry_un:"0001",named_entry_verified:true},"indeterminate");
check("Severe experience cannot override N2 negative",{...solid(),more_severe_experience:true},"conflict");
check("Orgmet referral does not invent UN",{...solid(),organometallic:true,trials:[{...negativeSolid(),ignites_during_fall:true}]},"criteria_met","I");
check("Verified Class 4.3 candidate referred",{...solid(),competing_evidence:[{class:"4.3",evidence_id:"N5",verified:true}],trials:[{...negativeSolid(),ignites_during_fall:true}]},"criteria_met","I");
check("Unverified Class 4.3 candidate blocked",{...solid(),competing_evidence:[{class:"4.3",evidence_id:"N5",verified:false}]},"indeterminate");
check("Article N4 not automated",{...heat(),is_article:true},"unsupported");
