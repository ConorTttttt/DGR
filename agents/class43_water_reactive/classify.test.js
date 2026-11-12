'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {evaluateClass43}=require('./classify');
const fixture=()=>({
 sample_id:'SYN-43',test_report:{document_id:'SYNTHETIC-ONLY',locator:'synthetic://N5',
 sha256:'a'.repeat(64),issuer:'SYNTHETIC',sample_id:'SYN-43'},
 material:{kind:'substance',form:'liquid',pyrophoric:'no',organometallic:'no'},
 test:{method:'MTC_REV8_N5',sample_commercial_form:true,temperature_c:20,atmospheric_pressure:true,
 distilled_water:true,atmosphere:'air',preliminary:[
 {stage:'trough',gas_evolved:'no',spontaneous_gas_ignition:'no'},
 {stage:'filter_paper',gas_evolved:'no',spontaneous_gas_ignition:'no'},
 {stage:'pile',gas_evolved:'yes',spontaneous_gas_ignition:'no'}],
 terminal:{gas_flammability:'flammable',reactivity_behavior:'slowly',pg_I_absence_documented:true,
 pg_II_absence_documented:true,runs:Array.from({length:3},()=>({
 sample_mass_g:'10',gas_volume_ml:'150',observed_hours:'7',trend_at_7h:'steady',
 hourly_rates_l_kg_h:Array(7).fill('1.01'),one_minute_volumes_l_kg:['0.001']}))}}
});
const cases=[
 ['PG III >1',()=>{},'criteria_met','III'],
 ['exact 1 negative',x=>x.test.terminal.runs.forEach(r=>r.hourly_rates_l_kg_h.fill('1')),'criteria_not_met'],
 ['below 1 negative',x=>x.test.terminal.runs.forEach(r=>r.hourly_rates_l_kg_h.fill('0.9999')),'criteria_not_met'],
 ['tiny decimal above 1',x=>x.test.terminal.runs.forEach(r=>r.hourly_rates_l_kg_h.fill('1.00000000000000000001')),'criteria_met','III'],
 ['PG II exactly 20',x=>{x.test.terminal.reactivity_behavior='readily';x.test.terminal.runs[0].hourly_rates_l_kg_h[2]='20'},'criteria_met','II'],
 ['below 20 PG III',x=>x.test.terminal.runs[0].hourly_rates_l_kg_h[2]='19.9999999999999999999','criteria_met','III'],
 ['PG I exactly 10 per minute',x=>x.test.terminal.runs[2].one_minute_volumes_l_kg=['10'],'criteria_met','I'],
 ['minute just below 10',x=>x.test.terminal.runs[2].one_minute_volumes_l_kg=['9.9999999999999999999'],'criteria_met','III'],
 ['missing report',x=>delete x.test_report,'indeterminate',null,'reference_unverified'],
 ['conflicting source',x=>x.conflicting_evidence=true,'indeterminate',null,'conflicting'],
 ['pyrophoric test forbidden by ADR',x=>x.material.pyrophoric='yes','indeterminate',null,'method_invalid'],
 ['unknown pyrophoric',x=>x.material.pyrophoric='unknown','indeterminate',null,'missing'],
 ['nitrogen method conflict',x=>x.test.atmosphere='nitrogen','indeterminate',null,'method_invalid'],
 ['unknown gas flammability',x=>x.test.terminal.gas_flammability='unknown','indeterminate',null,'missing'],
 ['wrong test temperature',x=>x.test.temperature_c=25,'indeterminate',null,'method_invalid'],
 ['missing repeat',x=>x.test.terminal.runs.pop(),'indeterminate',null,'missing'],
 ['invalid sample 25+ grams',x=>x.test.terminal.runs[0].sample_mass_g='25.0000000000001','indeterminate',null,'method_invalid'],
 ['valid exactly 25g',x=>x.test.terminal.runs[0].sample_mass_g='25','criteria_met','III'],
 ['gas volume 100ml inclusive',x=>x.test.terminal.runs[0].gas_volume_ml='100','criteria_met','III'],
 ['gas volume below 100ml',x=>x.test.terminal.runs[0].gas_volume_ml='99.9999999999999','indeterminate',null,'method_invalid'],
 ['gas volume 250ml inclusive',x=>x.test.terminal.runs[0].gas_volume_ml='250','criteria_met','III'],
 ['gas volume above 250ml',x=>x.test.terminal.runs[0].gas_volume_ml='250.00000000001','indeterminate',null,'method_invalid'],
 ['solid exactly 1 percent fines',x=>{x.material.form='solid';x.test.fines_under_500um_mass_percent='1';x.test.friable=false},'criteria_met','III'],
 ['solid just over 1 percent unground',x=>{x.material.form='solid';x.test.fines_under_500um_mass_percent='1.0000000000000000001';x.test.friable=false},'indeterminate',null,'method_invalid'],
 ['solid friable unground',x=>{x.material.form='solid';x.test.fines_under_500um_mass_percent='0';x.test.friable=true},'indeterminate',null,'method_invalid'],
 ['solid ground valid',x=>{x.material.form='solid';x.test.fines_under_500um_mass_percent='2';x.test.friable=false;x.test.ground_before_terminal=true},'criteria_met','III'],
 ['solid missing preparation',x=>x.material.form='solid','indeterminate',null,'missing'],
 ['erratic 7h no extension',x=>x.test.terminal.runs[0].trend_at_7h='erratic','indeterminate',null,'method_invalid'],
 ['erratic 120h extended',x=>{x.test.terminal.runs[0].trend_at_7h='erratic';x.test.terminal.runs[0].observed_hours='120'},'criteria_met','III'],
 ['unknown mixture extrapolation',x=>x.material.kind='mixture','indeterminate',null,'other'],
 ['actual commercial mixture',x=>{x.material.kind='mixture';x.material.whole_mixture_tested=true;x.material.commercial_mixture_confirmed=true},'criteria_met','III'],
 ['article out of N5 scope',x=>x.material.kind='article','indeterminate',null,'other'],
 ['organometallic flowchart',x=>x.material.organometallic='yes','indeterminate',null,'other'],
 ['PG II absent I not documented',x=>{x.test.terminal.reactivity_behavior='readily';x.test.terminal.pg_I_absence_documented=false;x.test.terminal.runs[0].hourly_rates_l_kg_h[1]='20'},'criteria_met',null,'missing'],
 ['PG III absent II not documented',x=>x.test.terminal.pg_II_absence_documented=false,'criteria_met',null,'missing'],
 ['no gas, no volume negative',x=>{x.test.terminal.gas_flammability='no_gas';x.test.terminal.runs.forEach(r=>{r.gas_volume_ml='0';r.hourly_rates_l_kg_h.fill('0');r.one_minute_volumes_l_kg=['0']})},'criteria_not_met'],
 ['no gas contradicts measured volume',x=>{x.test.terminal.gas_flammability='no_gas';x.test.terminal.runs.forEach(r=>r.hourly_rates_l_kg_h.fill('0'))},'indeterminate',null,'conflicting'],
 ['confirmed nonflammable gas',x=>x.test.terminal.gas_flammability='nonflammable','criteria_not_met'],
 ['spontaneous gas ignition class positive',x=>{x.test.preliminary=[{stage:'trough',gas_evolved:'yes',spontaneous_gas_ignition:'yes'}];delete x.test.terminal},'criteria_met',null,'missing'],
 ['spontaneous gas ignition vigorous PG I',x=>{x.test.preliminary=[{stage:'trough',gas_evolved:'yes',spontaneous_gas_ignition:'yes'}];x.test.reacts_vigorously_at_ambient=true;x.test.general_spontaneous_ignition_tendency=true;delete x.test.terminal},'criteria_met','I'],
 ['known nonviolent skips preliminary',x=>{x.test.preliminary=[];x.test.skip_preliminary=true;x.test.known_not_violent_documented=true},'criteria_met','III'],
 ['undocumented preliminary skip blocked',x=>{x.test.preliminary=[];x.test.skip_preliminary=true},'indeterminate',null,'method_invalid']
];
for(const [name,mutate,status,candidate=null,reason=null] of cases) test(name,()=>{
 const i=fixture();mutate(i);const o=evaluateClass43(i);
 assert.equal(o.criteria_status,status);
 assert.deepEqual(o.packing_group_candidates.map(c=>c.value),candidate?[candidate]:[]);
 if(reason)assert.ok(o.unresolved_evidence.some(e=>e.reason===reason),JSON.stringify(o.unresolved_evidence));
 assert.equal(o.hazard_class,'4.3');
 assert.equal(Object.hasOwn(o,'un_number'),false);
 assert.equal(Object.hasOwn(o,'final_packing_group'),false);
});
test('oxidizing water-reactive solid prohibition referred; no automatic UN number',()=>{
 const i=fixture();i.material.form='solid';i.test.fines_under_500um_mass_percent='0';i.test.friable=false;
 i.other_class_findings=[{hazard_class:'5.1',status:'criteria_met',evidence_id:'synthetic-oxidizer'}];
 const o=evaluateClass43(i);
 assert.equal(o.criteria_status,'criteria_met');
 assert.ok(o.subsidiary_risk_candidates.some(c=>c.hazard_class==='5.1'));
 assert.ok(o.unresolved_evidence.some(e=>e.field_id==='carriage_acceptance'));
 assert.equal(Object.hasOwn(o,'un_number'),false);
});
