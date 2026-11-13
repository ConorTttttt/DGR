# Agent 11 handover to Lead Agent — 13 November 2026

**Status:** DRAFT, unreviewed, not approved for transport or SDS Section 14. Branch: agent11/adr2025-class7-radioactive. All changes are under agents/agent11/; shared infrastructure and other agents' files untouched.

## Deliverables
- class7.py: deterministic Decimal-based single-material radionuclide concentration/whole-consignment activity screen, LSA/SCO/fissile material screening, separate package arithmetic.
- radionuclides.json: eight manually curated Table 2.2.7.2.2.1 rows, with four basic radionuclide values each; fallback Table 2.2.7.2.2.2 retained but not auto-selected.
- rules.json: 18 machine-readable rules; regulatory_register.csv: 27 clause/table/exception rows.
- SOURCE_MANIFEST.json: precise ADR 2025 ECE/TRANS/352 English Vols I+II and UN test manual Rev.8/Amendment 1 metadata; corrigendum review reminder.
- tests/test_class7.py: 30 positive/negative/threshold/missing-evidence developer regression tests; test_results.txt records 30 PASS locally, no independent regulatory validation.
- README.md: input and scope; UNSUPPORTED.md: 16 groups of blocked routes and handoffs.

## Decisions and traceability

1. Vol.I 2.2.7.1.1 and 2.2.7.2.2.1 require that BOTH activity concentration Bq/g and total consignment activity Bq strictly EXCEED their appropriate values. Exact threshold equality is not positive. Multi-nuclide reciprocal formula from Vol.I 2.2.7.2.2.4; no guessed radioactive limits.
2. Quantities carry value, actual unit, source ID, method and measurement date; all nuclide activities must share an ISO activity_reference_date. Whole consignment and homogeneous unshielded material basis must be explicitly evidenced, or INDETERMINATE.
3. Fissile definition exclusions in Vol.I 2.2.7.1.3 are separated from fissile exceptions in 2.2.7.2.3.5(a)-(f); the latter, and 2.2.7.2.3.6/CV33(4.3), require independent nuclear criticality review. No mass-only safe transport claim.
4. LSA-I/II/III and SCO-I/II only generate material-characteristic candidates. Surface area 300cm2 averaging, accessible/inaccessible fixed and removable contamination and two emitter groups are required. SCO-III, special form and low-dispersible claims must pass applicable tests and authority approvals.
5. Volume II calculations are segregated from the initial material gate: Type A and excepted material activity comparisons and single package TI/category are optional numerical screens, never package or consignment decisions. Part 4-7 obligations and approvals (4.1.9, 5.1.5, 6.4, 7.5.11 CV33) remain external.
6. final_un_number, packing_group, and transport_not_regulated always return null. The Lead Agent must separately resolve Table 2.2.7.2.1.1, official Chapter 3.2 Table A, Chapter 3.3 SP 290/369, 1.7.1.4 exemptions and 1.7.5 subsidiary hazards.

## Required independent review before merge

- Full Table 2.2.7.2.2.1 digitization and independent transcription of A1/A2, exempt concentrations and exempt consignment activities. Audit all footnotes (a)-(g), daughter equilibrium, chemical forms, uranium absorption type, Unlimited A2 routes.
- Independently verify numeric boundary fixtures, uncertainty handling and calibration; establish evidence format for time-of-shipment activity and certified decay correction. Do not treat self-asserted evidence completeness or certificate flags as proof.
- Review 1.7.1.4 natural material/ore exclusions, contamination, fissile <0.25g exclusion, special-form/leaching tests and competent-authority certificate validity by route/jurisdiction.
- Complete FISSILE exceptions 2.2.7.2.3.5(a)-(f) with CV33, 6.4.11 and approved designs; complete special-form and low-dispersible routes per 2.2.7.2.3.3/.4, 6.4.12/.20/.23.
- Distinguish SCO contaminated non-radioactive objects from a homogeneous material mass Bq/g gate; build an independently reviewed SCO-only evidence/consignment pathway.
- Implement full LSA/SCO industrial package, Type A/Type B(U)/Type B(M)/Type C, UF6, excepted packages, TI factors for overpack/container, certificates, shipment notification, exclusive use, consignor declarations and official named-entry checks.
- Approve shared schema; map status to other agents' multiple-hazard precedence and SDS Section 14 synthesis. Run CI in repository and independent regulatory tests, then have human reviewer approve.
- Check official corrigenda ECE/TRANS/352/Corr.1 and Corr.2 against the supplied volumes. Preliminary check of Corr.2 found no changes to Chapter 2.2.7, but this is not approval.

## Primary regulatory references

ADR 2025 ECE/TRANS/352 Volume I (English), 1.7.1.4, 1.7.5, 2.2.7.1.1-.3, 2.2.7.2.1.1, 2.2.7.2.2.1-.6, 2.2.7.2.3.1-.6, 2.2.7.2.4.1-.6, 2.2.7.2.5 and Chapter 3.3. Volume II (English): 4.1.9, 5.1.5, 6.4, 7.5.11 CV33. Refer to regulatory_register.csv for exact rule mappings.

**No regulatory validation is claimed.** Source Manual of Tests and Criteria Rev.8/Amendment 1 does not itself provide an alternate Class 7 radionuclide-limit table for this module.
