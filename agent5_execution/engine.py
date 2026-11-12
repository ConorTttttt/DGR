"""Fail-closed, rule-data-driven SDS Section 14 execution prototype.

This module contains no transport classification rules. Its input contract is
provisional until accepted by the Lead Agent. Standard-library only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
import hashlib
import json
import re
from typing import Any, Mapping

ENGINE_VERSION = "0.1.0"
CONTRACT_VERSION = "0.1.0"
FIELDS = frozenset({
    "transport_status", "un_number", "proper_shipping_name",
    "transport_hazard_class", "subsidiary_risks", "packing_group",
    "environmental_hazards", "special_precautions", "maritime_bulk_transport",
})
COMPARATORS = frozenset({"eq", "ne", "gt", "gte", "lt", "lte"})
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Invalid input/bundle or policy precondition (not a DG decision)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _require(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ContractError(code, message)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _iso_date(value: Any, name: str) -> date:
    _require(isinstance(value, str), "INVALID_DATE", f"{name} must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ContractError("INVALID_DATE", f"{name} must be an ISO date") from exc
    _require(parsed.isoformat() == value, "INVALID_DATE", f"{name} must be YYYY-MM-DD")
    return parsed


def _decimal(value: Any) -> Decimal:
    _require(isinstance(value, str), "INVALID_DECIMAL", "decimal values must be exact strings")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ContractError("INVALID_DECIMAL", "invalid decimal string") from exc
    _require(parsed.is_finite(), "INVALID_DECIMAL", "decimal must be finite")
    return parsed


def _typed_value(value: Any) -> None:
    _require(isinstance(value, dict), "INVALID_VALUE", "typed value must be an object")
    kind = value.get("type")
    raw = value.get("value")
    _require(kind in ("boolean", "text", "decimal"), "INVALID_VALUE", "unknown fact value type")
    if kind == "boolean":
        _require(type(raw) is bool, "INVALID_VALUE", "boolean value required")
    elif kind == "text":
        _require(isinstance(raw, str), "INVALID_VALUE", "text value required")
    else:
        _decimal(raw)


def canonical_sha256(value: Any) -> str:
    """Stable digest independent of JSON mapping insertion order."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ContractError("DUPLICATE_JSON_KEY", f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def parse_bundle_json(payload: str) -> dict[str, Any]:
    """Parse strictly; callers should not use permissive json.load on bundles."""
    try:
        value = json.loads(payload, object_pairs_hook=_no_duplicate_keys,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               ContractError("INVALID_JSON_NUMBER", "nonfinite JSON number")))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ContractError("INVALID_JSON", "malformed JSON bundle") from exc
    _require(isinstance(value, dict), "INVALID_BUNDLE", "bundle must be an object")
    return value


def _validate_predicate(node: Any, depth: int = 0) -> None:
    _require(depth <= 24, "INVALID_PREDICATE", "predicate nesting exceeds limit")
    _require(isinstance(node, dict), "INVALID_PREDICATE", "predicate must be an object")
    op = node.get("op")
    if op in ("all", "any"):
        children = node.get("conditions")
        _require(isinstance(children, list) and 0 < len(children) <= 128,
                 "INVALID_PREDICATE", "all/any require 1..128 conditions")
        for child in children:
            _validate_predicate(child, depth + 1)
    elif op == "not":
        _validate_predicate(node.get("condition"), depth + 1)
    elif op in COMPARATORS:
        _require(_nonempty(node.get("fact")), "INVALID_PREDICATE", "fact ID required")
        _typed_value(node.get("expected"))
        if op in ("gt", "gte", "lt", "lte"):
            _require(node["expected"]["type"] == "decimal", "INVALID_PREDICATE",
                     "ordered comparisons require decimal type")
    else:
        raise ContractError("INVALID_PREDICATE", f"unsupported predicate operator: {op!r}")


