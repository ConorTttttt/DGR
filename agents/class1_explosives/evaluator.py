"""ADR 2025 Class 1: document/decision gate only, not autonomous explosives classification.
Regulatory verification and competent-authority approval are external trust services.
"""
from copy import deepcopy

CLAUSES = {
    "scope": "2.2.1.1.1", "suspected": "2.2.1.1.2",
    "entry": "2.2.1.1.3", "code": "2.2.1.1.4",
    "division": "2.2.1.1.5", "group": "2.2.1.1.6",
    "fireworks": "2.2.1.1.7.2", "exclusion": "2.2.1.1.8.1",
    "authority": "2.2.1.1.9.1", "nonacceptance": "2.2.1.2.1",
    "group_k": "2.2.1.2.2", "row": "3.2.1", "sp": "3.3.1",
    "tests": "2.3.0", "oxidizer": "2.1.3.7",
}
GROUPS = set("ABCDEFGHJKLNS")
DIVISIONS = {"1.1", "1.2", "1.3", "1.4", "1.5", "1.6"}
BLOCKERS = {"indeterminate", "authority_required", "prohibited_for_carriage", "conflict", "unsupported"}

def evaluate(req):
    if req.get("regime") != "ADR" or req.get("edition") != "2025":
        raise ValueError("ADR 2025 only; no edition fallback")
    evidence = req.get("evidence", [])
    evidence_by_id = {e["id"]: e for e in evidence if isinstance(e, dict) and e.get("id")}
    auth = req.get("authority", {})
    c = req.get("candidate", {})
    flags = set(req.get("cross_class_flags", []))
    sp = deepcopy(req.get("special_provisions", []))
    used = {"scope", "suspected", "code", "division", "group"}
    result = {
        "schema_version": "1.0.0-rc1", "assessment_id": req["assessment_id"],
        "regime": "ADR", "edition": "2025", "class": "1", "rule_id": "ADR25-C1-GATE",
        "status": "indeterminate", "primary_class_candidates": [], "subsidiary_risks": [],
        "packing_group_candidates": [], "exclusions": [], "unresolved_evidence": [],
        "expert_decisions": [], "table_a_candidates": [],
        "special_provision_outcomes": sp, "evidence_refs": deepcopy(evidence),
        "clause_refs": [], "assignment_permitted": False, "requires_independent_review": True,
    }
    if auth.get("decision_id"):
        result["expert_decisions"].append({
            "id": auth["decision_id"], "decision_type": "class1_classification_or_exclusion",
            "status": auth.get("status", "pending"),
            "authority_reference": auth.get("document_ref"),
            "verification": auth.get("verification", "unverified"),
        })
    if c.get("table_a_row_id") and c.get("un_number"):
        result["table_a_candidates"].append({
            "row_id": c["table_a_row_id"], "un_number": c["un_number"],
            "status": c.get("table_a_row_status", "provisional"), "source_clause": "3.2.1",
        })
    def done(status, reason=None, *clause_keys):
        used.update(clause_keys)
        result["status"] = status
        if reason:
            result["unresolved_evidence"].append({
                "id": status, "reason": reason, "blocks_assignment": True,
            })
        result["clause_refs"] = [
            {"source_id": "adr2025_vol1_en", "clause": CLAUSES[x], "edition": "ADR 2025",
             "verification": "text_checked"} for x in sorted(used)
        ]
        return result
    def authority_valid():
        ref = auth.get("document_ref")
        return (auth.get("status") == "approved"
            and auth.get("verification") == "externally_verified"
            and auth.get("scope_matches") is True
            and bool(auth.get("decision_id")) and ref in evidence_by_id
            and evidence_by_id[ref].get("admissibility") == "verified")
    if flags.intersection({"unduly_sensitive", "spontaneous_reaction", "no_legal_table_a_entry"}):
        return done("prohibited_for_carriage", "Nonacceptance pathway asserted; independent validation required", "nonacceptance")
    if c.get("group") == "K":
        return done("prohibited_for_carriage", "Group K not accepted for carriage", "group_k")
    if any(x.get("status") == "prohibits" for x in sp):
        return done("prohibited_for_carriage", "Special provision prohibits carriage", "sp")
    screen = req.get("hazard_screen")
    if screen == "excluded_approved":
        used.update({"exclusion", "tests", "authority"})
        if not authority_valid():
            return done("authority_required", "External approval for Class 1 exclusion not verified")
        if not any(e.get("kind") == "test_report" and e.get("admissibility") == "verified" for e in evidence):
            return done("indeterminate", "Exclusion test basis missing")
        result["exclusions"].append({
            "scope": "Class 1 only; screen other ADR classes",
            "basis_clause": CLAUSES["exclusion"], "evidence_ids": [auth["document_ref"]],
            "authority_decision_id": auth["decision_id"],
        })
        return done("excluded_from_class")
    if screen in (None, "not_assessed"):
        return done("indeterminate", "No explosive-properties screen")
    if screen in ("suspected", "confirmed_no_explosive_properties"):
        return done("authority_required", "Potential or negative Class 1 evidence still needs validated exclusion route", "exclusion")
    if screen != "confirmed_explosive":
        return done("unsupported", "Unrecognized Class 1 scope")
    used.update({"entry", "tests", "authority", "row", "sp"})
    division, group = c.get("division"), c.get("group")
    if division not in DIVISIONS or group not in GROUPS:
        return done("indeterminate", "Division or compatibility group not established")
    if ((division == "1.5" and group != "D") or
        (division == "1.6" and group != "N") or
        (group == "N" and division != "1.6") or
        (group == "S" and division != "1.4")):
        return done("conflict", "Unsupported division/group combination")
    if not authority_valid():
        return done("authority_required", "Competent-authority written classification not authenticated")
    code = division + group
    if auth.get("approved_code") != code or auth.get("approved_un_number") != c.get("un_number"):
        return done("conflict", "Authority code or UN number disagrees")
    if auth.get("approved_row_id") != c.get("table_a_row_id"):
        return done("conflict", "Authority and Table A row mapping disagree")
    if c.get("table_a_row_status") != "source_verified" or not c.get("entry_is_applicable"):
        return done("indeterminate", "Exact applicable Table A row not independently verified")
    if c.get("n_o_s_or_sample") and not c.get("competent_authority_conditions_complete"):
        return done("authority_required", "Competent-authority conditions of carriage incomplete")
    if req.get("product_kind") == "sample" and c.get("un_number") == "0190" and not c.get("n_o_s_or_sample"):
        return done("conflict", "UN 0190 sample approval pathway absent")
    if "fireworks_analogy" in flags:
        used.add("fireworks")
        if req.get("product_kind") != "pyrotechnic_article":
            return done("conflict", "Fireworks analogy for an incompatible article type")
        if "packaging_dependent" not in flags:
            return done("indeterminate", "Fireworks analogy packaging evidence absent")
    else:
        valid = {
            x.get("series") for x in req.get("test_series", [])
            if x.get("result") == "recorded" and x.get("assessed_by_expert") is True
            and evidence_by_id.get(x.get("evidence_id"), {}).get("admissibility") == "verified"
        }
        # Conservative *software* prerequisites, not a replacement for MTC test flow.
        needed = {"1.5": {"5", "6"}, "1.6": {"7"}}.get(division, {"6"})
        if not needed.issubset(valid):
            return done("indeterminate", "Appropriate expert-reviewed MTC test-series evidence absent")
    if any(x.get("status") in {"not_evaluated", "uncertain", "requires_authority"} for x in sp):
        return done("indeterminate", "Unresolved special-provision outcome")
    if not isinstance(c.get("un_number"), str) or len(c["un_number"]) != 4 or not c["un_number"].isdigit():
        return done("indeterminate", "Four-digit UN number missing")
    refs = [auth["document_ref"]] + [
        x.get("evidence_id") for x in req.get("test_series", []) if x.get("result") == "recorded"
    ]
    result["primary_class_candidates"].append({
        "class": "1", "classification_code": code, "division": division,
        "compatibility_group": group, "packing_group": None,
        "evidence_ids": list(dict.fromkeys(x for x in refs if x)),
        "authority_decision_id": auth["decision_id"], "status": "authority_confirmed",
    })
    return done("criteria_met")
