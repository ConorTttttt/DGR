# Agent 5 interface proposal (pending Lead Agent agreement)

This is an implementation proposal, not a regulatory interpretation. Contract version 0.1.0.

## Rule bundle

Each bundle is JSON with:

- schema_version (0.1.0), bundle_id, bundle_version (SemVer), regime (opaque transport mode), edition (opaque regulatory edition), effective_from and effective_until (inclusive ISO dates).
- approval: {status: "approved", reviewer, reviewed_on, approval_reference}. This is a metadata gate, not cryptographic authentication.
- required_fields_for_regulated: externally reviewed list of mandatory final fields, never inferred by the engine.
- sources: array of {source_id, authority_kind, edition, uri, sha256}. authority_kind is regulatory_text or synthetic_test. Synthetic sources cannot execute without explicit test opt-in.
- rules: array of {rule_id, when, citations, effects}; every citation specifies {source_id, clause}. An effect setting transport_status to not_regulated_for_transport additionally requires exhaustive_scope: true and a nonempty exhaustive_scope_rationale, which itself must receive legal review.

## Predicate grammar

Condition operators: all, any, not, eq, ne, gt, gte, lt, lte. "all" and "any" take a nonempty conditions list; "not" takes one condition. Comparisons specify a fact ID and an expected typed value.

Supported fact/expected types: boolean, text, decimal. Decimal values are precise base-10 strings; ordered comparisons only accept decimal. A missing, unevidenced, malformed or mistyped input fact has truth value UNKNOWN, not FALSE. Logical operations use three-valued Kleene semantics.

## Effect grammar

Each effect sets {field, value}. Recognised fields are transport_status, un_number, proper_shipping_name, transport_hazard_class, subsidiary_risks, packing_group, environmental_hazards, special_precautions, maritime_bulk_transport.

Recognised explicit transport statuses: regulated and not_regulated_for_transport. A missing status or no matching rule cannot establish not regulated. No field is calculated or sourced from CLP/GHS by this engine.

## Evaluation request

{input_id, regime, bundle_id, bundle_version, on_date, facts}.

- The caller must pin the exact rule bundle ID, version, mode and evaluation date.
- facts maps fact IDs to {type, value, evidence: [{ref, locator}, ...]}. Evidence source authenticity and admissibility require independent external assessment.

## Output statuses

- BLOCKED: invalid contract, unapproved/test-only bundle, missing provenance, incompatible edition/mode/version or outside effective dates. section14 is empty.
- INDETERMINATE: a missing or unknown rule outcome, no matched rule, conflicting effects, absent explicit status or missing completeness fields. section14 is empty; provisional_effects are diagnostic only, NOT publishable as SDS Section 14.
- DECIDED: all predicates known, matching effects consistent, explicit transport status and complete externally configured mandatory fields. STILL not legally validated until independent review.

Every result includes engine/result schema version, issues, request and bundle hashes. Full evaluations include exact-clause rule traces, evidence references, matched rules, edition/regime metadata and field-level source citations. Run-to-run timestamps are omitted.

## Version governance

Rule bundles are immutable in the proposed deployment process: use bundle ID + SemVer + SHA-256 + source document hashes. New editions/amendments require a new bundle/review and effective date range, never an implicit "latest" upgrade. The engine does not verify cryptographic approver signatures or compare source sha256 with authoritative documents; these must be verified in the trusted release process.

## Dependencies and approvals requested

1. Lead Agent to establish final shared schemas and naming, plus rule evaluation/approval boundaries.
2. Agent 1 to supply authoritative source registry with verified document digests, exact clauses, edition IDs and links.
3. Classification rule agents to supply reviewed conditions/effects and demonstrate negative-outcome exhaustive scope; resolve priority and exception precedence outside this evaluator.
4. Independent reviewer to validate source interpretation, input admissibility, conflict/unknown semantics and correct SDS 14.1–14.7 mapping.
5. Security/release owner to establish genuine approval authentication, immutable artifact storage, controlled deployment, audit retention and rollback.

## Known limitations

No real legal provisions or thresholds are encoded. No regulatory classifications have been verified. This implementation has no dependency graph, claim trust signature verification, automatic modal crosswalk, UN lookup, partial-SDS publishing, configurable precedence engine, or validated resource sandbox. Rule-list array order affects bundle digest though evaluation order is sorted by rule ID; review all inputs in a trusted CI pipeline.
