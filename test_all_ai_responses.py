# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import manuscript_assistant
import knowledge_explorer
import semantic_search
import manuscript_variant_ai
import timeline_explorer
import tamil_voice

print("--- 1. Testing AI Manuscript Assistant ---")
qa_res = manuscript_assistant.ask_manuscript_assistant(
    question="தஞ்சைப் பெரிய கோயிலைக் கட்டியது யார்?",
    document_text=manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"],
    document_title="தஞ்சைப் பெரிய கோயில் கல்வெட்டு",
)
assert qa_res["success"] and qa_res["found"], f"Assistant failed: {qa_res}"
print(f"Assistant PASS (Confidence: {qa_res['confidence']})")

print("--- 2. Testing Knowledge Explorer (NER + Graph) ---")
graph_res = knowledge_explorer.run_knowledge_explorer(
    manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
)
assert graph_res["entities"], "Knowledge Explorer found 0 entities!"
print(f"Knowledge Explorer PASS ({len(graph_res['entities'])} entities, {len(graph_res['relationships'])} relationships)")

print("--- 3. Testing Semantic Manuscript Search ---")
search_res = semantic_search.semantic_search_manuscripts("பெருவுடையார் கோயில் விமானம்")
assert search_res["success"] and len(search_res["results"]) > 0, "Semantic search found no matches!"
print(f"Semantic Search PASS (Top hit: {search_res['results'][0]['title']} score={search_res['results'][0]['score']})")

print("--- 4. Testing Manuscript Variant Comparison AI ---")
var_res = manuscript_variant_ai.compare_manuscript_variants(
    "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன்",
    "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன்"
)
assert var_res["success"], "Variant comparison failed!"
print(f"Variant AI PASS (Agreement={var_res['agreement_percentage']}%, Orthographic variants={var_res['orthographic_count']})")

print("--- 5. Testing Historical Timeline Explorer ---")
events = timeline_explorer.extract_timeline_events(
    manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"],
    "தஞ்சைப் பெரிய கோயில் கல்வெட்டு"
)
assert len(events) > 0, "Timeline extraction found 0 events!"
print(f"Timeline Explorer PASS ({len(events)} events extracted)")

print("--- 6. Testing Smart Tamil Voice (gTTS) ---")
v_res = tamil_voice.synthesize_tamil_speech("வணக்கம். தமிழ் மரபுச் சுவடிகள் காப்பகம்.")
assert v_res["success"] and len(v_res["audio_bytes"]) > 0, "Voice synthesis failed!"
print(f"Smart Voice PASS ({len(v_res['audio_bytes'])} bytes synthesized)")

print("\n" + "="*60)
print("ALL 6 AI MODEL RESPONSE SUITES PASSED 100%!")
print("="*60)
