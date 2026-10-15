# -*- coding: utf-8 -*-
"""Test Suite for Feature 1: AI Manuscript Assistant."""

import sys
if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass

import manuscript_assistant

def test_manuscript_assistant():
    print("=" * 70)
    print("  Testing Feature 1: AI Manuscript Assistant")
    print("=" * 70)

    # Test 1: Digital Library Available
    lib = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS
    assert len(lib) >= 4, "Digital library should contain at least 4 manuscripts"
    print(f"[PASS] Digital Library loaded with {len(lib)} manuscripts.")

    # Test 2: Inscription Question (Positive case)
    thanjavur_text = lib["thanjavur_inscription"]["text"]
    res1 = manuscript_assistant.ask_manuscript_assistant(
        thanjavur_text,
        "தஞ்சைப் பெரிய கோயிலைக் கட்டியவர் யார்?",
        document_title="தஞ்சைப் பெரிய கோயில் கல்வெட்டு"
    )
    assert res1["success"] is True and res1["found"] is True
    assert "இராஜராஜ சோழன்" in res1["answer_tamil"]
    assert len(res1["supporting_passages"]) >= 1
    print(f"[PASS] Question 1 answered with evidence: Passage #{res1['supporting_passages'][0]['passage_number']}")
    print(f"       Tamil Answer: {res1['answer_tamil']}")
    print(f"       Confidence: {res1['confidence_percentage']}")

    # Test 3: Tolkappiyam Question (Count intent)
    tolk_text = lib["tolkappiyam"]["text"]
    res2 = manuscript_assistant.ask_manuscript_assistant(
        tolk_text,
        "தொல்காப்பியத்தில் எத்தனை அதிகாரங்கள் உள்ளன?",
        document_title="தொல்காப்பியம்"
    )
    assert res2["success"] is True and res2["found"] is True
    assert "மூன்று பெரும் அதிகாரங்களை" in res2["answer_tamil"]
    print(f"[PASS] Question 2 answered: {res2['answer_tamil']}")

    # Test 4: Unanswerable Question (Strict Anti-Hallucination)
    res3 = manuscript_assistant.ask_manuscript_assistant(
        thanjavur_text,
        "அலெக்சாண்டர் எப்போது இந்தியா மீது படையெடுத்தார்?",
        document_title="தஞ்சைப் பெரிய கோயில் கல்வெட்டு"
    )
    assert res3["success"] is True and res3["found"] is False
    assert "போதுமான சான்றுகள் இந்த ஆவணத்தில் காணப்படவில்லை" in res3["answer_tamil"]
    print(f"[PASS] Question 3 correctly refused due to lack of evidence (Anti-Hallucination verified).")

    print("=" * 70)
    print("  FEATURE 1: ALL TESTS PASSED SUCCESSFULLY (100%)!")
    print("=" * 70)

if __name__ == "__main__":
    test_manuscript_assistant()
