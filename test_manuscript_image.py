# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ocr_engine

print("--- Testing render_text_as_manuscript_image ---")

# 1. Test basic single argument
img1 = ocr_engine.render_text_as_manuscript_image("ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன்")
assert img1 is not None and img1.size[0] == 1000, f"Failed basic render: {img1}"
print("Test 1 (Basic positional) PASS:", img1.size)

# 2. Test with title keyword argument (as called in app.py line 866)
img2 = ocr_engine.render_text_as_manuscript_image(
    "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன்",
    title="தஞ்சைப் பெரிய கோயில் கல்வெட்டு (1010 CE)"
)
assert img2 is not None, "Failed render with title"
print("Test 2 (With title kwarg) PASS:", img2.size)

# 3. Test with arbitrary kwargs
img3 = ocr_engine.render_text_as_manuscript_image(
    "தொல்காப்பியம் எழுத்ததிகாரம்",
    title="தொல்காப்பியம்",
    width=800,
    min_height=350,
    some_unsupported_kwarg="safe",
    extra_data=12345
)
assert img3 is not None and img3.size[0] == 800, f"Failed render with kwargs: {img3}"
print("Test 3 (With **kwargs & custom width) PASS:", img3.size)

# 4. Test backward-compatibility when 2nd positional argument is int width
img4 = ocr_engine.render_text_as_manuscript_image(
    "சிலப்பதிகாரம் புகார் காண்டம்",
    1200,
    500
)
assert img4 is not None and img4.size[0] == 1200, f"Failed positional width: {img4}"
print("Test 4 (Positional integer width) PASS:", img4.size)

# 5. Test empty text safety
img5 = ocr_engine.render_text_as_manuscript_image("")
assert img5 is not None, "Failed empty text"
print("Test 5 (Empty text handling) PASS:", img5.size)

print("\n" + "="*50)
print("ALL 5 MANUSCRIPT IMAGE TESTS PASSED 100%!")
print("="*50)
