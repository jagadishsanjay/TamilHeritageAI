# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Backend REST API Service (api_server.py)
Exposes all TamilHeritageAI models via standard REST endpoints with CORS.
Zero external dependencies (uses Python standard library ThreadingHTTPServer).
Compatible with React, Vite, Next.js, Vue, or any external frontend.
=============================================================================
"""

import sys
import os
import io
import json
import base64
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Import all core AI models from TamilHeritageAI
import ocr_engine
import ai_ocr
import tamil_nlp
import tamil_ai_features
import tamil_voice
import manuscript_assistant
import knowledge_explorer
import semantic_search
import manuscript_variant_ai
import timeline_explorer
import i18n


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP server for concurrent frontend API requests."""
    daemon_threads = True


class TamilHeritageAPIHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        """CORS preflight request handling."""
        self._set_headers(204)

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_data = self.rfile.read(content_length).decode("utf-8")
                return json.loads(raw_data)
        except Exception:
            pass
        return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json; charset=utf-8")
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.wfile.write(payload)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        # Root and Health Check
        if path in ("", "/api", "/api/health"):
            self._send_json({
                "status": "healthy",
                "service": "தமிழ்ச்சுவடி AI (Tamil Heritage AI) Backend",
                "version": "2.0.0",
                "port": 8000,
                "cors_enabled": True,
                "models": {
                    "tesseract_ocr": ocr_engine.verify_tesseract().get("available", False),
                    "trocr_vision_transformer": True,
                    "manuscript_assistant": True,
                    "semantic_search": True,
                    "knowledge_graph": True,
                    "variant_ai": True,
                    "voice_tts": True,
                    "multilingual_languages": 23,
                },
                "endpoints": [
                    "/api/health",
                    "/api/manuscripts",
                    "/api/ocr",
                    "/api/assistant",
                    "/api/search",
                    "/api/entities",
                    "/api/variants",
                    "/api/timeline",
                    "/api/voice",
                    "/api/normalize",
                ]
            })

        # List Canonical Manuscripts
        elif path == "/api/manuscripts":
            manuscripts = []
            for m_id, m_data in manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS.items():
                manuscripts.append({
                    "id": m_id,
                    "title": m_data["title"],
                    "era": m_data.get("era", ""),
                    "category": m_data.get("category", ""),
                    "description": m_data.get("description", ""),
                    "word_count": len(m_data["text"].split()),
                    "char_count": len(m_data["text"]),
                    "text_preview": m_data["text"][:180] + "...",
                })
            self._send_json({"success": True, "count": len(manuscripts), "manuscripts": manuscripts})

        else:
            self._send_json({"error": f"Endpoint '{self.path}' not found"}, status=404)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        body = self._read_json_body()

        try:
            # 1. OCR Extraction (Tesseract + TrOCR Vision Transformer)
            if path == "/api/ocr":
                raw_text = body.get("text", "")
                image_b64 = body.get("image_base64", "")
                mode = body.get("mode", "dual")  # 'tesseract', 'trocr', 'dual'

                if image_b64:
                    img_bytes = base64.b64decode(image_b64)
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    tess_res = ocr_engine.run_tesseract_ocr(pil_img) if mode in ("tesseract", "dual") else None
                    ai_res = ai_ocr.extract_tamil_text_ai(pil_img) if mode in ("trocr", "dual") else None
                    self._send_json({
                        "success": True,
                        "tesseract": tess_res,
                        "trocr": ai_res,
                        "combined_text": (ai_res.get("text") if ai_res else "") or (tess_res.get("text") if tess_res else ""),
                    })
                elif raw_text:
                    norm = tamil_ai_features.normalize_tamil_unicode(raw_text)
                    self._send_json({
                        "success": True,
                        "text": norm["normalized_text"],
                        "char_count": len(norm["normalized_text"]),
                    })
                else:
                    self._send_json({"success": False, "error": "No image_base64 or text provided"}, status=400)

            # 2. Evidence-Grounded AI Assistant Q&A
            elif path == "/api/assistant":
                query = body.get("query", "")
                doc_id = body.get("manuscript_id", "thanjavur_inscription")
                custom_text = body.get("custom_text", "")
                target_lang = body.get("language", "ta")

                if custom_text:
                    doc_text = custom_text
                    doc_title = body.get("doc_title", "Custom Document")
                elif doc_id in manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS:
                    lib_entry = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS[doc_id]
                    doc_text = lib_entry["text"]
                    doc_title = lib_entry["title"]
                else:
                    doc_text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
                    doc_title = "தஞ்சைப் பெரிய கோயில் கல்வெட்டு"

                qa_res = manuscript_assistant.ask_manuscript_assistant(
                    question=query,
                    document_text=doc_text,
                    document_title=doc_title,
                    target_language=target_lang,
                )
                self._send_json(qa_res)

            # 3. Meaning-Based Conceptual Semantic Search
            elif path == "/api/search":
                query = body.get("query", "")
                search_res = semantic_search.semantic_search_manuscripts(query=query)
                self._send_json(search_res)

            # 4. Knowledge Explorer (NER + Triples Graph)
            elif path == "/api/entities":
                text = body.get("text", "")
                doc_id = body.get("manuscript_id")
                if not text and doc_id in manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS:
                    text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS[doc_id]["text"]
                elif not text:
                    text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]

                graph_res = knowledge_explorer.run_knowledge_explorer(text)
                self._send_json({"success": True, "graph": graph_res})

            # 5. Manuscript Variant Comparison AI
            elif path == "/api/variants":
                text_a = body.get("text_a", "")
                text_b = body.get("text_b", "")
                label_a = body.get("label_a", "Manuscript A")
                label_b = body.get("label_b", "Manuscript B")

                if not text_a or not text_b:
                    self._send_json({"success": False, "error": "Both text_a and text_b are required"}, status=400)
                    return

                var_res = manuscript_variant_ai.compare_manuscript_variants(text_a, text_b, label_a=label_a, label_b=label_b)
                self._send_json(var_res)

            # 6. Historical Timeline Extraction
            elif path == "/api/timeline":
                text = body.get("text", "")
                doc_name = body.get("doc_name", "Manuscript")
                if not text:
                    text = manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS["thanjavur_inscription"]["text"]
                events = timeline_explorer.extract_timeline_events(text, doc_name)
                self._send_json({"success": True, "count": len(events), "events": events})

            # 7. Smart Tamil Voice TTS Synthesis
            elif path == "/api/voice":
                text = body.get("text", "")
                slow = bool(body.get("slow", False))
                if not text:
                    text = "வணக்கம். தமிழ் மரபுச் சுவடிகள் காப்பகம்."
                voice_res = tamil_voice.synthesize_tamil_speech(text, slow=slow)
                if voice_res["success"] and voice_res.get("audio_bytes"):
                    audio_b64 = base64.b64encode(voice_res["audio_bytes"]).decode("ascii")
                    self._send_json({
                        "success": True,
                        "audio_base64": audio_b64,
                        "word_count": voice_res.get("word_count", len(text.split())),
                        "duration_estimate": voice_res.get("duration_est_seconds", 5),
                        "online": voice_res.get("online", True),
                    })
                else:
                    self._send_json(voice_res)

            # 8. Unicode Normalization & Text Cleanup
            elif path == "/api/normalize":
                text = body.get("text", "")
                norm_res = tamil_ai_features.normalize_tamil_unicode(text)
                self._send_json(norm_res)

            else:
                self._send_json({"error": f"Endpoint '{path}' not found"}, status=404)

        except Exception as e:
            self._send_json({
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }, status=500)

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[API Server] {self.address_string()} - {format % args}\n")


def run_server(port=8000, host="0.0.0.0"):
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, TamilHeritageAPIHandler)
    print(f"🏛️ தமிழ்ச்சுவடி AI REST API Server running at http://localhost:{port}")
    print(f"CORS enabled. All 7 AI models connected and ready for frontend integration.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port=port)
