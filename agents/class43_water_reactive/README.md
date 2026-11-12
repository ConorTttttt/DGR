# ADR 2025 — Class 4.3 (Agent 6) water-reactive flammable-gas candidate evaluator

**State: DRAFT / provisional; not independently reviewed.** This module **cannot** assign a final UN number, proper shipping name, classification code, Table A packing group, carriage permission, or publishable SDS Section 14 result.

## Interface and ownership

- Ownership: `agents/class43_water_reactive/`, branch `agent6/adr2025-class43-water-reactive`. Do not edit Lead/other agent files.
- Public function: `const { evaluateClass43 } = require('./classify');`
- Input contract: `evidence.schema.json`; reports must identify the tested sample, primary laboratory document, issuer, document locator and SHA-256.
- Output: Lead Agent 0 `class_evaluation`-shaped object (PR #6 contract version 0.1.0); candidate/negative/indeterminate only. An external adapter must construct the canonical `evidence` array and validate the full integration packet. PR #8 has a different status taxonomy requiring a Lead decision.
- Subclass/UN/PG/SP reconciliation remains with other agents. All PG candidates are **intrinsic test candidates**, not ADR Table A column (4) assignments.

## Source register

- ADR 2025, ECE/TRANS/352 Volume I, **Chapter 2.2.43 §§2.2.43.1.1–1.8, §2.2.43.2, §2.2.43.3** and footnotes; Chapter 2.1 §§2.1.3.1–2.1.3.7, 2.1.3.10; §2.3.5 and Figure 2.3.5.
- UN Manual of Tests and Criteria **Revision 8**, Part III **§§33.5.1–33.5.4.5**, Test N.5. Amendment 1 checked by local text scan for explicit §33.5/N.5 changes (none found); substantive independent confirmation remains pending.
- Supplementary upstream references: ADR Chapter 3.2 Table A and Chapter 3.3, especially all named entries and their special provisions. No automatic matching is included.
- SHA-256, edition, local filename and PDF-page metadata: `rule_register.json`. Official ADR source directory: https://unece.org/adr-2025-files. ADR English corrigenda 1 and 2 are listed by UNECE; independent check of their applicability to this module is pending.

## Intrinsic Class 4.3 test criteria (not final classification)

| Test finding | Effect | Exact authority |
| --- | --- | --- |
| Spontaneous ignition of gas at **any** N.5 stage | Class 4.3 criterion met | ADR §2.2.43.1.5(a); MTC §33.5.4.4.1(a) |
| Confirmed flammable gas **>1 L/kg/h** | Class 4.3 criterion met | ADR §2.2.43.1.5(b); MTC §33.5.4.4.1(b) |
| Reacts vigorously at ambient temperature, gas generally tends to ignite spontaneously | PG **I** candidate, with affirmative evidence | ADR §2.2.43.1.8(a) |
| Flammable gas **≥10 L/kg during any 1-minute period** | PG **I** candidate | ADR §2.2.43.1.8(a) |
| Reacts readily, max rate **≥20 L/kg/h**, PG I demonstrably not met | PG **II** candidate | ADR §2.2.43.1.8(b) |
| Reacts slowly, max rate **>1 L/kg/h**, neither I nor II applies | PG **III** candidate | ADR §2.2.43.1.8(c) |

**Units are not interchangeable:** N.5's `one_minute_volumes_l_kg` denotes **L/kg over a measured one-minute period**, not L/kg/h. `hourly_rates_l_kg_h` denotes L/kg/h. Comparisons are performed on base-10 decimal representations using BigInt fixed-point logic, so close boundary values do not collapse to IEEE-754 doubles. **Equality at 1 L/kg/h is class-negative**, not Class 4.3 positive; equality at 10 L/kg/minute-period is PG I; equality at 20 L/kg/h is PG II when the PG I exclusion and reaction-behaviour requirements are independently supported.

## N.5 evidence method

MTC §33.5.3.1 and §33.5.4.3:
1. Test the actual commercial solid or liquid at 20 °C with distilled water. Document gas emergence and spontaneous gas ignition for **trough**, **filter-paper-on-water** and **pile plus a few drops of water**. A verified N.5 known-nonviolent route may proceed directly to §33.5.4.3.5. Stop the test once gas spontaneously ignites.
2. For solid test material, inspect particles smaller than **500 μm**; if **more than 1% by mass** is such powder **or** the substance is friable, grind the entire sample before terminal testing.
3. Perform **three** terminal tests at 20 °C / atmospheric pressure, maximum **25 g** test substance; aim to collect **100–250 ml** gas, read volumes over seven hours at **one-hour intervals**. If erratic/increasing after seven hours, extend up to **five days** unless the prescribed stabilization/sufficiency conditions for early stop are documented.
4. Document identity and flammability of evolved gas; if chemical identity is unknown, test for flammability. Missing, incompatible or conflicting evidence is not a negative result.
5. Emit only provisional class and PG candidates, with rule and evidence references. An independent review must authenticate the input document and verify sample identity, test details and full ADR applicability.

## Explicit unsupported and external gates

`unsupported_cases.md` lists all blocked routes. Key examples: pyrophorics (ADR §2.2.43.1.3 conflicts with MTC §33.5.3.1 nitrogen test advice), organometallic N.1–N.5 flowchart (ADR §2.3.5), articles and named entries, mixing/solution entry rules, waste default PG-II prohibition for Class 4.3, incomplete gas identity, invalid temperatures, and UN 3133 prohibition on carriage **if** actually assigned. Both final UN assignment and primary/subsidiary precedence are explicitly deferred.

## Tests and release status

`classify.test.js` contains **43 synthetic Node tests**, covering positive, negative, strict/inclusive threshold, near-boundary fixed-point, incompatible-test and missing-evidence scenarios. `test_results.json` distinguishes **28/28 earlier developmental V8 checks passed** from **current Node suite not executed**. Run:

```sh
node --check agents/class43_water_reactive/classify.js
node --check agents/class43_water_reactive/classify.test.js
node --test agents/class43_water_reactive/classify.test.js
```

Independent validation, CI, source corrigenda reconciliation, complete named-entry Table A rows and full special-provision evaluation are **not complete**. Do not merge for live SDS classification or treat any class-negative outcome as globally not regulated.
