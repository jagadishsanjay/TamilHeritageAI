"""
தமிழ்ச்சுவடி AI – Test Suite for the 4 New NLP Features (test_4_new_nlp_features.py)
===================================================================================
Tests and verifies:
 1. Tamil Keyword Extraction        (extract_tamil_keywords)
 2. Tamil Text Summarisation        (summarize_tamil_text)
 3. Smart Tamil Text Search         (smart_tamil_search)
 4. Document Question Answering     (answer_document_question)
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass

import tamil_nlp

def run_tests():
    print("=" * 75)
    print("  தமிழ்ச்சுவடி AI – 4 New NLP Features Automated Test Suite")
    print("=" * 75)
    t_start = time.time()

    # Actual Tamil Heritage Sample OCR Text (combining Sangam, Historical Inscription, & Mixed English)
    sample_text = (
        "தொல்காப்பியம் தமிழ் மொழியின் மிகத் தொன்மையான இலக்கண நூலாகும். "
        "இந்நூல் எழுத்து, சொல், பொருள் ஆகிய மூன்று அதிகாரங்களைக் கொண்டுள்ளது. "
        "பண்டைய காலத்தில் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டினார். "
        "சோழர்களின் ஆட்சிக் காலத்தில் தமிழ் இலக்கியமும் கலைகளும் பெரும் வளர்ச்சி அடைந்தன. "
        "செகுவேரா Tamil Heritage Series Vol. 2 contains valuable ancient palm-leaf inscriptions. "
        "சுவடிகளில் எழுதப்பட்ட வரலாற்றுச் சான்றுகள் தமிழகத்தின் பழம்பெருமையை பறைசாற்றுகின்றன."
    )

    # -------------------------------------------------------------
    # FEATURE 1: Tamil Keyword Extraction
    # -------------------------------------------------------------
    print("\n--- [Feature 1] Tamil Keyword Extraction ---")
    kw_res = tamil_nlp.extract_tamil_keywords(sample_text, top_n=6, include_phrases=True)
    assert kw_res["success"] is True, "Feature 1 failed to execute"
    assert len(kw_res["keywords"]) > 0, "No keywords extracted"
    print(f"  Total tokens processed: {kw_res['total_tokens']}")
    print(f"  Language distribution: {kw_res['language_distribution']}")
    print("  Top extracted keywords & keyphrases:")
    for k in kw_res["keywords"][:5]:
        print(f"    • {k['term']} ({k['type']} | {k['language']} | Score: {k['score']})")
    assert any("தொல்காப்பியம்" in k["term"] for k in kw_res["keywords"]), "Expected 'தொல்காப்பியம்' keyword"
    print("  [PASS] Feature 1 verified successfully.")

    # -------------------------------------------------------------
    # FEATURE 2: Tamil Text Summarisation
    # -------------------------------------------------------------
    print("\n--- [Feature 2] Tamil Text Summarisation ---")
    sum_res = tamil_nlp.summarize_tamil_text(sample_text, max_sentences=2)
    assert sum_res["success"] is True, "Feature 2 failed to execute"
    assert sum_res["summary_sentence_count"] == 2, f"Expected 2 sentences, got {sum_res['summary_sentence_count']}"
    assert "வாக்கிய முக்கியத்துவப் பிரித்தெடுப்புச் சுருக்கம்" in sum_res["methodology"]
    print(f"  Methodology: {sum_res['methodology']}")
    print(f"  Original sentences: {sum_res['original_sentence_count']} -> Summary sentences: {sum_res['summary_sentence_count']}")
    print(f"  Compression: {sum_res['compression_percentage']}%")
    print(f"  Summary output:\n    \"{sum_res['summary']}\"")
    print("  [PASS] Feature 2 verified successfully.")

    # -------------------------------------------------------------
    # FEATURE 3: Smart Tamil Text Search
    # -------------------------------------------------------------
    print("\n--- [Feature 3] Smart Tamil Text Search ---")
    # Simulate multi-document corpora
    active_doc = {"name": "chola_inscription.txt", "text": sample_text}
    pdf_pages = [
        {"page_number": 1, "text": "முதலாம் இராஜராஜ சோழன் தஞ்சை பெரிய கோயிலைக் கட்டினார்."},
        {"page_number": 2, "text": "பாண்டிய மன்னர்கள் மதுரையில் தமிழ்ச் சங்கம் அமைத்து வளர்த்தனர்."},
    ]
    batch_results = [
        {"filename": "doc_manuscript_1.jpg", "text": "பழமையான ஓலைச்சுவடிகளில் மருத்துவக் குறிப்புகள் உள்ளன."},
    ]
    ocr_history = [
        {"id": 1, "filename": "sample_tamil.jpg", "text": "செகுவேரா", "timestamp": "2026-10-15 17:00:00"},
    ]

    # Search for "சோழன்"
    search_res = tamil_nlp.smart_tamil_search(
        query="சோழன்",
        active_doc=active_doc,
        pdf_pages=pdf_pages,
        batch_results=batch_results,
        ocr_history=ocr_history,
    )
    assert search_res["success"] is True, "Feature 3 search failed"
    assert search_res["total_matches"] >= 2, f"Expected at least 2 matches for 'சோழன்', got {search_res['total_matches']}"
    print(f"  Query: 'சோழன்' -> Found {search_res['total_matches']} matches across {search_res['total_documents_matched']} documents:")
    for match in search_res["results"][:3]:
        print(f"    • [{match['doc_source']}] {match['reference']}: {match['snippet']}")
    print("  [PASS] Feature 3 verified successfully.")

    # -------------------------------------------------------------
    # FEATURE 4: Document Question Answering
    # -------------------------------------------------------------
    print("\n--- [Feature 4] Document Question Answering ---")
    # Sub-test 4A: Question with answer present in text
    q1 = "தஞ்சைப் பெரிய கோயிலைக் கட்டியது யார்?"
    qa_res1 = tamil_nlp.answer_document_question(q1, context_text=sample_text, doc_name="தஞ்சைக் கல்வெட்டு")
    assert qa_res1["success"] is True, "QA 4A failed"
    assert qa_res1["found"] is True, "QA 4A answer should be found"
    assert "இராஜராஜ சோழன்" in qa_res1["answer"], f"Expected 'இராஜராஜ சோழன்' in answer, got: {qa_res1['answer']}"
    print(f"  Q1: '{q1}'")
    print(f"  A1: \"{qa_res1['answer']}\"")
    print(f"  Reference: {qa_res1['reference']} | Confidence: {qa_res1['confidence_percentage']}")

    # Sub-test 4B: Question with answer NOT present in text
    q2 = "அசோகர் எப்போது கலிங்கப் போரை நடத்தினார்?"
    qa_res2 = tamil_nlp.answer_document_question(q2, context_text=sample_text, doc_name="தஞ்சைக் கல்வெட்டு")
    assert qa_res2["success"] is True, "QA 4B failed"
    assert qa_res2["found"] is False, "QA 4B answer should NOT be found"
    assert "காணப்படவில்லை" in qa_res2["answer"], f"Expected 'காணப்படவில்லை', got: {qa_res2['answer']}"
    print(f"  Q2 (Unanswerable): '{q2}'")
    print(f"  A2: \"{qa_res2['answer']}\"")
    print("  [PASS] Feature 4 verified successfully.")

    t_elapsed = time.time() - t_start
    print("\n" + "=" * 75)
    print(f"  ALL 4 NEW NLP FEATURES PASSED VERIFICATION IN {t_elapsed:.2f}s (100% SUCCESS)!")
    print("=" * 75)
    return True

if __name__ == "__main__":
    run_tests()
