"""Agent 14 ADR 2025 hazard precedence: provisional, deterministic, fail-closed.

Integration input is Lead Agent v0.1.0 evidence-scoped class_evaluations;
Table A row selection remains solely with Agent 1 / Agent 4. No SDS release.
"""
from __future__ import annotations
import json
from itertools import permutations
from pathlib import Path
import re

MATRIX = json.loads((Path(__file__).parent / "precedence_matrix.json").read_text())
CLASSES = ("1","2","3","4.1","4.2","4.3","5.1","5.2","6.1","6.2","7","8","9")
NO_PG = {"1","2","5.2","6.2","7"}
SPECIAL_SUBTYPES = ("3","4.1","4.2")


def blocked(code, detail, trace=None, preliminary=None):
    return {"status":"BLOCKED", "publishable":False, "assignment_permitted":False,
            "primary_class":None, "packing_group":None, "un_number":None,
            "selected_table_a_row_id":None, "subsidiary_classes":[],
            "blocking_issues":[{"code":code,"detail":detail}],
            "provisional_precedence":preliminary, "trace":trace or [],
            "edition":"ADR-2025-EN", "review_state":"provisional_not_approved"}


def _evidence_ok(packet, evidence_id):
    e = next((e for e in packet.get("evidence",[])
              if isinstance(e,dict) and e.get("evidence_id")==evidence_id),None)
    return bool(e and e.get("state") in ("known","explicit_negative")
                and e.get("references") and e.get("source_documents")
                and e.get("review_state")!="rejected")


def _assertion(packet, item, states=("applies","does_not_apply")):
    return bool(isinstance(item,dict) and item.get("status") in states
                and item.get("evidence_ids")
                and all(_evidence_ok(packet,i) for i in item["evidence_ids"]))


def _screen(packet):
    if not isinstance(packet,dict) or packet.get("contract_version")!="0.1.0":
        return [],"Lead integration contract 0.1.0 required"
    r=packet.get("regulatory_context",{})
    if (r.get("regime"),r.get("edition_id"),r.get("source_set_id")) != (
        "ADR","ADR-2025-EN","adr2025-en-provisional-v1"):
        return [],"Edition / source set mismatch"
    ev=packet.get("evidence",[])
    if len(ev)!=len({x.get("evidence_id") for x in ev if isinstance(x,dict)}):
        return [],"Duplicate evidence"
    findings=packet.get("class_evaluations",[])
    if len(findings)!=13 or {f.get("hazard_class") for f in findings
                            if isinstance(f,dict)}!=set(CLASSES):
        return [],"Exactly 13 unique class screening records required"
    positives=[]
    ids=set()
    for f in findings:
        c=f["hazard_class"]
        if (f.get("coverage_status") not in ("evaluated","not_applicable")
                or f.get("criteria_status") not in (
                    "criteria_met","criteria_not_met","exception_applies")
                or f.get("unresolved_evidence") or not f.get("evidence_ids")
                or not f.get("references")
                or not all(_evidence_ok(packet,i) for i in f["evidence_ids"])):
            return [],f"{c}: incomplete, conflicting or unreferenced finding"
        if any("clp" in str(next(e for e in ev if e.get("evidence_id")==i).get(
                "method","")).lower() or "ghs" in str(next(e for e in ev if e.get(
                "evidence_id")==i).get("method","")).lower() for i in f["evidence_ids"]):
            return [],f"{c}: CLP/GHS cannot replace ADR class evidence"
        if f["criteria_status"]=="exception_applies" and not any(
                x.get("status")=="applies" and x.get("references")
                and x.get("evidence_ids") for x in f.get("exclusions",[])):
            return [],f"{c}: exception without cited supporting evidence"
        pc=f.get("primary_class_candidates",[])
        if f["criteria_status"]!="criteria_met":
            if pc:return [],f"{c}: nonpositive finding contains positive candidate"
            continue
        if len(pc)!=1:return [],f"{c}: exactly one positive candidate required"
        item=pc[0]
        cid=item.get("candidate_id")
        if (not cid or cid in ids or item.get("hazard_class")!=c
                or not item.get("evidence_ids") or not item.get("references")
                or not all(_evidence_ok(packet,i) for i in item["evidence_ids"])):
            return [],f"{c}: invalid/duplicate positive candidate"
        ids.add(cid)
        pgc=f.get("packing_group_candidates",[])
        pgvals={x.get("value") for x in pgc}
        if (len(pgvals)>1 or not pgvals.issubset({"I","II","III"})
                or any(not x.get("evidence_ids") or not x.get("references")
                       or not all(_evidence_ok(packet,i) for i in x["evidence_ids"])
                       for x in pgc)):
            return [],f"{c}: contradictory/unsupported PG candidates"
        if c in NO_PG and pgc:return [],f"{c}: numeric packing group not applicable"
        positives.append({"class":c,"pg":next(iter(pgvals)) if pgvals else None,
                          "candidate_id":cid,"origin_ids":[cid],
                          "rule_ids":f.get("rule_ids",[])})
    return sorted(positives,key=lambda x:CLASSES.index(x["class"])),None


