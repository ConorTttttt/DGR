# Agent 9 → Lead Agent — Class 6.1 audit handover

**Status: DRAFT, candidate-only, unvalidated.** No claim of independent regulatory approval. Target: supplement Agent 3's Class 6.1 prototype in draft PR #2; no edits to Agent 3's files are authorized or made here.

## PR #2 audit findings

Existing `agents/agent3/adr2025/class61.py` provides oral/dermal/dust-mist/vapour numerical thresholds and time conversion but lacks explicit route/test provenance and mixture implementations. It conflates pending human experience with boolean attestations, has no explicit dust/mist trigger or sample >90% respirable validation, does not implement §2.2.61.1.7.2 special Class 8 PG I dust rule, and lacks §2.2.61.1.9/.10/.11 mixture/pesticide methods. It allows a provisional PG I positive route despite unchecked other routes; the new implementation retains only an explicitly candidate label and fail-closed final assignment. It also misses chemical instability/prohibited substances, aerosol test eligibility, source metadata and named-entry gates.

## What the Agent 9 module delivers

* 27 clause- and edition-indexed requirement records plus 26 exception/blocker records.
* Deterministic decimal PG I/II/III candidate logic for whole-carried-material oral, dermal, aerosol and vapour routes.
* 1h vs 4h precedence, species/observation/sample and inhalation form, concentration, temperature/pressure checks.
* Oral/dermal 1-active and multi-active mixture methods; vapour constituent formula and threshold animal-series alternatives.
* Human-experience expert referral, tear gas floor, Class 8 dust/mist PG I competition explicit state, missing-route distinction, pesticide and named-entry flags.
* 38 synthetic Python unittest groups passed locally; no CI or independent lab data asserted.

## Required Lead mapping

The module is intentionally side-by-side under `agents/class61/`. To integrate, Lead must map `evaluate(e)`/`route_results`/`missing_evidence`/`referrals` to the canonical evidence schema/registry and decide whether to replace or wrap Agent 3's `adr2025.class61`. Don't perform a blind textual merge. Lead must issue a schema and attestation contract, guard against CLP/GHS shortcuts, and ensure source evidence is authenticated. The current `screen.*_reviewed` fields are caller attestations and **not proof** of named-entry approval.

## Precedence agent (Class 8) handoff

Priority referral: ADR 2.2.61.1.7.2 and 2.1.3.5.3(h): where a candidate substance meets Class 8 and has dust/mist inhalation PG I, only allow a Class 6.1 allocation if oral or dermal toxicity reaches PG I or II. If both are PG III/less, Class 8 takes precedence if appropriate; if either is unknown, block/referral. Separate determination of the major hazard must use §2.1.3.10 and exact actual Table A candidate entry. The Agent 9 engine **never selects** the primary class or final PG.

## Named-entry / pesticide handoff

Pesticide (§2.2.61.1.11/.11.1/.11.2) requires active substance, preparation type, liquid/solid physical form, subsidiary hazards and PSN from §3.1.2. WHO data can supply LD50, not WHO transport category. Lead/Agent 1 must reconcile 2.2.61.3 collective list, Chapter 3.2 Table A exact UN entry and PG column (4), and Chapter 3.3 SP including 386. Check 2.2.61.2.2 carriage prohibitions (HCN forms, carbonyls, TCDD, UN2249, phosphides) and 2.2.61.2.1 instability. No automated UN/PSN claim.

## Known limitations, requested actions

1. Independent reviewer compare every entry in `rule_register.json` with the supplied ADR 2025 English pages and inspect ECE/TRANS/352 Corr.1 and Corr.2. Cross-check MTC Rev.8 and Amendment 1 for any relevant cross-references. No Class 6.1 LD50/LC50 test method is substituted from the MTC.
2. Verify human evidence priority against toxicological expert judgement and validated tests; document test confidence limits and any animal study variants. The engine currently requires specifically documented species/14-day observations; other valid study formats are **escalated**, not dismissed as negatives.
3. Independently verify 2.2.61.1.9 liquid vapour mixture partial-pressure units/molar-fraction closure; verify vapor composition, non-ideal equilibrium and LD50 formula synergy. Review whether the full test-method admissibility contract should be delegated to a lab-evidence adapter.
4. Review the §2.2.61.1.7.2 Class 8 exception and the inhalation-PG I general precedence condition with Agent 2; add cross-class expert benchmark cases.
5. Verify pesticides, Named Entry, Table A and SP dependencies with Agent 1, and cross-check final PG decision against applicable Table A exact entry and any restrictions.
6. Run the Python unittest suite independently in CI and develop true experimental golden cases with chain-of-custody evidence and uncertainty evaluation; run static/security/type analysis.
7. Approve canonical schema, code ownership, PR stacking strategy, independent regulatory sign-off and rollback before merge to production.

## Explicit release block

`assignment_permitted=False`; no `UN`, final `PG`, primary class, PSN, UN numbering or SDS Section 14 output. Do not mark approved until competent independent regulatory review and Lead sign-off.
