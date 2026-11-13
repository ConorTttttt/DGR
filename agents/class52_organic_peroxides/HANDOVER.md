# Agent 8 handover — ADR 2025 Class 5.2 organic peroxides

**Branch:** agent8/adr2025-class52-organic-peroxides. **Owned files only:** `agents/class52_organic_peroxides/**`. **Regulatory state:** provisional / independently unreviewed. No SDS Section 14 or carriage approval.

## Deliverables and execution
- `classify.js` deterministic Class 5.2 candidate implementation aligned with Lead's v1.0.0-rc1 payload, fail-closed statuses, no PG/UN finalization.
- `rules.json` 37 regulatory and source-exact rule references with implementation dispositions; `exceptions.json` 29 limitations/exception blockers; `sources.json` SHA256-pinned supplied ADR volumes and UN MTC Rev8 + Amend1.
- `test_cases.json`, `classify.test.js`, `test_results.json`: 71/71 synthetic V8 cases passed; Node CLI not executed here and independent regulatory validation is NOT claimed.

## Regulatory decisions
ADR §2.2.52.1.5 available oxygen = 16×Σ(nᵢ×cᵢ/mᵢ) in mass %; exact <=1% when H2O2<=1%, exact <=0.5% when 1%<H2O2<=7%. These are Class 5.2-only exclusions. Types A–G per MTC Rev8 §20.4.3; A is prohibited for carriage; G outside Class 5.2 requirements; B–F type is not a PG. Current 2.2.52.4 formulation/IBC520/T23 rows require complete attested matches. Changed concentrations, diluents or other formulation features invalidate the original assertion. Mixtures require separate SADT despite components individually stable. Unlisted approval by origin authority and recognition in the first ADR contracting party for non-ADR origins. Qualifying samples: data no more dangerous than B, OP2, no more than 10kg/transport unit, verified safe thermal/phase conditions.

Diluent A BP>=150°C; B BP>=60°C and <150°C, flash>=5°C, BP>=SADT50kg+60°C; compatible solids and authorized water, other diluents require reassessment. Temp control: B/C <=50°C, D medium <=50°C or low/no <=45°C, E/F <=45°C. ADR §7.1.7.3.5 provides packaging-dependent control/emergency deltas. Actual carriage must avoid unsafe phase separation. No auto assignment from CLP/GHS.

Candidate UN 3101–3120 from §2.2.52.3 and Table A (blank PG col.4) does NOT constitute final assignment; no row IDs or SP checks are resolved. Type B Table A includes subsidiary Class 1 label, forwarded for precedence. Articles UN3545, other special formulations and tank/IBC permissions deferred.

## Independent-review blockers / assumptions requiring approval
1. Compare each clause and source metadata with ADR 2025 English and Corr.1/Corr.2 (not supplied); check latest signed corrections and full Table A, §2.2.52.4 formulation footnotes including Exempt rows.
2. MTC Rev8 English §20.4.3(b) appears to omit a phrase about type B package thermal explosion; independent specialist review of official source, flowchart, A–G and H methods/waivers, and Amendment1 §25/§28 is mandatory. The current implementation uses thermal-explosion evidence but cannot claim full validated test-series routing.
3. Lab data needed: full chemical formula/concentration, molecular masses, appropriate MTC 21–28 results/waivers, 50kg SADT, actual-package SADT, confinement effect, thermal decomposition/phase stability, flash/boiling points and desensitizer compatibility/spillage consequences. Current test fixtures are *synthetic* only.
4. Authenticate competent-authority decisions, all carriage conditions, recognized origin, revisions and expiration. Verify P520 packing methods, maximum package contents, IBC520 and T23 eligibility; no automatic substance entry.
5. Lead Agent must resolve precise Table A `row_id`, UN/PG column (4), SP 122/181/274 and any formulation-specific remarks, subsidiary risks/precedence, ADR §7.1.7 carriage controls and all cross-class gates before any Section 14 release.
6. Independently execute the committed Node test suite, add real validated gold cases, complete regulatory/security/CI integration review with rollback; do not merge or release beforehand.

**Important nuance:** Listed exact formulations with externally verified listed thermal status can yield a candidate without a new SADT input if the formula is unchanged; this assumption is subject to independent review. Mixtures always require an actual measured SADT. Missing results always block, never mean not-dangerous.

## Post-draft review correction
The initial strict mixture route was refined: existing verified listed-component mixtures under §2.2.52.1.7 require actual SADT and verified most-dangerous-component carriage conditions, while significantly different/new mixtures require §2.2.52.1.8 authority. Complete-component, organic-liquid and IBC/T23 receptacle checks were tightened. Re-tested on revised source with synthetic V8 fixtures. Independently review these interpretations before merge.

## Precision/evidence schema addition
Added JSON Schema Draft 2020-12 with route-specific positive evidence prerequisites while permitting incomplete evidence for explicit status reporting. The B diluent BP−SADT(50kg) >=60°C threshold now uses exact signed decimal comparison, including 70.1−10.1 boundary cases. Synthetic tests increased to 82; independent lab and regulatory approval remain outstanding.
