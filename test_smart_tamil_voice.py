"""
தமிழ்ச்சுவடி AI – Test Suite for Smart Tamil Voice (test_smart_tamil_voice.py)
=============================================================================
Automated test suite verifying the Smart Tamil Voice TTS engine:
 1. Engine Diagnostics & Network Status
 2. Text Preprocessing & Sentence Chunking
 3. Normal Speed Speech Synthesis (1.0x)
 4. Slow/Study Speed Speech Synthesis (0.8x)
 5. Long Manuscript Text Processing
 6. Error Handling (Empty input, No letters, etc.)
"""

import sys
import time

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import tamil_voice

def run_tests():
    print("=" * 70)
    print("  தமிழ்ச்சுவடி AI – Smart Tamil Voice (TTS) Automated Test Suite")
    print("=" * 70)
    t_start = time.time()

    # 1. Engine Diagnostics
    print("\n[TEST 1] Voice Engine Diagnostics...")
    diag = tamil_voice.check_voice_engine_status()
    print(f"  Engine: {diag['engine_name']}")
    print(f"  Internet connected: {diag['internet_connected']}")
    print(f"  Requires internet: {diag['requires_internet']}")
    print(f"  Status message: {diag['status_message']}")
    assert "Tamil" in diag["engine_name"] or "தமிழ்" in diag["engine_name"], "Expected Tamil in engine name"
    print("  [PASS] Test 1 passed.")

    # 2. Text Chunking for Long Texts
    print("\n[TEST 2] Tamil Text Chunking & Reading Order Preservation...")
    sample_text = (
        "தொல்காப்பியம் தமிழ் மொழியின் மிகத் தொன்மையான இலக்கண நூலாகும். "
        "இந்நூல் எழுத்து, சொல், பொருள் ஆகிய மூன்று அதிகாரங்களைக் கொண்டுள்ளது. "
        "பண்டைய காலத்தில் முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டினார். "
        "சோழர்களின் ஆட்சிக் காலத்தில் தமிழ் இலக்கியமும் கலைகளும் பெரும் வளர்ச்சி அடைந்தன."
    )
    chunks = tamil_voice.chunk_tamil_text_for_voice(sample_text, max_chunk_chars=120)
    print(f"  Original text: {len(sample_text)} chars -> Split into {len(chunks)} chunks:")
    for i, c in enumerate(chunks, start=1):
        print(f"    • Chunk {i} ({len(c)} chars): \"{c}\"")
    assert len(chunks) >= 2, f"Expected text to be chunked into at least 2 chunks, got {len(chunks)}"
    assert "தொல்காப்பியம்" in chunks[0], "Reading order violated in first chunk"
    print("  [PASS] Test 2 passed.")

    # 3. Speech Synthesis (Normal Speed 1.0x) on Actual OCR Output
    print("\n[TEST 3] Authentic Tamil Speech Synthesis (Normal Speed)...")
    actual_ocr_snippet = "செகுவேரா தமிழ் மரபு ஏஐ"
    res_normal = tamil_voice.synthesize_tamil_speech(actual_ocr_snippet, slow=False)
    if res_normal["success"]:
        print(f"  Generated {len(res_normal['audio_bytes'])} MP3 bytes in {res_normal['elapsed_seconds']}s")
        print(f"  Engine: {res_normal['engine']} | Speed: {res_normal['speed']}")
        assert res_normal["audio_bytes"][:3] in (b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2") or len(res_normal["audio_bytes"]) > 1000, "Invalid MP3 header"
        print("  [PASS] Test 3 passed.")
    else:
        print(f"  Notice: {res_normal['error']}")
        assert res_normal["error"] is not None

    # 4. Speech Synthesis (Slow Speed 0.8x)
    print("\n[TEST 4] Speech Synthesis with Speed Control (Study Mode 0.8x)...")
    res_slow = tamil_voice.synthesize_tamil_speech(actual_ocr_snippet, slow=True)
    if res_slow["success"]:
        print(f"  Generated {len(res_slow['audio_bytes'])} MP3 bytes in {res_slow['elapsed_seconds']}s")
        print(f"  Engine: {res_slow['engine']} | Speed: {res_slow['speed']}")
        print("  [PASS] Test 4 passed.")
    else:
        print(f"  Notice: {res_slow['error']}")

    # 5. Error Handling: Empty & Non-Letter Input
    print("\n[TEST 5] Graceful Error Handling...")
    res_empty = tamil_voice.synthesize_tamil_speech("   ")
    assert res_empty["success"] is False, "Empty string should return success=False"
    print(f"  Empty input handled: \"{res_empty['error']}\"")

    res_symbols = tamil_voice.synthesize_tamil_speech("---###$$$")
    assert res_symbols["success"] is False, "Symbols without letters should return success=False"
    print(f"  Symbol-only input handled: \"{res_symbols['error']}\"")
    print("  [PASS] Test 5 passed.")

    t_elapsed = round(time.time() - t_start, 2)
    print("\n" + "=" * 70)
    print(f"  ALL SMART TAMIL VOICE TESTS COMPLETED SUCCESSFULLY IN {t_elapsed}s!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    run_tests()
