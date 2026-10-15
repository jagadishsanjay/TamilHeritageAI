# -*- coding: utf-8 -*-
"""Test Suite for Feature 2: Tamil Knowledge Explorer."""

import sys
if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass

import knowledge_explorer
import manuscript_assistant

def test_knowledge_explorer():
    print("=" * 70)
    print("  Testing Feature 2: Tamil Knowledge Explorer")
    print("=" * 70)

    # Test 1: Inscription Knowledge Graph
    thanjavur_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
    res = knowledge_explorer.run_knowledge_explorer(thanjavur_text)

    assert res["success"] is True
    assert res["total_entities"] >= 3, f"Expected at least 3 entities, found {res['total_entities']}"
    assert res["total_relationships"] >= 1, f"Expected at least 1 relationship, found {res['total_relationships']}"
    assert "<svg" in res["graph_html"]

    print(f"[PASS] Extracted {res['total_entities']} entities from Thanjavur inscription:")
    for ent in res["entities"]:
        print(f"       • {ent['name']} ({ent['type']} - {ent['label_ta']})")

    print(f"[PASS] Identified {res['total_relationships']} relationships with supporting evidence:")
    for rel in res["relationships"]:
        evidence_tag = "DIRECT" if rel["is_direct_evidence"] else "CONTEXT"
        print(f"       • [{evidence_tag}] {rel['source']} -> {rel['relationship']} -> {rel['target']}")
        print(f"         Evidence (Sentence #{rel['sentence_number']}): {rel['supporting_passage'][:90]}...")

    # Test 2: Tolkappiyam Graph
    tolk_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["tolkappiyam"]["text"]
    res_tolk = knowledge_explorer.run_knowledge_explorer(tolk_text)
    assert res_tolk["success"] is True
    assert res_tolk["total_entities"] >= 3
    print(f"[PASS] Tolkappiyam graph successfully parsed {res_tolk['total_entities']} entities and {res_tolk['total_relationships']} relationships.")

    print("=" * 70)
    print("  FEATURE 2: ALL TESTS PASSED SUCCESSFULLY (100%)!")
    print("=" * 70)

if __name__ == "__main__":
    test_knowledge_explorer()
