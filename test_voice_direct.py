# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import tamil_voice

text = "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டினார்."
res = tamil_voice.synthesize_tamil_speech(text)
print("Voice synthesis success:", res.get("success"))
print("Audio bytes length:", len(res.get("audio_bytes", b"")))
print("Engine:", res.get("engine"))
print("Duration est:", res.get("duration_est_seconds"))
assert res.get("success"), "Voice synthesis failed!"
assert len(res.get("audio_bytes", b"")) > 0, "No audio bytes generated!"
print("Voice synthesis test: 100% PASS!")
