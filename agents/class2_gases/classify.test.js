"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {evaluateClass2,mixture}=require("./classify");
const e=(value,unit,method="MEASURED")=>({value,unit,method,id:"SYNTHETIC_EVIDENCE"});
function gas(){
 return {route:"gas",form:"compressed",evidence:{
 vapour_pressure_50_kpa:e(301,"kPa"),fully_gaseous_20c_101_3kpa:e(true,"boolean"),
 critical_temperature_c:e(-50,"degC"),
 lowest_ignitable_concentration_vol_pct:e(13,"vol_pct","ISO_10156_2017"),
 flammable_range_percentage_points:e(11,"percentage_points","ISO_10156_2017"),
 oxidizing_power_pct:e(23.5,"percent","ISO_10156_2017"),
 known_toxic_to_humans:e(false,"boolean","EVALUATED_LITERATURE"),
 known_corrosive_to_humans:e(false,"boolean","EVALUATED_LITERATURE"),
 inhalation_lc50_ppm:e(5001,"ppm","ADR_2.2.61.1"),
 human_skin_eye_mucosal_destruction:e(false,"boolean","EVALUATED_LITERATURE"),
 toxic_solely_due_to_corrosivity:e(false,"boolean","EVALUATED_LITERATURE"),
 chemically_unstable:e(false,"boolean","STABILITY_ASSESSMENT")
 }};
}
function aerosol(){
 return {route:"aerosol",evidence:{
 propellant_toxic_gas:e(false,"boolean","ADR_CLASS2_ASSESSMENT"),
 propellant_pyrophoric_P200:e(false,"boolean","P200_TABLE2_NOTE_C"),
 contents_nonpropellant_toxic_pg:e("none","category","ADR_CLASS61_ASSESSMENT"),
 contents_nonpropellant_corrosive_pg:e("none","category","ADR_CLASS8_ASSESSMENT"),
 aerosol_contains_oxidizing_gas:e(false,"boolean","ISO_10156_2017"),
 aerosol_flammable_mass_pct:e(85,"mass_pct","COMPOSITION_ASSESSMENT"),
 aerosol_heat_combustion_kj_g:e(30,"kJ/g","ASTM_D240")
 }};
}
function chemical(){
 return {route:"chemical_under_pressure",evidence:{
 in_aerosol_dispenser:e(false,"boolean","PACKAGING_RECORD"),
 propellant_toxic_gas:e(false,"boolean","ADR_CLASS2_ASSESSMENT"),
 propellant_pyrophoric_P200:e(false,"boolean","P200_TABLE2_NOTE_C"),
 propellant_oxidizing_gas:e(false,"boolean","ISO_10156_2017"),
 contents_nonpropellant_toxic_pg:e("none","category","ADR_CLASS61_ASSESSMENT"),
 contents_nonpropellant_corrosive_pg:e("none","category","ADR_CLASS8_ASSESSMENT"),
 contents_eligible_flam_form:e(false,"boolean","CLASS2_2.2.2.1.7b_EVALUATION"),
 prohibited_other_class_component:e(false,"boolean","COMPONENT_TRANSPORT_ASSESSMENT")
 }};
}
const check=(d,status,group)=>{const r=evaluateClass2(d);assert.equal(r.status,status);if(group!==undefined)assert.equal(r.hazard_group_candidate,group);assert.equal(r.un_number,null);assert.equal(r.packing_group,null);assert.equal(r.table_a_row_id,null);assert.equal(r.final_sds_section14_permitted,false);return r;};
test("gas 13 volume % exactly is flammable",()=>check(gas(),"class2_group_candidate","F"));
test("gas 12 percentage point range exactly is flammable",()=>{const d=gas();d.evidence.lowest_ignitable_concentration_vol_pct.value=13.1;d.evidence.flammable_range_percentage_points.value=12;check(d,"class2_group_candidate","F");});
test("both flammable alternatives negative => O or A with other evidence",()=>{const d=gas();d.evidence.lowest_ignitable_concentration_vol_pct.value=13.001;d.evidence.dilutes_or_replaces_atmospheric_oxygen=e(true,"boolean","PHYSICAL_ASSESSMENT");check(d,"class2_group_candidate","A");});
test("oxidizing power exactly 23.5 is negative",()=>{const d=gas();d.evidence.lowest_ignitable_concentration_vol_pct.value=20;d.evidence.dilutes_or_replaces_atmospheric_oxygen=e(true,"boolean","PHYSICAL_ASSESSMENT");check(d,"class2_group_candidate","A");});
test("oxidizing power above 23.5 is positive",()=>{const d=gas();d.evidence.lowest_ignitable_concentration_vol_pct.value=20;d.evidence.oxidizing_power_pct.value=23.50001;check(d,"class2_group_candidate","O");});
test("toxic LC50 5000 ppm inclusive gives TF",()=>{const d=gas();d.evidence.inhalation_lc50_ppm.value=5000;check(d,"class2_group_candidate","TF");});
test("toxic LC50 5000.01 ppm negative gives F",()=>{const d=gas();d.evidence.inhalation_lc50_ppm.value=5000.01;check(d,"class2_group_candidate","F");});
test("T outranks O and F in gas hazard group",()=>{const d=gas();d.evidence.inhalation_lc50_ppm.value=1000;d.evidence.oxidizing_power_pct.value=26;check(d,"class2_group_candidate","TF");});
test("gas definition vapour pressure exactly 300 kPa not sufficient",()=>{const d=gas();d.evidence.vapour_pressure_50_kpa.value=300;d.evidence.fully_gaseous_20c_101_3kpa.value=false;check(d,"outside_class2_gas_definition_not_non_dg",null);});
test("gas definition pressure >300 kPa sufficient even if 20C false",()=>{const d=gas();d.evidence.fully_gaseous_20c_101_3kpa.value=false;check(d,"class2_group_candidate","F");});
test("critical temperature exactly -50 C compressed",()=>check(gas(),"class2_group_candidate","F"));
test("critical temperature above -50 with negative phase evidence cannot be compressed",()=>{const d=gas();d.evidence.critical_temperature_c.value=-49.999;d.evidence.entirely_gaseous_at_minus50=e(false,"boolean");check(d,"blocked_unsupported");});
test("critical temperature above -50 with documented fully gaseous package still compressed",()=>{const d=gas();d.evidence.critical_temperature_c.value=-49.999;d.evidence.entirely_gaseous_at_minus50=e(true,"boolean");check(d,"class2_group_candidate","F");});
test("high-pressure liquefied at +65 C inclusive",()=>{const d=gas();d.form="liquefied";d.evidence.critical_temperature_c.value=65;d.evidence.partially_liquid_above_minus50=e(true,"boolean");assert.equal(check(d,"class2_group_candidate","F").physical_form.subtype,"high_pressure");});
test("low-pressure liquefied above +65 C",()=>{const d=gas();d.form="liquefied";d.evidence.critical_temperature_c.value=65.001;d.evidence.partially_liquid_above_minus50=e(true,"boolean");assert.equal(check(d,"class2_group_candidate","F").physical_form.subtype,"low_pressure");});
test("adsorbed 101.3 kPa exact limit is excluded",()=>{const d=gas();d.form="adsorbed";d.evidence.adsorbed_on_solid_porous_material=e(true,"boolean");d.evidence.internal_pressure_20_kpa=e(101.3,"kPa");d.evidence.internal_pressure_50_kpa=e(299,"kPa");check(d,"blocked_unsupported");});
test("adsorbed 300 kPa at 50 C exact limit excluded",()=>{const d=gas();d.form="adsorbed";d.evidence.adsorbed_on_solid_porous_material=e(true,"boolean");d.evidence.internal_pressure_20_kpa=e(100,"kPa");d.evidence.internal_pressure_50_kpa=e(300,"kPa");check(d,"blocked_unsupported");});
test("adsorbed both strict pressure limits passes candidate",()=>{const d=gas();d.form="adsorbed";d.evidence.adsorbed_on_solid_porous_material=e(true,"boolean");d.evidence.internal_pressure_20_kpa=e(100,"kPa");d.evidence.internal_pressure_50_kpa=e(299.9,"kPa");check(d,"class2_group_candidate","F");});
test("mixture harmonic calculation toxicity",()=>{const d=gas();delete d.evidence.inhalation_lc50_ppm;d.components=[{mole_fraction:0.5,toxicity_index_ppm:1000,toxicity_index_source:"P200",evidence_id:"a",corrosive:false},{mole_fraction:0.5,toxicity_index_ppm:2000,toxicity_index_source:"P200",evidence_id:"b",corrosive:false}];check(d,"class2_group_candidate","TF");});
test("corrosive mixture triggers TFC",()=>{const d=gas();delete d.evidence.inhalation_lc50_ppm;d.components=[{mole_fraction:0.5,toxicity_index_ppm:1000,toxicity_index_source:"P200",evidence_id:"a",corrosive:true},{mole_fraction:0.5,toxicity_index_ppm:2000,toxicity_index_source:"P200",evidence_id:"b",corrosive:false}];check(d,"class2_group_candidate","TFC");});
test("incorrect mole fraction sum blocks",()=>{const d=gas();d.components=[{mole_fraction:0.8,toxicity_index_ppm:1000,toxicity_index_source:"P200",evidence_id:"a",corrosive:false}];check(d,"blocked_unsupported");});
test("missing hazard evidence never means unregulated",()=>{const d=gas();delete d.evidence.oxidizing_power_pct;const r=check(d,"blocked_missing_evidence",null);assert.ok(r.missing_evidence.includes("evidence.oxidizing_power_pct"));});
test("incomplete initial data blocks",()=>{const d=gas();d.evidence={};check(d,"blocked_missing_evidence",null);});
test("invalid unit is blocked",()=>{const d=gas();d.evidence.oxidizing_power_pct.unit="kPa";check(d,"blocked_unsupported");});
test("comparable ISO method requires authority reference",()=>{const d=gas();d.evidence.oxidizing_power_pct.method="AUTHORITY_EQUIVALENT";check(d,"blocked_unsupported");});
test("unstable gas with no precautions prohibited",()=>{const d=gas();d.evidence.chemically_unstable.value=true;d.evidence.decomposition_precautions_satisfactory=e(false,"boolean","DOCUMENTED_PACKING_CONTROL");d.evidence.p200_10_r_applicable_and_satisfied=e(false,"boolean","P200_RECORD");check(d,"not_accepted_for_carriage");});
test("explicit UN 2421 prohibition",()=>{const d=gas();d.preexisting_named_un="2421";check(d,"not_accepted_for_carriage");});
test("UN 1052 external Class 8 exception",()=>{const d=gas();d.preexisting_named_un="1052";check(d,"outside_class2_special_named_exception");});
test("aerosol 85% + 30 kJ/g inclusive is F",()=>check(aerosol(),"class2_group_candidate","F"));
test("aerosol at 1% and below 20 kJ/g non-F",()=>{const d=aerosol();d.evidence.aerosol_flammable_mass_pct.value=1;d.evidence.aerosol_heat_combustion_kj_g.value=19.999;check(d,"class2_group_candidate","A");});
test("aerosol at exactly 20 kJ/g requires MTC section 31 test",()=>{const d=aerosol();d.evidence.aerosol_flammable_mass_pct.value=1;d.evidence.aerosol_heat_combustion_kj_g.value=20;const r=check(d,"blocked_missing_evidence",null);assert.ok(r.missing_evidence.includes("evidence.mtc31_aerosol_result"));});
test("aerosol intermediate MTC result flammable",()=>{const d=aerosol();d.evidence.aerosol_flammable_mass_pct.value=50;d.evidence.mtc31_aerosol_result=e("flammable","category","MTC_REV8_SECTION31");check(d,"class2_group_candidate","F");});
test("aerosol toxic propellant prohibited",()=>{const d=aerosol();d.evidence.propellant_toxic_gas.value=true;check(d,"not_accepted_for_carriage");});
test("aerosol content toxicity PG I prohibited",()=>{const d=aerosol();d.evidence.contents_nonpropellant_toxic_pg.value="I";check(d,"not_accepted_for_carriage");});
test("aerosol oxidizing plus corrosive CO",()=>{const d=aerosol();d.evidence.aerosol_flammable_mass_pct.value=1;d.evidence.aerosol_heat_combustion_kj_g.value=19;d.evidence.aerosol_contains_oxidizing_gas.value=true;d.evidence.contents_nonpropellant_corrosive_pg.value="II";check(d,"class2_group_candidate","CO");});
test("aerosol unsupported oxidizing+flammable blocks",()=>{const d=aerosol();d.evidence.aerosol_contains_oxidizing_gas.value=true;check(d,"blocked_unsupported");});
test("chemical under pressure A",()=>check(chemical(),"class2_group_candidate","A"));
test("chemical under pressure FC",()=>{const d=chemical();d.evidence.contents_eligible_flam_form.value=true;d.evidence.contents_nonpropellant_corrosive_pg.value="III";check(d,"class2_group_candidate","FC");});
test("chemical under pressure TF",()=>{const d=chemical();d.evidence.contents_eligible_flam_form.value=true;d.evidence.contents_nonpropellant_toxic_pg.value="II";check(d,"class2_group_candidate","TF");});
test("chemical under pressure toxin+corrosivity PG II excluded",()=>{const d=chemical();d.evidence.contents_nonpropellant_toxic_pg.value="II";d.evidence.contents_nonpropellant_corrosive_pg.value="III";check(d,"not_accepted_for_carriage");});
test("chemical under pressure oxidizing propellant excluded",()=>{const d=chemical();d.evidence.propellant_oxidizing_gas.value=true;check(d,"not_accepted_for_carriage");});
test("chemical under pressure prohibited other class component excluded",()=>{const d=chemical();d.evidence.prohibited_other_class_component.value=true;check(d,"not_accepted_for_carriage");});
test("article route explicitly unsupported",()=>check({route:"article"},"blocked_unsupported",null));

test("aerosol uses fixed ADR classification code 5",()=>{assert.equal(check(aerosol(),"class2_group_candidate","F").classification_code_candidate,"5");});
test("chemical under pressure uses ADR code 8FC",()=>{const d=chemical();d.evidence.contents_eligible_flam_form.value=true;d.evidence.contents_nonpropellant_corrosive_pg.value="II";assert.equal(check(d,"class2_group_candidate","FC").classification_code_candidate,"8FC");});
test("chemical packaged in aerosol dispenser is rerouted",()=>{const d=chemical();d.evidence.in_aerosol_dispenser.value=true;check(d,"requires_aerosol_route");});
test("gas cartridge uses fixed ADR classification code 5 when eligible",()=>{const d=gas();d.route="cartridge";d.evidence.propellant_pyrophoric_P200=e(false,"boolean","P200_TABLE2_NOTE_C");assert.equal(check(d,"class2_group_candidate","F").classification_code_candidate,"5");});
test("dissolved gas code is 4, not 4F",()=>{const d=gas();d.form="dissolved";d.preexisting_named_un="1001";d.evidence.dissolved_in_liquid_solvent_under_pressure=e(true,"boolean");assert.equal(check(d,"class2_group_candidate","F").classification_code_candidate,"4");});
