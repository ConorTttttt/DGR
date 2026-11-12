"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { evaluateClass51 } = require("./classify.js");
const repeat = (n) => Array(5).fill(n);
function base(method) {
  return {physicalState:method==="O.2"?"liquid":"solid",
    explosiveScreening:"negative",knownExperienceConflict:false,
    test:{method, reportId:"SYNTHETIC-DO-NOT-USE", laboratory:"test-fixture",
      sampleId:"fixture-only",manualEdition:"Rev.8", protocolConformant:true,
      referencesConformant:true,testConditionsConformant:true,
      sampleRepresentative:true,uncertaintyResolved:true}};
}
function o1(time4=25,time1=90){
 const x=base("O.1");
 x.test.references={pgI:{burnTimesSeconds:repeat(10)},
   pgII:{burnTimesSeconds:repeat(30)},pgIII:{burnTimesSeconds:repeat(70)}};
 x.test.sampleRatios={
  "4:1":{ignited:true,burnTimesSeconds:repeat(time4)},
  "1:1":{ignited:true,burnTimesSeconds:repeat(time1)}};
 return x;
}
function o3(rate4=1.5,rate1=0.5) {
 const x=base("O.3");
 const run=n=>({burnRatesGPerS:repeat(n),rSquared:repeat(0.99),
   relativeStdDevPercent:0,massLossTraceVerified:true});
 x.test.references={pgI:run(4),pgII:run(2),pgIII:run(1)};
 x.test.sampleRatios={"4:1":{ignited:true,...run(rate4)},
     "1:1":{ignited:true,...run(rate1)}};
 return x;
}
function o2(seconds=25,pressure=2070) {
 const x=base("O.2");
 x.test.spontaneousIgnition=false;
 x.test.peakPressureRiseKpaGauge=pressure;
 x.test.referenceTimesSeconds={pgI:repeat(10),pgII:repeat(30),pgIII:repeat(70)};
 x.test.sampleTimesSeconds=repeat(seconds);
 return x;
}
const check=(inp,status,pg=null,cls=null)=>{
 const r=evaluateClass51(inp);
 assert.equal(r.status,status,JSON.stringify(r.issues));
 assert.equal(r.pgCandidate,pg);
 assert.equal(r.classCandidate,cls);
 assert.equal(r.finalPackingGroup,null);
 assert.equal(r.finalUNNumber,null);
 assert.equal(r.tableARowId,null);
 assert.equal(r.blockingForAssignment,true);
 return r;
};
test("O.1: strict PG I and inclusive II/III boundaries (seven synthetic cases)",()=>{
 for(const [value,pg] of [[9.999,"I"],[10,"II"],[10.001,"II"],
   [29.999,"II"],[30,"II"],[30.001,"III"],[70,"III"]])
   check(o1(value),"criteria_met",pg,"5.1");
});
test("O.1: one favorable 1:1 ratio can control PG",()=>{
 check(o1(80,9),"criteria_met","I","5.1");
});
test("O.1: both verified non-ignitions produce only method-limited negative",()=>{
 const x=o1(100,100);
 for(const r of ["4:1","1:1"]) x.test.sampleRatios[r]=
   {ignited:false,fiveNonIgnitionsVerified:true};
 check(x,"criteria_not_met");
});
test("O.1: ignited but slower than PG III is held for review",()=>{
 const r=check(o1(71,72),"requires_expert_review",null,"5.1");
 assert.ok(r.issues.some(x=>x.code==="O1_IGNITION_WITHOUT_PG"));
});
test("O.1: missing ratio, missing trials and inverted reference gate",()=>{
 const x=o1();delete x.test.sampleRatios["1:1"];
 check(x,"insufficient_evidence");
 const y=o1();y.test.sampleRatios["4:1"].burnTimesSeconds=[1,1];
 check(y,"insufficient_evidence");
 const z=o1();z.test.references.pgII.burnTimesSeconds=repeat(5);
 check(z,"requires_expert_review");
});
test("O.3: strict PG I, inclusive II/III, negative and ratio comparison",()=>{
 for(const [val,status,pg,cls] of [
  [4.0001,"criteria_met","I","5.1"],[4,"criteria_met","II","5.1"],
  [3.999,"criteria_met","II","5.1"],[2,"criteria_met","II","5.1"],
  [1.999,"criteria_met","III","5.1"],[1,"criteria_met","III","5.1"],
  [0.999,"criteria_not_met",null,null]])
    check(o3(val,0.2),status,pg,cls);
 check(o3(0.5,4.01),"criteria_met","I","5.1");
});
test("O.3: both ratios explicitly non-igniting gives method negative",()=>{
 const x=o3();
 for(const k of ["4:1","1:1"])x.test.sampleRatios[k]=
   {ignited:false,fiveNonIgnitionsVerified:true};
 check(x,"criteria_not_met");
});
test("O.3: invalid R2, standard deviation, absent trace reject",()=>{
 for(const field of ["rSquared","relativeStdDevPercent","massLossTraceVerified"]){
   const x=o3();
   x.test.sampleRatios["4:1"][field]=field==="rSquared"?repeat(0.89)
      :field==="relativeStdDevPercent"?20.001:false;
   check(x,"insufficient_evidence");
 }
 const x=o3();x.test.sampleRatios["1:1"].relativeStdDevPercent=20;
 check(x,"criteria_met","III","5.1");
});
test("O.2: strict PG I, inclusive II/III and negative > nitric acid",()=>{
 for(const [v,status,pg,cl] of [
  [9.999,"criteria_met","I","5.1"],[10,"criteria_met","II","5.1"],
  [29.999,"criteria_met","II","5.1"],[30,"criteria_met","II","5.1"],
  [30.001,"criteria_met","III","5.1"],[70,"criteria_met","III","5.1"],
  [70.001,"criteria_not_met",null,null]])
    check(o2(v),status,pg,cl);
});
test("O.2: pressure 2070 inclusive; 2069.999 negative",()=>{
 check(o2(5,2070),"criteria_met","I","5.1");
 check(o2(5,2069.999),"criteria_not_met");
});
test("O.2: spontaneous ignition is PG I without pressure time runs",()=>{
 const x=base("O.2");x.test.spontaneousIgnition=true;
 check(x,"criteria_met","I","5.1");
});
test("O.2: missing pressure/time and inverted calibration",()=>{
 const x=o2();delete x.test.peakPressureRiseKpaGauge;check(x,"insufficient_evidence");
 const y=o2();y.test.sampleTimesSeconds=[20,20];check(y,"insufficient_evidence");
 const z=o2();z.test.referenceTimesSeconds.pgI=repeat(50);
 check(z,"requires_expert_review");
});
test("missing report controls and method/physical-state mismatch",()=>{
 const x=o1();delete x.test.reportId;check(x,"insufficient_evidence");
 const y=o1();y.test.method="O.2";check(y,"requires_expert_review");
 const z=o1();z.test.method="O.4";check(z,"requires_expert_review");
 const a=o1();a.test.uncertaintyResolved=false;check(a,"insufficient_evidence");
 const b=o1();b.test.manualEdition="Rev.7";check(b,"requires_expert_review");
});
test("mixtures require as-presented evidence, not component-weighting",()=>{
 const x=o1();x.isMixture=true;check(x,"insufficient_evidence");
 x.formulationAsPresentedTested=true;check(x,"criteria_met","II","5.1");
});
test("GHS shortcuts, known-experience conflict and explosive-screen hold",()=>{
 const a=o1();a.sourceOfClassification="GHS";check(a,"requires_expert_review");
 const b=o1();b.knownExperienceConflict=true;check(b,"requires_expert_review");
 const c=o1();c.explosiveScreening="positive";check(c,"requires_expert_review");
 const d=o1();c.explosiveScreening="unknown"; d.explosiveScreening="unknown";
 check(d,"insufficient_evidence");
});
test("unstable, combined hazards and separate subsidiary candidates",()=>{
 const x=o3();x.chemicallyUnstable=true;
 check(x,"not_accepted_for_carriage");
 const y=o3();y.otherHazards={selfHeating:true,toxic:true};
 const r=check(y,"not_accepted_for_carriage");
 assert.deepEqual(r.subsidiaryCandidates.sort(),["4.2","6.1"]);
 const z=o3();z.otherHazards={corrosive:true,toxic:true};
 assert.deepEqual(check(z,"criteria_met","III","5.1").subsidiaryCandidates.sort(),["6.1","8"]);
});
test("ammonium nitrate combustibles strict >0.2% ban",()=>{
 const x=o1();x.composition={isAmmoniumNitrate:true,combustibleMassPercent:0.2};
 check(x,"criteria_met","II","5.1");
 x.composition.combustibleMassPercent=0.200001;
 check(x,"not_accepted_for_carriage");
 const y=o1();y.composition={isAmmoniumNitrate:true,combustibleMassPercent:0.4};
 y.class1ConstituentVerified=true;
 check(y,"requires_expert_review");
});
test("acid percent boundaries and ammonium salt mixture bans",()=>{
 const x=o2();x.composition={chemicalIdentity:"perchloric_acid_solution",massPercent:72};
 check(x,"criteria_met","II","5.1");
 x.composition.massPercent=72.0001;check(x,"not_accepted_for_carriage");
 const y=o2();y.composition={chemicalIdentity:"chloric_acid_solution",massPercent:10};
 check(y,"criteria_met","II","5.1");
 y.composition.massPercent=10.01;check(y,"not_accepted_for_carriage");
 const z=o1();z.composition={ammoniumSaltMixedWith:"hypochlorite"};
 check(z,"not_accepted_for_carriage");
});
test("non-stabilized peroxide and fluor exception require positive evidence",()=>{
 const a=o2();a.composition={chemicalIdentity:"hydrogen_peroxide",stabilized:false};
 check(a,"not_accepted_for_carriage");
 const b=o2();b.composition={chemicalIdentity:"hydrogen_peroxide_aqueous",stabilized:false,massPercent:60.01};
 check(b,"not_accepted_for_carriage");
 const c=o2();c.composition={isHalogenatedFluorCompound:true};
 check(c,"not_accepted_for_carriage");
 const d=o2();d.composition={isHalogenatedFluorCompound:true,verifiedNamedUN:"1745"};
 check(d,"criteria_met","II","5.1");
});
function fertilizer(exitBox,outcome="oxidizing_solid") {
 const x=base("O.1");x.composition={isSolidAmmoniumNitrateFertilizer:true};
 x.fertilizerRoute={exitBox,flowchartAudited:true,compositionVerified:true,
   series2NoExplosiveProperties:true,outcome,recordId:"synthetic"};
 return x;
}
test("Section39 forbidden fertilizer exits cannot be overridden by O.1",()=>{
 for(const box of [4,6,8,15,31,33])check(fertilizer(box),"not_accepted_for_carriage");
});
test("Section39 authority-limited exits and verified exception are non-final",()=>{
 for(const box of [20,23,39])check(fertilizer(box),"not_accepted_for_carriage");
 const x=fertilizer(20);Object.assign(x.fertilizerRoute,{
   suitabilityForCarriageDemonstrated:true,competentAuthorityApprovalVerified:true,
   approvedClass:"5.1",approvedUNIs2067:false});
 check(x,"requires_expert_review",null,"5.1");
});
test("Section39 fertilizer 5.1 / Class9 / Class1 and missing series2",()=>{
 const a=fertilizer(36);check(a,"criteria_met",null,"5.1");
 const b=fertilizer(27,"class9");check(b,"criteria_not_met");
 const c=fertilizer(10,"class1");check(c,"requires_expert_review");
 const d=fertilizer(36);delete d.fertilizerRoute.series2NoExplosiveProperties;
 check(d,"insufficient_evidence");
 const e=fertilizer(36);delete e.fertilizerRoute.flowchartAudited;
 check(e,"insufficient_evidence");
});
test("articles and absence of evidence remain blocked, not harmless",()=>{
 const a=o1();a.isArticle=true;check(a,"requires_expert_review");
 const b={physicalState:"solid",explosiveScreening:"negative"};check(b,"insufficient_evidence");
 const c={physicalState:"solid"};check(c,"insufficient_evidence");
 const d=o1();d.physicalState="gas";check(d,"requires_expert_review");
});
