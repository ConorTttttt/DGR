# Agent 5 -> Lead Agent: ADR 2025 Class 4.2 handover

**Branch:** `agent5/class42-adr2025-evidence-rules`. **Base:** `main`. **Owned files:** exclusively `agents/class42/`. **PR:** draft; no merge approval implied. **Review:** none, release prohibited.

## Scope and interface

`evaluateClass42(evidence)` provides **three isolated** hazard pathways: pyrophoric solid N.2, pyrophoric liquid N.3, self-heating N.4. The caller selects the pathway and must screen the other relevant pathways separately. It is not safe to treat one negative test as global proof of not-dangerous status. Uses Lead Agent v1.0.0-rc1 candidate/status field names from draft PR #8; unlike the Lead contract, this module has no orchestration and may require a Lead-owned adapter. All `final_un_number`, `final_packing_group` are `null`, `assignment_permitted=false`, `requires_independent_review=true`.

Registry: 36 entries in `rules.json`; exceptions: 28 in `exceptions.json`. Typed test evidence: `evidence.schema.json`. Synthetic test file: `class42.test.js` (62 scenarios). Source provenance/hashes: `sources.json`. No other agent files modified.

## Source evidence and exact boundary interpretation

| Requirement | Supporting edition and clause | Implementation / review state |
| --- | --- | --- |
| Pyrophoric definition, solutions/mixtures, 5 minutes | ADR 2025 §2.2.42.1.1 | N.2/N.3 paths separate |
| Codes S, SW, SO, ST, SC | ADR §2.2.42.1.2 and §2.2.42.3 | Metadata only; no UN assignment |
| N.O.S. tests and experience | ADR §2.2.42.1.4 | MTC required; more-severe experience flags blocker |
| N.2 ignition on drop/≤5 min | ADR §2.2.42.1.5(a); MTC Rev.8 §33.4.4.3–.4 | Six negatives or one positive; PG I |
| N.3 inert carrier/filter 5 min | ADR §2.2.42.1.5(b)(i)–(ii); MTC §33.4.5.3–.4 | Six carrier trials, then three filter trials; PG I |
| N.4 100 mm 140°C within 24h | ADR §2.2.42.1.5(c); MTC §33.4.6.3–.4 | Strict >200°C or ignition; negative screen otherwise |
| N.4 package exemption ≤3 m³ | ADR §2.2.42.1.5(c) Note 1; MTC §33.4.6.4.2(b) | 100 mm at 120°C negative; ≤3,000 L includes equality |
| N.4 package exemption ≤450 L | ADR §2.2.42.1.5(c) Note 2; MTC §33.4.6.4.2(c) | 100 mm at 100°C negative; ≤450 L includes equality |
| Pyrophoric PG I | ADR §2.2.42.1.8(a) | Provisional |
| N.4 25 mm 140°C positive PG II | ADR §2.2.42.1.8(b); MTC §33.4.6.4.3 | Provisional; 100 mm test optional if 25 mm already positive |
| N.4 100 mm positive/25 mm negative PG III | ADR §2.2.42.1.8(c); MTC §33.4.6.4.4 | Only if package-volume exceptions not met |
| Mixture actual degree of danger | ADR §2.2.42.1.6 and §2.1.3 | Sample formulation/mixture evidence required |
| Named substance negative check | ADR §2.2.42.1.7 | Additional manual review required |
| Not accepted UN 3255/UN 3127 conditional | ADR §2.2.42.2; §2.1.3.7 | Explicit verified named-entry gate |
| Organometallic routing | ADR §2.3.5 and Figure 2.3.5 | Cross-class/UN-integrator referral |
| Primary/subsidiary precedence | ADR §2.1.3.10 | Never resolved here |
| Table A / PG / SP | ADR §3.2.1, §3.3.1 | Never resolved here |
| Method details | UN MTC Rev.8 §§33.4.4–33.4.6 | Partial algorithm + upstream protocol conformance attestation |
| Rev.8 Amend.1 | ST/SG/AC.10/11/Rev.8/Amend.1 | No §33.4 literal changes found; independent check pending |

## Specific PG and evidence limitations

