"""Fail-closed ADR 2025 integration router. Engineering policy only; no legal classification."""
import json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent
CLASSES = ("1","2","3","4.1","4.2","4.3","5.1","5.2","6.1","6.2","7","8","9")

def result(state, stage, issues, trace):
    return {
        "contract_version": "0.1.0", "state": state, "next_stage": stage,
        "publishable": False,
        "blocking_issues": [{"code": k, "detail": v} for k,v in sorted(set(issues))],
        "trace": [{"step": s, "state": v, "details": d} for s,v,d in trace],
    }

def blocked(issues, trace):
    return result("BLOCKED", "none", issues, trace)

def ready(state, stage, trace):
    return result(state, stage, [], trace)

def citation_issues(packet, registered):
    errors = []
    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("references", "row_source_reference"):
                    for citation in value if isinstance(value,list) else [value]:
                        if citation["source_id"] not in registered:
                            errors.append(("UNKNOWN_SOURCE", path + "/" + key))
                walk(value, path + "/" + key)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path + "/" + str(i))
    walk(packet, "$")
    return errors

def route(packet: Any, schema=None, registry=None):
    """Pure deterministic next-stage decision. NEVER returns publishable classification."""
    if schema is None:
        schema = json.loads((ROOT/"schemas/integration_packet.schema.json").read_text())
    if registry is None:
        registry = json.loads((ROOT/"reference_registry.json").read_text())
    trace, issues = [], []
    errors = sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(packet),
                    key=lambda e: ("/".join(map(str,e.path)),e.message))
    if errors:
        return blocked([("INVALID_PACKET", "/".join(map(str,e.path))+": "+e.message) for e in errors],
                       [("contract","blocked","Invalid JSON Schema packet")])
    trace.append(("contract","passed","Versioned JSON Schema packet"))
    if registry["source_set_id"] != packet["regulatory_context"]["source_set_id"]:
        issues.append(("SOURCE_SET_MISMATCH","Unpinned source set"))
    if registry["edition_id"] != packet["regulatory_context"]["edition_id"]:
        issues.append(("EDITION_MISMATCH","Incompatible edition"))
    issues.extend(citation_issues(packet, {s["source_id"] for s in registry["sources"]}))
    evidence = {e["evidence_id"]:e for e in packet["evidence"]}
    if len(evidence) != len(packet["evidence"]):
        issues.append(("DUPLICATE_EVIDENCE","Duplicate evidence_id"))
    for e in packet["evidence"]:
        if e["state"] in ("known","explicit_negative") and not e.get("source_documents"):
            issues.append(("MISSING_PRIMARY_EVIDENCE",e["evidence_id"]))
    classes = {c["hazard_class"]:c for c in packet["class_evaluations"]}
    if len(classes) != len(packet["class_evaluations"]):
        issues.append(("DUPLICATE_CLASS","Duplicated class module"))
    for cl in sorted(set(CLASSES)-set(classes)):
        issues.append(("UNASSESSED_CLASS",cl))
    primary = {}
    for c in packet["class_evaluations"]:
        cl = c["hazard_class"]
        if c["coverage_status"] in ("not_assessed","incomplete") or c["criteria_status"]=="indeterminate":
            issues.append(("CLASS_UNRESOLVED",cl))
        if c["unresolved_evidence"]:
            issues.append(("UNRESOLVED_EVIDENCE",cl))
        if c["coverage_status"] in ("evaluated","not_applicable") and (not c["references"] or not c["evidence_ids"]):
            issues.append(("CLASS_WITHOUT_SUPPORT",cl))
        for evid in c["evidence_ids"]:
            if evid not in evidence or evidence[evid]["state"] in ("unknown","not_measured","conflicting"):
                issues.append(("UNRELIABLE_EVIDENCE",cl+"/"+evid))
        for cand in c["primary_class_candidates"]:
            if cand["hazard_class"] != cl:
                issues.append(("PRIMARY_CLASS_MISMATCH",cand["candidate_id"]))
            if any(e not in evidence for e in cand["evidence_ids"]):
                issues.append(("CANDIDATE_EVIDENCE_MISSING",cand["candidate_id"]))
        for pg in c["packing_group_candidates"]:
            if any(e not in evidence for e in pg["evidence_ids"]):
                issues.append(("PG_EVIDENCE_MISSING",pg["candidate_id"]))
        if c["criteria_status"] == "criteria_met":
            if not c["primary_class_candidates"]:
                issues.append(("POSITIVE_WITHOUT_PRIMARY_CANDIDATE",cl))
            for cand in c["primary_class_candidates"]:
                if cand["candidate_id"] in primary:
                    issues.append(("DUPLICATE_CANDIDATE",cand["candidate_id"]))
                primary[cand["candidate_id"]] = cand
        elif c["primary_class_candidates"]:
            issues.append(("UNEXPECTED_PRIMARY_CANDIDATE",cl))
        if c["criteria_status"] == "exception_applies" and not any(
                x["status"]=="applies" and x["effect_scope"] in ("class_criterion","classification")
                for x in c["exclusions"]):
            issues.append(("EXCEPTION_WITHOUT_BASIS",cl))
    trace.append(("class_screen","checked","13 class pathways; positives, negatives, exceptions, unknowns"))
    expert = {d["decision_id"]:d for d in packet["expert_decisions"]}
    if len(expert)!=len(packet["expert_decisions"]):
        issues.append(("DUPLICATE_EXPERT_DECISION","Duplicate decision_id"))
    for d in packet["expert_decisions"]:
        if d["state"]!="approved" or d["verification_state"]!="externally_verified":
            issues.append(("EXPERT_DECISION_UNRESOLVED",d["decision_id"]))
    for c in packet["class_evaluations"]:
        for did in c["expert_decision_ids"]:
            if did not in expert:
                issues.append(("EXPERT_DECISION_MISSING",did))
    if any(s=="rejected" for s in packet["release_checks"].values()):
        issues.append(("RELEASE_REVIEW_REJECTED","External review rejected"))
    if issues:
        return blocked(issues,trace)
    if not primary:
        n=packet["negative_scope"]
        if (n["state"]!="independently_reviewed" or not n["all_pathways_accounted_for"]
                or not n["named_entries_checked"] or not n["references"]
                or n.get("expert_decision_id") not in expert):
            return blocked([("NEGATIVE_SCOPE_UNPROVEN","Exhaustive independently verified negative and named-entry screening missing")],trace)
        trace.append(("negative_scope","review_required","No global non-dangerous conclusion is emitted"))
        return ready("READY_FOR_RELEASE_REVIEW","external_review",trace)
    p=packet["precedence"]
    if p["state"]=="conflict":
        return blocked([("PRECEDENCE_CONFLICT","Resolution conflict")],trace)
    if p["state"]=="not_started":
        trace.append(("precedence","delegated","ADR 2.1.3.5 / 2.1.3.10 resolver, not Agent 0"))
        return ready("READY_FOR_PRECEDENCE","precedence",trace)
    chosen=p["primary_candidate_id"]
    if chosen not in primary:
        return blocked([("PRECEDENCE_SELECTION_INVALID","Unknown positive primary candidate")],trace)
    if p["state"]=="not_required" and len(primary)!=1:
        return blocked([("PRECEDENCE_REQUIRED","Multiple primary candidates")],trace)
    if p["state"]=="resolved" and not p["references"]:
        return blocked([("PRECEDENCE_BASIS_MISSING","Exact clause reference needed")],trace)
    if p.get("expert_decision_id") and p["expert_decision_id"] not in expert:
        return blocked([("PRECEDENCE_APPROVAL_MISSING","Missing expert decision")],trace)
    trace.append(("precedence","checked","No regulatory precedence matrix computed by Lead"))
    a=packet["assignment"]
    if a["state"]=="conflict":
        return blocked([("UN_ASSIGNMENT_CONFLICT","Named/Table A conflict")],trace)
    if a["state"] in ("not_started","candidates_only"):
        trace.append(("assignment","delegated","Agent 4 Table A row screening"))
        return ready("READY_FOR_ASSIGNMENT","assignment",trace)
    if not a["candidate_set_complete"] or a.get("named_entry_screening")!="complete":
        return blocked([("ROW_SCREENING_UNPROVEN","Table A and named entries not exhaustively checked")],trace)
    if a["assigned_class"] != primary[chosen]["hazard_class"]:
        return blocked([("ROW_CLASS_CONFLICT","Selected primary differs from row class")],trace)
    if a["packing_group_consistency"] in ("unchecked","mismatch"):
        return blocked([("PG_TABLE_A_UNRESOLVED","PG not checked against row")],trace)
    pg_candidates={g["value"] for c in packet["class_evaluations"] if c["hazard_class"]==a["assigned_class"] for g in c["packing_group_candidates"]}
    if a["packing_group_consistency"]=="matched" and (not a.get("selected_packing_group") or a["selected_packing_group"] not in pg_candidates):
        return blocked([("PG_CANDIDATE_CONFLICT","Selected Table A PG unsupported by criterion candidate")],trace)
    if a["packing_group_consistency"]=="not_applicable" and a.get("selected_packing_group") is not None:
        return blocked([("PG_NOT_APPLICABLE_CONFLICT","PG selected despite not-applicable assertion")],trace)
    trace.append(("table_a","checked","Unique row, class, named entry, PG consistency"))
    if a["special_provision_assessment"]=="conflict" or any(s["state"]=="conflict" for s in a["special_provision_outcomes"]):
        return blocked([("SP_CONFLICT","Contradictory special provision")],trace)
    if (a["special_provision_assessment"] in ("not_started","incomplete") or
        any(s["state"]=="unresolved" for s in a["special_provision_outcomes"])):
        trace.append(("special_provisions","delegated","Agent 1/4 must resolve all row SP codes"))
        return ready("READY_FOR_SPECIAL_PROVISIONS","special_provisions",trace)
    trace.append(("release","external_review_required","No authenticated external sign-off mechanism; publishable=false"))
    return ready("READY_FOR_RELEASE_REVIEW","external_review",trace)

if __name__=="__main__":
    import sys
    print(json.dumps(route(json.loads(Path(sys.argv[1]).read_text())),indent=2,sort_keys=True))