def validate_bundle(bundle: Mapping[str, Any], *, allow_test_rules: bool = False) -> None:
    """Pre-execution validation. It does NOT establish legal rule correctness."""
    _require(isinstance(bundle, dict), "INVALID_BUNDLE", "bundle must be an object")
    _require(bundle.get("schema_version") == CONTRACT_VERSION, "SCHEMA_VERSION_MISMATCH",
             "unsupported rule contract version")
    for name in ("bundle_id", "regime", "edition"):
        _require(_nonempty(bundle.get(name)), "INVALID_BUNDLE", f"{name} required")
    _require(isinstance(bundle.get("bundle_version"), str) and
             SEMVER.fullmatch(bundle["bundle_version"]) is not None,
             "INVALID_VERSION", "bundle_version must be semver")
    start = _iso_date(bundle.get("effective_from"), "effective_from")
    until = _iso_date(bundle.get("effective_until"), "effective_until")
    _require(start <= until, "INVALID_DATE", "effective interval reversed")
    approval = bundle.get("approval")
    _require(isinstance(approval, dict) and approval.get("status") == "approved",
             "UNAPPROVED_BUNDLE", "rule bundle must be explicitly approved")
    for name in ("reviewer", "reviewed_on", "approval_reference"):
        _require(_nonempty(approval.get(name)), "INVALID_APPROVAL", f"approval.{name} required")
    _iso_date(approval["reviewed_on"], "reviewed_on")
    required = bundle.get("required_fields_for_regulated")
    _require(isinstance(required, list) and bool(required) and
             len(required) == len(set(required)) and
             all(isinstance(f, str) and f in FIELDS - {"transport_status"} for f in required),
             "INVALID_COMPLETENESS", "approved required_fields_for_regulated list required")
    sources = bundle.get("sources")
    _require(isinstance(sources, list) and bool(sources), "MISSING_PROVENANCE",
             "nonempty source registry required")
    by_id: dict[str, dict[str, Any]] = {}
    for source in sources:
        _require(isinstance(source, dict), "MISSING_PROVENANCE", "source must be an object")
        for name in ("source_id", "edition", "uri"):
            _require(_nonempty(source.get(name)), "MISSING_PROVENANCE", f"source.{name} required")
        _require(source["source_id"] not in by_id, "DUPLICATE_SOURCE", "duplicate source ID")
        _require(source["edition"] == bundle["edition"], "EDITION_MISMATCH",
                 "source edition and bundle edition differ")
        _require(isinstance(source.get("sha256"), str) and
                 HEX_SHA256.fullmatch(source["sha256"]) is not None,
                 "MISSING_PROVENANCE", "source document SHA-256 required")
        kind = source.get("authority_kind")
        _require(kind in ("regulatory_text", "synthetic_test"), "INVALID_SOURCE",
                 "unsupported source kind")
        _require(kind != "synthetic_test" or allow_test_rules, "TEST_RULES_DISABLED",
                 "synthetic rules cannot execute without test mode")
        by_id[source["source_id"]] = source
    rules = bundle.get("rules")
    _require(isinstance(rules, list) and bool(rules) and len(rules) <= 10000,
             "INVALID_BUNDLE", "nonempty bounded rules array required")
    seen: set[str] = set()
    for rule in rules:
        _require(isinstance(rule, dict) and _nonempty(rule.get("rule_id")),
                 "INVALID_RULE", "rule ID required")
        _require(rule["rule_id"] not in seen, "DUPLICATE_RULE", "duplicate rule ID")
        seen.add(rule["rule_id"])
        _validate_predicate(rule.get("when"))
        citations = rule.get("citations")
        _require(isinstance(citations, list) and bool(citations), "MISSING_PROVENANCE",
                 "each rule requires source citations")
        for cite in citations:
            _require(isinstance(cite, dict) and cite.get("source_id") in by_id and
                     _nonempty(cite.get("clause")), "MISSING_PROVENANCE",
                     "rule citation must identify registered source and exact clause")
        effects = rule.get("effects")
        _require(isinstance(effects, list) and bool(effects), "INVALID_EFFECT",
                 "each rule requires at least one effect")
        observed: set[str] = set()
        for effect in effects:
            _require(isinstance(effect, dict) and effect.get("field") in FIELDS,
                     "INVALID_EFFECT", "unsupported Section 14 field")
            field = effect["field"]
            _require(field not in observed, "INVALID_EFFECT", "duplicate field in one rule")
            observed.add(field)
            value = effect.get("value")
            _require(value is not None and type(value) in (str, bool, int, list),
                     "INVALID_EFFECT", "effect value must be an explicit JSON scalar or list")
            if type(value) is list:
                _require(bool(value) and all(type(v) in (str, bool, int) for v in value),
                         "INVALID_EFFECT", "effect arrays must contain simple scalar values")
            if field == "transport_status":
                _require(value in ("regulated", "not_regulated_for_transport"),
                         "INVALID_EFFECT", "transport status must be explicit and recognized")
                if value == "not_regulated_for_transport":
                    _require(rule.get("exhaustive_scope") is True and
                             _nonempty(rule.get("exhaustive_scope_rationale")) and
                             len(effects) == 1,
                             "NON_REGULATED_NOT_JUSTIFIED",
                             "not-regulated decision requires explicit exhaustive scope")
    # All source metadata, effects and conditions are reviewed separately from code.