def _row_key(x,ctx):
    c,g=x["class"],x["pg"]
    if c=="6.1" and g in ("I","II"):
        route=ctx.get("toxicity_route",{}).get("value")
        return f"6.1/{g}/{route}" if route in ("DERMAL","ORAL","INHAL") else None
    if c=="9":return None
    return f"{c}/{g}" if g else None


def _col_key(x,ctx):
    c,g=x["class"],x["pg"]
    if c=="6.1" and g=="I":
        route=ctx.get("toxicity_route",{}).get("value")
        return f"6.1/I/{route}" if route in ("DERMAL","ORAL") else None
    if c=="6.1" and g=="II":return "6.1/II"
    if c=="9":return "9/NA"
    return f"{c}/{g}" if g else None


def _cell(a,b,ctx):
    for left,right in ((a,b),(b,a)):
        r,c=_row_key(left,ctx),_col_key(right,ctx)
        row=MATRIX["rows"].get(r)
        if not row or c not in MATRIX["columns"]:continue
        ix=MATRIX["columns"].index(c)-row["start"]
        if not 0<=ix<len(row["values"]):continue
        v=row["values"][ix]
        locator=f"2.1.3.10/page107/{r}/{c}"
        if isinstance(v,dict):
            state=ctx.get("material_form",{}).get("value")
            if state not in ("SOL","LIQ"):
                return None,"PHYSICAL_FORM_UNKNOWN: distinguish solid from liquid"
            v=v[state]
        if v.endswith("*"):
            pest=ctx.get("pesticide",{}).get("status")
            if pest not in ("applies","does_not_apply"):
                return None,"PESTICIDE_FOOTNOTE_UNRESOLVED"
            v="6.1, III" if pest=="applies" else v[:-1]
            locator+="/footnote-a"
        m=re.fullmatch(r"(3|4\.1|4\.2|4\.3|5\.1|6\.1|8|9)(?:,\s*(I|II|III))?",v)
        if not m:return None,"INVALID_MATRIX_CELL: "+locator+" "+v
        cc,pg=m.groups()
        win=left if left["class"]==cc else right if right["class"]==cc else None
        if win is None:return None,"MATRIX_UNEXPECTED_CLASS: "+locator
        return {"class":cc,"pg":pg,"candidate_id":win["candidate_id"],
                "origin_ids":sorted(set(left["origin_ids"]+right["origin_ids"])),
                "rule_ids":sorted(set(left["rule_ids"]+right["rule_ids"]+
                                       ["A14-MATRIX:"+locator])),
                "cell":{"row":r,"column":c,"result":v,"locator":locator}},None
    return None,"MATRIX_INTERSECTION_MISSING: "+a["class"]+" vs "+b["class"]


def _fold(active,ctx):
    if len(active)>5:
        return None,"MATRIX_PERMUTATION_SCOPE_UNSUPPORTED: >5 hazards",[]
    outcomes={}
    for order in permutations(active):
        current=order[0]
        trail=[]
        for other in order[1:]:
            current,error=_cell(current,other,ctx)
            if error:return None,error,trail
            trail.append(current["cell"])
        key=(current["class"],current["pg"])
        outcomes.setdefault(key,(current,trail))
        if len(outcomes)>1:
            return None,"MATRIX_ORDER_CONTRADICTION: permutations disagree",trail
    result,trail=next(iter(outcomes.values()))
    return result,None,trail


