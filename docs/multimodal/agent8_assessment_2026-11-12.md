# Agent 8 — Multimodal expansion: regulatory/data/licensing assessment

> **Status:** PROPOSED / RESEARCH ONLY; **not legally validated**, not an executable rule set, and not approved by Lead Agent.
>
> **Research cut-off:** 2026-11-12 (UTC). **Baseline:** ADR 2025, English. **Owner:** Agent 8. **Repository:** DGR. **No engine changes made.**

## 1. Scope and source hierarchy

The SDS output requirement is Regulation (EU) 2020/878, Annex II, **Section 14** (14.1–14.7). It expressly requests transport information for road, rail, sea, inland waterways and air where relevant, and requires information gaps or inapplicability to be stated. Under EU transport law, Directive 2008/68/EC provides the road/rail/inland-waterway interface. This document does **not** determine which regulatory regime applies to any particular real shipment.

Normative sources by mode: ADR (UNECE); RID (OTIF/COTIF Appendix C); ADN (UNECE); IMDG Code (IMO, packaged sea cargo); ICAO Annex 18 and Doc 9284 (international air). IATA DGR is an airline-industry implementation/operational reference that must not replace the ICAO legal authority. For sea **bulk** cargo, separately evaluate applicable IMO instruments rather than treating the packaged-goods IMDG Code as comprehensive.

The project already has a preliminary ADR 2025 Parts 1–3 clause index under `regulations/adr/2025/`. Its README states **132 index entries**, **zero transcribed Table A rows**, and no validated executable rules as of the inspection. This assessment **does not alter any Agent 1 artifacts** or assert that any shared schemas already exist.

## 2. Framework/edition/source register

| Mode | Authority, edition and temporal applicability (as of 2026-11-12) | Regulatory references to verify for integration | Difference from ADR | Source |
|---|---|---|---|---|
| ADR — road (baseline) | UNECE, **ECE/TRANS/352**, ADR 2025, effective 2025-01-01, English, Volumes I–II | Vol. I, Parts 1–3, especially Chapter 2.1, 3.2 Table A and Chapter 3.3; Vol. II, Parts 4–9 | Road carriage conditions, road exemptions and tunnel/vehicle provisions. | https://unece.org/adr-2025-files |
| RID — rail | OTIF, RID 2025, Appendix C to COTIF with Annex, effective 2025-01-01 | RID Parts 1–7, especially Chapters 2.1, 3.2, 3.3; verify entry/column equivalence individually | Rail-specific operational/vehicle/tank provisions. OTIF confirms harmonisation with ADR/ADN, **not** legal identity. | https://otif.org/test/en/?page_id=1105 |
| ADN — inland waterways | UNECE, **ECE/TRANS/351**, ADN 2025, effective 2025-01-01 | ADN Chapter 3.2 **Tables A and C**; 3.2.3.1 explanation of Table C; Parts 7–9 as relevant | Dry-cargo versus tank-vessel regimes, vessel type and filling constraints; tank-vessel-only environmental hazard disclosures may differ from other modes. | https://unece.org/transport/dangerous-goods/adn-2025 |
| IMDG — packaged sea | IMO, **2024 Edition, Amendment 42-24**, adopted through MSC.556(108), mandatory 2026-01-01 | IMDG 2.10 (marine pollutants), 3.2 (DGL), 3.3 (special provisions), 5.4 (transport information), 7.2 (segregation): **candidate review references, not yet locally validated** | Marine-pollutant criteria, maritime stowage/segregation and packaging provisions. | https://www.imo.org/en/publications/pages/imdg%20code.aspx |
| ICAO TI — air | ICAO, **Doc 9284, 2025–2026 Edition**, in effect 2025-01-01 to 2026-12-31, with addendum/corrigenda | ICAO TI Parts 2–5 (classification, list, packing, shipper duties): **candidate part-level references pending purchase and verification** | Air-only prohibitions/restrictions, passenger vs cargo aircraft, quantity limits, packing and possible ID-number entries. | https://www.icao.int/Dangerous-Goods/Technical-Instructions |
| IATA — industry air implementation | IATA DGR **67th Edition (2026)** | 67th DGR plus current addenda, State and operator variations; chapter/paragraph crosswalk **not verified** | Airline acceptance and operator/State variations; do not treat IATA text alone as statutory authority. | https://www.iata.org/dgr |
| IMO bulk cargo — separate scope | Applicable SOLAS/MARPOL instruments and IBC, IMSBC, IGC or other applicable Code | REACH Annex II §14.7; IBC chapters 17 and 18 where relevant | Bulk cargo regimes are distinct from packaged IMDG classification; needs its own scope decision and content model. | https://eur-lex.europa.eu/eli/reg/2020/878/oj |

