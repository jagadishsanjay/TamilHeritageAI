# -*- coding: utf-8 -*-
"""Test Suite for Phase 3: Research-Level AI Upgrades (Features 7, 8, 9, 10)."""

import sys
if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass

import ai_evaluation
import ocr_review_workflow
import source_trust_layer
import manuscript_assistant

def run_phase3_tests():
    print("=" * 75)
    print("  Testing Phase 3 Research Features (7: Eval, 8: Review, 9: Trust, 10: Tracking)")
    print("=" * 75)

    # -------------------------------------------------------------
    # 1. Feature 7 & 10: Evaluation & Experiment Tracking
    # -------------------------------------------------------------
    print("\n[TEST 7 & 10] AI Evaluation Metrics & Experiment Tracking...")
    # Test CER & WER computation
    ref_txt = "ஸ்வஸ்திஸ்ரீ முதலாம் இராஜராஜ சோழன்"
    hyp_txt = "ஸ்வஸ்திஸ்ரீ முதலாம் இராஜராஜ சோழன்"
    cer_res = ai_evaluation.compute_character_error_rate(ref_txt, hyp_txt)
    wer_res = ai_evaluation.compute_word_error_rate(ref_txt, hyp_txt)

    assert cer_res["cer"] >= 0.0 and cer_res["cer"] <= 1.0
    assert wer_res["wer"] >= 0.0 and wer_res["wer"] <= 1.0
    print(f"  CER: {cer_res['cer_percentage']} | Character Accuracy: {cer_res['character_accuracy']}%")
    print(f"  WER: {wer_res['wer_percentage']} | Word Accuracy: {wer_res['word_accuracy']}%")

    # Run full benchmark evaluation suite
    full_eval = ai_evaluation.run_full_evaluation_suite(experiment_name="Unit Test Experiment Run")
    assert full_eval["success"] is True
    assert full_eval["retrieval_evaluation"]["precision_at_1"] >= 0.5
    assert full_eval["qa_evaluation"]["anti_hallucination_refusal_rate"] == "100%"
    print(f"  Retrieval P@1: {full_eval['retrieval_evaluation']['precision_at_1_pct']}")
    print(f"  QA Refusal Rate (Zero Hallucination): {full_eval['qa_evaluation']['anti_hallucination_refusal_rate']}")
    print(f"  Logged Experiment ID: {full_eval['experiment_record']['experiment_id']}")
    print("  [PASS] Features 7 & 10 verified.")

    # -------------------------------------------------------------
    # 2. Feature 8: OCR Correction Review Workflow
    # -------------------------------------------------------------
    print("\n[TEST 8] OCR Correction Review Workflow...")
    sample_ocr = "தொல்காப்பியம் சோழன் காலத்தில் ஞாலம் காக்க எழுதப்பட்டது."
    anomalies = ocr_review_workflow.detect_ocr_anomalies(sample_ocr)
    assert len(anomalies) >= 2, f"Expected at least 2 detected items, found {len(anomalies)}"

    # Check classical protection on 'ஞாலம்'
    protected_items = [a for a in anomalies if a.get("is_protected")]
    print("  Protected items found:", [p["original_word"] for p in protected_items])
    assert len(protected_items) >= 1, "Classical word should be protected"
    assert any("ஞாலம்" in p["original_word"] for p in protected_items)
    print(f"  Protected Classical Vocabulary: {protected_items[0]['original_word']} - {protected_items[0]['explanation']}")

    # Apply accepted corrections
    accepted = [{"original_word": "தொல்காப்பியம்", "suggested_word": "தொல்காப்பியம்"}]
    revised = ocr_review_workflow.apply_accepted_corrections(sample_ocr, accepted)
    assert "தொல்காப்பியம்" in revised and "தொல்காப்பியம்" not in revised
    # Original text must remain unchanged
    assert "தொல்காப்பியம்" in sample_ocr
    print("  Correction applied to revised text while preserving original transcription.")
    print("  [PASS] Feature 8 verified.")

    # -------------------------------------------------------------
    # 3. Feature 9: Source Traceability and Trust Layer
    # -------------------------------------------------------------
    print("\n[TEST 9] Source Traceability and Trust Layer...")
    thanjavur_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
    
    # 3a. Direct Verbatim Quote (Level 1)
    quote_claim = "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டி முடித்தார்."
    t1 = source_trust_layer.audit_claim_traceability(quote_claim, thanjavur_text, "thanjavur_inscription", "தஞ்சைக் கல்வெட்டு")
    assert t1["trust_level"] == "DIRECT_QUOTE"
    assert t1["sentence_number"] == 1
    print(f"  Claim 1 Audit: Trust Level = {t1['trust_level']} (Sentence #{t1['sentence_number']})")

    # 3b. Source-Derived Fact (Level 2)
    fact_claim = "முதலாம் இராஜராஜ சோழன் தஞ்சைப் பெரிய கோயிலைக் கட்டினார்"
    t2 = source_trust_layer.audit_claim_traceability(fact_claim, thanjavur_text, "thanjavur_inscription", "தஞ்சைக் கல்வெட்டு")
    assert t2["trust_level"] in ("DIRECT_QUOTE", "SOURCE_DERIVED")
    print(f"  Claim 2 Audit: Trust Level = {t2['trust_level']} (Confidence: {int(t2['confidence_score']*100)}%)")

    # 3c. Insufficient Evidence (Level 0)
    unsupported_claim = "அசோகர் மௌரியப் பேரரசை ஆண்டார்"
    t0 = source_trust_layer.audit_claim_traceability(unsupported_claim, thanjavur_text, "thanjavur_inscription", "தஞ்சைக் கல்வெட்டு")
    assert t0["trust_level"] == "INSUFFICIENT_EVIDENCE"
    print(f"  Claim 3 Audit (Unsupported): Trust Level = {t0['trust_level']} (Correctly Flagged)")
    print("  [PASS] Feature 9 verified.")

    print("\n" + "=" * 75)
    print("  ALL PHASE 3 RESEARCH FEATURES (7, 8, 9, 10) PASSED TESTS (100%)!")
    print("=" * 75)

if __name__ == "__main__":
    run_phase3_tests()