def _precedence(packet,active,ctx):
    if not active:
        return None,"NO_GLOBAL_NEGATIVE: independent complete hazard review needed",[]
    if len(active)==1:
        return active[0],None,[{"rule_id":"A14-SINGLE","clause":"2.1.2.1"}]
    for c in SPECIAL_SUBTYPES:
        if any(a["class"]==c for a in active) and not _assertion(
                packet,ctx.get("absolute_subtypes",{}).get(c)):
            return None,"ABSOLUTE_SUBTYPE_UNRESOLVED: "+c,[]
    if any(a["class"]=="5.1" for a in active) and ctx.get(
            "oxidizer_explosive_screen")!="cleared":
        return None,"OXIDIZER_EXPLOSIVE_SCREEN_UNRESOLVED: 2.1.3.7",[]
    toxic=next((a for a in active if a["class"]=="6.1"),None)
    if toxic and toxic["pg"] in ("I","II") and not _assertion(
            packet,ctx.get("toxicity_route"),("known",)):
        return None,"TOXICITY_ROUTE_UNRESOLVED: 2.1.3.10",[]
    ranked=[]
    for a in active:
        c=a["class"]
        if c=="7":
            rec=ctx.get("radioactive_exception")
            if not _assertion(packet,rec):
                return None,"CLASS7_EXCEPTED_PACKAGE_UNRESOLVED: 2.1.3.5.3(a)",[]
            if rec["status"]=="applies":
                if rec.get("sp290_verified") is not True or rec.get("un3507") is not False:
                    return None,"SP290_UN3507_EXCEPTION_UNVERIFIED",[]
                continue
            ranked.append((0,a,"2.1.3.5.3(a)"))
        elif c=="1":ranked.append((1,a,"2.1.3.5.3(b)"))
        elif c=="2":ranked.append((2,a,"2.1.3.5.3(c)"))
        elif c=="3" and ctx["absolute_subtypes"][c]["status"]=="applies":
            ranked.append((3,a,"2.1.3.5.3(d)"))
        elif c=="4.1" and ctx["absolute_subtypes"][c]["status"]=="applies":
            ranked.append((4,a,"2.1.3.5.3(e)"))
        elif c=="4.2" and ctx["absolute_subtypes"][c]["status"]=="applies":
            ranked.append((5,a,"2.1.3.5.3(f)"))
        elif c=="5.2":ranked.append((6,a,"2.1.3.5.3(g)"))
        elif c=="6.1" and a["pg"]=="I" and ctx["toxicity_route"]["value"]=="INHAL":
            corrosion=next((x for x in active if x["class"]=="8"),None)
            if corrosion:
                carveout=ctx.get("inhalation_corrosive_exception")
                if not _assertion(packet,carveout):
                    return None,"CLASS8_INHALATION_CARVEOUT_UNRESOLVED: 2.1.3.5.3(h)",[]
                if carveout["status"]=="applies":
                    ranked.append((7,corrosion,"2.1.3.5.3(h) exception"))
                    continue
            ranked.append((7,a,"2.1.3.5.3(h)"))
        elif c=="6.2":ranked.append((8,a,"2.1.3.5.3(i)"))
    if ranked:
        _,chosen,rule=min(ranked,key=lambda x:x[0])
        chosen={**chosen,"origin_ids":sorted(a["candidate_id"] for a in active),
                "rule_ids":chosen["rule_ids"]+["A14-ABS:"+rule]}
        return chosen,None,[{"rule_id":"A14-ABS","clause":rule,
                             "winner":chosen["candidate_id"],
                             "rejected":[x["candidate_id"] for x in active
                                         if x["candidate_id"]!=chosen["candidate_id"]]}]
    remaining=[a for a in active if not (a["class"]=="7"
               and ctx.get("radioactive_exception",{}).get("status")=="applies")]
    if len(remaining)==1:
        return remaining[0],None,[{"rule_id":"A14-SP290","clause":"2.1.3.5.3(a);3.3.1 SP290",
                                   "class7_not_primary":True}]
    if any(a["pg"] is None and a["class"]!="9" for a in remaining):
        return None,"MATRIX_PG_UNKNOWN: PG required to choose table axis",[]
    r,err,trail=_fold(remaining,ctx)
    return r,err,[{"rule_id":"A14-MATRIX","clause":"2.1.3.10","cell":c} for c in trail]