**Edition warning:** IMO Amendment **43-26** was adopted in 2026; IMO states voluntary application from 2027-01-01 and envisaged mandatory entry into force 2028-01-01. A published next edition is **not** automatically an applicable edition. Source: https://www.imo.org/en/mediacentre/meetingsummaries/pages/ccc-12-meeting-summary.aspx

**Correction warning:** Official IMO **December 2025 errata/corrigenda** for Amendment 42-24 cover, among other provisions, section 2.5.3.2.4 and SP 188. These need a provenance-aware correction layer; do not silently overwrite a base text value. Source: https://wwwcdn.imo.org/localresources/en/publications/Documents/Supplements/English/QO200E_errata_December2025_PQ.pdf

**Air corrections:** ICAO lists Addendum No. 1 (2026-03-27) and Corrigendum No. 2 (2026-05-07) for Doc 9284, 2025–2026. Source: https://www.icao.int/publications/doc-series/doc-9284

## 3. SDS 14 mapping (directly supported by EU Annex II)

- **14.1 UN number or ID number**: preserve identifier **namespace** (UN/ID) and the applicable mode; use an explicit `not_determined` state rather than empty string semantics.
- **14.2 UN proper shipping name**: retain exact mode-specific name and applicable technical-name supplements. ADN **Tables A and C** and sea technical-name supplements are explicitly referenced in Annex II.
- **14.3 Transport hazard class(es)**: primary hazard class and applicable subsidiary risk(s), verified per mode.
- **14.4 Packing group**: explicit value / legally not applicable / unknown are distinct outcomes.
- **14.5 Environmental hazards**: capture maritime marine-pollutant criteria and ADN **tank-vessel-only** environmentally hazardous status separately where applicable.
- **14.6 Special precautions for user**: precautions for each relevant mode; distinguish classification facts from downstream conditions of carriage.
- **14.7 Maritime transport in bulk according to IMO instruments**: include only when **intended** for bulk carriage under IMO instruments; a packaged-goods IMDG entry alone cannot answer it.

Reference: Commission Regulation (EU) 2020/878, Annex, replacement of Annex II to REACH, §14 and §§14.1–14.7: https://eur-lex.europa.eu/eli/reg/2020/878/oj

## 4. Mode-specific differences requiring data (NOT rules yet)

| Differential | Mode | Data/inputs required | Planned output boundary |
|---|---|---|---|
| UN or ID number, possible distinct PSN | All; ID especially relevant to air | Mode-specific official DGL/identifier table with effective edition and name qualifiers | Classification result, not inferred from ADR |
| Non-overlapping entry/special provision | RID, ADN, IMDG, ICAO | Complete mode list, special provision text, correction version and cross-references | Mode override only when explicit provision reviewed |
| Marine pollutant | IMDG | Mode-specific marine pollution criteria, composition/test evidence, applicable entries | Separate marine pollutant result; not simple mapping of CLP aquatic toxicity |
| ADN tank-vessel environmental hazard | ADN | Tank-vessel intended use, ADN Table C, applicable environmental assessment | Additional 14.5 statement when relevant |
| Passenger/cargo aircraft permission | ICAO/IATA | Packing instruction, passenger/cargo quantities, forbidden entries, State/operator variation data | Transport/acceptance conditions, not “not regulated” |
| Stowage and segregation | IMDG | Maritime segregation and stowage provisions plus co-loaded cargo details | Shipment condition, not generally decidable from SDS alone |
| Rail and vessel conditions | RID, ADN | Wagon, tank, vessel, quantity, route, packaging and operation facts | Carriage conditions / insufficient shipment evidence |
| Bulk sea cargo | IMO bulk | Intended bulk shipment, product type, bulk-specific IMO code data | Independent 14.7 branch; not an IMDG packaged-goods fallback |

