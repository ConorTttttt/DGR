'use strict';
// ADR 2025 Class 4.3 provisional intrinsic-criteria candidate evaluator.
// Pure, deterministic; no CLP/GHS mapping, UN assignment, release or automatic evidence authentication.
function evaluateClass43(input) {
  "use strict";
  // Exact fixed-point comparison: no binary-float rounding at ADR cut-offs.
  function compareDecimal(a,b) {
    const x=String(a), y=String(b), valid=/^(0|[1-9]\d*)(\.\d+)?$/;
    if (!valid.test(x)||!valid.test(y)) return NaN;
    const xf=(x.split(".")[1]||"").length, yf=(y.split(".")[1]||"").length;
    const dp=Math.max(xf,yf);
    const xi=BigInt(x.replace(".",""))*10n**BigInt(dp-xf);
    const yi=BigInt(y.replace(".",""))*10n**BigInt(dp-yf);
    return xi>yi?1:xi<yi?-1:0;
  }
  const ADR = "ADR2025_ECE_TRANS_352_VOL_I";
  const MTC = "UN_MTC_REV8_PART_III";
  const cite = (clause, source_id = ADR) => ({ source_id, clause });
  const citations = [cite("2.2.43.1.1"), cite("2.2.43.1.4"), cite("2.2.43.1.5"), cite("33.5.4.4", MTC)];
  const sample = input && typeof input.sample_id === "string" && input.sample_id.trim() ? input.sample_id.trim() : "UNSPECIFIED";
  const evidenceId = "class43-n5:" + sample;
  const out = {
    module_id: "agent6.adr2025.class43.v0.1.0",
    hazard_class: "4.3",
    coverage_status: "incomplete",
    criteria_status: "indeterminate",
    evidence_ids: [],
    references: citations,
    primary_class_candidates: [],
    subsidiary_risk_candidates: [],
    packing_group_candidates: [],
    exclusions: [],
    unresolved_evidence: [],
    expert_decision_ids: [],
    limitations: [
      "PROVISIONAL: not independently reviewed or suitable for SDS Section 14 release",
      "No final UN number, classification code, proper shipping name or Table A packing group",
      "Refer multi-hazard precedence to Agent 0 / precedence agent; Table A and special provisions require separate review"
    ],
    rule_ids: []
  };
  const issue = (field_id, reason, detail) => out.unresolved_evidence.push({ field_id, reason, detail });
  const mark = rule => { if (!out.rule_ids.includes(rule)) out.rule_ids.push(rule); };
  const report = input && input.test_report;
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    issue("input", "missing", "Structured input object is required"); return out;
  }
  if (!input.sample_id || typeof input.sample_id !== "string") issue("sample_id", "missing", "Sample identity required");
  if (!report || typeof report !== "object" || !report.document_id || !report.locator ||
      !/^[a-f0-9]{64}$/.test(report.sha256 || "") || !report.issuer ||
      report.sample_id !== input.sample_id) {
    issue("test_report", "reference_unverified", "Sample-linked laboratory document ID, issuer, locator and 64-character SHA-256 required");
  } else out.evidence_ids.push(evidenceId);
  const material = input.material || {};
  if (!["substance", "mixture", "article"].includes(material.kind)) issue("material.kind", "missing", "Specify substance, mixture or article");
  if (!["solid", "liquid"].includes(material.form)) issue("material.form", "other", "N.5 module covers solids/liquids; article routing is separate");
  if (material.kind === "article") { mark("ADR43_ARTICLE_GATE"); issue("material.kind", "other", "Articles require named-entry and content-specific review; do not classify article from bulk N.5"); }
  if (material.kind === "mixture") {
    mark("ADR43_MIXTURE_ACTUAL_DANGER");
    if (material.whole_mixture_tested !== true || material.commercial_mixture_confirmed !== true)
      issue("material.whole_mixture_tested", "other", "Whole commercial mixture required; no constituent-only or CLP/GHS derivation (ADR 2.2.43.1.6, 2.1.3)");
  }
  if (material.pyrophoric === "yes") {
    mark("ADR43_PYROPHORIC_PROHIBITION");
    issue("material.pyrophoric", "method_invalid", "ADR 2.2.43.1.3 says N.5 method shall not apply to pyrophoric substances; MTC 33.5.3.1 offers a nitrogen procedure. Refer to Class 4.2, Lead and expert review.");
  } else if (material.pyrophoric !== "no") issue("material.pyrophoric", "missing", "Documented pyrophoric screening needed before using N.5 under ADR");
  if (material.organometallic === "yes") {
    mark("ADR43_ORGANOMETALLIC_ROUTE");
    issue("material.organometallic", "other", "ADR 2.3.5 flowchart / N.1-N.5 and other class candidates require separate joint review");
  }
  if (input.conflicting_evidence === true) issue("conflicting_evidence", "conflicting", "Conflicting reports cannot be silently reconciled");
  if (input.experience_more_stringent === true) {
    mark("ADR43_EXPERIENCE");
    issue("experience_more_stringent", "other", "ADR 2.2.43.1.4 and 2.1.3.1 require more stringent experience to be considered; expert determination outstanding");
  }
  const test = input.test || {};
  if (test.method !== "MTC_REV8_N5") issue("test.method", "method_invalid", "UN MTC Rev.8 Part III 33.5.4 Test N.5 required");
  if (test.sample_commercial_form !== true) issue("test.sample_commercial_form", "method_invalid", "Commercial form testing required by MTC 33.5.3.1");
  if (test.temperature_c !== 20) issue("test.temperature_c", "method_invalid", "Test N.5 prescribed distilled water / ambient 20 °C");
  if (test.atmospheric_pressure !== true) issue("test.atmospheric_pressure", "method_invalid", "N.5 terminal repeats require atmospheric pressure");
  if (test.distilled_water !== true) issue("test.distilled_water", "method_invalid", "N.5 steps require distilled water");
  if (test.atmosphere !== "air") issue("test.atmosphere", "method_invalid", "Air required for non-pyrophoric N.5; nitrogen route requires ADR conflict review");
  const preliminary = Array.isArray(test.preliminary) ? test.preliminary : [];
  const order = ["trough", "filter_paper", "pile"];
  let ignition = false;
  let preliminaryValid = true;
  if (test.skip_preliminary === true) {
    mark("MTC_N5_KNOWN_NONVIOLENT_ROUTE");
    if (test.known_not_violent_documented !== true || preliminary.length !== 0) {
      preliminaryValid = false;
      issue("test.skip_preliminary", "method_invalid", "N.5 §33.5.4.3.1 skip requires supported known-nonviolent condition and no conflicting stages");
    }
  } else {
    if (preliminary.length === 0) {
      preliminaryValid = false;
      issue("test.preliminary", "missing", "Trough, filter paper and pile steps required unless justified skip");
    }
    let stopAtIgnition = false;
    preliminary.forEach((s,i) => {
      if (stopAtIgnition || s.stage !== order[i] ||
          !["yes", "no"].includes(s.gas_evolved) ||
          !["yes", "no"].includes(s.spontaneous_gas_ignition)) {
        preliminaryValid = false;
        return;
      }
      if (s.spontaneous_gas_ignition === "yes") { ignition = true; stopAtIgnition = true; }
    });
    if (!ignition && preliminary.length !== 3) preliminaryValid = false;
    if (!preliminaryValid) issue("test.preliminary", "method_invalid", "Stages must be ordered trough/filter_paper/pile, with explicit observations; stop after first ignition");
  }
  if (material.form === "solid" && !ignition) {
    const fines = Number(test.fines_under_500um_mass_percent);
    if (test.fines_under_500um_mass_percent === undefined ||
        !Number.isFinite(fines) || fines < 0 || fines > 100 || typeof test.friable !== "boolean") {
      issue("test.solid_particle_preparation", "missing", "Record <500 μm fraction (%) and friability (N.5 §33.5.4.3.5)");
    } else if ((compareDecimal(test.fines_under_500um_mass_percent, "1") > 0 || test.friable === true) && test.ground_before_terminal !== true) {
      issue("test.ground_before_terminal", "method_invalid", "Grind entire sample when fraction <500 μm exceeds 1% mass or material is friable");
    }
  }
  if (out.unresolved_evidence.length) return out;
  mark("ADR43_ELIGIBILITY");
  const classified = () => {
    out.criteria_status = "criteria_met";
    out.coverage_status = "incomplete";
    out.primary_class_candidates.push({
      candidate_id: "agent6:class43:" + sample, hazard_class: "4.3",
      evidence_ids: [evidenceId],
      references: [cite("2.2.43.1.5"), cite("33.5.4.4.1", MTC)]
    });
  };
  const pg = (value, adrClause, mtcClause) => {
    out.packing_group_candidates.push({
      candidate_id: "agent6:class43:pg:" + sample + ":" + value,
      value, evidence_ids: [evidenceId],
      references: [cite(adrClause), cite(mtcClause, MTC)],
      limitation: "INTRINSIC N.5 PG CANDIDATE ONLY; verify applicability and PG against a uniquely matched ADR 2025 Table A row, named entry, SPs and multi-hazard precedence"
    });
    out.coverage_status = "evaluated";
  };
  const appendSubsidiary = () => {
    for (const h of (Array.isArray(input.other_class_findings) ? input.other_class_findings : [])) {
      if (!h || h.status !== "criteria_met" || !["3", "4.1", "4.2", "5.1", "6.1", "8"].includes(h.hazard_class) ||
          typeof h.evidence_id !== "string" || !h.evidence_id.trim()) continue;
      out.subsidiary_risk_candidates.push({
        candidate_id: "agent6:class43:subsidiary:" + sample + ":" + h.hazard_class,
        hazard_class: h.hazard_class, evidence_ids: [h.evidence_id],
        references: [cite("2.2.43.1.2"), cite("2.1.3.5.3"), cite("2.1.3.10")]
      });
    }
    if (material.form === "solid" && out.subsidiary_risk_candidates.some(x=>x.hazard_class==="5.1")) {
      mark("ADR43_UN3133_CARRIAGE_PROHIBITION_GATE");
      issue("carriage_acceptance", "other", "Potential water-reactive oxidizing solid; if UN 3133 actually assigned, ADR §2.2.43.2 prohibits carriage unless Class 1 requirements are met. No UN number assigned here.");
    }
  };
  if (ignition) {
    mark("ADR43_SPONTANEOUS_GAS_IGNITION");
    classified();
    appendSubsidiary();
    if (test.reacts_vigorously_at_ambient === true && test.general_spontaneous_ignition_tendency === true) {
      mark("ADR43_PG_I_VIGOROUS");
      pg("I", "2.2.43.1.8(a)", "33.5.4.4.2");
    } else issue("packing_group.I", "missing", "Ignition establishes class criterion, but PG I additionally requires vigorous reaction and general ignition tendency or >=10 L/kg over any one-minute period");
    return out;
  }
  const terminal = test.terminal;
  if (!terminal || !Array.isArray(terminal.runs) || terminal.runs.length !== 3) {
    issue("test.terminal.runs", "missing", "Three N.5 terminal repeats required without preliminary spontaneous ignition"); return out;
  }
  if (!["flammable","nonflammable","no_gas","unknown"].includes(terminal.gas_flammability)) {
    issue("test.terminal.gas_flammability", "missing", "Identify emitted gas flammability or document no gas");
    return out;
  }
  if (terminal.gas_flammability === "unknown") {
    issue("test.terminal.gas_flammability", "missing", "Unknown chemical identity requires flammability testing under N.5 §33.5.4.3.5"); return out;
  }
  const decimal = (v) => {
    if (typeof v !== "string" && typeof v !== "number") return NaN;
    if (!/^(0|[1-9]\d*)(\.\d+)?$/.test(String(v))) return NaN;
    return Number(v);
  };
  let maxHour = "0", maxMinute = "0", fullValid = true;
  for (const [i,run] of terminal.runs.entries()) {
    if (!run || !Array.isArray(run.hourly_rates_l_kg_h) || run.hourly_rates_l_kg_h.length !== 7 ||
        !Array.isArray(run.one_minute_volumes_l_kg) || run.one_minute_volumes_l_kg.length === 0) {
      fullValid = false; issue("test.terminal.runs["+i+"]", "missing", "Seven 1-hour rates and one-minute window evidence required for PG completeness"); continue;
    }
    const mass = decimal(run.sample_mass_g), volume = decimal(run.gas_volume_ml), hours = decimal(run.observed_hours);
    if (!Number.isFinite(mass) || compareDecimal(run.sample_mass_g, "0") <= 0 || compareDecimal(run.sample_mass_g, "25") > 0 ||
        !Number.isFinite(volume) || compareDecimal(run.gas_volume_ml, "0") < 0 ||
        (compareDecimal(run.gas_volume_ml, "0") > 0 && (compareDecimal(run.gas_volume_ml, "100") < 0 || compareDecimal(run.gas_volume_ml, "250") > 0)) ||
        !Number.isFinite(hours) || compareDecimal(run.observed_hours, "7") < 0 || compareDecimal(run.observed_hours, "120") > 0) {
      fullValid = false; issue("test.terminal.runs["+i+"].setup", "method_invalid", "Mass (0,25] g, target gas volume 100–250 ml if evolved, observed 7–120 h"); continue;
    }
    if (!["steady","decreasing","erratic","increasing"].includes(run.trend_at_7h)) {
      fullValid = false; issue("test.terminal.runs["+i+"].trend", "missing", "Record 7-hour trend"); continue;
    }
    if (["erratic","increasing"].includes(run.trend_at_7h) &&
        !(compareDecimal(run.observed_hours,"120") === 0 || (compareDecimal(run.observed_hours,"7") > 0 && run.extension_resolved_steady_or_decreasing === true && run.sufficient_data_for_group === true))) {
      fullValid = false; issue("test.terminal.runs["+i+"].extension", "method_invalid", "Erratic/increasing 7-hour trend requires extension up to five days or documented early resolution with sufficient evidence");
    }
    const hoursArray = run.hourly_rates_l_kg_h.map(decimal);
    const minuteArray = run.one_minute_volumes_l_kg.map(decimal);
    if ([...hoursArray, ...minuteArray].some(n=>!Number.isFinite(n) || n<0)) {
      fullValid = false; issue("test.terminal.runs["+i+"].measurements", "method_invalid", "Rates must be finite, nonnegative measured base-10 values"); continue;
    }
    for (const v of run.hourly_rates_l_kg_h) if (compareDecimal(v,maxHour)>0) maxHour=String(v);
    for (const v of run.one_minute_volumes_l_kg) if (compareDecimal(v,maxMinute)>0) maxMinute=String(v);
  }
  if (!fullValid) return out;
  mark("MTC_N5_COMPLETE_REPEATS");
  if (terminal.gas_flammability === "no_gas" && compareDecimal(maxHour, "0") !== 0) {
    issue("test.terminal.gas_flammability", "conflicting", "No-gas finding contradicts positive gas evolution"); return out;
  }
  if (terminal.gas_flammability === "nonflammable" || (terminal.gas_flammability === "no_gas" && compareDecimal(maxHour, "0") === 0)) {
    out.criteria_status = "criteria_not_met"; out.coverage_status="evaluated"; mark("ADR43_NEGATIVE_TEST"); return out;
  }
  if (compareDecimal(maxHour, "1") <= 0 && compareDecimal(maxMinute, "10") < 0) {
    out.criteria_status = "criteria_not_met"; out.coverage_status="evaluated";
    mark("ADR43_BOUNDARY_STRICT_GT_1"); return out;
  }
  // Any >=10 L/kg during one minute qualifies for Class 4.3 and the highest intrinsic PG.
  if (compareDecimal(maxMinute, "10") >= 0) {
    mark("ADR43_PG_I_MINUTE_INCLUSIVE");
    classified(); appendSubsidiary(); pg("I", "2.2.43.1.8(a)", "33.5.4.4.2"); return out;
  }
  if (compareDecimal(maxHour, "1") <= 0) {
    issue("test.terminal.measurement_consistency", "conflicting", "One-minute gas volume indicates class-positive rate but all hourly rates <=1; request expert review");
    return out;
  }
  mark("ADR43_HOURLY_GT_1");
  classified(); appendSubsidiary();
  if (compareDecimal(maxHour, "20") >= 0) {
    mark("ADR43_PG_II_HOURLY_INCLUSIVE");
    if (terminal.reactivity_behavior === "readily" && terminal.pg_I_absence_documented === true) {
      pg("II","2.2.43.1.8(b)","33.5.4.4.3");
    } else issue("packing_group.II", "missing", "PG II needs readily reacting behaviour and affirmative documentary exclusion of PG I");
  } else {
    mark("ADR43_PG_III_HOURLY_STRICT_GT_1");
    if (terminal.reactivity_behavior === "slowly" &&
        terminal.pg_I_absence_documented === true && terminal.pg_II_absence_documented === true) {
      pg("III","2.2.43.1.8(c)","33.5.4.4.4");
    } else issue("packing_group.III", "missing", "PG III needs slowly reacting behaviour plus documented exclusion of PG I and II");
  }
  return out;
}
module.exports = { evaluateClass43 };
