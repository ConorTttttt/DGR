// Agent 10 - provisional ADR 2025 Class 6.2 evaluator. No final UN/PG/Section 14 assignment.
// Pure function; standard Node.js ESM; no CLP/GHS inference.
export const classifyClass62 = function classifyClass62(input) {
  const SRC = "ADR 2025 ECE/TRANS/352 (Vol.I)";
  const ENTRIES = {
    "2814": {code:"I1", sp:["318"], description:"Category A infectious substance affecting humans"},
    "2900": {code:"I2", sp:["318"], description:"Category A infectious substance affecting animals only"},
    "3373": {code:"I4", sp:["319"], description:"Category B biological substance"},
    "3291": {code:"I3", sp:["565"], description:"Medical or clinical waste"},
    "3549": {code:"I3", sp:["395"], description:"Eligible solid Category A medical waste for disposal"}
  };
  const f = input && typeof input === "object" ? input : {};
  const out = {
    schema_version:"0.1.0",
    agent:"10",
    regulatory_source:SRC,
    transport_mode:f.mode ?? null,
    decision:"insufficient_evidence",
    evidence_state:"incomplete",
    class_candidate:null,
    category:null,
    classification_code_candidates:[],
    un_entry_candidates:[],
    packing_group:null,
    packing_group_status:"not_assigned",
    table_a_lookup_required:false,
    special_provision_dependencies:[],
    subsidiary_hazard_candidates:Array.isArray(f.other_hazard_cues) ? [...new Set(f.other_hazard_cues.filter(x=>typeof x==="string"))] : [],
    other_class_integration_required:true,
    final_sds_section14_assignment_permitted:false,
    decision_trace:[],
    missing_evidence:[],
    review_gates:[],
    notes:[]
  };
  function rule(id,clause){out.decision_trace.push({id,clause,source:SRC});}
  function missing(...fields){for(const x of fields){if(!out.missing_evidence.includes(x))out.missing_evidence.push(x);}}
  function gate(...fields){for(const x of fields){if(!out.review_gates.includes(x))out.review_gates.push(x);}}
  function done(status,state){out.decision=status;out.evidence_state=state;return out;}
  function excluded(id,clause,reason) {
    rule(id,clause);
    out.notes.push(reason);
    gate("Resolve other dangerous-goods classes and ADR Part 1 applicability before any global non-regulated declaration");
    return done("conditional_adr_non_subject","verified_negative_class62_or_specific_exception");
  }
  function candidates(nums,id,clause,category) {
    rule(id,clause);
    out.un_entry_candidates=[...new Set(nums)];
    out.class_candidate="6.2";
    out.category=category;
    out.classification_code_candidates=[...new Set(nums.map(n=>ENTRIES[n].code))];
    out.special_provision_dependencies=[...new Set(nums.flatMap(n=>ENTRIES[n].sp))];
    out.table_a_lookup_required=true;
    out.packing_group_status="verified_blank_in_adr2025_table_a_column_4_for_these_candidate_rows";
    gate("Independent Table A row selection, variants and column 6 special provisions");
    gate("Global named-entry, other-class and subsidiary-hazard integration");
    return done("class62_candidate","positive");
  }
  function evidence(){return Array.isArray(f.evidence_refs) && f.evidence_refs.some(x=>typeof x==="string" && x.trim());}
  function professional(){const p=f.professional_judgement;return !!(p && typeof p.record_ref==="string" && p.record_ref.trim() && typeof p.basis==="string" && p.basis.trim());}
  function assessCategory() {
    const a=f.category_a_assessment;
    if(a==="met") {
      if(!evidence()){missing("evidence_refs for Category A severity and exposure form");return "incomplete";}
      rule("62-CATA","2.2.62.1.4.1");
      return "A";
    }
    if(a==="doubt") {
      if(!professional()) {missing("professional_judgement.record_ref","professional_judgement.basis");gate("Record a qualified assessment of Category A doubt under Note 2");return "review";}
      rule("62-CATA-DOUBT","2.2.62.1.4.1 Note 2");
      return "A";
    }
    if(a==="not_met") {
      if(!evidence()){missing("evidence_refs substantiating Category A exclusion");return "incomplete";}
      rule("62-CATB","2.2.62.1.4.2");
      return "B";
    }
    missing("category_a_assessment: met | not_met | doubt");
    gate("Assess Category A severity, infectious form, source history, symptoms and endemic conditions");
    return "review";
  }
  function pathwayFromPathogen(idPrefix) {
    if(f.pathogen_state==="no_infectious_substances") {
      if(!evidence()){missing("evidence_refs establishing absence of infectious substances");return done("insufficient_evidence","incomplete");}
      return excluded("62-NO-INFECTIOUS","2.2.62.1.5.1","No infectious substances established; this is not a global other-class clearance.");
    }
    if(f.pathogen_state==="nonpathogenic_microorganisms") {
      if(!evidence()){missing("evidence_refs proving non-pathogenicity");return done("insufficient_evidence","incomplete");}
      return excluded("62-NONPATHOGENIC","2.2.62.1.5.2","Microorganisms documented non-pathogenic to humans and animals.");
    }
    if(!["known","reasonably_expected"].includes(f.pathogen_state)) {
      missing("pathogen_state: known | reasonably_expected | verified negative","evidence_refs");
      gate("Investigate suspected pathogens; absence of evidence is not a negative result");
      return done("insufficient_evidence","unknown");
    }
    if(!evidence()){missing("evidence_refs identifying pathogenic basis or reasonable expectation");return done("insufficient_evidence","incomplete");}
    rule("62-SCOPE","2.2.62.1.1");
    const cat=assessCategory();
    if(cat==="review")return done("requires_expert_review","unresolved_category_a");
    if(cat==="incomplete")return done("insufficient_evidence","incomplete");
    if(cat==="B")return candidates(["3373"],idPrefix+"-B","2.2.62.1.4.2","B");
    if(f.affects_humans===true)return candidates(["2814"],idPrefix+"-A-H","2.2.62.1.4.1(a)-(b)","A");
    if(f.affects_humans===false && f.affects_animals===true)return candidates(["2900"],idPrefix+"-A-A","2.2.62.1.4.1(a)-(b)","A");
    missing("affects_humans","affects_animals","medical source circumstances supporting target species");
    gate("Category A human-versus-animal-only determination by evidence/professional judgement");
    return done("requires_expert_review","unresolved_species_effect");
  }
  if(f.mode!=="ADR_ROAD") {
    rule("62-MODE","2.2.62.1.5.8 Note 2");
    gate("Determine governing mode-specific regulations; ADR 2025 is only a road baseline");
    if(f.mode==="AIR")out.notes.push("ADR 2.2.62.1.5.8 Note 2 refers to packaging (a)-(c) for air; this engine does not issue an ICAO/IATA classification.");
    return done("mode_not_supported","not_evaluated_for_transport_mode");
  }
  if(!["substance","culture","patient_specimen","biological_product","medical_waste","medical_device","live_animal","gmo","toxin"].includes(f.kind)) {
    missing("kind: substance | culture | patient_specimen | biological_product | medical_waste | medical_device | live_animal | gmo | toxin");
    return done("insufficient_evidence","incomplete");
  }
  // Conflicting high-risk and exemption assertions must be adjudicated, not silently prioritised.
  if(f.kind==="medical_waste" && f.category_a_assessment==="met" &&
     ["known","reasonably_expected"].includes(f.pathogen_state) &&
     (f.waste_low_probability===true || (["18 01 04","18 02 03"].includes(f.waste_catalogue_code) && f.waste_catalogue_verified===true))) {
    rule("62-CONFLICT-WASTE","2.2.62.1.11.1-2");
    gate("Reconcile Category A evidence against low-probability or exempt waste-catalogue assertion");
    return done("requires_expert_review","contradictory_evidence");
  }
  if(f.kind==="patient_specimen" && f.minimal_pathogen_likelihood===true &&
     f.category_a_assessment==="met" && ["known","reasonably_expected"].includes(f.pathogen_state)) {
    rule("62-CONFLICT-SPECIMEN","2.2.62.1.4.1;2.2.62.1.5.8");
    gate("Reconcile Category A evidence against claimed minimal likelihood before specimen exemption");
    return done("requires_expert_review","contradictory_evidence");
  }
  if(f.kind==="live_animal") {
    if(f.infection_origin==="natural_or_unintentional") {
      rule("62-LIVE-NATURAL","2.2.62.1.1 Note 1");
      gate("Check applicable national rules in origin, transit and destination");
      return done("national_animal_rules_review","outside_this_class62_material_entry_path");
    }
    if(f.infection_origin!=="intentional"){missing("infection_origin");return done("insufficient_evidence","incomplete");}
    rule("62-LIVE-INTENTIONAL","2.2.62.1.12.1;2.2.62.2");
    if(f.competent_authority_approval===true && evidence()) {
      gate("Verify authority approval scope, national conditions and whether carriage by other means is feasible");
      return done("requires_competent_authority_review","documented_authority_permission_pending_scope_review");
    }
    missing("competent_authority_approval and its recorded evidence");
    gate("Intentionally infected live animals require competent authority-approved terms; no ordinary automatic UN entry");
    return done("requires_competent_authority_approval","authority_gate_unresolved");
  }
  if(f.kind==="toxin" && f.toxin_without_infectious_agent===true) {
    if(!evidence()){missing("evidence_refs proving toxin is unaccompanied by infectious substances/organisms");return done("insufficient_evidence","incomplete");}
    rule("62-TOXIN-REFERRAL","2.2.62.1.1 Note 2");
    gate("Class 6.1 toxin pathway; assess UN 3172 or 3462 without assigning entry here");
    return done("referred_to_other_class","verified_not_class62_for_this_path");
  }
  if(f.kind==="gmo" && f.pathogen_state==="no_infectious_substances") {
    if(!evidence()){missing("evidence_refs for genetically modified organism noninfectious determination");return done("insufficient_evidence","incomplete");}
    rule("62-GMO-REFERRAL","2.2.62.1.10");
    gate("Refer to ADR 2.2.9 genetic modification classification; no Class 9 assignment here");
    return done("referred_to_other_class","verified_not_class62_for_this_path");
  }
  if(f.inactivation_verified===true) {
    if(!evidence()){missing("evidence_refs of validated pathogen neutralisation/inactivation and no remaining health risk");return done("insufficient_evidence","incomplete");}
    return excluded("62-INACTIVATED","2.2.62.1.5.3","Inactivation verified to remove health risk; remaining other classes not assessed.");
  }
  if(f.kind==="medical_device" && f.drained_of_free_liquid===true && evidence()) {
    return excluded("62-DEVICE-DRAINED","2.2.62.1.5.3 Note","Medical equipment drained of free liquid meets the paragraph's criteria; cross-class assessment remains.");
  }
  if(f.kind==="patient_specimen") {
    if(f.specimen_exclusion==="dried_blood_spot" && f.blood_drop_on_absorbent===true && evidence())
      return excluded("62-DRIED-BLOOD","2.2.62.1.5.5","Dried blood spot prepared on absorbent material.");
    if(f.specimen_exclusion==="faecal_occult_blood" && evidence())
      return excluded("62-FOBT","2.2.62.1.5.6","Faecal occult blood screening specimen.");
    if(f.specimen_exclusion==="transfusion_or_transplant" && f.specimen_purpose_verified===true &&
       ["transfusion","transfusion_product_preparation","transplantation","related_sample"].includes(f.specimen_purpose) && evidence())
      return excluded("62-TRANSFUSION","2.2.62.1.5.7","Blood/component, tissue/organ or related sample within the stated transfusion/transplant purposes.");
    if(f.minimal_pathogen_likelihood===true) {
      rule("62-MINIMAL-JUDGEMENT","2.2.62.1.5.8 Note 1");
      if(!professional()){missing("professional_judgement.record_ref","professional_judgement.basis");gate("Professional judgement on minimal likelihood from source history/symptoms/circumstances/endemic conditions");return done("requires_expert_review","unverified_minimal_likelihood");}
      const p=f.specimen_packaging||{};
      const mark=f.specimen_species==="animal"?"Exempt animal specimen":"Exempt human specimen";
      if(!["human","animal"].includes(f.specimen_species)){missing("specimen_species");return done("insufficient_evidence","incomplete");}
      if(p.mark!==mark){missing("specimen_packaging.mark exact exempt specimen marking");return done("insufficient_evidence","packaging_unproven");}
      if(p.method==="tripack") {
        const checks=["primary_leakproof","secondary_leakproof","outer_adequate","packaging_verified"];
        for(const key of checks)if(p[key]!==true)missing("specimen_packaging."+key);
        if(!(typeof p.outer_width_mm==="number" && p.outer_width_mm>=100))missing("specimen_packaging.outer_width_mm >= 100");
        if(!(typeof p.outer_height_mm==="number" && p.outer_height_mm>=100))missing("specimen_packaging.outer_height_mm >= 100");
        if(f.specimen_is_liquid===true && p.absorbent_all_contents!==true)missing("specimen_packaging.absorbent_all_contents");
        if(f.multiple_fragile_primaries===true && p.fragile_separated!==true)missing("specimen_packaging.fragile_separated");
        if(out.missing_evidence.length)return done("insufficient_evidence","packaging_unproven");
        return excluded("62-MINIMAL-TRIPACK","2.2.62.1.5.8(a)-(c)","Professionally assessed minimal-risk specimen with deemed-compliant packaging and correct marking.");
      }
      if(p.method==="alternative_no_leakage" && p.no_leakage_demonstrated===true && evidence()) {
        rule("62-MINIMAL-ALTERNATIVE","2.2.62.1.5.8");
        gate("Independent review of alternative packaging leakage evidence; three-component conditions are a deemed-compliance route");
        return done("requires_expert_review","alternative_package_compliance_review");
      }
      missing("specimen_packaging.method and verified leak-prevention evidence");
      return done("insufficient_evidence","packaging_unproven");
    }
  }
  if(f.kind==="medical_device") {
    rule("62-DEVICE","2.2.62.1.5.9");
    if(f.device_category_a===true){gate("No §2.2.62.1.5.9 relief for devices containing Category A; verify applicable named entry");return done("named_entry_review_required","category_a_device");}
    if(f.device_other_class_dangerous===true){gate("No device relief when another dangerous goods class applies");return done("referred_to_other_class","other_class_device");}
    if(f.device_category_a!==false || f.device_other_class_dangerous!==false){
      missing("device_category_a (explicitly assessed)","device_other_class_dangerous (explicitly assessed)");
      return done("requires_expert_review","device_exception_exclusions_unresolved");
    }
    if(!["disinfection","cleaning","sterilization","repair","equipment_evaluation"].includes(f.device_carriage_purpose)){
      missing("device_carriage_purpose (approved enumerated purpose)");
      return done("insufficient_evidence","device_purpose_unverified");
    }
    const p=f.device_packaging||{};
    for(const key of ["protects_against_breakage_puncture_leak","construction_6_1_4_or_6_6_4","general_4_1_1_1_and_4_1_1_2","retains_on_1_2m_drop"]) if(p[key]!==true)missing("device_packaging."+key);
    if(!(typeof p.drop_height_m==="number" && p.drop_height_m>=1.2))missing("device_packaging.drop_height_m >= 1.2");
    if(!["USED MEDICAL DEVICE","USED MEDICAL EQUIPMENT"].includes(p.mark))missing("device_packaging.mark");
    if(p.overpack_used===true && p.mark_visible!==true && p.overpack_marked!==true)missing("device_packaging.overpack_marked_or_mark_visible");
    if(!evidence())missing("evidence_refs verifying device and packaging conditions");
    if(out.missing_evidence.length)return done("insufficient_evidence","device_package_conditions_unproven");
    out.notes.push("Only §2.2.62.1.5.9 remains applicable; not an unconditional global ADR exemption.");
    return done("limited_provisions_exemption","verified_qualified_device_exception");
  }
  if(f.kind==="biological_product") {
    if(f.national_authority_manufacture_packaging_verified===true &&
       f.healthcare_personal_use===true && ["final_packaging","distribution"].includes(f.biological_carriage_purpose) && evidence()) {
      return excluded("62-BIOLOGICAL-A","2.2.62.1.9(a)","Qualifying nationally regulated, manufactured/packaged product for final packaging or distribution and personal health care; competent authority/local restrictions still possible.");
    }
    rule("62-BIOLOGICAL-B","2.2.62.1.9(b)");
    gate("Verify product's national authority status, actual form, licensing and destination competent-authority requirements");
  }
  if(f.kind==="medical_waste") {
    if(f.waste_decontaminated===true && evidence())
      return excluded("62-WASTE-DECONTAMINATED","2.2.62.1.11.3","Decontaminated former infectious waste: check other dangerous classes.");
    if(["18 01 04","18 02 03"].includes(f.waste_catalogue_code) && f.waste_catalogue_verified===true && evidence())
      return excluded("62-WASTE-CODE-EXEMPT","2.2.62.1.11.2 Note 2","Verified waste catalogue non-infectious-handling code 18 01 04 or 18 02 03.");
    if(["18 01 03","18 02 02"].includes(f.waste_catalogue_code) && !f.diagnosis_recorded) {
      rule("62-WASTE-CODE-DIAGNOSIS","2.2.62.1.11.1 Note 2");
      missing("diagnosis_recorded; clinical/veterinary evidence for infectious category");
      return done("requires_expert_review","waste_code_is_not_a_complete_classification");
    }
    if(f.waste_low_probability===true && evidence()) {
      return candidates(["3291"],"62-WASTE-LOW-PROB","2.2.62.1.11.2","B_or_low_probability_waste");
    }
    if(!["known","reasonably_expected"].includes(f.pathogen_state)){
      missing("waste_low_probability established OR pathogen_state and Category A/B evidence","evidence_refs");
      return done("insufficient_evidence","unknown_waste_infectious_status");
    }
    if(!evidence()){missing("evidence_refs for waste infection-category diagnosis");return done("insufficient_evidence","incomplete");}
    const cat=assessCategory();
    if(cat==="review")return done("requires_expert_review","waste_category_unresolved");
    if(cat==="incomplete")return done("insufficient_evidence","incomplete");
    if(cat==="B")return candidates(["3291"],"62-WASTE-B","2.2.62.1.11.1(b)","B");
    if(f.affects_humans!==true && !(f.affects_humans===false && f.affects_animals===true)){
      missing("affects_humans","affects_animals");return done("requires_expert_review","waste_category_a_species_unresolved");
    }
    const ordinary=f.affects_humans===true?"2814":"2900";
    let nums=[ordinary];
    if(f.waste_state==="solid" && ["human_medical_treatment","animal_veterinary_treatment"].includes(f.waste_origin) && f.waste_carriage_purpose==="disposal") {
      nums.push("3549");
      rule("62-WASTE-3549-ELIGIBLE","2.2.62.1.11.1(a);3.3.1 SP395");
      gate("UN 3549 is optional ('may') and limited to eligible solid medical waste for disposal; choose row with integration lead");
    } else {
      rule("62-WASTE-3549-INELIGIBLE","2.2.62.1.11.1(a);3.3.1 SP395");
      out.notes.push("UN 3549 not proposed without verified solid medical-treatment waste for disposal; liquid or bio-research waste cannot use it.");
    }
    return candidates(nums,"62-WASTE-A","2.2.62.1.11.1(a)","A");
  }
  if(f.natural_pathogen_level===true && f.no_significant_infection_risk===true && evidence()) {
    return excluded("62-NATURAL-LEVEL","2.2.62.1.5.4","Naturally encountered pathogen concentration with no significant infection risk, such as qualifying food/water.");
  }
  return pathwayFromPathogen("62-PRIMARY");
};
