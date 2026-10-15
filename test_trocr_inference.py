# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import ai_ocr
from PIL import Image

print("Loading TrOCR Vision Transformer model...")
pipeline = ai_ocr.load_tamil_ai_model(device_override="cpu")
print("Load success:", pipeline.get("success"))
if pipeline.get("success"):
    print("Device:", pipeline.get("device"))
    # Test sample inference
    img = Image.open("samples/sample_tamil.jpg").convert("RGB")
    res = ai_ocr.extract_tamil_text_ai(img, model=pipeline["model"], processor=pipeline["processor"], device=pipeline["device"], auto_slice=False)
    print("Inference success:", res.get("success"))
    print("Inference text length:", len(res.get("text", "")))
    print("Inference preview:", repr(res.get("text", "")[:80]))
else:
    print("Error loading model:", pipeline.get("error"))
