# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 11 & 12: Cross-Manuscript Discovery & Literary Theme Analyzer
(cross_manuscript_discovery.py)
Cross-document knowledge linking, passage alignment, and classical Tamil thematic classification.
=============================================================================
Features:
  1. Cross-Manuscript Knowledge Discovery (Feature 11):
     - Identifies shared entities, semantic passage affinities, and thematic links.
     - Strict distinction: EXACT_MATCH vs SEMANTIC_SIMILARITY vs INFERRED_RELATIONSHIP.
     - Strict disclaimer: Never claims similarity proves common authorship or direct dependence.
     - Role-based document access permission checks.
  2. Tamil Literary Theme Analyzer (Feature 12):
     - Classical taxonomies: Dharma/Governance, Architecture, Grammar/Linguistics,
       Maritime Trade/Geography, Classical Poetics/Epics.
     - Passage grouping with sentence-level citations.
     - Transparent AI interpretation labeling (not epigraphical dogma).
     - Integration with Human-in-the-Loop review for theme rejection/editing.
=============================================================================
"""

import re
import unicodedata
from typing import Dict, List, Any, Optional, Set, Tuple

import tamil_nlp
import manuscript_assistant
import knowledge_explorer
import semantic_search
import knowledge_verification

# =====================================================================
# 🏛️ Classical Tamil Literary & Heritage Theme Definitions
# =====================================================================
HERITAGE_THEMES = [
    {
        "id": "THEME_GOVERNANCE_DHARMA",
        "name_ta": "அறம், நீதி & ஆட்சிமுறை (Dharma, Ethics & Governance)",
        "name_en": "Dharma, Royal Ethics & Governance",
        "color": "#F59E0B",
        "icon": "⚖️",
        "keywords": ["அறம்", "நீதி", "அறத்துப்பால்", "மன்னன்", "ஆட்சி", "வேந்தன்", "அரசியல்", "குடிமக்கள்", "நெறி", "பொதுமறை", "அரசன்", "செங்கோல்"],
        "description_ta": "அறநெறி, மன்னரின் கடமைகள், மக்கள் நல்வாழ்வு மற்றும் நீதி இலக்கியக் கோட்பாடுகள்.",
        "description_en": "Classical Tamil principles of ethical living, righteous kingship, justice, and statecraft.",
    },
    {
        "id": "THEME_ARCHITECTURE_EPIGRAPHY",
        "name_ta": "கட்டடக்கலை, சிற்பம் & கல்வெட்டு (Architecture & Epigraphy)",
        "name_en": "Temple Architecture, Sculpture & Epigraphs",
        "color": "#10B981",
        "icon": "🏛️",
        "keywords": ["கோயில்", "விமானம்", "தட்சிண மேரு", "தச்சர்", "சிற்பம்", "கல்வெட்டு", "மூலவர்", "பெருவுடையார்", "கட்டினார்", "செப்பு", "சாசனம்"],
        "description_ta": "கோயில் கட்டடக் கலை, விமான நிர்மாணம், பெருந்தச்சர்கள் மற்றும் கல்வெட்டு ஆவணங்கள்.",
        "description_en": "Dravidian temple architecture, vimana engineering, master sculptors, and inscriptional records.",
    },
    {
        "id": "THEME_GRAMMAR_LINGUISTICS",
        "name_ta": "இலக்கணம், சொல் & மொழி நெறிகள் (Linguistics & Grammar)",
        "name_en": "Tamil Linguistics, Grammar & Poetics",
        "color": "#3B82F6",
        "icon": "📜",
        "keywords": ["எழுத்து", "சொல்", "பொருள்", "இலக்கணம்", "அதிகாரம்", "இயல்", "தொல்காப்பியம்", "பாயிரம்", "முந்துநூல்", "செய்யுள்", "யாப்பு"],
        "description_ta": "எழுத்து, சொல், பொருள் இலக்கணப் பாகுபாடுகள் மற்றும் செய்யுள் இயற்றல் நெறிகள்.",
        "description_en": "Phonology, morphology, poetics, metrics, and formal rules of classical Tamil language.",
    },
    {
        "id": "THEME_MARITIME_TRADE_GEOGRAPHY",
        "name_ta": "கடல் வணிகம் & புவியியல் எல்லைகள் (Maritime Trade & Geography)",
        "name_en": "Maritime Trade, Port Cities & Geography",
        "color": "#06B6D4",
        "icon": "🌊",
        "keywords": ["பூம்புகார்", "காவிரி", "கடல்", "வணிகம்", "துறைமுகம்", "வேங்கடம்", "குமரி", "கானல்வரி", "வைகை", "மதுரை", "நாவாய்", "கலம்"],
        "description_ta": "பண்டைக்கால தமிழகத்தின் எல்லைகள், காவிரிப்பூம்பட்டினத் துறைமுக வாணிகம் மற்றும் நதிக்கரை நாகரிகங்கள்.",
        "description_en": "Ancient Tamil port cities, maritime trade routes, navigational terms, borders, and river civilizations.",
    },
    {
        "id": "THEME_CLASSICAL_EPIC_POETICS",
        "name_ta": "காப்பிய மரபு & வாழ்வியல் (Classical Epic & Poetics)",
        "name_en": "Classical Epic Narrative & Society",
        "color": "#EC4899",
        "icon": "❤️",
        "keywords": ["சிலப்பதிகாரம்", "காப்பியம்", "கண்ணகி", "கோவலன்", "மாதவி", "ஊழ்வினை", "பத்தினி", "அகவாழ்க்கை", "புறவாழ்க்கை", "நாடகமேடை"],
        "description_ta": "ஐம்பெருங் காப்பிய மரபு, மக்களின் வாழ்வியல், நாட்டியக் கலை மற்றும் இலக்கியக் கதையாடல்.",
        "description_en": "Classical narrative epics, social life, performing arts, drama, and human relationships.",
    },
]

# Epigraphical Research Disclaimer
CROSS_DISCOVERY_DISCLAIMER_TA = (
    "சான்றாதார எச்சரிக்கை: இரு சுவடிகளிலும் காணப்படும் பொதுமைப் பண்புகள் கருத்துக் கூற்றுகளின் தொடர்பைக் குறிக்கின்றனவே அன்றி, "
    "அவை ஒரே ஆசிரியர் இயற்றியவை என்றோ அல்லது நேரடி வரலாற்றுத் தொடர்பு உடையவை என்றோ நிரூபிக்காது."
)
CROSS_DISCOVERY_DISCLAIMER_EN = (
    "Epigraphical Notice: Observed similarities indicate textual or conceptual affinity and do NOT prove "
    "common authorship or direct historical dependence."
)


# =====================================================================
# 🔍 Feature 11: Cross-Manuscript Knowledge Discovery
# =====================================================================
def discover_cross_manuscript_connections(
    doc_id_a: str,
    doc_id_b: str,
    user_role: str = "RESEARCHER",
    custom_library: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Discovers connections, shared entities, semantic passage similarities,
    and thematic intersections across two manuscripts in the digital library.
    Respects document permissions and classifies connection rigor.
    """
    lib = custom_library if custom_library else manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS
    
    if not doc_id_a or not doc_id_b or doc_id_a not in lib or doc_id_b not in lib:
        return {
            "success": False,
            "message": "தேர்ந்தெடுக்கப்பட்ட சுவடிகள் நூலகத்தில் இல்லை.",
            "connections": [],
        }

    if doc_id_a == doc_id_b:
        return {
            "success": False,
            "message": "ஒரே சுவடியை அதனுடனேயே ஒப்பிட முடியாது. இருவேறு சுவடிகளைத் தேர்ந்தெடுக்கவும் (Cannot compare a manuscript with itself).",
            "connections": [],
        }

    doc_a = lib[doc_id_a]
    doc_b = lib[doc_id_b]

    # Permission check: If doc has restricted flag, only authenticated roles can view
    if (doc_a.get("restricted", False) or doc_b.get("restricted", False)) and user_role == "GUEST_VIEWER":
        return {
            "success": False,
            "message": "அனுமதி மறுக்கப்பட்டது: பாதுகாக்கப்பட்ட சுவடிகளை பார்வையாளர்கள் ஆய்வு செய்ய இயலாது.",
            "connections": [],
        }

    # Extract entities from both documents
    ent_a_list = knowledge_explorer.extract_heritage_entities(doc_a["text"])
    ent_b_list = knowledge_explorer.extract_heritage_entities(doc_b["text"])

    ent_a = {e["name"]: e for e in ent_a_list}
    ent_b = {e["name"]: e for e in ent_b_list}

    shared_entity_names = set(ent_a.keys()).intersection(set(ent_b.keys()))

    sentences_a = tamil_nlp.segment_sentences(doc_a["text"])
    sentences_b = tamil_nlp.segment_sentences(doc_b["text"])

    discovered_connections = []

    # 1. EXACT_SHARED_ENTITY Connections (Exact historical name/term match)
    for name in shared_entity_names:
        meta_a = ent_a[name]
        pass_a = [s for s in sentences_a if name in s]
        pass_b = [s for s in sentences_b if name in s]

        # Check if entity has human verification status
        v_status = knowledge_verification.get_item_verification_status(f"ENTITY_{name}")

        discovered_connections.append({
            "connection_type": "EXACT_SHARED_ENTITY",
            "type_label_ta": "நேரடி வரலாற்று உருப்படி (Exact Shared Entity)",
            "type_label_en": "Exact Entity Match",
            "badge_color": "#10B981",
            "concept_name": name,
            "entity_type": meta_a["type"],
            "verification_status": v_status["status"],
            "verification_badge_ta": v_status["status_label_ta"],
            "evidence_doc_a": {
                "title": doc_a["title"],
                "doc_id": doc_id_a,
                "passage": pass_a[0] if pass_a else "",
            },
            "evidence_doc_b": {
                "title": doc_b["title"],
                "doc_id": doc_id_b,
                "passage": pass_b[0] if pass_b else "",
            },
            "interpretation_ta": f"இரு சுவடிகளிலும் '{name}' ({meta_a['label_ta']}) எனும் வரலாற்று உருப்படி நேரடியாக இடம்பெற்றுள்ளது.",
            "interpretation_en": f"Both documents explicitly record the historical entity '{name}' ({meta_a['type']}).",
        })

    # 2. SEMANTIC_PASSAGE_SIMILARITY Connections (Conceptual passage alignment)
    # Uses semantic concept clusters and root overlap across documents
    seen_semantic_pairs = set()
    for s_a in sentences_a:
        exp_a = semantic_search.expand_query_semantics(s_a)
        clusters_a = set(exp_a["matched_clusters"])
        for s_b in sentences_b:
            exp_b = semantic_search.expand_query_semantics(s_b)
            clusters_b = set(exp_b["matched_clusters"])
            shared_clusters = clusters_a.intersection(clusters_b)
            
            # Check either shared concept clusters or significant token intersection
            words_a = set(re.findall(r"[\u0B80-\u0BFA]{3,}", s_a))
            words_b = set(re.findall(r"[\u0B80-\u0BFA]{3,}", s_b))
            common_words = words_a.intersection(words_b)

            if shared_clusters or (len(common_words) >= 2 and not any(c in shared_entity_names for c in common_words)):
                c_key = f"{s_a[:20]}_{s_b[:20]}"
                if c_key in seen_semantic_pairs:
                    continue
                seen_semantic_pairs.add(c_key)
                
                c_name = list(shared_clusters)[0] if shared_clusters else " / ".join(list(common_words)[:3])
                discovered_connections.append({
                    "connection_type": "SEMANTIC_SIMILARITY",
                    "type_label_ta": "பொருள்சார் உரை ஒப்புமை (Semantic Passage Echo)",
                    "type_label_en": "Semantic Passage Similarity",
                    "badge_color": "#3B82F6",
                    "concept_name": f"கருத்துப் புலம்: {c_name}",
                    "entity_type": "PASSAGE_SIMILARITY",
                    "verification_status": "TENTATIVE_AI",
                    "verification_badge_ta": "AI உரை ஒப்புமை (Unreviewed)",
                    "evidence_doc_a": {
                        "title": doc_a["title"],
                        "doc_id": doc_id_a,
                        "passage": s_a,
                    },
                    "evidence_doc_b": {
                        "title": doc_b["title"],
                        "doc_id": doc_id_b,
                        "passage": s_b,
                    },
                    "interpretation_ta": f"இரு சுவடிகளிலும் '{c_name}' சார்ந்த இணையான வாசகங்களும் வரலாற்றுச் சூழலும் பதிவாகியுள்ளன.",
                    "interpretation_en": f"Both texts demonstrate conceptual resonance in the domain: {c_name}.",
                })
                break # Avoid redundant matches per sentence

    # 3. INFERRED_THEMATIC_RELATIONSHIP (Shared domain taxonomy)
    themes_a = analyze_document_themes(doc_a["text"])
    themes_b = analyze_document_themes(doc_b["text"])

    theme_ids_a = {t["theme_id"] for t in themes_a["detected_themes"]}
    theme_ids_b = {t["theme_id"] for t in themes_b["detected_themes"]}
    shared_theme_ids = theme_ids_a.intersection(theme_ids_b)

    for th_id in shared_theme_ids:
        th_meta = next(t for t in HERITAGE_THEMES if t["id"] == th_id)
        pass_a = next((t["passages"][0] for t in themes_a["detected_themes"] if t["theme_id"] == th_id and t["passages"]), "")
        pass_b = next((t["passages"][0] for t in themes_b["detected_themes"] if t["theme_id"] == th_id and t["passages"]), "")

        discovered_connections.append({
            "connection_type": "INFERRED_THEMATIC_RELATIONSHIP",
            "type_label_ta": "ஊகிக்கப்பட்ட கருப்பொருள் இணைப்பு (Inferred Thematic Affinity)",
            "type_label_en": "Inferred Thematic Affinity",
            "badge_color": "#F59E0B",
            "concept_name": th_meta["name_ta"],
            "entity_type": "THEME",
            "verification_status": "TENTATIVE_AI",
            "verification_badge_ta": "ஊகிக்கப்பட்ட கருப்பொருள் (Inferred)",
            "evidence_doc_a": {
                "title": doc_a["title"],
                "doc_id": doc_id_a,
                "passage": pass_a,
            },
            "evidence_doc_b": {
                "title": doc_b["title"],
                "doc_id": doc_id_b,
                "passage": pass_b,
            },
            "interpretation_ta": f"இரு சுவடிகளும் '{th_meta['name_ta']}' எனும் பொதுவான வரலாற்று/இலக்கியக் கருப்பொருளைக் கையாள்கின்றன.",
            "interpretation_en": f"Both documents share thematic treatment of '{th_meta['name_en']}'.",
        })

    return {
        "success": True,
        "doc_a": {"id": doc_id_a, "title": doc_a["title"], "era": doc_a.get("era", "Classical")},
        "doc_b": {"id": doc_id_b, "title": doc_b["title"], "era": doc_b.get("era", "Classical")},
        "total_connections": len(discovered_connections),
        "shared_entities_count": len(shared_entity_names),
        "shared_themes_count": len(shared_theme_ids),
        "connections": discovered_connections,
        "disclaimer_ta": CROSS_DISCOVERY_DISCLAIMER_TA,
        "disclaimer_en": CROSS_DISCOVERY_DISCLAIMER_EN,
    }