* N.2 (powder only): 1–2 mL, about 1 m fall onto non-combustible surface, 6 repetitions unless positive earlier; 300.000 s positive, 300.001 s negative only if all 6 runs complete. No 5-min negative inferred from absent values.
* N.3: ≈5 mL inert-carrier stage, 6 runs; only after all six negatives proceed to 0.5 mL indented-filter stage, 3 runs, 25±2°C, 50±5% RH. Charring is itself a positive criterion. Physical fixture quantities, grade and hardware conformance require external raw-report attestation.
* N.4: 25/100 mm sample cubes, oven 100/120/140°C ±2°C, thermocouple and geometry controls in §33.4.6.2. Strict `>` sample temperature versus oven +60°C; 24h observation. ADR nominal >200/180/160°C may differ near an actual-oven tolerance boundary; the module blocks disagreement. **Package volume is per package, not consignment**, and 450 L and 3,000 L are inclusive. PG II/III remain candidates only.
* ADR §2.2.42.1.5(c) 27 m³ / 50°C and §2.2.42.1.8(b) 450 L / 50°C scale-up conditions are **not algorithmically adjudicated**. No transformation from ordinary N.4 data is invented. Expert referral is necessary if invoked.
* Named-entry applicability, article codes, organometallic flowchart, chemicals with combined hazards, dangerous-other-class substances, package conditions and PG column (4) need downstream verified evidence. Potential Class 4.1/4.3/5.1 candidates are referred, not prioritized.

## Results and testing

`class42.test.js` has 62 distinct synthetic `node:test` declarations. It was fetched back from GitHub and executed against the exact GitHub-fetched `class42.js` in a V8 harness that shims the test and assertion API: **62 passed, 0 failed**. An initial 30-case developmental V8 check also passed. Final source/result object SHAs are in `test_results.json`.

Coverage: solid/liquid 300s inclusive cutoff (300.001 negative); six/three repetitions; N.2 sample 1/2mL limits; N.3 23/27°C and 45/55% RH; N.4 200/180/160°C boundary, oven ±2°C, positive/negative 25/100 mm, package 450/450.001 and 3,000/3,000.001L, missing temperature/volume/test, cross-class, named and prohibited cases, conflicting repeated tests. These **do not establish real-world regulatory correctness**. Node CLI, GitHub CI, lab validation, schema validator and independent golden benchmarks remain outstanding.

## Mandatory Lead review decisions and unresolved issues

1. **Adopt or adapt the draft canonical schema/status taxonomy** from PR #8, reconciling candidate vs full finding and how a package-specific exemption is represented. Merge statuses only through Lead-owned adapter.
2. **Bind test evidence to authenticated lab reports**, signed provenance, calibration, test apparatus, raw thermograms, sample formulation/particle size, mixture details, package volume and method conformance. Boolean flags are not sufficient legal substantiation.
3. **Independently review the 36 rule references** against supplied official PDF page images, Rev.8 Amendment 1 and both 2025 English corrigenda. Resolve ADR nominal thresholds versus actual oven +60°C near tolerance.
4. **Resolve 27 m³ / 450 L >50°C exception criteria** and what independent scale-up study could justify them. Current evaluator cannot reach these exceptions automatically.
5. **Implement article, named-entry and special-provision gateways**; refer §2.2.42.3 codes and Table A exact importer row IDs. Verify PG column (4) and actual package route; no local entry selection.
6. **Resolve dangerous competing 4.1, 4.3 and 5.1 paths, Class 1 UN3127 exception**, organometallic §2.3.5 N.1–N.5 and secondary hazards ST/SC/SW/SO using cross-class precedence. No unilateral labels.
7. **Scope and assay mixture cases**, altered concentrations/stabilizers/wetting liquids, ageing, oils/catalysts, temperature exposure, unusual articles and tests impracticable by physical state.
8. **Validate 62 synthetic tests in actual Node CI**, JSON Schema validator, and expert-labelled raw test datasets; add security and branch ownership CI. Avoid generating any final SDS release until all sign-offs and rollback steps exist.
9. **Regulatory release guard:** independent qualified reviewer signoff, change-control approval, regression tests, verified Table A/SP/legal transport acceptance, complete audit log and source hashes. Keep draft until then.

Self-heating liquids are specifically marked unsupported under the powder/granular N.4 cube protocol, pending an expert-supported method or exact named-entry decision. A low-temperature N.4 positive conflicting with a negative 100 mm @140°C is blocked, and all N.4 findings carry an external 27 m³ / 450 L scale-up exclusion review requirement.

No independently approved classification or legal declaration is included here. The Class 4.2 module is **provisional and not production-ready**.