A common UN number or hazard class is insufficient to assert that all these conditions are met. Classifying a substance and determining whether a particular consignment can travel are **different decisions**.

## 5. Publication access, copyright and licensing: acquisition gates

| Publisher/data | Public access found | Current rights evidence | Required clearance before systematic ingestion, digitisation, SaaS use or redistribution |
|---|---|---|---|
| UNECE ADR 2025 | Official downloadable PDFs | Uploaded ADR Vol II copyright page and official landing page say UN copyright (2024), all rights reserved; excerpt reproduction permissions explicitly referenced. | Confirm machine extraction, internal structured storage, commercial software/SaaS use and downstream display/redistribution rights with UN Publications / rights holder. Free download is **not** an open-data licence. |
| UNECE ADN 2025 | Official downloadable PDF | UNECE says copyright UN 2024, all rights reserved; online text for information; directs to official paper edition and Copyright Clearance Center for excerpts. | Same UN permission review, including structured Tables A/C. |
| OTIF RID 2025 | Official publicly linked edition, with English version shown | Public retrieval **does not establish** rights to redistribute or create reusable commercial data. Specific digital/data licence not verified. | Contact OTIF about index/structured DGL/derivative software licensing and permitted publication. |
| IMO IMDG 42-24 | Commercial Code; official amendment information and errata accessible | IMO expressly says use of all or part of IMO sales publications in print or electronic format requires permission and is subject to royalty agreements. | Written IMO permissions/royalty terms for extraction, storage, software use, customer distribution and update feed. |
| ICAO Doc 9284 2025–2026 | Paid ICAO publication; errata/addenda public | ICAO Store lists single-user digital licence, five-year digital access, no editing original or printing, multi-user licences by quote. | Separate ICAO agreement for ingestion, multiple developers/users, automated classification, commercial embedding and outputs. |
| IATA DGR 67th/2026 | Paid annual manual; selected public change guides/addenda | IATA marks publication rights reserved; **specific automated-use/data licence terms not independently verified**. | Request IATA written grant/data product entitlement for software/data derivation, API, storage and customer access; separately assess operator-variation coverage. |
| IMO bulk instruments | Publisher-dependent and likely licensed for commercial source texts | Do not presume an IMDG purchase includes IBC/IMSBC/IGC or supplements. | Clear rights by instrument and edition, separately from packaged IMDG. |

Official permission/access references:
- ADR source catalogue: https://unece.org/adr-2025-files
- ADN edition notice: https://unece.org/transport/dangerous-goods/adn-2025
- RID access: https://otif.org/test/en/?page_id=1105
- IMO copyright terms: https://www.imo.org/en/publications/pages/permissionrequests.aspx
- ICAO licence and product: https://store.icao.int/en/technical-instructions-for-the-safe-transport-of-dangerous-goods-by-air-doc-9284
- IATA manual: https://www.iata.org/dgr

**Compliance control (engineering proposal):** Each source record must store `licence_review_state`, permitted uses, publisher, edition, access expiry, authorised users, derived-data entitlement, source URI, access date and legal approver. An unknown licence state **blocks bulk ingestion and reproduction**; it does **not** block storing metadata and original paraphrased source links.

