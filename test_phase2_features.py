# -*- coding: utf-8 -*-
"""Test Suite for Phase 2: Features 4, 5, and 6."""

import sys
if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass

import semantic_search
import manuscript_variant_ai
import timeline_explorer
import manuscript_assistant
import tamil_nlp

def run_phase2_tests():
    print("=" * 75)
    print("  Testing Phase 2 Features (Semantic Search, Variant AI, Timeline)")
    print("=" * 75)

    # -------------------------------------------------------------
    # Test Feature 4: Semantic Search
    # -------------------------------------------------------------
    print("\n[TEST 4] Semantic Search Across Tamil Manuscripts...")
    # Meaning query 'கோயில்' -> should match Brihadisvara Temple inscription
    res_sem1 = semantic_search.semantic_search_manuscripts("கோயில் கட்டடக் கலை")
    assert res_sem1["success"] is True and res_sem1["total_matches"] >= 1
    top_hit = res_sem1["results"][0]
    print(f"  Top hit: {top_hit['doc_title']} - Score: {top_hit['score']}")
    print(f"  Exact matches: {top_hit['exact_matches']} | Semantic matches: {top_hit['semantic_matches']}")
    print(f"  Passage snippet: {top_hit['passage'][:80]}")
    assert top_hit["doc_id"] == "thanjavur_inscription"
    assert "Brihadisvara" in top_hit["doc_title"] or "தஞ்சை" in top_hit["doc_title"]

    # Bilingual query 'king ruler chola'
    res_sem2 = semantic_search.semantic_search_manuscripts("king chola empire")
    assert res_sem2["success"] is True and res_sem2["total_matches"] >= 1
    print(f"  Bilingual Query: 'king chola empire' -> Matched {res_sem2['total_matches']} passages.")
    print("  [PASS] Feature 4 verified.")

    # -------------------------------------------------------------
    # Test Feature 5: Manuscript Variant Comparison AI
    # -------------------------------------------------------------
    print("\n[TEST 5] Manuscript Variant Comparison AI...")
    text_a = (
        "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டினார். "
        "இக்கோயிலின் மூலவர் பெருவுடையார் என்றும் விமானம் தட்சிண மேரு என்றும் குறிப்பிடப்பட்டுள்ளது. "
        "கோயிலுக்கு அளித்த கொடைகள் அனைத்தும் கல்வெட்டில் பொறிக்கப்பட்டுள்ளன."
    )
    # Text B has: 1 orthographic sandhi variation, 1 substantial word change, 1 added sentence
    text_b = (
        "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டி முடித்தார். "
        "இக்கோயிலின் மூலவர் பெருவுடையார் என்றும் விமானம் தட்சிண மேரு என்றும் கல்வெட்டுகளில் குறிப்பிடப்பட்டுள்ளது. "
        "சோழர்களின் ஆட்சிக் காலத்தில் தமிழகத்தில் கலை பெரும் வளர்ச்சி அடைந்தது."
    )
    var_res = manuscript_variant_ai.compare_manuscript_variants(text_a, text_b, label_a="கல்வெட்டுப் பிரதி A", label_b="ஓலைச்சுவடிப் பிரதி B")
    assert var_res["success"] is True
    assert var_res["total_aligned_rows"] >= 3
    print(f"  Compared: {var_res['total_lines_a']} lines A vs {var_res['total_lines_b']} lines B.")
    print(f"  Alignment Breakdown: {var_res['identical_count']} Identical, {var_res['orthographic_count']} Orthographic, {var_res['substantial_count']} Substantial.")
    print("  [PASS] Feature 5 verified.")

    # -------------------------------------------------------------
    # Test Feature 6: Historical Context & Timeline Explorer
    # -------------------------------------------------------------
    print("\n[TEST 6] Historical Context & Timeline Explorer...")
    thanjavur_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
    tl_events = timeline_explorer.extract_timeline_events(thanjavur_text, "தஞ்சைக் கல்வெட்டு")
    assert len(tl_events) >= 1
    top_ev = tl_events[0]
    assert top_ev["is_source_stated"] is True
    assert top_ev["year_numeric"] == 1010
    print(f"  Extracted {len(tl_events)} timeline anchors:")
    for ev in tl_events:
        print(f"    • {ev['era_display']}: {ev['title']} ({ev['dating_badge']})")
    tl_html = timeline_explorer.generate_timeline_html(tl_events)
    assert "<div" in tl_html
    print("  [PASS] Feature 6 verified.")

    print("\n" + "=" * 75)
    print("  ALL PHASE 2 FEATURES (4, 5, 6) PASSED TESTS SUCCESSFULLY (100%)!")
    print("=" * 75)

if __name__ == "__main__":
    run_phase2_tests()
