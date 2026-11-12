"""Agent 3 temporary deterministic interface; awaiting Lead Agent's shared schema."""
from math import isfinite

EDITION = 'ADR 2025'
SOURCE_ID = 'ECE/TRANS/352 (Vol.I)'
SOURCE_URL = 'https://unece.org/sites/default/files/2025-01/2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf'


def numeric(value, *, allow_zero=False):
    """Accept only finite real measurements, rejecting booleans, strings and nulls."""
    if type(value) not in (int, float) or not isfinite(value):
        return False
    return value >= 0 if allow_zero else value > 0


def decide(cls, status, rule_id, clauses, *, pg=None, missing=(), notes=(), data=None):
    """Never emits a global transport exemption or an SDS Section 14 final classification."""
    assert status in ('criteria_met', 'criteria_not_met', 'indeterminate')
    assert pg in (None, 'I', 'II', 'III')
    return {
        'hazard_class': str(cls), 'status': status, 'candidate_packing_group': pg,
        'rule_id': rule_id, 'source': {'edition': EDITION, 'document': SOURCE_ID,
                                      'url': SOURCE_URL, 'clauses': list(clauses)},
        'missing_evidence': sorted(set(missing)), 'limitations': list(notes),
        'candidate_data': data or {}, 'requires_independent_review': True,
        'is_final_section_14_classification': False,
    }


def blocked(cls, rule, clauses, *missing, notes=(), pg=None, data=None):
    return decide(cls, 'indeterminate', rule, clauses, missing=missing, notes=notes, pg=pg, data=data)