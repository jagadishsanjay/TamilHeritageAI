# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 6: Historical Context & Timeline Explorer
(timeline_explorer.py)
Source-grounded historical timeline extraction and chronological contextualisation
for Tamil manuscripts, palm leaves, and inscriptions.
=============================================================================
Features:
  1. Chronological Event Extraction: Detects dates (CE/BCE/Regnal years), eras, and rulers.
  2. Grounded Linkage: Every timeline card is bound directly to its supporting manuscript line.
  3. Strict Epigraphical Dating Distinction:
     - சான்றாதாரக் காலம் (Source-Stated Explicit Date - e.g. Inscription stated 1010 CE).
     - வரலாற்று ஊகக் காலம் (Historical Inferred Era - Scholarly consensus/Tradition).
     - பிரதியெடுக்கப்பட்ட காலம் (Copy Date vs Composition Date distinction).
  4. Interactive Vertical Timeline HTML Component with Heritage Styling.
  5. Graceful Empty States when documents lack chronological data.
=============================================================================
"""

import re
import html
import unicodedata
from typing import Dict, List, Any, Optional

import tamil_nlp
import manuscript_assistant

# Historical chronological anchors for Tamil literature & epigraphy
HISTORICAL_ANCHOR_PATTERNS = [
    {
        "pattern": r"கி\.பி\.?\s*1010|1010\s*ஆம்\s*ஆண்டு",
        "year_numeric": 1010,
        "era_label": "கி.பி. 1010 (11th Century CE)",
        "period": "இடைக்காலச் சோழர் பேரரசு (Imperial Chola Dynasty)",
        "ruler": "முதலாம் இராஜராஜ சோழன் (Rajaraja Chola I)",
        "event_summary": "தஞ்சைப் பெரிய கோயில் (இராஜராஜேஸ்வரம்) கட்டி முடிக்கப்பட்டு கல்வெட்டு பொறிக்கப்பட்டது.",
        "is_source_stated": True,
    },
    {
        "pattern": r"சங்க\s*காலம்|முந்துநூல்|தொல்காப்பிய",
        "year_numeric": -300,
        "era_label": "கி.மு. 3 ஆம் நூற்றாண்டு - சங்க காலம் (c. 3rd Century BCE)",
        "period": "சங்க காலம் (Classical Sangam Era)",
        "ruler": "சங்க கால மூவேந்தர்கள் (Chera, Chola, Pandya Kings)",
        "event_summary": "தொல்காப்பியம் தமிழ் இலக்கண முழுமை பெற்று அரங்கேற்றப்பட்ட தொன்மையான காலம்.",
        "is_source_stated": False, # Scholarly consensus / traditional dating
    },
    {
        "pattern": r"சிலப்பதிகாரம்|செங்குட்டுவன்|பூம்புகார்",
        "year_numeric": 200,
        "era_label": "கி.பி. 2 - 5 ஆம் நூற்றாண்டு (c. 2nd-5th Century CE)",
        "period": "சங்க மருவிய காப்பிய காலம் (Post-Sangam Epic Era)",
        "ruler": "சேரன் செங்குட்டுவன் (Chera King Senguttuvan)",
        "event_summary": "இளங்கோவடிகள் சிலப்பதிகாரக் காப்பியத்தை இயற்றிய மரபுப் பதிவுக் காலம்.",
        "is_source_stated": False,
    },
    {
        "pattern": r"திருக்குறள்|திருவள்ளுவர்|பரிமேலழகர்",
        "year_numeric": 50,
        "era_label": "கி.மு. 1 ஆம் நூற்றாண்டு - கி.பி. 1 ஆம் நூற்றாண்டு (c. 1st Century CE)",
        "period": "செம்மொழி நீதி இலக்கியக் காலம் (Classical Ethics Era)",
        "ruler": "பண்டைக்கால தமிழகம் (Ancient Tamilakam)",
        "event_summary": "திருவள்ளுவர் உலகப் பொதுமறையாம் திருக்குறளை உலகிற்கு அருளிய அறக் காலம்.",
        "is_source_stated": False,
    },
]


def extract_timeline_events(document_text: str, document_title: str = "சுவடி ஆவணம்") -> List[Dict[str, Any]]:
    """
    Extracts chronological markers and historical events explicitly grounded
    in the manuscript text.
    """
    if not document_text or not document_text.strip():
        return []

    norm_text = unicodedata.normalize("NFC", document_text)
    sentences = tamil_nlp.segment_sentences(norm_text)
    events = []
    seen_years = set()

    # 1. Check for explicit CE/BCE patterns in text
    year_matches = list(re.finditer(r"(கி\.பி\.|கி\.மு\.)\s*(\d{2,4})", norm_text))
    for m in year_matches:
        era_prefix = m.group(1).replace(".", "").strip()
        yr_val = int(m.group(2))
        numeric_val = yr_val if era_prefix == "கிபி" else -yr_val

        # Find matching sentence
        matching_sents = [s for s in sentences if m.group(0) in s]
        supporting_passage = matching_sents[0] if matching_sents else norm_text[:120]

        events.append({
            "year_numeric": numeric_val,
            "era_display": f"{m.group(1)} {yr_val}",
            "period_label_ta": f"{m.group(1)} {yr_val}",
            "period": "கல்வெட்டு / சுவடி ஆதாரக் காலம் (Source-Attested Era)",
            "title": f"ஆவணக் குறிப்பு: {m.group(0)}",
            "event_summary": f"சுவடியில் நேரடியாகக் குறிப்பிடப்பட்டுள்ள வரலாற்று ஆண்டு: {m.group(0)}.",
            "is_source_stated": True,
            "dating_badge": "சான்றாதாரக் காலம் (Source-Stated Explicit Date)",
            "badge_color": "#4CAF50",
            "supporting_passage": supporting_passage,
            "document_title": document_title,
            "certainty": "உறுதியானது (High Epigraphical Certainty)",
        })
        seen_years.add(numeric_val)

    # 2. Check for heritage anchors present in the text
    for anchor in HISTORICAL_ANCHOR_PATTERNS:
        if anchor["year_numeric"] not in seen_years:
            if re.search(anchor["pattern"], norm_text, re.IGNORECASE):
                # Find matching passage
                matching_sents = [s for s in sentences if re.search(anchor["pattern"], s, re.IGNORECASE)]
                passage = matching_sents[0] if matching_sents else norm_text[:120]

                is_stated = anchor["is_source_stated"] and re.search(r"\d{3,4}", passage)
                badge_text = "சான்றாதாரக் காலம் (Source-Stated Date)" if is_stated else "வரலாற்று ஊகக் காலம் (Historical Inferred Era)"
                badge_col = "#4CAF50" if is_stated else "#0288D1"
                certainty_text = "நேரடி ஆதாரக் குறிப்பு (Explicit Citation)" if is_stated else "ஆராய்ச்சி ஒருமித்த கருத்து (Scholarly Consensus)"

                events.append({
                    "year_numeric": anchor["year_numeric"],
                    "era_display": anchor["era_label"],
                    "period_label_ta": anchor["era_label"],
                    "period": anchor["period"],
                    "title": anchor["ruler"],
                    "event_summary": anchor["event_summary"],
                    "is_source_stated": bool(is_stated),
                    "dating_badge": badge_text,
                    "badge_color": badge_col,
                    "supporting_passage": passage,
                    "document_title": document_title,
                    "certainty": certainty_text,
                })
                seen_years.add(anchor["year_numeric"])

    # Sort chronologically by year_numeric ascending
    events.sort(key=lambda x: x["year_numeric"])
    return events


def generate_timeline_html(events: List[Dict[str, Any]]) -> str:
    """Renders a responsive, interactive vertical heritage timeline in HTML/CSS."""
    if not events:
        return (
            "<div style='padding:25px; text-align:center; color:#9E9E9E; background:#1C140D; border:1px solid #4D3117; border-radius:8px;'>"
            "⏳ இந்த ஆவணத்தில் நம்பகமான காலக் குறிப்புகள் அல்லது வரலாற்று ஆண்டுகள் கண்டறியப்படவில்லை.<br>"
            "<small style='color:#BCAAA4;'>வரலாற்று காலவரிசைக்கு கி.பி./கி.மு. அல்லது மன்னர் மரபுகள் குறிப்பிடப்பட்ட சுவடிகளைத் தேர்ந்தெடுக்கவும்.</small>"
            "</div>"
        )

    cards_html = []
    for idx, ev in enumerate(events, start=1):
        era = html.escape(ev["era_display"])
        period = html.escape(ev["period"])
        title = html.escape(ev["title"])
        summary = html.escape(ev["event_summary"])
        badge = html.escape(ev["dating_badge"])
        badge_color = ev["badge_color"]
        certainty = html.escape(ev["certainty"])
        passage = html.escape(ev["supporting_passage"])
        doc = html.escape(ev["document_title"])

        cards_html.append(
            f"""
            <div style="position: relative; padding-left: 35px; margin-bottom: 24px;">
                <!-- Timeline Dot -->
                <div style="position: absolute; left: 0; top: 4px; width: 16px; height: 16px; border-radius: 50%; background: #D4AF37; border: 3px solid #140C07; box-shadow: 0 0 8px rgba(212, 175, 55, 0.6);"></div>
                
                <!-- Event Card -->
                <div style="background: linear-gradient(135deg, #1F150E 0%, #170E08 100%); border: 1.5px solid #5D4037; border-left: 4px solid {badge_color}; border-radius: 8px; padding: 14px 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <span style="font-size: 1.1rem; font-weight: bold; color: #E6CA65; font-family: 'Cinzel', serif;">{era}</span>
                        <span style="background: rgba(255,255,255,0.08); color: {badge_color}; border: 1px solid {badge_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.78rem; font-weight: bold;">{badge}</span>
                    </div>
                    <div style="color: #FFECB3; font-weight: 600; font-size: 0.98rem; margin: 4px 0;">{title} | <small style="color: #B0BEC5;">{period}</small></div>
                    <div style="color: #ECEFF1; font-size: 0.92rem; margin: 6px 0; line-height: 1.5;">{summary}</div>
                    
                    <!-- Evidence Box -->
                    <div style="background: #120A05; border: 1px dashed #795548; padding: 8px 12px; border-radius: 6px; margin-top: 8px;">
                        <small style="color: #D4AF37; font-weight: bold;">📜 ஆதாரச் சுவடி வரி ({doc}) - {certainty}:</small>
                        <div style="color: #D7CCC8; font-size: 0.88rem; font-style: italic; margin-top: 2px;">"{passage}"</div>
                    </div>
                </div>
            </div>
            """
        )

    timeline_container = f"""
    <div style="position: relative; padding: 15px 10px; margin-left: 10px; border-left: 2px solid #5D4037;">
        {''.join(cards_html)}
    </div>
    """
    return timeline_container
