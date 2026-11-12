# ADR 2025 independent regulatory release checklist

**All items remain OPEN.** For each checked item, record reviewer name/identity, signed decision, date, exact clause(s), source digest, test evidence and release artifact identifier.

- [ ] Exact ADR edition ECE/TRANS/352 Vol.I/II (English) and applicability date pinned; do not silently load later editions or other modes.
- [ ] Authenticate primary official document bytes/digests; local Volume I SHA-256 consistency is not enough to authenticate original delivery.
- [ ] Reconcile English Corr.1 and Corr.2 for every affected clause and row, including UN 3423 column (20) and 2.1.3.10 Note 2.
- [ ] Review applicability of UN Manual of Tests and Criteria Revision 8 and Amendment 1, documenting every changed test method.
- [ ] Independently validate every operative class rule, boundary, exception, unsuitable test, subsidiary risk and incomplete-evidence outcome.
- [ ] Confirm every class or division relevant to the product is assessed and global negative cases have independently evidenced all-class and named-entry screening.
- [ ] Independently verify all used absolute-precedence rules, 2.1.3.10 table cells and notes against rendered original pages.
- [ ] Verify Table A row IDs, all multi-row UN numbers, name/classification codes/PG, prohibited carriage and row-specific special provisions.
- [ ] Check all assigned 3.3.1 special provisions and exact conditional effects; keep LQ, EQ and carriage relief separate from classification.
- [ ] Verify competent authority/expert decisions' authenticity, scope, approved conditions and current validity.
- [ ] Pass synthetic contract tests, independently verified real golden cases, adversarial/missing/conflicting inputs and threshold-boundary suites.
- [ ] Independently review implementation, mode separation, source provenance, data provenance, hash/signature checks, immutable bundles and rollback plan.
- [ ] Confirm copyright/licensing and authorized distribution of any Table A-derived data in this public repository.
- [ ] Obtain independent regulatory and software approvals; release controller signs only after all blockers close.

**Current release result: NOT APPROVED.** The routing interface permanently emits publishable=false and cannot itself authorize SDS Section 14.
