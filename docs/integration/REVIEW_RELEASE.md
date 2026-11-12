# Integration plan, decision log and release review protocol
Status: draft; independent approval required.

## Orchestration sequence
1. Pin ADR 2025 English edition, corrected-source layers, MTC test-method version and source hashes.
2. Adapt PR #3 dotted-field input/provenance without turning missing into false.
3. Run Class1 and PR #2 hazard evaluators, then remaining relevant classes; collect scoped candidates only.
4. Resolve primary/subsidiary precedence, mixtures, PG/null, prohibitions, exceptions and authority decisions.
5. Call PR #1 UN selector with a reviewed complete candidate set, then exact PR #5 Table A row identifier (not UN number alone).
6. Resolve every column (6) special provision against 3.3.1 and correction text; SP unknown is blocked.
7. PR #4 deterministic engine applies only reviewed rule bundles; DECIDED is NOT SDS approval.
8. Release only after independent expert, source, security and schema sign-off.

## Lead architecture decisions
D-01: class decisions are scoped, never final SDS. D-02: unknown/CA/conflict/prohibited block. D-03: Class1 PG always null. D-04: preserve exact row_id and 4-digit UN. D-05: SPs are evaluated *after* row selection. D-06: authentic CA documents are trusted external inputs, never an output of software. D-07: fireworks analogy requires competent-authority agreement and applicable package conditions. D-08: Class1 exclusion does not mean global non-DG. D-09: source edition/corrigenda and MTC amendment are separately pinned. D-10: public bulk source reproduction requires rights clearance.

## Two-person review
Ownership check; JSON/schema test and no-negative-default proof; independent clause interpretation against rendered official PDF; independent legal predictions for positive/negative/missing/blocked cases; verify official source sha, Table A rows, all SP conditions, authority scope and source corrections; authenticated approval by reviewer different from author; versioned rule bundle signature and rollback. Any unresolved clause or evidential uncertainty blocks release.

## Release checklist (all initially unchecked)
- [ ] Official source hashes, 2025 dates, jurisdiction, Corr.1/Corr.2 and Rev.8/Amend.1 independently reconciled.
- [ ] Complete class screens, explosion-sensitive delegations, relevant tests and authority documents reviewed.
- [ ] Class1 divisions/groups covered, Group K/non-accepted path blocked, no PG.
- [ ] Row selection, multiple UN rows, technical name, SPs and exclusions independently reviewed.
- [ ] Expert-labelled golden cases, hostile/unknown cases, integration CI and legal validation pass.
- [ ] Cryptographic approval, audit, rollback, rights review and SDS 14.1–14.7 sign-off complete.

The 2,939 rows in PR #5 passed structural extraction only; source/reviewer approval and complete SP effects remain outstanding. MTC Amendment1 includes Part I Sections 11, 12 and 18 changes and cannot be silently ignored. The 2027 draft is out of scope.