No opinion on enforceability of copyright/database rights is given; obtain publisher/legal approval.

## 6. Proposed shared-interface contract (pending Lead Agent)

Do **not** create or modify shared schemas from this Agent 8 document. The following fields are an interface request, not an implemented contract:

- **Request:** `material_evidence_id`, `intended_modes[]`, `territories[]`, `assessment_date`, `purpose: SDS14|consignment`, `packaged_or_bulk`, optionally quantity/packaging, aircraft type, vessel type, operator and route.
- **Mode context:** `mode`, `regime`, `edition_id`, `amendment_id`, `correction_set_id`, `effective_from/to`, `jurisdiction`.
- **Classification:** `regulatory_scope_status`, `identifier_type: UN|ID|other`, `identifier`, `entry_id`, `proper_shipping_name`, `hazards[]`, `packing_group_status/value`, `environmental_flags[]`.
- **Operational conditions:** `carriage_permission`, `conditions[]`, `operator_variations[]`; must not overwrite classification state.
- **Evidence:** `source_clause_refs[]`, `source_hash_or_revision`, `test_evidence_refs[]`, `missing_evidence[]`, `unresolved_interpretations[]`, `review_state`.
- **SDS output:** 14.1–14.7 per mode and user-facing explanation of any incomplete or irrelevant data.

**Required state distinctions (design proposal):**
1. `regulated` — affirmative mode determination;
2. `not_subject_established` — supported affirmative determination based on a specified mode-specific rule, including its conditions;
3. `insufficient_evidence` — cannot decide;
4. `rule_not_implemented` — source known but rule not encoded;
5. `out_of_scope` — mode/transport scenario not applicable, with justification;
6. `requires_authority_review` — reserved uncertain interpretation.

`carriage_prohibited` or `operator_not_accepted` is a **separate** condition that must never be converted to `not_subject_established`.

## 7. Mode-override gate and deterministic rule contract

An override may be introduced **only after** Lead Agent confirms the shared request/result schemas and canonical transport state semantics. Each override must then have:

- immutable `rule_id`, `mode`, edition, source clause(s), effective dates and amendment/correction chain;
- specific evidence inputs, applicability predicate and exact priority relative to shared base rule;
- explicit output state, exclusions and special-provision conditions;
- conflict resolution and no silent fallback across modes;
- golden cases, negative cases, boundary cases, edition transition tests, and second-person legal/regulatory sign-off.

**Fail-closed invariant:** if there is no authoritative complete source, a missing data row, ambiguous selection, missing test, unresolved conflict or unreviewed source revision, do not return “Not regulated for transport”. Return a specific unresolved state and the blocking evidence.

**Other invariants:** a road LQ/EQ exemption is not automatically portable to other modes; a prohibition on transport is not absence of hazard classification; a missing packing group is not proof that no PG applies; 14.7 is not synonymous with IMDG packaged carriage.

## 8. Proposed acceptance tests (NOT executed as regulatory tests)

| ID | Test input / fixture condition | Expected property |
|---|---|---|
| M-001 | ADR result known, IMDG source row absent | IMDG = `rule_not_implemented` or `insufficient_evidence`; **not** copied as a definitive ADR result |
| M-002 | IMDG marine-pollutant evidence unknown | Separate marine-pollutant status = unknown; no inferred negative |
| M-003 | ADN tank-vessel scenario absent/unknown | Do not present tank-vessel-only determination as a universal waterway result |
| M-004 | Air DGL source licence or edition unavailable | Air status blocked; no automatic “not regulated” |
| M-005 | ICAO carriage forbidden but hazard entry established | Classification remains represented; carriage permission separately “forbidden” |
| M-006 | 2026 shipment with IMDG 43-26 edition supplied | Flag edition not routinely applicable without early-use authority; keep 42-24 context |
| M-007 | 2027 shipment with overlapping IMDG transition edition alternatives | Evaluate selected edition, lawful transition and territory; do not silently merge amendments |
| M-008 | SDS 14.7 requested for packaged-only context | 14.7 = not applicable **with reason**, not a copied IMDG entry |
| M-009 | Exact same UN number but multiple named entries | Retain distinct entry identifiers, do not deduplicate by UN number |
| M-010 | Existing classification evidence below required quality | Output missing evidence + clause provenance, no definitive negative |
| M-011 | IATA operator variation conflicts with standard ICAO allowance | Preserve ICAO classification and show separately scoped operator acceptance result |
| M-012 | New corrigendum impacts any referenced clause | Mark affected rule pending re-review and prevent stale silent reuse |