# =====================================================================
# 📚 Feature 12: Tamil Literary Theme Analyzer
# =====================================================================
def analyze_document_themes(
    document_text: str,
    doc_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyzes and groups manuscript sentences by classical Tamil themes.
    Identifies supporting passages, attaches bilingual summaries,
    transparently labels AI interpretations, and reflects human verification status.
    """
    if not document_text or not document_text.strip():
        return {
            "success": False,
            "detected_themes": [],
            "total_themes": 0,
        }

    norm_text = unicodedata.normalize("NFC", document_text)
    sentences = tamil_nlp.segment_sentences(norm_text)

    theme_matches = []

    for theme in HERITAGE_THEMES:
        matched_sentences = []
        theme_keywords = theme["keywords"]

        for s_idx, sent in enumerate(sentences, start=1):
            sent_norm = unicodedata.normalize("NFC", sent.lower())
            overlap = [kw for kw in theme_keywords if kw in sent_norm]
            if overlap:
                matched_sentences.append({
                    "sentence_idx": s_idx,
                    "sentence": sent.strip(),
                    "matched_keywords": overlap,
                    "relevance_score": round(len(overlap) / max(len(theme_keywords) * 0.3, 1), 2),
                })

        if matched_sentences:
            matched_sentences.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # Check if this theme for this doc has been reviewed or rejected by human
            item_key = f"THEME_{doc_id}_{theme['id']}" if doc_id else f"THEME_{theme['id']}"
            v_status = knowledge_verification.get_item_verification_status(item_key)

            theme_matches.append({
                "theme_id": theme["id"],
                "theme_name_ta": theme["name_ta"],
                "theme_name_en": theme["name_en"],
                "icon": theme["icon"],
                "color": theme["color"],
                "description_ta": theme["description_ta"],
                "description_en": theme["description_en"],
                "evidence_count": len(matched_sentences),
                "passages": [s["sentence"] for s in matched_sentences],
                "detailed_passages": matched_sentences,
                "ai_interpretation_note": "⚠️ [AI கருத்துப் பகுப்பாய்வு விளக்கம் - ஆய்வாளர் மீள்பார்வைக்குரியது (AI-Generated Interpretation)]",
                "verification_status": v_status["status"],
                "verification_badge_ta": v_status["status_label_ta"],
                "is_rejected_by_human": v_status["status"] == "REJECTED",
            })

    # Sort descending by evidence count
    theme_matches.sort(key=lambda x: x["evidence_count"], reverse=True)

    return {
        "success": True,
        "total_themes": len(theme_matches),
        "detected_themes": theme_matches,
    }