def evaluate(packet, context=None, selection=None):
    """Return provisional reconciliation, never a publishable SDS classification."""
    ctx=context or {}
    positive,error=_screen(packet)
    if error:return blocked("SCREENING_INCOMPLETE",error)
    for name in ("material_form","toxicity_route","pesticide"):
        x=ctx.get(name)
        allowed=("applies","does_not_apply") if name=="pesticide" else ("known",)
        if x is not None and not _assertion(packet,x,allowed):
            return blocked("CONTEXT_UNVERIFIED",name+" evidence unverified")
    if any(ctx.get(x) for x in ("unknown_waste_default","carriage_prohibited",
                                 "competent_authority_pending","named_entry_conflict")):
        return blocked("REGULATORY_EXCEPTION_HOLD","Waste, prohibition, authority or name review pending")
    primary,error,rules=_precedence(packet,positive,ctx)
    if error:return blocked(error.split(":")[0],error,rules)
    trace=[{"rule_id":"A14-SCREEN","clause":"2.1.2.1",
            "positive_candidate_ids":[x["candidate_id"] for x in positive],
            "negative_findings_are_class_scoped":True}]+rules
    prior={"class":primary["class"],"packing_group":primary["pg"],
           "candidate_id":primary["candidate_id"],"rule_ids":primary["rule_ids"]}
    if selection is None:
        return blocked("TABLE_A_ROW_MISSING","Agent 1/4 must supply a unique verified Table A row",trace,prior)
    if selection.get("candidate_set_complete") is not True or selection.get(
            "named_entry_screening")!="complete":
        return blocked("UN_SELECTOR_INCOMPLETE","Named vs specific/generic hierarchy unresolved",trace,prior)
    row=selection.get("selected_row")
    if not isinstance(row,dict) or selection.get("selector_status")!="table_a_verified":
        return blocked("TABLE_A_ROW_UNVERIFIED","Row not confirmed by UN selector",trace,prior)
    verified=row.get("verification",{})
    if (verified.get("edition")!="ADR-2025-EN" or not all(
            verified.get(k) is True for k in ("identity","column_cells","corrigenda"))
            or row.get("source_id")!="ADR25_VOL1" or not row.get("row_id")
            or not re.fullmatch(r"[0-9]{4}",str(row.get("un_number","")))):
        return blocked("ROW_PROVENANCE_UNVERIFIED","Source/edition/corrigenda/identity not checked",trace,prior)
    cells=row.get("columns",{})
    if not all(k in cells and isinstance(cells[k],str) for k in ("3a","3b","4","5","6")):
        return blocked("ROW_CELLS_MISSING","Require exact 3a/3b/4/5/6 source cells",trace,prior)
    final=primary
    override=None
    if cells["3a"]!=primary["class"]:
        override=selection.get("named_exception")
        if (not isinstance(override,dict) or override.get("clause") not in
                ("2.1.3.3","2.1.3.4.1","2.1.3.4.2","2.1.3.4.3")
                or override.get("target_class")!=cells["3a"]
                or override.get("verified") is not True
                or not _assertion(packet,override,("applies",))):
            return blocked("ROW_CLASS_CONTRADICTION","Class differs without verified named-entry exception",trace,prior)
        hits=[a for a in positive if a["class"]==cells["3a"]]
        if len(hits)!=1:
            return blocked("OVERRIDE_CLASS_NOT_EVIDENCED","Named row class not positively assessed",trace,prior)
        final=hits[0]
        trace.append({"rule_id":"A14-NAMED-EXCEPTION","clause":override["clause"],
                      "matrix_primary_rejected":primary["class"],
                      "named_primary":final["class"],
                      "reason":override.get("reason","verified named-entry exception")})
    pg=cells["4"].strip().upper() or None
    if pg not in (None,"I","II","III"):
        return blocked("INVALID_ROW_PG","Unsupported value in column 4",trace,prior)
    if pg and final["class"] in NO_PG:
        return blocked("PG_NOT_APPLICABLE","No numeric PG for this class",trace,prior)
    if override is None and primary["pg"] is not None and primary["pg"]!=pg:
        return blocked("MATRIX_ROW_PG_CONTRADICTION","Matrix and exact column 4 disagree",trace,prior)
    if pg is None and final["pg"] is not None:
        return blocked("CANDIDATE_ROW_PG_CONTRADICTION","Numeric specialist PG with blank column 4",trace,prior)
    if pg is not None and final["pg"]!=pg:
        if not (override is None and primary["pg"]==pg
                and selection.get("matrix_pg_change_acknowledged") is True):
            return blocked("SPECIALIST_PG_CONTRADICTION","PG change requires explicit matrix acknowledgement",trace,prior)
        trace.append({"rule_id":"A14-PG-CHANGE","clause":"2.1.3.10",
                      "specialist_pg":final["pg"],"matrix_pg":primary["pg"],
                      "table_a_pg":pg})
    if pg is not None and primary["pg"] is None and override is None and final["pg"]!=pg:
        return blocked("PG_UNDETERMINED","Matrix has no PG and specialist PG not supported",trace,prior)
    extras=(set(override.get("subsidiary_classes",[])) if override else
            {x["class"] for x in positive}-{final["class"]})
    if ctx.get("radioactive_exception",{}).get("status")=="applies":extras.discard("7")
    if ctx.get("environmental_only_class9") is True:extras.discard("9")
    labels=row.get("verified_label_classes")
    if (row.get("label_cell_verified") is not True or not isinstance(labels,list)
            or len(labels)!=len(set(labels)) or any(x not in CLASSES for x in labels)):
        return blocked("COL5_LABELS_UNVERIFIED","Agent 1 must audit normalized class labels",trace,prior)
    if set(labels)!=extras|{final["class"]}:
        return blocked("SUBSIDIARY_LABEL_CONTRADICTION","Exact column 5 conflicts with evidenced classes",trace,prior)
    codes=[x for x in re.split(r"[\s,;]+",cells["6"].strip()) if x]
    if any(not re.fullmatch(r"\d+",x) for x in codes):
        return blocked("COLUMN6_SP_UNPARSEABLE","Unrecognised special provision code",trace,prior)
    outcomes=selection.get("special_provision_outcomes")
    if not isinstance(outcomes,list) or sorted(x.get("code","") for x in outcomes)!=sorted(codes):
        return blocked("SP_CODE_SET_INCOMPLETE","Resolve every exact column 6 code",trace,prior)
    if any(x.get("status") not in ("applies","does_not_apply")
           or x.get("verified") is not True or not x.get("source_clause")
           or not x.get("evidence_ids")
           or not all(_evidence_ok(packet,i) for i in x["evidence_ids"]) for x in outcomes):
        return blocked("SP_EVIDENCE_UNRESOLVED","SP results require 3.3.1 citation and evidence",trace,prior)
    trace.append({"rule_id":"A14-TABLE-A-CELLS","clause":"3.2.1(3a),(3b),(4),(5),(6)",
                  "row_id":row["row_id"],"source_id":row["source_id"],
                  "un_number":row["un_number"],
                  "exact_cells":{k:cells[k] for k in ("3a","3b","4","5","6")},
                  "alternative_rejections":"class/PG/labels/SP mismatches fail closed"})
    trace.append({"rule_id":"A14-SP","clause":"3.3.1","resolved_codes":codes})
    return {"status":"RECONCILED_PROVISIONAL","publishable":False,
            "assignment_permitted":False, "primary_class":final["class"],
            "packing_group":pg,"un_number":row["un_number"],
            "proper_shipping_name":row.get("proper_shipping_name"),
            "classification_code":cells["3b"],
            "selected_table_a_row_id":row["row_id"],
            "subsidiary_classes":sorted(extras,key=CLASSES.index),
            "blocking_issues":[],"provisional_precedence":prior,
            "trace":trace,"edition":"ADR-2025-EN",
            "review_state":"provisional_not_approved"}
