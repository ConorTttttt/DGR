# Agent 13 — unsupported cases, exceptions and review blockers

| Case | Clause/source | Current behaviour | Owner or action |
|---|---|---|---|
| Actual UN Table A rows, Column (4) PG, Column (6) SP | ADR 2025 3.2.1, 3.3 | Only externals with matching evidenced row can produce PG III on aquatic candidate; all else PG null | Agent 1 + Lead must verify entries, no blind attestations |
| Environmental hazard with another class/Class 9 entry | 2.1.3.8; 2.2.9.1.10.6 | Environmental-role descriptor; no primary 3077/3082 or PG | Agent 2 decides primary/subsidiary/marking and precedence |
| CLP fallback when aquatic data unavailable | 2.2.9.1.10.5 | No CLP inference or automatic conversion | Lead to approve narrowly evidenced source-based fallback, if any |
| Incomplete trophic coverage and unusual algae | Table 2.2.9.1.10.3.1 Notes 1–5; Figure 2.2.9.1.10.3.1 | Requires completeness/professional review; no negative if missing | Aquatic scientist; integrate per-trophic workflow |
| Metals, poorly soluble inorganic species | 2.2.9.1.10.1.3 | No mechanistic metal/speciation model | Specialist GHS Annex 9/10 assessment |
| Unlisted/unknown aquatic ingredients | 2.2.9.1.10.4.6.5 | Categories non-definitive, negative never asserted | Require constituent/provenance and composition verification |
| Highly toxic ingredient below 0.1% | 2.2.9.1.10.4.1; 4.6.4 | Conservatively include known contributors regardless of threshold; M always required | Lead approve conservative policy |
| Acute + chronic additive fractions with missing endpoint or incompatible taxa | 2.2.9.1.10.4.5.2–5.4 | Blocks full combined computation | Test-expert review; alternate component-specific methods |
| Bridge claims without documentary similarity | 2.2.9.1.10.4.4.2–4.4.6 | Indeterminate unless all per-principle evidence attestations are present | Reviewer verifies real test/composition records |
| Battery type tests, prototypes, damaged/defective, small cells, installed in equipment/CTU, sodium exceptions | 2.2.9.1.7.1/1.7.2; 2.2.9.2; 3.3 SP188/230/310/376/387/389/400/636/670; MTC 38.3 | No SP applicability engine; must provide battery standard-design checks and SP review; noncompliance blocks rather than means non-dangerous | Agent 1 and battery specialist; include ADR 2025 + MTC Amendment1 delta |
| Lithium battery 38.3.5 test-summary button-cell exception | 2.2.9.1.7.1(g) | Exempted only when `button_cells_installed=True`; QMP/type-test still needed | Verify special context |
| Vehicles, hybrid batteries, damaged machinery, lithium-ion powered vehicles UN3556/3557, sodium powered vehicles UN3558 | 2.2.9.1.14; 2.2.9.3 M11; 3.3 | M11 entry-only pathway; no vehicle heuristics | Agent 1, vehicle specialist |
| Asbestos in bonded forms, PCB/PCT articles, capacitor thresholds and PCB mixture exclusion | 2.2.9.1.4–.5; 2.2.9.1.14; 2.2.9.3 | Limited identity and numeric threshold evidence; all SP/entry exemptions unresolved | Agent 1 SP lookup; material expert |
| GMMOs/GMOs competent authority authorization, ready-to-administer medicines, live animals | 2.2.9.1.11 Notes 1–5 | Requires class 6.1/6.2 and authorizations; no blanket relief | Agent 2 + Lead + competence authority |
| Class 9 packing group for non-aquatic entries and entries with no PG | 2.2.9.1.15; 3.2.1 Table A (4) | Always null pending verified entry-specific row; no auto-PG | Agent 1 controls DGL |
| Known classifications with source only 'CLP' | 2.2.9.1.10.5 + project prohibition | Rejected for summation constituent basis | Lead source-evidence policy |
| Corigenda ECE/TRANS/352 Corr.1/Corr.2 | UNECE ADR 2025 index | Delta assessment outstanding | Lead regulatory QA |

No case can output a global `not_regulated` state. `criteria_not_met` is restricted to fully evidenced local pathways; it does not negate another transport class or restriction.
