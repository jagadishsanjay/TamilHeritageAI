# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Automated Test Suite for Phase 4 Features
(test_phase4_features.py)
Validates Features 11, 12, 13, 14, and 15:
  - Feature 11: Cross-Manuscript Knowledge Discovery
  - Feature 12: Tamil Literary Theme Analyzer
  - Feature 13: Manuscript Collection Insights
  - Feature 14: Human-in-the-Loop Knowledge Verification
  - Feature 15: Digital Heritage Export and Preservation
=============================================================================
"""

import sys
import os
import json
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import cross_manuscript_discovery
import collection_intelligence
import knowledge_verification
import manuscript_assistant


def test_feature_11_cross_manuscript_discovery():
    print("\n--- Testing Feature 11: Cross-Manuscript Knowledge Discovery ---")
    
    # Run discovery between Thanjavur Inscription and Silappadikaram
    res = cross_manuscript_discovery.discover_cross_manuscript_connections(
        doc_id_a="thanjavur_inscription",
        doc_id_b="silappadikaram",
        user_role="RESEARCHER",
    )
    
    assert res["success"] is True, "Discovery failed"
    assert "connections" in res, "Connections missing"
    assert res["total_connections"] > 0, "No connections discovered"
    assert "disclaimer_ta" in res, "Disclaimer missing"
    assert "disclaimer_en" in res, "English disclaimer missing"
    
    # Verify distinction of types
    types_found = {c["connection_type"] for c in res["connections"]}
    print(f"  Discovered connection types: {types_found}")
    valid_types = {"EXACT_SHARED_ENTITY", "SEMANTIC_SIMILARITY", "INFERRED_THEMATIC_RELATIONSHIP"}
    assert any(t in valid_types for t in types_found), "Missing categorized connection types"
    
    # Test permission enforcement
    # Restricted doc test
    mock_lib = {
        "doc1": {"title": "Doc 1", "text": "சோழன் ஆண்டான்.", "restricted": True},
        "doc2": {"title": "Doc 2", "text": "சேரன் ஆண்டான்.", "restricted": False},
    }
    perm_res = cross_manuscript_discovery.discover_cross_manuscript_connections(
        doc_id_a="doc1",
        doc_id_b="doc2",
        user_role="GUEST_VIEWER",
        custom_library=mock_lib,
    )
    assert perm_res["success"] is False, "Guest role was erroneously allowed to access restricted document"
    print("  Permission check passed: GUEST_VIEWER correctly blocked from restricted manuscripts.")
    print(f"  Total valid connections between Thanjavur & Silappadikaram: {res['total_connections']}")
    print("  Feature 11 Passed! [PASS]")


def test_feature_12_tamil_literary_theme_analyzer():
    print("\n--- Testing Feature 12: Tamil Literary Theme Analyzer ---")
    
    # Test on Tolkappiyam text
    tolkappiyam_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["tolkappiyam"]["text"]
    theme_res = cross_manuscript_discovery.analyze_document_themes(tolkappiyam_text, doc_id="tolkappiyam")
    
    assert theme_res["success"] is True, "Theme analysis failed"
    assert theme_res["total_themes"] > 0, "No themes identified"
    
    top_theme = theme_res["detected_themes"][0]
    print(f"  Top Identified Theme: {top_theme['theme_name_ta']} ({top_theme['theme_name_en']})")
    print(f"  Evidence Passages Count: {top_theme['evidence_count']}")
    assert top_theme["theme_id"] == "THEME_GRAMMAR_LINGUISTICS", "Linguistics theme should be primary for Tolkappiyam"
    assert "ai_interpretation_note" in top_theme, "Transparent AI interpretation note missing"
    assert top_theme["passages"], "Passages must not be empty"
    print("  Feature 12 Passed! [PASS]")


def test_feature_13_collection_intelligence():
    print("\n--- Testing Feature 13: Manuscript Collection Insights ---")
    
    mock_session_history = [
        {"filename": "test_scan_01.jpg", "preview": "ஸ்வஸ்திஸ்ரீ இராஜராஜ சோழன்", "text": "ஸ்வஸ்திஸ்ரீ இராஜராஜ சோழன்"},
        {"filename": "empty_scan.png", "preview": "", "text": ""}, # simulate processing failure
    ]
    
    report = collection_intelligence.get_collection_intelligence_report(session_history=mock_session_history)
    
    assert report["success"] is True, "Collection intelligence report failed"
    assert report["total_documents"] >= 4, "Should count library docs + session uploads"
    assert report["indexed_documents_count"] >= 3, "Library docs should be counted as indexed"
    assert report["unindexed_documents_count"] >= 1, "Session upload should be counted as unindexed"
    assert len(report["processing_failures"]) >= 1, "Failed scan should be caught in processing failures"
    assert report["total_passages"] > 0, "Total passages must be positive"
    assert report["total_words"] > 0, "Total words must be positive"
    assert report["unique_vocabulary_types"] > 0, "Unique types must be positive"
    assert "%" in report["type_token_ratio_pct"], "TTR must be formatted as percentage"
    assert len(report["document_entity_links"]) > 0, "Bipartite document-entity graph must not be empty"
    assert "grantha_characters" in report["script_characteristics"], "Script characteristics missing"
    
    print(f"  Total Indexed Docs: {report['indexed_documents_count']}")
    print(f"  Unindexed Docs: {report['unindexed_documents_count']}")
    print(f"  Processing Failures Detected: {len(report['processing_failures'])}")
    print(f"  Vocabulary Type-Token Ratio: {report['type_token_ratio_pct']}")
    print(f"  Grounded Summary: {report['collection_grounded_summary'][:80]}...")
    print("  Feature 13 Passed! [PASS]")


def test_feature_14_knowledge_verification():
    print("\n--- Testing Feature 14: Human-in-the-Loop Knowledge Verification ---")
    
    # 1. Test unauthorized attempt (Guest / Student role)
    guest_attempt = knowledge_verification.save_verification_decision(
        item_id="ENTITY_சோழன்_TEST",
        item_type="ENTITY",
        original_ai_prediction={"name": "சோழன்", "type": "RULER"},
        decision="ACCEPT",
        reviewer_role="GUEST_VIEWER",
        reviewer_name="Student Viewer",
    )
    assert guest_attempt["success"] is False, "Guest role should be forbidden from approving facts"
    assert guest_attempt["status"] == "UNAUTHORIZED", "Status must be UNAUTHORIZED"
    print("  Security Check Passed: Unauthorized role correctly blocked.")
    
    # 2. Test authorized approval by Chief Epigraphist
    epigraphist_approval = knowledge_verification.save_verification_decision(
        item_id="ENTITY_சோழன்_TEST",
        item_type="ENTITY",
        original_ai_prediction={"name": "சோழன்", "type": "RULER"},
        decision="ACCEPT",
        reviewer_role="CHIEF_EPIGRAPHIST",
        reviewer_name="முதன்மை ஆய்வாளர் (Dr. K. Swaminathan)",
        notes="கல்வெட்டு ஆதாரத்துடன் சரிபார்க்கப்பட்டது.",
    )
    assert epigraphist_approval["success"] is True, "Chief Epigraphist should be authorized"
    assert epigraphist_approval["record"]["status"] == "HUMAN_VERIFIED", "Status should be HUMAN_VERIFIED"
    
    # 3. Test verification status query
    item_stat = knowledge_verification.get_item_verification_status("ENTITY_சோழன்_TEST")
    assert item_stat["is_verified"] is True, "Item should report verified"
    assert item_stat["reviewer_name"] == "முதன்மை ஆய்வாளர் (Dr. K. Swaminathan)"
    
    # 4. Test unreviewed item returns TENTATIVE_AI
    unreviewed_stat = knowledge_verification.get_item_verification_status("RANDOM_UNREVIEWED_ITEM_123")
    assert unreviewed_stat["is_verified"] is False, "Unreviewed item must not be marked verified"
    assert unreviewed_stat["status"] == "TENTATIVE_AI", "Must be TENTATIVE_AI"
    
    # 5. Test Audit Trail
    audit = knowledge_verification.get_audit_trail()
    assert len(audit) >= 2, "Audit log must record both blocked and approved events"
    print(f"  Audit trail length: {len(audit)} entries recorded.")
    print("  Feature 14 Passed! [PASS]")


def test_feature_15_digital_heritage_export():
    print("\n--- Testing Feature 15: Digital Heritage Export and Preservation ---")
    
    doc = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]
    
    # 1. Plain Text UTF-8 Export
    txt_out = collection_intelligence.export_plain_text(
        doc_title=doc["title"],
        doc_text=doc["text"],
        era=doc["era"],
        category=doc["category"],
        provenance="தஞ்சைப் பெரிய கோயில் தெற்குச் சுவர்",
        verification_status="HUMAN_VERIFIED",
        reviewer_name="Dr. S. Rajagopal",
        confidence_score=0.98,
    )
    assert "தமிழ் மரபு ஆவண எண்மக் காப்பகம்" in txt_out, "Plain text missing header"
    assert "HUMAN_VERIFIED" in txt_out, "Review status missing"
    assert "98%" in txt_out, "Confidence missing"
    print("  UTF-8 Plain Text Export validated.")
    
    # 2. TEI P5 XML Export
    xml_out = collection_intelligence.export_tei_xml(
        doc_id="thanjavur_inscription",
        doc_title=doc["title"],
        doc_text=doc["text"],
        era=doc["era"],
        category=doc["category"],
        verification_status="HUMAN_VERIFIED",
        reviewer_name="Dr. S. Rajagopal",
    )
    assert '<?xml version="1.0" encoding="UTF-8"?>' in xml_out, "XML header missing"
    assert "<teiHeader>" in xml_out, "teiHeader missing"
    assert "<TEI" in xml_out and "</TEI>" in xml_out, "TEI root missing"
    assert '<div type="transcription"' in xml_out, "transcription div missing"
    print("  Standard TEI P5 XML Export validated.")
    
    # 3. TEI JSON Export
    json_out = collection_intelligence.export_tei_json(
        doc_id="thanjavur_inscription",
        doc_title=doc["title"],
        doc_text=doc["text"],
        era=doc["era"],
        category=doc["category"],
        verification_status="HUMAN_VERIFIED",
    )
    parsed_json = json.loads(json_out)
    assert "teiHeader" in parsed_json, "teiHeader missing in JSON"
    assert "textBody" in parsed_json, "textBody missing in JSON"
    assert parsed_json["textBody"]["total_sentences"] > 0, "Passages missing"
    print("  TEI JSON Export validated.")
    
    # 4. Batch Preservation Archive Export
    batch_docs = list(manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS.values())
    batch_json = collection_intelligence.export_collection_batch_tei_json(batch_docs)
    parsed_batch = json.loads(batch_json)
    assert "collectionMetadata" in parsed_batch, "Collection metadata missing"
    assert len(parsed_batch["documents"]) == len(batch_docs), "All documents must be present in batch"
    print(f"  Batch Collection Archive validated ({len(parsed_batch['documents'])} documents).")
    
    # 5. HTML Dossier Export
    html_out = collection_intelligence.export_html_dossier(
        doc_title=doc["title"],
        doc_text=doc["text"],
        era=doc["era"],
        category=doc["category"],
    )
    assert "<!DOCTYPE html>" in html_out, "HTML header missing"
    assert doc["title"] in html_out, "Title missing in HTML"
    print("  Printable HTML Dossier validated.")
    print("  Feature 15 Passed! [PASS]")


if __name__ == "__main__":
    print("=====================================================================")
    print("🔬 தமிழ்ச்சுவடி AI – PHASE 4 AUTOMATED TEST SUITE")
    print("=====================================================================")
    test_feature_11_cross_manuscript_discovery()
    test_feature_12_tamil_literary_theme_analyzer()
    test_feature_13_collection_intelligence()
    test_feature_14_knowledge_verification()
    test_feature_15_digital_heritage_export()
    print("=====================================================================")
    print("🎉 ALL PHASE 4 FEATURES (11, 12, 13, 14, 15) PASSED 100% SUCCESSFULLY!")
    print("=====================================================================")
