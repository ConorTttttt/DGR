# Unsupported-case, exception and failure-mode register — ADR 2025 Class 4.3

**Provisional**. Every item must be explicitly resolved; a missing result is not a negative Class 4.3 finding and a Class 4.3-negative result is not a global "not dangerous goods" finding.

| ID | Pathway / issue | ADR / MTC authority | Required gate / owner |
| --- | --- | --- | --- |
| U01 | Pyrophoric substance: ADR says do **not** apply N.5, while MTC describes N.5 under nitrogen | ADR 2.2.43.1.3; MTC 33.5.3.1 | Reject test route; Class 4.2 specialist + independent regulatory interpretation |
| U02 | Organometallic substance/solution/formulation, including pyrophoric or self-heating and flammable diluent routes | ADR 2.3.5 Figure 2.3.5; MTC N.1–N.5 | Dedicated flowchart and precedence approval |
| U03 | Article containing water-reactive substances; N.5 on bulk contents not sufficient for article entry | ADR 2.2.43.1.1–1.2, 2.2.43.3 | Agent 4 named-entry/SP and article evidence review |
| U04 | Named entries or contradictory named entry information | ADR 2.2.43.1.4, 2.2.43.1.7, 3.2 Table A | Verify actual named row, test-supported exception and SP |
| U05 | Mixture inferred from components or CLP/GHS categories rather than actual offered-mixture N.5 test | ADR 2.2.43.1.6, 2.1.3.1–2.1.3.4 | Fail closed; representative whole-mixture and Ch 2.1 screening |
| U06 | Named-predominant mixtures with exceptions (a)-(d) | ADR 2.1.3.3 | Agent 4 resolves correct entry; do not reuse neat substance automatically |
| U07 | Waste composition poorly known and purported default PG II | ADR 2.1.3.5.5 | Explicitly unavailable to substances of Class 4.3; review waste-specific evidence |
| U08 | Multiple hazard classes/suspected hazard precedence | ADR 2.1.3.5.3–.5.4, 2.1.3.10 | Lead/precedence specialist only |
| U09 | Water-reactive solid plus oxidizing hazard; UN 3133 potential | ADR 2.2.43.2; 2.1.3.7 | If row UN3133 actually assigned: carriage disallowed absent Class 1 requirements; no automatic UN assignment |
| U10 | Pyrophoric dust/powder, pyrophoric metals or alloys | ADR 2.2.43.3 footnotes (a),(b) | Refer Class 4.2; do not test automatically as non-pyrophoric |
| U11 | Metals/alloys that are readily flammable but not pyrophoric, self-heating or gas-emitting on water | ADR 2.2.43.3 footnote (a) | Potential Class 4.1; negative is not global non-dangerous |
| U12 | Compounds of phosphorus with heavy metals (e.g. iron, copper), entry scope depends on substance | ADR 2.2.43.3 footnote (a) | Human identity/entry check; no structural auto exemption |
| U13 | Chlorosilanes that do **not** emit flammable gas with water; FP below 23°C vs at/above 23°C | ADR 2.2.43.3 footnote (c) | Separate Class 3 / Class 8 evidence review and flash-point gate |
| U14 | More-stringent real-world experience conflicts with or exceeds N.5 test | ADR 2.2.43.1.4; 2.1.3.1 | Explicit expert review; never override downward |
| U15 | Gas identity unknown / flammability not tested | MTC 33.5.4.3.5 | Unresolved; test gas flammability |
| U16 | Missing sample ID, source hash, issuer, authentic source or contradictory primary reports | Lead v0.1.0 contract; ADR 2.2.43.1.4 | Block; authenticate primary sources and resolve conflict |
| U17 | Solid powder >1 mass% under 500 μm or friable but no whole-sample grinding | MTC 33.5.4.3.5 | Reject N.5 result; repeat correct method |
| U18 | Incorrect sample form, temperature 20°C, distilled water, or ambient pressure | MTC 33.5.3.1; 33.5.4.3.2–.5 | Reject incompatible test |
| U19 | Missing stage order/observations or unsupported skip-to-terminal assertion | MTC 33.5.4.3.1–.4 | Complete or document known nonviolent route |
| U20 | Fewer than three terminal repeats, mass above 25 g, incorrect 100–250 ml target, missing hourly data | MTC 33.5.4.3.5 | Method invalid/incomplete; do not assert a negative |
| U21 | Erratic/increasing gas evolution after 7 h without valid extension/stop | MTC 33.5.4.3.5 | Extend up to five days or document prescribed sufficiency |
| U22 | No general ignition tendency evidence, or PG I / PG II exclusion absent | ADR 2.2.43.1.8(a)–(c) | Class may be positive but PG stays unresolved; no assumed lower PG |
| U23 | Conflation of 10 L/kg over one minute with 20 L/kg/h | ADR 2.2.43.1.8(a)-(b) | Unit-specific typed measurement paths and boundary tests |
| U24 | Nonflammable gas positively measured, no spontaneous gas ignition | ADR 2.2.43.1.5 | Class-scoped negative only if full valid method; other classes remain possible |
| U25 | Other emitted gases (toxic, corrosive) or environmental risk | ADR 2.2.43.1.2, 2.1.3.8 | Other class specialists provide supported candidates |
| U26 | Any candidate UN number, classification code W/WF/WS/WO/WT/WC/WFC, PG or named-entry SP not verified | ADR 2.2.43.1.2; 2.2.43.3; Ch 3.2/3.3 | Agent 4; unique row + Column (4) PG + SP review mandatory |
| U27 | ADR English Corrigenda 1 and 2 not independently reconciled against source extracts | UNECE ECE/TRANS/352/Corr.1 and Corr.2 | Lead legal source review before sign-off |
| U28 | Manual Amendment 1 text-scanned as not mentioning N.5 but no independent amendment sign-off | UN MTC Rev8/Amend1 | Confirm complete official source and applicability |
| U29 | Valid external authority decision, identity of signer or professional approval not authenticated | Lead contract | No regulatory validation or SDS publication |
| U30 | Contradictory no-gas statement and positive measured gas collection / rate | MTC 33.5.4.3.5 | Fail closed; laboratory clarification |
| U31 | Simultaneous contradictory measurements, nonmonotonic series or no timestamped linkage between minute/hour readings | MTC 33.5.4.3.5 | External lab data-quality review; this module does not prove dynamic consistency |
| U32 | Current evaluator requires seven hourly rates and one-minute observations for a PG-complete negative | MTC 33.5.4.3.5; ADR 2.2.43.1.8 | Deliberately conservative implementation gate, not claimed to be a literal regulatory data-format requirement |

**Engineering constraints vs law:** JSON keys, source hashes, exact BigInt comparator, required complete repeated observations and output statuses are conservative engineering assumptions. Legal requirements are those cited in ADR/MTC, not software-enforced field formats.
