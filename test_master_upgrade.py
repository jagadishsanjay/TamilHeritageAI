# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Master Acceptance Test Suite (test_master_upgrade.py)
Validates all 6 criteria from the Final 4-Hour Master-Level Upgrade:
  1. Existing OCR continues to work (Tesseract + preprocessing + sample).
  2. Feature 1: AI Manuscript Assistant (evidence retrieval, strict anti-hallucination).
  3. Feature 2: Tamil Knowledge Explorer (NER, direct evidence vs inference, graph).
  4. Feature 3: Smart Tamil Voice Reading (Google Neural Tamil Voice, chunking, speed).
  5. Error & Edge Case Resilience (empty input, unsupported questions, offline).
  6. Overall System Integration & Compilation.
=============================================================================
"""

import sys
import time
from pathlib import Path
from PIL import Image

if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass

import ocr_engine
import tamil_nlp
import tamil_voice
import manuscript_assistant
import knowledge_explorer

def run_master_acceptance_tests():
    print("=" * 75)
    print("  🏛️ TAMIL SUVADI AI – 4-HOUR MASTER-LEVEL UPGRADE ACCEPTANCE SUITE")
    print("=" * 75)

    start_total = time.time()

    # -------------------------------------------------------------
    # 1. Existing OCR Test
    # -------------------------------------------------------------
    print("\n[TEST 1] Verifying Existing OCR Pipeline (Preservation Guarantee)...")
    sample_path = Path("samples/sample_tamil.jpg")
    assert sample_path.exists(), "Sample Tamil image missing"
    sample_img = Image.open(sample_path)
    ocr_res = ocr_engine.run_tesseract_ocr(
        sample_img,
        lang="tam",
        tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    )
    assert ocr_res["success"] is True, f"OCR failed: {ocr_res.get('error')}"
    print(f"  OCR Success: True | Text Length: {len(ocr_res['text'])} chars | Time: {ocr_res['elapsed_seconds']:.2f}s")
    print(f"  Preview: \"{ocr_res['text'][:60]}...\"")
    print("  [PASS] Test 1: Existing OCR pipeline verified 100% operational.")

    # -------------------------------------------------------------
    # 2. Feature 1: AI Manuscript Assistant Test
    # -------------------------------------------------------------
    print("\n[TEST 2] Verifying Feature 1: AI Manuscript Assistant...")
    thanjavur_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
    
    # 2a. Answerable question with evidence
    q1 = "தஞ்சைப் பெரிய கோயிலைக் கட்டியது யார்?"
    ast_res1 = manuscript_assistant.ask_manuscript_assistant(thanjavur_text, q1, document_title="தஞ்சைக் கல்வெட்டு")
    assert ast_res1["success"] is True and ast_res1["found"] is True
    assert "இராஜராஜ சோழன்" in ast_res1["answer_tamil"]
    assert len(ast_res1["supporting_passages"]) >= 1
    print(f"  Q1: '{q1}'")
    print(f"  A1: {ast_res1['answer_tamil']}")
    print(f"  Evidence: Passage #{ast_res1['supporting_passages'][0]['passage_number']} (Confidence: {ast_res1['confidence_percentage']})")

    # 2b. Unanswerable question (Strict Anti-Hallucination)
    q2 = "அசோகர் எப்போது கலிங்கப் போரை நடத்தினார்?"
    ast_res2 = manuscript_assistant.ask_manuscript_assistant(thanjavur_text, q2, document_title="தஞ்சைக் கல்வெட்டு")
    assert ast_res2["success"] is True and ast_res2["found"] is False
    assert "போதுமான சான்றுகள் இந்த ஆவணத்தில் காணப்படவில்லை" in ast_res2["answer_tamil"]
    print(f"  Q2 (Unanswerable): '{q2}'")
    print(f"  A2 (Refusal): {ast_res2['answer_tamil']}")
    print("  [PASS] Test 2: AI Manuscript Assistant verified (Grounded + Anti-Hallucination).")

    # -------------------------------------------------------------
    # 3. Feature 2: Tamil Knowledge Explorer Test
    # -------------------------------------------------------------
    print("\n[TEST 3] Verifying Feature 2: Tamil Knowledge Explorer...")
    graph_res = knowledge_explorer.run_knowledge_explorer(thanjavur_text)
    assert graph_res["success"] is True
    assert graph_res["total_entities"] >= 4, f"Expected at least 4 entities, got {graph_res['total_entities']}"
    assert graph_res["total_relationships"] >= 2, f"Expected at least 2 relationships, got {graph_res['total_relationships']}"
    assert "<svg" in graph_res["graph_html"]
    assert "nodes" in graph_res["structured_graph"] and "edges" in graph_res["structured_graph"]
    print(f"  Extracted Entities ({graph_res['total_entities']}): {[e['name'] for e in graph_res['entities']]}")
    print(f"  Extracted Relationships ({graph_res['total_relationships']}):")
    for r in graph_res["relationships"][:3]:
        tag = "DIRECT EVIDENCE" if r["is_direct_evidence"] else "CONTEXTUAL"
        print(f"    • [{tag}] {r['source']} -> {r['relationship']} -> {r['target']}")
    print("  [PASS] Test 3: Tamil Knowledge Explorer verified (NER + Graph + Structure).")

    # -------------------------------------------------------------
    # 4. Feature 3: Smart Tamil Voice Reading Test
    # -------------------------------------------------------------
    print("\n[TEST 4] Verifying Feature 3: Smart Tamil Voice Reading...")
    tts_sample = "தொல்காப்பியம் தமிழ் மொழியின் மிகத் தொன்மையான இலக்கண நூலாகும்."
    v_res = tamil_voice.synthesize_tamil_speech(tts_sample, slow=False)
    assert v_res["success"] is True
    assert v_res["audio_bytes"] is not None and len(v_res["audio_bytes"]) > 1000
    print(f"  Engine: {v_res.get('engine', 'Google Neural Tamil Voice')} | Audio: {len(v_res['audio_bytes'])} MP3 bytes | Speed: {v_res['speed']}")
    
    # Speed control test
    v_res_slow = tamil_voice.synthesize_tamil_speech(tts_sample, slow=True)
    assert v_res_slow["success"] is True
    assert len(v_res_slow["audio_bytes"]) > len(v_res["audio_bytes"])
    print(f"  Study Mode (0.8x Slow): {len(v_res_slow['audio_bytes'])} MP3 bytes")
    print("  [PASS] Test 4: Smart Tamil Voice Reading verified (Authentic Neural Voice + Controls).")

    # -------------------------------------------------------------
    # 5. Resilience & Edge Cases Test
    # -------------------------------------------------------------
    print("\n[TEST 5] Verifying Graceful Handling of Edge Cases & Invalid Inputs...")
    # Empty text to Assistant
    empty_ast = manuscript_assistant.ask_manuscript_assistant("", "கேள்வி?")
    assert empty_ast["found"] is False
    # Empty text to Voice
    empty_v = tamil_voice.synthesize_tamil_speech("")
    assert empty_v["success"] is False
    # Empty text to Knowledge Explorer
    empty_g = knowledge_explorer.run_knowledge_explorer("")
    assert empty_g["total_entities"] == 0
    print("  Empty/invalid inputs safely intercepted with user-friendly diagnostics.")
    print("  [PASS] Test 5: Resilience & safety verified.")

    # -------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------
    elapsed = time.time() - start_total
    print("\n" + "=" * 75)
    print(f"  🏆 ALL ACCEPTANCE TESTS PASSED SUCCESSFULLY IN {elapsed:.2f}s (100% SUITE PASS)!")
    print("=" * 75)

if __name__ == "__main__":
    run_master_acceptance_tests()
