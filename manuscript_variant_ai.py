# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 5: Manuscript Variant Comparison AI
(manuscript_variant_ai.py)
Side-by-side textual criticism and variant alignment tool for Tamil palm-leaf
manuscripts, epigraphical recensions, and printed editions.
=============================================================================
Features:
  1. Passage & Verse Alignment: Levenshtein & SequenceMatcher alignment.
  2. Variant Categorisation:
     - Identical (ஒத்த வரிகள் / Exactly Identical)
     - Orthographic Variant (எழுத்து வடிவம் / சந்தி வேறுபாடு - Sandhi / Pulli / Archaic)
     - Lexical / Meaningful Variant (சொல் வேறுபாடு - Substantial textual difference)
     - Addition / Omission (சேர்க்கை / விடுபட்ட வரி)
  3. Side-by-Side Synchronised Display: Preserves both source texts intact.
  4. Human-Review Warning: Flags uncertain alignments for epigraphical scrutiny.
  5. Statistical Summary: Alignment ratios, variant counts, and similarity index.
=============================================================================
"""

import difflib
import unicodedata
from typing import Dict, List, Any, Optional, Tuple

import tamil_nlp

# Archaic Tamil orthographic mappings (e.g. palm-leaf without pulli, sandhi variations)
ARCHAIC_EQUIVALENCES = [
    ("க்", "க"), ("ச்", "ச"), ("ட்", "ட"), ("த்", "த"), ("ப்", "ப"), ("ற்", "ற"),
    ("ங்", "ங"), ("ஞ்", "ஞ"), ("ண்", "ண"), ("ந்", "ந"), ("ம்", "ம"), ("ன்", "ன"),
    ("கொ", "கொ"), ("கோ", "கோ"), ("கௌ", "கௌ"),
]


def strip_orthographic_noise(text: str) -> str:
    """Normalizes minor archaic orthography to test for underlying lexical identity."""
    t = unicodedata.normalize("NFC", text.strip())
    # Remove pulli / virama to test if only virama is missing (classic palm-leaf phenomenon)
    t_no_pulli = t.replace("\u0BCD", "")
    return t_no_pulli


def classify_text_difference(line_a: str, line_b: str) -> Dict[str, Any]:
    """
    Analyzes whether differences between two lines are minor orthographic/scribal
    peculiarities or meaningful lexical/thematic variants.
    """
    if line_a == line_b:
        return {
            "variant_type": "IDENTICAL",
            "label_ta": "முழுமையாக ஒத்தது (Identical)",
            "color": "#81C784",
            "is_uncertain": False,
            "similarity": 1.0,
        }

    # Similarity ratio
    matcher = difflib.SequenceMatcher(None, line_a, line_b)
    ratio = matcher.ratio()

    # Check for palm-leaf pulli omission or minor sandhi
    clean_a = strip_orthographic_noise(line_a)
    clean_b = strip_orthographic_noise(line_b)

    if clean_a == clean_b or ratio > 0.88:
        return {
            "variant_type": "ORTHOGRAPHIC",
            "label_ta": "எழுத்து / சந்தி வேறுபாடு (Orthographic / Sandhi Variant)",
            "description": "சொல்லின் அடிப்படை மாறவில்லை; புள்ளி அல்லது சந்தி எழுத்துக்களில் மட்டுமே வேறுபாடு உள்ளது (வழக்கமான சுவடிப் பிரதி பேதம்).",
            "color": "#FFD54F",
            "is_uncertain": False,
            "similarity": round(ratio, 3),
        }

    if ratio >= 0.45:
        return {
            "variant_type": "SUBSTANTIAL",
            "label_ta": "குறிப்பிடத்தக்க சொல் வேறுபாடு (Substantial Lexical Variant)",
            "description": "சொற்கள் அல்லது வாக்கிய அமைப்பில் மாறுபாடு உள்ளது. வெவ்வேறு சுவடிப் பதிப்பு அல்லது பிரதியெடுப்பாளர் மாற்றமாக இருக்கலாம்.",
            "color": "#FF8A65",
            "is_uncertain": False,
            "similarity": round(ratio, 3),
        }

    return {
        "variant_type": "UNCERTAIN_ALIGNMENT",
        "label_ta": "⚠️ மீள்பார்வை தேவை (Uncertain Alignment - Needs Review)",
        "description": "இரு வரிகளுக்கும் இடையேயான ஒப்புமை மிகக் குறைவு. வாக்கிய வரிசை மாறியிருக்கலாம் அல்லது வரி விடுபட்டிருக்கலாம்.",
        "color": "#E57373",
        "is_uncertain": True,
        "similarity": round(ratio, 3),
    }


def compare_manuscript_variants(
    text_a: str,
    text_b: str,
    label_a: str = "பிரதி A (Manuscript A)",
    label_b: str = "பிரதி B (Manuscript B / Edition)",
) -> Dict[str, Any]:
    """
    Aligns and compares two manuscript texts sentence-by-sentence.
    Preserves original versions and marks differences with precision.
    """
    sentences_a = [s.strip() for s in tamil_nlp.segment_sentences(text_a) if s.strip()]
    sentences_b = [s.strip() for s in tamil_nlp.segment_sentences(text_b) if s.strip()]

    matcher = difflib.SequenceMatcher(None, sentences_a, sentences_b)
    aligned_rows = []

    identical_count = 0
    orthographic_count = 0
    substantial_count = 0
    omission_count = 0
    addition_count = 0
    uncertain_count = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for a_idx, b_idx in zip(range(i1, i2), range(j1, j2)):
                identical_count += 1
                aligned_rows.append({
                    "line_no_a": a_idx + 1,
                    "line_no_b": b_idx + 1,
                    "text_a": sentences_a[a_idx],
                    "text_b": sentences_b[b_idx],
                    "status": "IDENTICAL",
                    "status_label_ta": "ஒத்தது (Identical)",
                    "color": "#4CAF50",
                    "is_uncertain": False,
                    "similarity": 1.0,
                    "note": "இரு பிரதிகளிலும் வரி முழுமையாக ஒத்துள்ளது.",
                })

        elif tag == "replace":
            # Compare lines pairwise
            max_len = max(i2 - i1, j2 - j1)
            for k in range(max_len):
                curr_a = sentences_a[i1 + k] if (i1 + k) < i2 else None
                curr_b = sentences_b[j1 + k] if (j1 + k) < j2 else None

                if curr_a and curr_b:
                    diff_info = classify_text_difference(curr_a, curr_b)
                    if diff_info["variant_type"] == "ORTHOGRAPHIC":
                        orthographic_count += 1
                    elif diff_info["variant_type"] == "SUBSTANTIAL":
                        substantial_count += 1
                    elif diff_info["is_uncertain"]:
                        uncertain_count += 1

                    aligned_rows.append({
                        "line_no_a": i1 + k + 1,
                        "line_no_b": j1 + k + 1,
                        "text_a": curr_a,
                        "text_b": curr_b,
                        "status": diff_info["variant_type"],
                        "status_label_ta": diff_info["label_ta"],
                        "color": diff_info["color"],
                        "is_uncertain": diff_info["is_uncertain"],
                        "similarity": diff_info["similarity"],
                        "note": diff_info.get("description", ""),
                    })
                elif curr_a and not curr_b:
                    omission_count += 1
                    aligned_rows.append({
                        "line_no_a": i1 + k + 1,
                        "line_no_b": "-",
                        "text_a": curr_a,
                        "text_b": "— [பிரதி B-யில் விடுபட்டுள்ளது] —",
                        "status": "OMISSION",
                        "status_label_ta": "விடுபட்ட வரி (Omitted in B)",
                        "color": "#EF5350",
                        "is_uncertain": False,
                        "similarity": 0.0,
                        "note": f"{label_b} பிரதியில் இந்த வரி காணப்படவில்லை.",
                    })
                elif curr_b and not curr_a:
                    addition_count += 1
                    aligned_rows.append({
                        "line_no_a": "-",
                        "line_no_b": j1 + k + 1,
                        "text_a": "— [பிரதி A-யில் இல்லை] —",
                        "text_b": curr_b,
                        "status": "ADDITION",
                        "status_label_ta": "புதிய சேர்க்கை (Added in B)",
                        "color": "#29B6F6",
                        "is_uncertain": False,
                        "similarity": 0.0,
                        "note": f"{label_a} பிரதியில் இல்லாத புதிய வரி.",
                    })

        elif tag == "delete":
            for a_idx in range(i1, i2):
                omission_count += 1
                aligned_rows.append({
                    "line_no_a": a_idx + 1,
                    "line_no_b": "-",
                    "text_a": sentences_a[a_idx],
                    "text_b": "— [விடுபட்டுள்ளது] —",
                    "status": "OMISSION",
                    "status_label_ta": "விடுபட்ட வரி (Omitted in B)",
                    "color": "#EF5350",
                    "is_uncertain": False,
                    "similarity": 0.0,
                    "note": f"{label_b} பிரதியில் இந்த வரி விடுபட்டுள்ளது.",
                })

        elif tag == "insert":
            for b_idx in range(j1, j2):
                addition_count += 1
                aligned_rows.append({
                    "line_no_a": "-",
                    "line_no_b": b_idx + 1,
                    "text_a": "— [இல்லை] —",
                    "text_b": sentences_b[b_idx],
                    "status": "ADDITION",
                    "status_label_ta": "புதிய சேர்க்கை (Added in B)",
                    "color": "#29B6F6",
                    "is_uncertain": False,
                    "similarity": 0.0,
                    "note": f"{label_a} பிரதியில் இல்லாத கூடுதல் வரி சேர்க்கை.",
                })

    total_compared = len(aligned_rows)
    agreement_percentage = round((identical_count / max(total_compared, 1)) * 100, 1)

    return {
        "success": True,
        "label_a": label_a,
        "label_b": label_b,
        "total_lines_a": len(sentences_a),
        "total_lines_b": len(sentences_b),
        "total_aligned_rows": total_compared,
        "identical_count": identical_count,
        "orthographic_count": orthographic_count,
        "substantial_count": substantial_count,
        "omission_count": omission_count,
        "addition_count": addition_count,
        "uncertain_count": uncertain_count,
        "agreement_percentage": agreement_percentage,
        "overall_similarity_pct": agreement_percentage,
        "aligned_rows": aligned_rows,
        "aligned_pairs": aligned_rows,
    }
