# Agent 12 — Class 8 ADR 2025 review module

**Provisional / independent regulatory validation not completed.** This is an isolated audit and integration proposal based on draft PR #2, not a replacement of Agent 3-owned files. Lead approval is required before integration and deployment.

Files:
- class8.py — evidence-scoped evaluator for skin tests, human evidence, UN MTC C.1 metal tests, mixture bridging and generic concentration decisions.
- tests/test_class8.py — 18 local unittest methods, including threshold and missing-evidence subcases.
- rules_register.json — 10 machine-readable, edition-pinned rules, inputs, thresholds, exceptions, and unsupported statuses.
- HANDOVER.md — source clause register, existing PR #2 audit, limitations, tests, and lead handover.

Run from repository root:

    python -m unittest discover -s agents/agent12/tests -v

The module never assigns a final UN entry, Table A packing group or SDS Section 14 determination; computed PG and DGL PG are separate. It does not infer ADR classification from GHS/CLP. Unresolved rules return indeterminate and all outputs require independent review.
