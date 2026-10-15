# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 9: Source Traceability and Trust Layer
(source_trust_layer.py)
Shared provenance, evidence attribution, and trustworthiness grading layer
for all AI-generated Tamil heritage and historical information.
=============================================================================
Trust Level Categories:
  1. LEVEL 1: DIRECT_QUOTE (நேரடி மேற்கோள்)
     - Exact verbatim substring directly attested in the source manuscript.
  2. LEVEL 2: SOURCE_DERIVED (ஆவண வழி உண்மை)
     - Factual claim logically entailed and directly supported by a specific verse/sentence.
  3. LEVEL 3: SCHOLARLY_INTERPRETATION (வரலாற்றுப் பின்னணி விளக்கம்)
     - Contextual scholarly domain knowledge (e.g. classical commentaries, dynasty era).
  4. LEVEL 4: CONTEXTUAL_INFERENCE (சூழல் அனுமானம்)
     - Probabilistic or tentative connection derived from co-occurrence; marked clearly.
  5. LEVEL 0: INSUFFICIENT_EVIDENCE (சான்று போதாது / ஆதாரமற்றது)
     - Claim lacks citation; flagged to prevent hallucinations.
=============================================================================
"""

import html
import unicodedata
from typing import Dict, List, Any, Optional

import tamil_nlp


TRUST_LEVEL_META = {
    "DIRECT_QUOTE": {
        "level": 1,
        "name_ta": "நேரடி ஆவண மேற்கோள் (Verbatim Quotation)",
        "badge": "🟢 சான்றாதார மேற்கோள்",
        "color": "#4CAF50",
        "bg_color": "rgba(76, 175, 80, 0.15)",
        "border_color": "#2E7D32",
        "description": "சுவடியில் உள்ள வரிகள் சொல் மாறாமல் நேரடியாக மேற்கோள் காட்டப்பட்டுள்ளன.",
    },
    "SOURCE_DERIVED": {
        "level": 2,
        "name_ta": "ஆவண வழி உண்மை (Source-Derived Fact)",
        "badge": "🟡 ஆவணச் சான்று",
        "color": "#FBC02D",
        "bg_color": "rgba(251, 192, 45, 0.15)",
        "border_color": "#F57F17",
        "description": "ஆவணத்தின் வாக்கியத்தை அடிப்படையாகக் கொண்டு பெறப்பட்ட வரலாற்று உண்மை.",
    },
    "SCHOLARLY_INTERPRETATION": {
        "level": 3,
        "name_ta": "வரலாற்றுப் பின்னணி விளக்கம் (Scholarly Interpretation)",
        "badge": "🔵 மரபு வழி விளக்கம்",
        "color": "#0288D1",
        "bg_color": "rgba(2, 136, 209, 0.15)",
        "border_color": "#01579B",
        "description": "செம்மொழி உரை மரபு மற்றும் வரலாற்று ஆய்வறிஞர்களின் ஒருமித்த கருத்து.",
    },
    "CONTEXTUAL_INFERENCE": {
        "level": 4,
        "name_ta": "சூழல் அனுமானம் (Contextual Inference)",
        "badge": "🟣 தற்காலிக அனுமானம்",
        "color": "#AB47BC",
        "bg_color": "rgba(171, 71, 188, 0.15)",
        "border_color": "#6A1B9A",
        "description": "ஆவணத்தில் ஒரே சூழலில் இடம்பெற்றுள்ளதால் ஊகிக்கப்படும் தற்காலிகத் தொடர்பு.",
    },
    "INSUFFICIENT_EVIDENCE": {
        "level": 0,
        "name_ta": "சான்றாதாரமற்றது (Insufficient Evidence)",
        "badge": "🔴 சான்று இல்லை",
        "color": "#EF5350",
        "bg_color": "rgba(239, 83, 80, 0.15)",
        "border_color": "#C62828",
        "description": "இந்தக் கூற்றை உறுதிப்படுத்த ஆவணத்தில் நேரடிச் சான்றுகள் காணப்படவில்லை.",
    },
}


def audit_claim_traceability(
    claim_text: str,
    source_document_text: str,
    source_doc_id: str,
    source_doc_title: str,
) -> Dict[str, Any]:
    """
    Evaluates a generated claim against the underlying manuscript text
    and assigns a strict epigraphical Trust Level with citation metadata.
    """
    if not claim_text or not claim_text.strip():
        return {
            "trust_level": "INSUFFICIENT_EVIDENCE",
            "meta": TRUST_LEVEL_META["INSUFFICIENT_EVIDENCE"],
            "supporting_passage": "",
            "sentence_number": 0,
            "document_id": source_doc_id,
            "document_title": source_doc_title,
            "confidence_score": 0.0,
        }

    c_norm = unicodedata.normalize("NFC", claim_text.strip())
    doc_norm = unicodedata.normalize("NFC", source_document_text.strip())
    sentences = tamil_nlp.segment_sentences(doc_norm)

    # 1. Level 1: Direct Verbatim Quote
    clean_quote = c_norm.replace('"', '').replace("'", '').replace("ஆவணச் சான்றின்படி:\n\n", "").strip()
    if len(clean_quote) >= 4:
        for s_idx, s in enumerate(sentences, start=1):
            if clean_quote in s or s in clean_quote:
                return {
                    "trust_level": "DIRECT_QUOTE",
                    "meta": TRUST_LEVEL_META["DIRECT_QUOTE"],
                    "supporting_passage": s,
                    "sentence_number": s_idx,
                    "document_id": source_doc_id,
                    "document_title": source_doc_title,
                    "confidence_score": 1.0,
                }

    # 2. Level 2: Source-Derived Fact via lexical entailment
    c_words = set(claim_text.split())
    best_sent = ""
    best_overlap = 0
    best_idx = 0

    for s_idx, s in enumerate(sentences, start=1):
        s_words = set(s.split())
        overlap = len(c_words.intersection(s_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_sent = s
            best_idx = s_idx

    overlap_ratio = best_overlap / max(len(c_words), 1)

    if overlap_ratio >= 0.45:
        return {
            "trust_level": "SOURCE_DERIVED",
            "meta": TRUST_LEVEL_META["SOURCE_DERIVED"],
            "supporting_passage": best_sent,
            "sentence_number": best_idx,
            "document_id": source_doc_id,
            "document_title": source_doc_title,
            "confidence_score": round(overlap_ratio, 3),
        }

    if overlap_ratio >= 0.20:
        return {
            "trust_level": "CONTEXTUAL_INFERENCE",
            "meta": TRUST_LEVEL_META["CONTEXTUAL_INFERENCE"],
            "supporting_passage": best_sent,
            "sentence_number": best_idx,
            "document_id": source_doc_id,
            "document_title": source_doc_title,
            "confidence_score": round(overlap_ratio, 3),
        }

    return {
        "trust_level": "INSUFFICIENT_EVIDENCE",
        "meta": TRUST_LEVEL_META["INSUFFICIENT_EVIDENCE"],
        "supporting_passage": "",
        "sentence_number": 0,
        "document_id": source_doc_id,
        "document_title": source_doc_title,
        "confidence_score": 0.0,
    }


def render_traceability_badge(audit_result: Dict[str, Any]) -> str:
    """Renders an interactive HTML provenance badge for a claim."""
    meta = audit_result["meta"]
    doc_title = html.escape(audit_result.get("document_title", "ஆவணம்"))
    sent_no = audit_result.get("sentence_number", 0)
    passage = html.escape(audit_result.get("supporting_passage", ""))
    conf = int(audit_result.get("confidence_score", 0.0) * 100)

    html_code = f"""
    <div style="background: {meta['bg_color']}; border: 1.5px solid {meta['border_color']}; border-radius: 6px; padding: 8px 14px; margin: 6px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <span style="color: {meta['color']}; font-weight: bold; font-size: 0.85rem;">{meta['badge']}</span>
            <span style="color: #ECEFF1; font-size: 0.78rem;">மூலம்: <b>{doc_title}</b> (வரி #{sent_no}) | உறுதிப்பாடு: {conf}%</span>
        </div>
        <div style="color: #D7CCC8; font-size: 0.82rem; margin-top: 4px;">{meta['description']}</div>
        {f'<div style="color: #FFF; font-style: italic; font-size: 0.86rem; margin-top: 4px; border-left: 2px solid {meta["color"]}; padding-left: 6px;">"{passage}"</div>' if passage else ''}
    </div>
    """
    return html_code