class Truth(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PredicateResult:
    truth: Truth
    missing_facts: frozenset[str] = frozenset()
    missing_evidence: frozenset[str] = frozenset()
    invalid_facts: frozenset[str] = frozenset()
    inspected_facts: frozenset[str] = frozenset()


def _merge(truth: Truth, parts: list[PredicateResult]) -> PredicateResult:
    return PredicateResult(truth,
                           frozenset().union(*(r.missing_facts for r in parts)),
                           frozenset().union(*(r.missing_evidence for r in parts)),
                           frozenset().union(*(r.invalid_facts for r in parts)),
                           frozenset().union(*(r.inspected_facts for r in parts)))


def _eval_predicate(node: dict[str, Any], facts: dict[str, Any]) -> PredicateResult:
    op = node["op"]
    if op in ("all", "any"):
        parts = [_eval_predicate(child, facts) for child in node["conditions"]]
        values = {p.truth for p in parts}
        if op == "all":
            value = Truth.FALSE if Truth.FALSE in values else (Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.TRUE)
        else:
            value = Truth.TRUE if Truth.TRUE in values else (Truth.UNKNOWN if Truth.UNKNOWN in values else Truth.FALSE)
        return _merge(value, parts)
    if op == "not":
        part = _eval_predicate(node["condition"], facts)
        inverse = {Truth.TRUE: Truth.FALSE, Truth.FALSE: Truth.TRUE, Truth.UNKNOWN: Truth.UNKNOWN}
        return _merge(inverse[part.truth], [part])
    name = node["fact"]
    if name not in facts:
        return PredicateResult(Truth.UNKNOWN, missing_facts=frozenset({name}), inspected_facts=frozenset({name}))
    fact = facts[name]
    if not isinstance(fact, dict):
        return PredicateResult(Truth.UNKNOWN, invalid_facts=frozenset({name}), inspected_facts=frozenset({name}))
    try:
        _typed_value(fact)
    except ContractError:
        return PredicateResult(Truth.UNKNOWN, invalid_facts=frozenset({name}), inspected_facts=frozenset({name}))
    evidence = fact.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(e, dict) or not _nonempty(e.get("ref")) or not _nonempty(e.get("locator"))
        for e in evidence
    ):
        return PredicateResult(Truth.UNKNOWN, missing_evidence=frozenset({name}), inspected_facts=frozenset({name}))
    expected = node["expected"]
    if expected["type"] != fact["type"]:
        return PredicateResult(Truth.UNKNOWN, invalid_facts=frozenset({name}), inspected_facts=frozenset({name}))
    left, right = fact["value"], expected["value"]
    if fact["type"] == "decimal":
        left, right = _decimal(left), _decimal(right)
    outcome = {
        "eq": lambda a, b: a == b,
        "ne": lambda a, b: a != b,
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
    }[op](left, right)
    return PredicateResult(Truth.TRUE if outcome else Truth.FALSE,
                           inspected_facts=frozenset({name}))


def _blocked(code: str, message: str, bundle: Any = None, request: Any = None) -> dict[str, Any]:
    def digest(value: Any) -> str | None:
        try:
            return canonical_sha256(value)
        except (TypeError, ValueError):
            return None
    return {
        "result_schema_version": CONTRACT_VERSION, "engine_version": ENGINE_VERSION,
        "decision_status": "BLOCKED", "section14": {},
        "issues": [{"code": code, "message": message}], "trace": [],
        "bundle_sha256": digest(bundle), "request_sha256": digest(request),
    }


