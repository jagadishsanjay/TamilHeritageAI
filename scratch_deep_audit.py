# -*- coding: utf-8 -*-
"""
Deep Stress Test and Bug Detection Probe for Tamil Suvadi AI
"""
import sys
import os
import json
import traceback

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def probe():
    findings = []
    
    # 1. Probe ai_evaluation for division by zero on empty strings
    try:
        import ai_evaluation
        # Test CER/WER on empty strings
        cer = ai_evaluation.compute_character_error_rate("", "")
        wer = ai_evaluation.compute_word_error_rate("", "")
        print(f"[TEST 1] ai_evaluation empty string: CER={cer}, WER={wer}")
    except Exception as e:
        findings.append(("ai_evaluation empty strings", type(e).__name__, str(e), traceback.format_exc()))

    # 2. Probe collection_intelligence on empty documents (TTR division by zero)
    try:
        import collection_intelligence
        # Test empty docs
        empty_res = collection_intelligence.get_collection_intelligence_report([])
        print(f"[TEST 2] collection_intelligence empty collection: {empty_res.get('total_documents')}")
        # Test doc with no words
        zero_word_doc = [{"id": "empty", "title": "Empty", "text": "   ", "era": "", "category": ""}]
        zero_res = collection_intelligence.get_collection_intelligence_report(zero_word_doc)
        print(f"[TEST 2b] collection_intelligence zero-word doc TTR: {zero_res.get('vocabulary_richness_ttr')}")
    except Exception as e:
        findings.append(("collection_intelligence division by zero", type(e).__name__, str(e), traceback.format_exc()))

    # 3. Probe XML Escaping in TEI Export
    try:
        import xml.etree.ElementTree as ET
        doc_with_special_chars = "ஸ்வஸ்திஸ்ரீ <Rajaraja> & Chola \"Kings\" 'temple' & 100% pure."
        xml_out = collection_intelligence.export_tei_xml("test_doc", "Test & Title <1>", doc_with_special_chars, "Era & 1", "Cat <1>")
        # Try parsing it to verify well-formed XML
        ET.fromstring(xml_out)
        print("[TEST 3] TEI XML Special Chars Escaped & Valid XML: PASS")
    except Exception as e:
        findings.append(("TEI XML Special Characters Escaping", type(e).__name__, str(e), traceback.format_exc()))

    # 4. Probe semantic_search with regex special characters
    try:
        import semantic_search
        regex_query = "[.*?]+()^${}\\|"
        search_res = semantic_search.semantic_search_manuscripts(regex_query)
        print(f"[TEST 4] Semantic search regex query: success={search_res.get('success')}")
    except Exception as e:
        findings.append(("semantic_search regex query crash", type(e).__name__, str(e), traceback.format_exc()))

    # 5. Probe manuscript_variant_ai with empty and whitespace-only lines
    try:
        import manuscript_variant_ai
        var_res = manuscript_variant_ai.compare_manuscript_variants("", "   ")
        print(f"[TEST 5] Variant comparison empty inputs: success={var_res.get('success')}")
    except Exception as e:
        findings.append(("manuscript_variant_ai empty inputs", type(e).__name__, str(e), traceback.format_exc()))

    # 6. Probe timeline_explorer with text containing no dates, negative dates, and malformed dates
    try:
        import timeline_explorer
        tl_none = timeline_explorer.extract_timeline_events("எந்த ஆண்டும் குறிப்பிடப்படவில்லை.", "No Date Doc")
        tl_bce = timeline_explorer.extract_timeline_events("கி.மு. 300 இல் இயற்றப்பட்டது.", "BCE Doc")
        print(f"[TEST 6] Timeline explorer edge dates: none_count={len(tl_none)}, bce_count={len(tl_bce)}")
    except Exception as e:
        findings.append(("timeline_explorer edge dates", type(e).__name__, str(e), traceback.format_exc()))

    # 7. Probe ocr_engine.preprocess_image with None or invalid array
    try:
        import ocr_engine
        res_prep = ocr_engine.preprocess_image(None)
        print(f"[TEST 7] Preprocess None image: returned {res_prep}")
    except Exception as e:
        findings.append(("ocr_engine.preprocess_image None crash", type(e).__name__, str(e), traceback.format_exc()))

    # 8. Probe tamil_voice with edge texts
    try:
        import tamil_voice
        chunks = tamil_voice.chunk_tamil_text_for_voice("அ" * 500, max_chunk_chars=100)
        print(f"[TEST 8] Tamil voice chunking repetitive text: {len(chunks)} chunks")
    except Exception as e:
        findings.append(("tamil_voice chunking crash", type(e).__name__, str(e), traceback.format_exc()))

    # 9. Probe Grantha preservation in tamil_nlp & tamil_ai_features
    try:
        import tamil_ai_features, tamil_nlp
        grantha_text = "ஸ்வஸ்திஸ்ரீ ஹரிஹரன் ஷண்முகம் ஜகந்நாதன்"
        norm_res = tamil_ai_features.normalize_tamil_unicode(grantha_text)
        assert "ஸ்வஸ்திஸ்ரீ" in norm_res["normalized_text"], "Grantha ligature stripped!"
        assert "ஷண்முகம்" in norm_res["normalized_text"], "Grantha sha stripped!"
        print("[TEST 9] Grantha preservation: PASS")
    except Exception as e:
        findings.append(("Grantha character corruption", type(e).__name__, str(e), traceback.format_exc()))

    # 10. Probe cross_manuscript_discovery on invalid IDs and self-comparison
    try:
        import cross_manuscript_discovery
        links_empty = cross_manuscript_discovery.discover_cross_manuscript_connections("", "")
        links_self = cross_manuscript_discovery.discover_cross_manuscript_connections("thanjavur_inscription", "thanjavur_inscription")
        assert not links_empty["success"], "Empty IDs should fail safely"
        assert not links_self["success"], "Self comparison should fail safely"
        print(f"[TEST 10] Cross-manuscript edge cases: empty={links_empty['message']}, self={links_self['message']}")
    except Exception as e:
        findings.append(("cross_manuscript_discovery edge cases", type(e).__name__, str(e), traceback.format_exc()))

    print("\n" + "="*50)
    print(f"Total Probe Findings: {len(findings)}")
    for name, err_type, msg, tb in findings:
        print(f"FAILED: {name} -> {err_type}: {msg}")
    print("="*50)

if __name__ == "__main__":
    probe()
