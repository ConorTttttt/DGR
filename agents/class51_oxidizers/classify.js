"use strict";
/**
 * Agent 7 - provisional ADR 2025 Class 5.1 candidate evaluator.
 * This module NEVER assigns a final UN number, Table A row, transport PG,
 * or publishable SDS result. Inputs are test-report evidence, not GHS/CLP labels.
 */
const EDITION = Object.freeze({
  adr: "ADR 2025, ECE/TRANS/352, Vol. I (English)",
  manual: "ST/SG/AC.10/11/Rev.8, Part III",
  amendment: "ST/SG/AC.10/11/Rev.8/Amend.1 (scope reviewed; no 34/39 override encoded)",
  status: "provisional_unreviewed"
});
const TEST_METHODS = Object.freeze({
  "O.1": { state: "solid", basis: "mean_burning_time_seconds", references: {
    pgI: "potassium bromate/cellulose 3:2", pgII: "potassium bromate/cellulose 2:3",
    pgIII: "potassium bromate/cellulose 3:7" }},
  "O.3": { state: "solid", basis: "mean_burning_rate_g_per_s", references: {
    pgI: "calcium peroxide/cellulose 3:1", pgII: "calcium peroxide/cellulose 1:1",
    pgIII: "calcium peroxide/cellulose 1:2" }},
  "O.2": { state: "liquid", basis: "mean_pressure_rise_time_seconds_690_to_2070_kpa_gauge",
    references: { pgI: "50% perchloric acid/cellulose 1:1",
      pgII: "40% aqueous sodium chlorate/cellulose 1:1",
      pgIII: "65% aqueous nitric acid/cellulose 1:1" }}
});
const AMMONIUM_FERTILIZER_FORBIDDEN = new Set([4,6,8,15,31,33]);
const AMMONIUM_FERTILIZER_AUTHORITY = new Set([20,23,39]);
const FLUOR_EXCEPTION_UN = new Set(["1745","1746","2495","1749","2548"]);
const isNumber = n => typeof n === "number" && Number.isFinite(n) && n >= 0;
const mean = a => a.reduce((v,n) => v+n, 0) / a.length;
const refs = (...r) => r;
function evaluateClass51(input) {
  const result = {
    schema_version: "agent7.adr2025.class51.finding.v0.1",
    assessment_id: typeof input?.assessmentId === "string" ? input.assessmentId : null,
    regime: "ADR", edition: "2025", class: "5.1", rule_id: "51-001",
    status: "indeterminate", specialistStatus: "insufficient_evidence",
    primary_class_candidates: [], subsidiary_risks: [], packing_group_candidates: [],
    exclusions: [], unresolved_evidence: [], expert_decisions: [],
    table_a_candidates: [], special_provision_outcomes: [], evidence_refs: [],
    clause_refs: [], assignment_permitted: false, requires_independent_review: true,
    classCandidate: null, pgCandidate: null,
    finalPackingGroup: null, finalUNNumber: null, tableARowId: null,
    evidenceUsed: [], missingEvidence: [], issues: [], subsidiaryCandidates: [],
    dependencies: ["ADR 2025 Chapter 3.2 Table A row/PG column (4)",
      "ADR 2025 3.3.1 special provisions via Table A column (6)",
      "ADR 2025 2.1.3 multiple-hazard precedence, Lead Agent decision",
      "competent reviewer/independent ADR 2025 release gate"],
    regulation: EDITION, blockingForAssignment: true
  };
  const issue = (code, clause, detail) => result.issues.push({code, clause, detail});
  const missing = (...keys) => { for (const k of keys) if (!result.missingEvidence.includes(k)) result.missingEvidence.push(k); };
  const stop = status => {
    result.specialistStatus = status;
    const code = result.issues.length ? result.issues[0].code : null;
    result.status = status === "not_accepted_for_carriage" ? "prohibited_for_carriage"
      : status === "insufficient_evidence" ? "indeterminate"
      : status === "requires_expert_review" ?
          (["FERTILIZER_AUTHORITY_EXCEPTION","FERTILIZER_AUTHORITY_EXIT"].includes(code)
            ? "authority_required"
          : ["EXPERIENCE_CONFLICT","INVALID_REFERENCE_ORDER",
              "FERTILIZER_EXIT_OUTCOME_MISMATCH"].includes(code) ? "conflict"
          : ["UNSUPPORTED_METHOD","EDITION_UNSUPPORTED","ARTICLE_ENTRY_REQUIRED",
              "ARTICLE_OR_STATE_UNSUPPORTED","FERTILIZER_NONTERMINAL_OR_UNKNOWN_BOX",
              "GHS_SHORTCUT_REJECTED"].includes(code) ? "unsupported"
          : "indeterminate") : status;
    const method = input?.test?.method;
    const pg = result.pgCandidate;
    const ruleSet = {
      "O.1": {I:"51-009",II:"51-010",III:"51-011",default:"51-006"},
      "O.3": {I:"51-012",II:"51-013",III:"51-014",default:"51-007"},
      "O.2": {I:"51-016",II:"51-017",III:"51-018",default:"51-015"}
    };
    result.rule_id = input?.composition?.isSolidAmmoniumNitrateFertilizer === true
      ? (code === "FERTILIZER_AUTHORITY_EXIT" || code === "FERTILIZER_PROHIBITED_EXIT"
          ? "51-023" : "51-008")
      : code === "UNSTABLE_UNACCEPTABLE" ? "51-019"
      : code === "COMBINED_51_SOLID_RESTRICTED" ? "51-020"
      : code && /PROHIBITED|HALOGENATED|AMMONIUM_NITRATE/.test(code) ? "51-021"
      : ruleSet[method] ? (ruleSet[method][pg] || ruleSet[method].default) : "51-001";
    result.primary_class_candidates = result.classCandidate
      ? [{class:"5.1",classification_code:null,division:null,compatibility_group:null,
          packing_group:null,evidence_ids:result.evidenceUsed.map(x=>x.reportId||x.recordId).filter(Boolean),
          authority_decision_id:null,status:result.status}] : [];
    result.subsidiary_risks = result.subsidiaryCandidates.map(c=>({
      class:c,evidence_ids:[],status:"indeterminate"}));
    result.packing_group_candidates = pg ? [{value:pg,
      evidence_ids:result.evidenceUsed.map(x=>x.reportId||x.recordId).filter(Boolean),
      status:"provisional_not_table_a_verified"}] : [];
    result.unresolved_evidence = result.missingEvidence.map(key=>({
      id:key,reason:"Required verified Class 5.1 evidence not supplied",blocks_assignment:true}));
    result.evidence_refs = result.evidenceUsed.map(x=>x.reportId||x.recordId).filter(Boolean);
    result.clause_refs = [...new Set(result.issues.flatMap(x=>x.clause.split(";").map(z=>z.trim())))];
    return result;
  };
  if (!input || typeof input !== "object" || Array.isArray(input))
    { missing("material evidence object"); return stop("insufficient_evidence"); }
  const p = input.composition || {};
  const hazards = input.otherHazards || {};
  for (const [k,code] of [["toxic","6.1"],["corrosive","8"],["flammableSolid","4.1"],
    ["selfHeating","4.2"],["waterReactive","4.3"]]) {
    if (hazards[k] === true) result.subsidiaryCandidates.push(code);
  }
  if (input.sourceOfClassification === "CLP" || input.sourceOfClassification === "GHS"
      || input.ghsCategoryAsTransportPG !== undefined) {
    issue("GHS_SHORTCUT_REJECTED","2.2.51.1.3","Transport test/entry evidence required.");
    return stop("requires_expert_review");
  }
  if (input.knownExperienceConflict === true) {
    issue("EXPERIENCE_CONFLICT","2.2.51.1.3","Known experience takes precedence; expert resolution needed.");
    return stop("requires_expert_review");
  }
  if (input.chemicallyUnstable === true) {
    if (input.stabilizationForTransportVerified !== true) {
      issue("UNSTABLE_UNACCEPTABLE","2.2.51.2.1","Decomposition/polymerization protection not verified.");
      return stop("not_accepted_for_carriage");
    }
    result.dependencies.push("verify stabilization and carriage conditions under 2.2.51.2.1");
  }
  if (input.prohibitedIdentity === true) {
    issue("LISTED_PROHIBITION","2.2.51.2.2","Explicit prohibited identity requires documented exception review.");
    return stop("not_accepted_for_carriage");
  }
  const id = p.chemicalIdentity;
  if (id === "hydrogen_peroxide" && p.stabilized === false
       || id === "hydrogen_peroxide_aqueous" && p.stabilized === false
          && isNumber(p.massPercent) && p.massPercent > 60
       || id === "tetranitromethane" && p.combustibleImpurities === true
       || id === "perchloric_acid_solution" && (isNumber(p.massPercent) && p.massPercent > 72
          || p.otherLiquidThanWater === true)
       || id === "chloric_acid_solution" && (isNumber(p.massPercent) && p.massPercent > 10
          || p.otherLiquidThanWater === true)
       || id === "ammonium_chlorate" || id === "ammonium_chlorite"
       || id === "ammonium_bromate" || id === "ammonium_permanganate"
       || id === "ammonium_nitrite"
       || p.ammoniumSaltMixedWith && ["chlorate","chlorite","hypochlorite","bromate",
          "permanganate","inorganic_nitrite"].includes(p.ammoniumSaltMixedWith)
       || p.potassiumNitrateSodiumNitriteAmmoniumSaltMixture === true) {
    issue("COMPOSITION_PROHIBITED","2.2.51.2.2","Specific identity/concentration/incompatibility ban.");
    return stop("not_accepted_for_carriage");
  }
  if (p.isAmmoniumNitrate === true && p.isSolidAmmoniumNitrateFertilizer !== true
      && isNumber(p.combustibleMassPercent) && p.combustibleMassPercent > 0.2) {
    issue("AMMONIUM_NITRATE_GT_0_2","2.2.51.2.2","Exception only where constituent of Class 1 substance/article.");
    return stop(input.class1ConstituentVerified === true ? "requires_expert_review" : "not_accepted_for_carriage");
  }
  // Material-specific evidence cannot be silently replaced by an absent prohibition flag.
  if (["hydrogen_peroxide","hydrogen_peroxide_aqueous"].includes(id)
      && typeof p.stabilized !== "boolean") missing("composition.stabilized");
  if (id === "hydrogen_peroxide_aqueous" && !isNumber(p.massPercent))
    missing("composition.massPercent: hydrogen peroxide aqueous");
  if (["perchloric_acid_solution","chloric_acid_solution"].includes(id)) {
    if (!isNumber(p.massPercent)) missing("composition.massPercent: acid solution");
    if (typeof p.otherLiquidThanWater !== "boolean")
      missing("composition.otherLiquidThanWater");
  }
  if (p.isAmmoniumNitrate === true && p.isSolidAmmoniumNitrateFertilizer !== true
      && !isNumber(p.combustibleMassPercent))
    missing("composition.combustibleMassPercent");
  if (p.isSolidAmmoniumNitrateFertilizer === true && input.physicalState !== "solid")
    missing("physicalState:solid for MTC Section 39 route");
  if (result.missingEvidence.length) {
    issue("IDENTITY_SPECIFIC_DATA_MISSING","2.2.51.2.2; MTC 39.2",
      "Missing composition/stabilization evidence cannot clear a specific transport prohibition.");
    return stop("insufficient_evidence");
  }
  if (p.isHalogenatedFluorCompound === true
      && !FLUOR_EXCEPTION_UN.has(String(p.verifiedNamedUN || ""))) {
    issue("HALOGENATED_FLUOR_RESTRICTED","2.2.51.2.2",
      "Only specified named UN exceptions; verification/entry selection external.");
    return stop("not_accepted_for_carriage");
  }
  if (input.explosiveScreening === "positive") {
    issue("CLASS1_SCREEN_POSITIVE","2.1.3.7; 2.2.51.2.2; MTC 34.4.3.1",
      "Refer Class 1 specialist before any Class 5.1 disposition.");
    return stop("requires_expert_review");
  }
  if (input.explosiveScreening !== "negative") {
    missing("explosiveScreening:negative with dated evidence");
    issue("CLASS1_SCREEN_PENDING","MTC 34.4.3.1; ADR 2.1.3.7",
      "Explosive properties not excluded within the required scope.");
    return stop("insufficient_evidence");
  }
  if (hazards.flammableSolid === true || hazards.selfHeating === true || hazards.waterReactive === true) {
    issue("COMBINED_51_SOLID_RESTRICTED","2.2.51.2.2; 2.2.51.3",
      "Oxidizing/flammable, self-heating or water-reactive solid collective entry not accepted unless Class 1 applies.");
    return stop("not_accepted_for_carriage");
  }
  if (p.isSolidAmmoniumNitrateFertilizer === true) {
    return evaluateFertilizer(input, result, issue, missing, stop);
  }
  if (!["solid","liquid"].includes(input.physicalState)) {
    missing("physicalState:solid|liquid");
    issue("ARTICLE_OR_STATE_UNSUPPORTED","2.2.51.1.2; 2.2.51.3",
      "Articles and unconfirmed state need named-entry specialist review.");
    return stop("requires_expert_review");
  }
  if (input.isArticle === true) {
    issue("ARTICLE_ENTRY_REQUIRED","2.2.51.1.2; 2.2.51.3",
      "O.1/O.2/O.3 cannot independently assign article entries.");
    return stop("requires_expert_review");
  }
  if (input.isMixture === true && input.formulationAsPresentedTested !== true) {
    missing("formulationAsPresentedTested");
    issue("MIXTURE_NOT_TESTED","2.2.51.1.4; 2.1.3",
      "Composition-weighted GHS/component classifications cannot replace transport tests.");
    return stop("insufficient_evidence");
  }
  const t = input.test;
  if (!t || typeof t !== "object") {missing("test report: O.1/O.2/O.3"); return stop("insufficient_evidence");}
  if (!Object.hasOwn(TEST_METHODS,t.method) || TEST_METHODS[t.method].state !== input.physicalState) {
    issue("UNSUPPORTED_METHOD","2.2.51.1.6; 2.2.51.1.9; MTC 34.4",
      "Exact supported method and physical state needed; authority/expert review.");
    return stop("requires_expert_review");
  }
  const required = ["reportId","laboratory","sampleId","manualEdition",
    "protocolConformant","referencesConformant","testConditionsConformant",
    "sampleRepresentative","uncertaintyResolved"];
  for (const key of required) {
    if (["reportId","laboratory","sampleId","manualEdition"].includes(key)
        ? typeof t[key] !== "string" || !t[key].trim()
        : t[key] !== true) missing("test."+key);
  }
  if (t.manualEdition !== "Rev.8" && t.manualEdition !== "Rev.8+Amend.1") {
    issue("EDITION_UNSUPPORTED","MTC Part III 34.4","Only documented Rev.8 pathways encoded.");
    return stop("requires_expert_review");
  }
  if (result.missingEvidence.length) return stop("insufficient_evidence");
  result.evidenceUsed.push({type:"UN_TEST_REPORT",method:t.method,reportId:t.reportId,
    sampleId:t.sampleId,laboratory:t.laboratory,edition:t.manualEdition});
  if (t.method === "O.2") return evaluateLiquid(t,result,issue,missing,stop);
  return evaluateSolid(t,result,issue,missing,stop);
}
function evaluateFertilizer(i,r,issue,missing,stop) {
  const f = i.fertilizerRoute;
  r.dependencies.push("MTC Rev.8 Part III Section 39 flowchart 39.5.1",
    "ADR 2.2.51.1.7 exception from tests O.1/O.3",
    "UN 2067 and UN 2071 named-entry/Table A/SP assessment (external)");
  if (!f || !Number.isInteger(f.exitBox) || f.compositionVerified !== true
       || f.flowchartAudited !== true) {
    missing("fertilizerRoute.exitBox","fertilizerRoute.compositionVerified",
      "fertilizerRoute.flowchartAudited");
    return stop("insufficient_evidence");
  }
  if (typeof f.recordId !== "string" || !f.recordId.trim()) {
    missing("fertilizerRoute.recordId: audited composition/flowchart report");
    return stop("insufficient_evidence");
  }
  r.evidenceUsed.push({type:"SECTION39_FLOWCHART",exitBox:f.exitBox,recordId:f.recordId});
  const validExit = new Set([4,6,8,9,15,18,19,20,23,25,26,31,33,35,36,39,42,43,44,45]);
  if (!validExit.has(f.exitBox)) {
    issue("FERTILIZER_NONTERMINAL_OR_UNKNOWN_BOX","MTC 39.5.1",
      "Exit must be a terminal box in Figure 39.1(a)-(c), not a decision or connector node.");
    return stop("requires_expert_review");
  }
  if (AMMONIUM_FERTILIZER_FORBIDDEN.has(f.exitBox)) {
    issue("FERTILIZER_PROHIBITED_EXIT","2.2.51.2.2; MTC 39.5.1",
      "Exit boxes 4/6/8/15/31/33 not accepted unless suitable Class 1 entry.");
    return stop("not_accepted_for_carriage");
  }
  if (AMMONIUM_FERTILIZER_AUTHORITY.has(f.exitBox)) {
    if (f.suitabilityForCarriageDemonstrated === true
        && f.competentAuthorityApprovalVerified === true
        && f.approvedClass === "5.1" && f.approvedUNIs2067 === false) {
      issue("FERTILIZER_AUTHORITY_EXCEPTION","2.2.51.2.2; MTC 39.4.3",
        "Alternative Class 5.1 route, other than UN 2067, depends on authenticated approval.");
      r.classCandidate = "5.1"; r.pgCandidate = null;
      return stop("requires_expert_review");
    }
    issue("FERTILIZER_AUTHORITY_EXIT","2.2.51.2.2; MTC 39.5.1",
      "Exit boxes 20/23/39 need Class 1 route or approved alternative Class 5.1 (not UN 2067).");
    return stop("not_accepted_for_carriage");
  }
  const outcomes = {
    oxidizing_solid: new Set([9,18,19,36,42]),
    class9: new Set([25]),
    not_classified: new Set([26,35,43,44,45])
  };
  if (!outcomes[f.outcome] || !outcomes[f.outcome].has(f.exitBox)) {
    issue("FERTILIZER_EXIT_OUTCOME_MISMATCH","MTC 39.5.1",
      "Terminal box and claimed outcome disagree; use signed source review, not fabricated result.");
    return stop("requires_expert_review");
  }
  if (f.outcome === "class1") {
    issue("FERTILIZER_CLASS1_ROUTE","MTC 39.4.4; 39.5.1","Refer Class 1 even if series 2 is negative.");
    return stop("requires_expert_review");
  }
  if (f.outcome === "class9" || f.outcome === "not_classified") {
    if (f.outcome === "class9" && (f.s1SelfSustainingDecompositionVerified !== true
        || typeof f.s1ReportId !== "string" || !f.s1ReportId.trim())) {
      missing("fertilizerRoute.s1SelfSustainingDecompositionVerified",
        "fertilizerRoute.s1ReportId");
      issue("FERTILIZER_S1_REQUIRED","MTC 39.4.7; 38.2.4; 39.5.1",
        "Class 9 self-sustaining-decomposition exit requires documented S.1 trough-test evidence.");
      return stop("insufficient_evidence");
    }
    issue("FERTILIZER_NON_51_ROUTE","MTC 39.4.7; 39.5.1",
      "Class 9/self-sustaining decomposition and other hazards must be evaluated independently.");
    return stop("criteria_not_met");
  }
  if (f.outcome !== "oxidizing_solid") {
    missing("fertilizerRoute.outcome");
    return stop("insufficient_evidence");
  }
  if (f.series2NoExplosiveProperties !== true) {
    missing("fertilizerRoute.series2NoExplosiveProperties");
    issue("SERIES2_REQUIRED","MTC 39.4.2",
      "UN 2067 route requires evidence of no explosive properties under test series 2.");
    return stop("insufficient_evidence");
  }
  r.classCandidate="5.1";
  r.dependencies.push("UN 2067 possibility only; not an assignment");
  issue("FERTILIZER_PG_UNDETERMINED","MTC 39; ADR 2.2.51.1.8",
    "O.1/O.3 PG substitution prohibited; retrieve exact named entry and PG from Table A.");
  return stop("criteria_met");
}
function evaluateSolid(t,r,issue,missing,stop) {
  const isO1=t.method==="O.1";
  const ref = t.references || {};
  const sample=t.sampleRatios || {};
  const metric=isO1?"burnTimesSeconds":"burnRatesGPerS";
  const getFive=(o,path,allowZero=true)=>{
    const arr=o && o[metric];
    if (!Array.isArray(arr)||arr.length!==5||!arr.every(n=>isNumber(n) && (allowZero||n>0))) {
      missing(path+"."+metric+" (five valid runs)");return null;
    }
    if (!isO1 && (!Array.isArray(o.rSquared)||o.rSquared.length!==5
      || !o.rSquared.every(n=>typeof n==="number"&&n>=0.90&&n<=1)
      || !isNumber(o.relativeStdDevPercent)||o.relativeStdDevPercent>20
      || o.massLossTraceVerified!==true)) {
      missing(path+".rSquared[5]>=0.90, relativeStdDevPercent<=20, massLossTraceVerified");
      return null;
    }
    return mean(arr);
  };
  const v={};
  for(const x of ["pgI","pgII","pgIII"]) v[x]=getFive(ref[x],"test.references."+x,!isO1);
  let anyIgnited=false, sufficient=true, readings=[];
  for(const ratio of ["4:1","1:1"]) {
    const s=sample[ratio];
    if (!s || typeof s.ignited !== "boolean") {
      missing("test.sampleRatios."+ratio+".ignited");sufficient=false;continue;
    }
    if (s.ignited) {
      anyIgnited=true;
      const m=getFive(s,"test.sampleRatios."+ratio,!isO1);
      if(m!==null)readings.push(m);else sufficient=false;
    } else if (!isO1) {
      // Non-burning O.3 experiments need an explicitly verified negative.
      if (s.fiveNonIgnitionsVerified!==true)
        { missing("test.sampleRatios."+ratio+".fiveNonIgnitionsVerified");sufficient=false; }
    } else if(s.fiveNonIgnitionsVerified!==true) {
      missing("test.sampleRatios."+ratio+".fiveNonIgnitionsVerified");sufficient=false;
    }
  }
  if (Object.values(v).some(x=>x===null)||!sufficient||r.missingEvidence.length)
    return stop("insufficient_evidence");
  if(isO1 ? !(v.pgI<v.pgII&&v.pgII<v.pgIII) : !(v.pgI>v.pgII&&v.pgII>v.pgIII)) {
    issue("INVALID_REFERENCE_ORDER","MTC 34.4.1 or 34.4.3",
      "Reference calibration order not monotonic; cannot use PG comparisons.");
    return stop("requires_expert_review");
  }
  const matches=(name,strict)=>readings.some(x=>isO1
    ? strict ? x<v[name] : x<=v[name] : strict ? x>v[name] : x>=v[name]);
  if(matches("pgI",true)) r.pgCandidate="I";
  else if(matches("pgII",false)) r.pgCandidate="II";
  else if(matches("pgIII",false)) r.pgCandidate="III";
  if (r.pgCandidate) {r.classCandidate="5.1";return stop("criteria_met");}
  if(isO1 && anyIgnited) {
    r.classCandidate="5.1";
    issue("O1_IGNITION_WITHOUT_PG","2.2.51.1.6(a); 2.2.51.1.8(a); MTC 34.4.1.4",
      "ADR Class 5.1 ignition route but PG comparison does not match; experience/expert review.");
    return stop("requires_expert_review");
  }
  issue("METHOD_SPECIFIC_NEGATIVE",isO1?"2.2.51.1.6(a); MTC 34.4.1.4.2(d)":
      "2.2.51.1.6(b); MTC 34.4.3.5.4(d)",
    "Only not Class 5.1 by this supported tested pathway, not not-dangerous by ADR.");
  return stop("criteria_not_met");
}
function evaluateLiquid(t,r,issue,missing,stop){
  if(typeof t.spontaneousIgnition!=="boolean"){
    missing("test.spontaneousIgnition");return stop("insufficient_evidence");
  }
  if(t.spontaneousIgnition){
    r.classCandidate="5.1";r.pgCandidate="I";
    r.evidenceUsed.push({type:"O2_SPONTANEOUS_IGNITION",verified:true});
    return stop("criteria_met");
  }
  if(!isNumber(t.peakPressureRiseKpaGauge)){
    missing("test.peakPressureRiseKpaGauge");return stop("insufficient_evidence");
  }
  if(t.peakPressureRiseKpaGauge<2070){
    issue("O2_BELOW_PRESSURE_GATE","2.2.51.1.9; MTC 34.4.2.4.2(d)",
      "Pressure rise below 2070 kPa gauge (method-specific negative).");
    return stop("criteria_not_met");
  }
  const refs=t.referenceTimesSeconds || {};
  if (!Array.isArray(t.sampleTimesSeconds)||t.sampleTimesSeconds.length!==5
     ||!t.sampleTimesSeconds.every(n=>isNumber(n)&&n>0)) {
    missing("test.sampleTimesSeconds: five trials, 690-to-2070 kPa gauge");
  }
  for(const k of ["pgI","pgII","pgIII"]){
    if(!Array.isArray(refs[k])||refs[k].length!==5
       ||!refs[k].every(n=>isNumber(n)&&n>0))
      missing("test.referenceTimesSeconds."+k+": five trials");
  }
  if(r.missingEvidence.length)return stop("insufficient_evidence");
  const v={pgI:mean(refs.pgI),pgII:mean(refs.pgII),pgIII:mean(refs.pgIII)};
  if(!(v.pgI<v.pgII&&v.pgII<v.pgIII)){
    issue("INVALID_REFERENCE_ORDER","MTC 34.4.2.3-34.4.2.4","Reference times invalid/contradictory.");
    return stop("requires_expert_review");
  }
  const sample=mean(t.sampleTimesSeconds);
  if(sample<v.pgI)r.pgCandidate="I";
  else if(sample<=v.pgII)r.pgCandidate="II";
  else if(sample<=v.pgIII)r.pgCandidate="III";
  if(r.pgCandidate){r.classCandidate="5.1";return stop("criteria_met");}
  issue("O2_ABOVE_NITRIC_ACID","2.2.51.1.9; MTC 34.4.2.4.2(d)",
    "Pressure gate met but pressure rise time greater than 65% nitric acid comparator.");
  return stop("criteria_not_met");
}
module.exports={evaluateClass51,TEST_METHODS,EDITION};