def evaluate(bundle: Mapping[str, Any], request: Mapping[str, Any], *,
             allow_test_rules: bool = False) -> dict[str, Any]:
    """Evaluate one explicitly pinned, approved bundle. Never infer a negative decision.

    BLOCKED = invalid contract, approval, edition, or engine execution precondition.
    INDETERMINATE = inconclusive evidence, no applicable result, or conflicting rules.
    DECIDED = only with an explicit approved transport_status and completeness.
    """
    try:
        validate_bundle(bundle, allow_test_rules=allow_test_rules)
        _require(isinstance(request, dict), "INVALID_REQUEST", "request must be an object")
        _require(_nonempty(request.get("input_id")), "INVALID_REQUEST", "input_id required")
        _require(request.get("regime") == bundle["regime"], "REGIME_MISMATCH",
                 "request regime must match pinned bundle")
        _require(request.get("bundle_id") == bundle["bundle_id"] and
                 request.get("bundle_version") == bundle["bundle_version"],
                 "BUNDLE_PIN_MISMATCH", "explicit bundle ID and version required")
        on_date = _iso_date(request.get("on_date"), "on_date")
        _require(_iso_date(bundle["effective_from"], "effective_from") <= on_date <=
                 _iso_date(bundle["effective_until"], "effective_until"),
                 "OUTSIDE_EFFECTIVE_DATES", "request date outside approved bundle validity")
        facts = request.get("facts")
        _require(isinstance(facts, dict), "INVALID_REQUEST", "facts object required")
        # Every fact is inspected only when referenced by a predicate, but the
        # request must remain serializable to establish an immutable digest.
        request_hash = canonical_sha256(request)
        bundle_hash = canonical_sha256(bundle)
        trace: list[dict[str, Any]] = []
        issues: list[dict[str, str]] = []
        produced: dict[str, Any] = {}
        matched_citations: dict[str, list[dict[str, str]]] = {}
        unknown = False
        matching_rules: list[str] = []
        for rule in sorted(bundle["rules"], key=lambda r: r["rule_id"]):
            result = _eval_predicate(rule["when"], facts)
            evidence_refs = sorted({
                item["ref"] for fact_id in result.inspected_facts
                if isinstance(facts.get(fact_id), dict)
                for item in facts[fact_id].get("evidence", [])
                if isinstance(item, dict) and _nonempty(item.get("ref"))
            })
            trace.append({
                "rule_id": rule["rule_id"], "predicate": result.truth.value,
                "missing_facts": sorted(result.missing_facts),
                "missing_evidence": sorted(result.missing_evidence),
                "invalid_facts": sorted(result.invalid_facts),
                "inspected_facts": sorted(result.inspected_facts),
                "evidence_refs": evidence_refs,
                "citations": sorted(rule["citations"], key=lambda c: (c["source_id"], c["clause"])),
                "applied_effects": rule["effects"] if result.truth is Truth.TRUE else [],
            })
            if result.truth is Truth.UNKNOWN:
                unknown = True
                for kind, values in (("MISSING_FACT", result.missing_facts),
                                     ("MISSING_EVIDENCE", result.missing_evidence),
                                     ("INVALID_FACT", result.invalid_facts)):
                    for item in sorted(values):
                        issues.append({"code": kind, "message": f"{rule['rule_id']}: {item}"})
            elif result.truth is Truth.TRUE:
                matching_rules.append(rule["rule_id"])
                for effect in rule["effects"]:
                    key = effect["field"]
                    value = effect["value"]
                    if key in produced and produced[key] != value:
                        issues.append({"code": "CONFLICTING_RULE_EFFECTS",
                                       "message": f"conflicting values for {key}"})
                    else:
                        produced[key] = value
                        matched_citations.setdefault(key, []).extend(rule["citations"])
        if not matching_rules:
            issues.append({"code": "NO_MATCHING_APPROVED_RULE", "message": "no rule established a decision"})
        if unknown:
            issues.append({"code": "UNKNOWN_RULE_OUTCOME", "message": "at least one rule could not be evaluated"})
        status = produced.get("transport_status")
        if status == "regulated":
            missing_fields = sorted(set(bundle["required_fields_for_regulated"]) - produced.keys())
            for field in missing_fields:
                issues.append({"code": "INCOMPLETE_REGULATED_OUTPUT", "message": f"missing {field}"})
        elif status == "not_regulated_for_transport":
            if set(produced) != {"transport_status"}:
                issues.append({"code": "CONFLICTING_RULE_EFFECTS",
                               "message": "non-regulated status combined with other field effects"})
        else:
            issues.append({"code": "NO_EXPLICIT_TRANSPORT_STATUS",
                           "message": "an approved explicit transport status was not established"})
        # Never expose partially determined Section 14 data as a final classification.
        decided = not issues and status in ("regulated", "not_regulated_for_transport")
        return {
            "result_schema_version": CONTRACT_VERSION, "engine_version": ENGINE_VERSION,
            "decision_status": "DECIDED" if decided else "INDETERMINATE",
            "transport_status": status if decided else None,
            "section14": produced if decided else {},
            "provisional_effects": {} if decided else produced,
            "issues": sorted(issues, key=lambda x: (x["code"], x["message"])),
            "trace": trace, "matched_rule_ids": matching_rules,
            "field_citations": {k: sorted(v, key=lambda c: (c["source_id"], c["clause"]))
                                for k, v in sorted(matched_citations.items())},
            "bundle_id": bundle["bundle_id"], "bundle_version": bundle["bundle_version"],
            "regime": bundle["regime"], "edition": bundle["edition"],
            "on_date": request["on_date"], "bundle_sha256": bundle_hash,
            "request_sha256": request_hash,
        }
    except ContractError as exc:
        return _blocked(exc.code, str(exc), bundle, request)
    except (TypeError, ValueError, KeyError, RecursionError, OverflowError) as exc:
        # No silent fallback on invalid/malicious/unsupported data.
        return _blocked("INVALID_EXECUTION_INPUT", type(exc).__name__, bundle, request)
