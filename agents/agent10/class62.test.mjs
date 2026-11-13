import test from 'node:test';
import assert from 'node:assert/strict';
import { classifyClass62 } from './class62.mjs';
// ADR 2025 clause-linked positive, negative, edge and missing-evidence checks.
const fixtures = [
  [
    "Category A human",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Category A animals only",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": false,
      "evidence_refs": [
        "clinical report"
      ],
      "affects_animals": true
    },
    "class62_candidate",
    [
      "2900"
    ]
  ],
  [
    "Category A both",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "affects_animals": true
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Category B patient",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "pathogen_state": "known",
      "category_a_assessment": "not_met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "class62_candidate",
    [
      "3373"
    ]
  ],
  [
    "Category B culture",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "not_met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "class62_candidate",
    [
      "3373"
    ]
  ],
  [
    "Unknown pathogen",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "unknown",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "insufficient_evidence",
    []
  ],
  [
    "No source evidence",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": []
    },
    "insufficient_evidence",
    []
  ],
  [
    "Unknown category A risk",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "unknown",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "requires_expert_review",
    []
  ],
  [
    "Category A doubt without expert",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "doubt",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "requires_expert_review",
    []
  ],
  [
    "Category A doubt documented",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "doubt",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      }
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Unknown effects",
    {
      "mode": "ADR_ROAD",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": null,
      "evidence_refs": [
        "clinical report"
      ],
      "affects_animals": null
    },
    "requires_expert_review",
    []
  ],
  [
    "Confirmed no infectious",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "no_infectious_substances",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "No infectious without evidence",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "no_infectious_substances",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": []
    },
    "insufficient_evidence",
    []
  ],
  [
    "Nonpathogenic",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "nonpathogenic_microorganisms",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Inactivated",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "inactivation_verified": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Inactivated no evidence",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [],
      "inactivation_verified": true
    },
    "insufficient_evidence",
    []
  ],
  [
    "Dried blood spot",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "evidence_refs": [
        "sample records"
      ],
      "specimen_exclusion": "dried_blood_spot",
      "blood_drop_on_absorbent": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Dried blood spot no absorbent",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "evidence_refs": [
        "sample records"
      ],
      "specimen_exclusion": "dried_blood_spot",
      "blood_drop_on_absorbent": false
    },
    "insufficient_evidence",
    []
  ],
  [
    "FOB screen",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "evidence_refs": [
        "sample records"
      ],
      "specimen_exclusion": "faecal_occult_blood",
      "blood_drop_on_absorbent": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Transfusion purpose",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "evidence_refs": [
        "sample records"
      ],
      "specimen_exclusion": "transfusion_or_transplant",
      "blood_drop_on_absorbent": true,
      "specimen_purpose": "transfusion",
      "specimen_purpose_verified": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Transplant related sample",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "evidence_refs": [
        "sample records"
      ],
      "specimen_exclusion": "transfusion_or_transplant",
      "blood_drop_on_absorbent": true,
      "specimen_purpose": "related_sample",
      "specimen_purpose_verified": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Unverified blood purpose",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "evidence_refs": [
        "sample records"
      ],
      "specimen_exclusion": "transfusion_or_transplant",
      "blood_drop_on_absorbent": true,
      "specimen_purpose": "transfusion",
      "specimen_purpose_verified": false
    },
    "insufficient_evidence",
    []
  ],
  [
    "Exempt specimen valid",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Specimen no judgement",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": null,
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "requires_expert_review",
    []
  ],
  [
    "Specimen exact outer 100 mm",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Specimen 99 mm width",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 99,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "insufficient_evidence",
    []
  ],
  [
    "Specimen 99 mm height",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 99,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "insufficient_evidence",
    []
  ],
  [
    "Specimen insufficient absorbent",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": false,
        "fragile_separated": true
      }
    },
    "insufficient_evidence",
    []
  ],
  [
    "Specimen fragile contact",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": false
      }
    },
    "insufficient_evidence",
    []
  ],
  [
    "Specimen absent mark",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "insufficient_evidence",
    []
  ],
  [
    "Animal specimen mark",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "animal",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt animal specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      }
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Alternative specimen pack",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "alternative_no_leakage",
        "mark": "Exempt human specimen",
        "no_leakage_demonstrated": true
      }
    },
    "requires_expert_review",
    []
  ],
  [
    "Medical waste A disposal solid",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal"
    },
    "class62_candidate",
    [
      "2814",
      "3549"
    ]
  ],
  [
    "Medical waste A liquid",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "liquid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal"
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Medical waste A bio research",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "bio_research",
      "waste_carriage_purpose": "disposal"
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Medical waste A not disposal",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "storage"
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Medical waste A animal",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": false,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "animal_veterinary_treatment",
      "waste_carriage_purpose": "disposal",
      "affects_animals": true
    },
    "class62_candidate",
    [
      "2900",
      "3549"
    ]
  ],
  [
    "Medical waste B",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "not_met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal"
    },
    "class62_candidate",
    [
      "3291"
    ]
  ],
  [
    "Medical waste low probability",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "unknown",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_low_probability": true
    },
    "class62_candidate",
    [
      "3291"
    ]
  ],
  [
    "Medical waste unknown",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "unknown",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_low_probability": false
    },
    "insufficient_evidence",
    []
  ],
  [
    "Waste high-risk code no diagnosis",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_catalogue_code": "18 01 03",
      "diagnosis_recorded": false
    },
    "requires_expert_review",
    []
  ],
  [
    "Waste low-risk code verified",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_catalogue_code": "18 01 04",
      "waste_catalogue_verified": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Waste low-risk code not verified",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_catalogue_code": "18 01 04",
      "waste_catalogue_verified": false
    },
    "class62_candidate",
    [
      "2814",
      "3549"
    ]
  ],
  [
    "Decontaminated medical waste",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_decontaminated": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Biological product national group A",
    {
      "mode": "ADR_ROAD",
      "kind": "biological_product",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "national_authority_manufacture_packaging_verified": true,
      "healthcare_personal_use": true,
      "biological_carriage_purpose": "distribution"
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Biological product experimental Category A",
    {
      "mode": "ADR_ROAD",
      "kind": "biological_product",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "national_authority_manufacture_packaging_verified": false,
      "healthcare_personal_use": false,
      "biological_carriage_purpose": "research"
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Biological product experimental B",
    {
      "mode": "ADR_ROAD",
      "kind": "biological_product",
      "pathogen_state": "known",
      "category_a_assessment": "not_met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "biological_carriage_purpose": "research"
    },
    "class62_candidate",
    [
      "3373"
    ]
  ],
  [
    "Medical device repair exception",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": false,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      }
    },
    "limited_provisions_exemption",
    []
  ],
  [
    "Medical device missing drop test",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": false,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": false,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      }
    },
    "insufficient_evidence",
    []
  ],
  [
    "Medical device Category A",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": true,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      }
    },
    "named_entry_review_required",
    []
  ],
  [
    "Medical device class 8",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": false,
      "device_other_class_dangerous": true,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      }
    },
    "referred_to_other_class",
    []
  ],
  [
    "Medical device origin unknown",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": null,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      }
    },
    "requires_expert_review",
    []
  ],
  [
    "Drained device",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": false,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      },
      "drained_of_free_liquid": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Natural concentration",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "natural_pathogen_level": true,
      "no_significant_infection_risk": true
    },
    "conditional_adr_non_subject",
    []
  ],
  [
    "Natural concentration still risk",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "natural_pathogen_level": true,
      "no_significant_infection_risk": false
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "Toxin noninfectious",
    {
      "mode": "ADR_ROAD",
      "kind": "toxin",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "toxin_without_infectious_agent": true
    },
    "referred_to_other_class",
    []
  ],
  [
    "Toxin with infectious",
    {
      "mode": "ADR_ROAD",
      "kind": "toxin",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "toxin_without_infectious_agent": false
    },
    "class62_candidate",
    [
      "2814"
    ]
  ],
  [
    "GMO non-infectious",
    {
      "mode": "ADR_ROAD",
      "kind": "gmo",
      "pathogen_state": "no_infectious_substances",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "referred_to_other_class",
    []
  ],
  [
    "Intentionally infected animal no approval",
    {
      "mode": "ADR_ROAD",
      "kind": "live_animal",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "infection_origin": "intentional",
      "competent_authority_approval": false
    },
    "requires_competent_authority_approval",
    []
  ],
  [
    "Intentionally infected animal approved",
    {
      "mode": "ADR_ROAD",
      "kind": "live_animal",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "infection_origin": "intentional",
      "competent_authority_approval": true
    },
    "requires_competent_authority_review",
    []
  ],
  [
    "Naturally infected animal",
    {
      "mode": "ADR_ROAD",
      "kind": "live_animal",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ],
      "infection_origin": "natural_or_unintentional"
    },
    "national_animal_rules_review",
    []
  ],
  [
    "Mode AIR",
    {
      "mode": "AIR",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "mode_not_supported",
    []
  ],
  [
    "Mode MARITIME",
    {
      "mode": "SEA",
      "kind": "culture",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "mode_not_supported",
    []
  ],
  [
    "Missing kind",
    {
      "mode": "ADR_ROAD",
      "kind": "unrecognized",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "clinical report"
      ]
    },
    "insufficient_evidence",
    []
  ],
  [
    "CLP only",
    {
      "mode": "ADR_ROAD",
      "kind": "substance",
      "clp_classification": "Acute Tox. 2"
    },
    "insufficient_evidence",
    []
  ],
  [
    "Medical waste contradictory low probability and Category A",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_low_probability": true
    },
    "requires_expert_review",
    []
  ],
  [
    "Medical waste contradictory exemption code and Category A",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_waste",
      "pathogen_state": "known",
      "category_a_assessment": "met",
      "affects_humans": true,
      "evidence_refs": [
        "medical diagnosis"
      ],
      "waste_state": "solid",
      "waste_origin": "human_medical_treatment",
      "waste_carriage_purpose": "disposal",
      "waste_catalogue_code": "18 01 04",
      "waste_catalogue_verified": true
    },
    "requires_expert_review",
    []
  ],
  [
    "Patient specimen contradictory Category A and minimal likelihood",
    {
      "mode": "ADR_ROAD",
      "kind": "patient_specimen",
      "minimal_pathogen_likelihood": true,
      "professional_judgement": {
        "record_ref": "clinical-pro-123",
        "basis": "known medical history, symptoms, circumstances and endemic conditions"
      },
      "specimen_species": "human",
      "specimen_is_liquid": true,
      "multiple_fragile_primaries": true,
      "evidence_refs": [
        "patient evaluation"
      ],
      "specimen_packaging": {
        "method": "tripack",
        "primary_leakproof": true,
        "secondary_leakproof": true,
        "outer_adequate": true,
        "packaging_verified": true,
        "outer_width_mm": 100,
        "outer_height_mm": 100,
        "mark": "Exempt human specimen",
        "absorbent_all_contents": true,
        "fragile_separated": true
      },
      "pathogen_state": "known",
      "category_a_assessment": "met"
    },
    "requires_expert_review",
    []
  ],
  [
    "Device drop boundary at 1.20m",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": false,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.2
      }
    },
    "limited_provisions_exemption",
    []
  ],
  [
    "Device drop boundary below 1.20m",
    {
      "mode": "ADR_ROAD",
      "kind": "medical_device",
      "device_category_a": false,
      "device_other_class_dangerous": false,
      "device_carriage_purpose": "repair",
      "evidence_refs": [
        "equipment log"
      ],
      "device_packaging": {
        "protects_against_breakage_puncture_leak": true,
        "construction_6_1_4_or_6_6_4": true,
        "general_4_1_1_1_and_4_1_1_2": true,
        "retains_on_1_2m_drop": true,
        "mark": "USED MEDICAL EQUIPMENT",
        "drop_height_m": 1.19
      }
    },
    "insufficient_evidence",
    []
  ]
];
for (const [name, input, decision, unEntries] of fixtures) {
  test(name, () => {
    const actual = classifyClass62(input);
    assert.equal(actual.decision, decision);
    assert.deepEqual(actual.un_entry_candidates, unEntries);
    assert.equal(actual.packing_group, null);
    assert.equal(actual.final_sds_section14_assignment_permitted, false);
    assert.equal(actual.regulatory_source, 'ADR 2025 ECE/TRANS/352 (Vol.I)');
    if (unEntries.length) {
      assert.equal(actual.table_a_lookup_required, true);
      assert.equal(actual.class_candidate, '6.2');
      assert.ok(actual.decision_trace.length);
    }
  });
}