No material-specific legal classifications were tested in this assessment; the table above is a **test specification**.

## 9. Dependencies and unresolved decisions

**Lead Agent:** authoritative shared schemas, status ontology, edition/effective-date model, rule-conflict priority, exception versus non-regulated distinction, Section 14 serializer.

**Agent 1:** complete and reviewed ADR baseline, particularly full Table A row data and special provisions. Existing index is preliminary only.

**Other specialists:** reviewed material composition/test evidence schema; environmental classification evidence; names/technical-name formatter; packaging/operational conditions separation; review sign-off process.

**Legal/procurement:** written permissions or defensible legal basis for bulk extraction, derived databases, commercial application, end-user display, digital storage and update notices for each publisher; no assumptions of free use.

**Open questions:**
1. Is the first release exclusively EU/UK SDS, or are US DOT 49 CFR and Canada TDG also required? Those are additional jurisdictions, not substitutes for ADR/RID/ADN.
2. Do we evaluate **SDS classification only**, or actual shipment acceptability (quantity, packaging, airline, route, tank/vessel)? Requirements differ sharply.
3. Will sea bulk cargo (14.7) be included in v1 or handled as a separately reviewed module?
4. Who obtains licensed IMO, ICAO and IATA texts/data rights, and who approves the licence register?
5. What is the project policy for applying corrigenda, retroactive corrections, country-specific derogations, multimodal movements and transition periods?

## 10. Handover

- **Deliverables created:** this research/requirements brief on an Agent 8 review branch; no code or executable classification rules.
- **Regulatory sources used:** EU Regulation 2020/878 Annex II §14; ADR 2025, ECE/TRANS/352; RID 2025/COTIF Appendix C; ADN 2025, ECE/TRANS/351; IMDG 42-24 and its December 2025 errata; ICAO Doc 9284 2025–2026; IATA DGR 67th (2026). Sources linked above. Uploaded UN Manual of Tests and Criteria Rev.8, ST/SG/AC.10/11/Rev.8, treated only as a supporting test reference. The IMDG 42-24 December 2025 corrigendum refers to Rev.8/**Amend.1** in one corrected definition; uploaded Rev.8 is not assumed to incorporate that amendment.
- **Rules and decisions made:** proposed mode independence, provenance/edition/licence gating, separate classification vs carriage status, and fail-closed semantics. **No legally operative rules decided.**
- **Assumptions requiring approval:** jurisdictional scope, inclusion of bulk sea, 14-only vs shipment checks, proposed field/state names and mode/source priority.
- **Outstanding questions and missing evidence:** full licensed source texts, rights agreements, complete DGL rows, formal mode-by-mode crosswalks, country/operator variations, ratified schemas.
- **Tests performed:** source metadata/page-title spot checks and repository inspection only; no material-classification, executable-rule or independent legal validation.
- **Dependencies / interfaces required:** Lead Agent shared schemas, Agent 1 baseline, evidence/test and publication licensing modules.
- **Recommended next tasks:** secure source licences; freeze shared schemas; compile clause-by-clause RID/ADN/IMDG/ICAO delta matrices; ingest under provenance; author and independently review golden cases; implement overrides only after all gates are met.

**Critical safety requirement: an incomplete or unsupported result must never be silently treated as “Not regulated for transport”.**
