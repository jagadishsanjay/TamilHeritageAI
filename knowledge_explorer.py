# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 2: Tamil Knowledge Explorer (knowledge_explorer.py)
AI-Powered Heritage Knowledge Graph & Entity-Relationship Explorer
=============================================================================
Features:
  1. Heritage Named Entity Recognition (NER) for Tamil Manuscripts:
     - People / Authors / Kings (நபர்கள் / மன்னர்கள் / ஆசிரியர்கள்)
     - Places & Geography (இடங்கள் / ஆறுகள் / நகரங்கள்)
     - Literary Works & Treatises (இலக்கியங்கள் / நூல்கள் / சுவடிகள்)
     - Historical Eras / Dynasties (வரலாற்று காலங்கள் / மரபுகள்)
     - Cultural & Linguistic Concepts (கருத்துக்கள் / இலக்கணக் கூறுகள்)
  2. Grounded Relationship Identification with Evidence:
     - Source-Supported Direct Evidence (ஆவணச் சான்றுடைய நேரடித் தொடர்பு)
     - Contextual Heritage Inference (சூழல் பின்னணித் தொடர்பு)
  3. Interactive SVG / HTML5 Knowledge Graph Visualization.
  4. Entity Drilldown: Connected nodes, relationship badges, supporting passages.
  5. Structured JSON Export for architectural compatibility.
=============================================================================
"""

import re
import html
import unicodedata
from typing import Dict, List, Any, Optional, Set, Tuple

import tamil_nlp

# =====================================================================
# 📚 Curated Tamil Heritage Knowledge Ontology & Patterns
# =====================================================================
KNOWN_HERITAGE_ENTITIES = {
    # People (PERSON)
    "இராஜராஜ சோழன்": {"type": "PERSON", "label_ta": "மன்னர் (King/Emperor)", "color": "#E65100"},
    "முதலாம் இராஜராஜ சோழன்": {"type": "PERSON", "label_ta": "மன்னர் (King/Emperor)", "color": "#E65100"},
    "தொல்காப்பியன்": {"type": "PERSON", "label_ta": "இலக்கண ஆசிரியர் (Grammarian)", "color": "#BF360C"},
    "திருவள்ளுவர்": {"type": "PERSON", "label_ta": "புலவர் / ஆசிரியர் (Philosopher)", "color": "#BF360C"},
    "இளங்கோவடிகள்": {"type": "PERSON", "label_ta": "காப்பியப் புலவர் (Epic Author)", "color": "#BF360C"},
    "குஞ்சரமல்லன்": {"type": "PERSON", "label_ta": "தலைமைத் தச்சர் (Chief Architect)", "color": "#8D6E63"},
    "செங்குட்டுவன்": {"type": "PERSON", "label_ta": "சேர மன்னன் (Chera King)", "color": "#E65100"},
    "கோவலன்": {"type": "PERSON", "label_ta": "காப்பியத் தலைவர் (Protagonist)", "color": "#F57C00"},
    "கண்ணகி": {"type": "PERSON", "label_ta": "காப்பியத் தலைவி (Heroine)", "color": "#D84315"},
    "மாதவி": {"type": "PERSON", "label_ta": "நாட்டிய நங்கை (Dancer)", "color": "#AD1457"},
    "பரிமேலழகர்": {"type": "PERSON", "label_ta": "உரையாசிரியர் (Commentator)", "color": "#6A1B9A"},

    # Places & Geography (LOCATION)
    "தஞ்சாவூர்": {"type": "LOCATION", "label_ta": "தலைநகரம் (Capital City)", "color": "#1B5E20"},
    "தஞ்சை": {"type": "LOCATION", "label_ta": "வரலாற்று நகரம் (Historic City)", "color": "#1B5E20"},
    "மதுரை": {"type": "LOCATION", "label_ta": "பாண்டியர் தலைநகரம் (Pandya Capital)", "color": "#2E7D32"},
    "பூம்புகார்": {"type": "LOCATION", "label_ta": "சோழர் துறைமுகம் (Chola Port City)", "color": "#00695C"},
    "காவிரிப்பூம்பட்டினம்": {"type": "LOCATION", "label_ta": "துறைமுக நகரம் (Port City)", "color": "#00695C"},
    "காவிரி": {"type": "LOCATION", "label_ta": "புனித நதி (Cauvery River)", "color": "#00838F"},
    "வைகை": {"type": "LOCATION", "label_ta": "நதி (Vaigai River)", "color": "#00838F"},
    "வடவேங்கடம்": {"type": "LOCATION", "label_ta": "வடக்கு எல்லை (Northern Border)", "color": "#33691E"},
    "தென்குமரி": {"type": "LOCATION", "label_ta": "தெற்கு எல்லை (Southern Border)", "color": "#33691E"},

    # Works & Treatises (WORK)
    "தொல்காப்பியம்": {"type": "WORK", "label_ta": "இலக்கண நூல் (Grammar Treatise)", "color": "#0D47A1"},
    "திருக்குறள்": {"type": "WORK", "label_ta": "நீதி இலக்கியம் (Universal Ethics)", "color": "#1565C0"},
    "சிலப்பதிகாரம்": {"type": "WORK", "label_ta": "தமிழ்க்காப்பியம் (Classical Epic)", "color": "#1976D2"},
    "தஞ்சைப் பெரிய கோயில்": {"type": "WORK", "label_ta": "கட்டடக் கலை நினைவுச் சின்னம் (Temple Monument)", "color": "#004D40"},
    "இராஜராஜேஸ்வரம்": {"type": "WORK", "label_ta": "கோயில் கல்வெட்டுப் பெயர் (Temple Name)", "color": "#004D40"},
    "கானல்வரி": {"type": "WORK", "label_ta": "இசைப்பாடல் பகுதி (Musical Verse)", "color": "#0277BD"},

    # Concepts & Linguistic Units (CONCEPT)
    "எழுத்து": {"type": "CONCEPT", "label_ta": "இலக்கண அதிகாரம் (Phonology)", "color": "#4A148C"},
    "சொல்": {"type": "CONCEPT", "label_ta": "இலக்கண அதிகாரம் (Morphology)", "color": "#4A148C"},
    "பொருள்": {"type": "CONCEPT", "label_ta": "இலக்கண அதிகாரம் (Poetics/Life)", "color": "#4A148C"},
    "அறத்துப்பால்": {"type": "CONCEPT", "label_ta": "அறப் பிரிவு (Virtue Section)", "color": "#6A1B9A"},
    "பொருட்பால்": {"type": "CONCEPT", "label_ta": "பொருள் பிரிவு (Wealth/Politics)", "color": "#6A1B9A"},
    "காமத்துப்பால்": {"type": "CONCEPT", "label_ta": "இன்பப் பிரிவு (Love Section)", "color": "#6A1B9A"},
    "பெருவுடையார்": {"type": "CONCEPT", "label_ta": "மூலவர் தெய்வம் (Deity)", "color": "#C2185B"},
    "தட்சிண மேரு": {"type": "CONCEPT", "label_ta": "விமானம் (Temple Vimana)", "color": "#C2185B"},

    # Eras & Dynasties (ERA)
    "சங்க காலம்": {"type": "ERA", "label_ta": "செம்மொழி காலம் (Sangam Era)", "color": "#37474F"},
    "சோழர்கள்": {"type": "ERA", "label_ta": "சோழப் பேரரசு (Chola Empire)", "color": "#455A64"},
    "கி.பி. 1010": {"type": "ERA", "label_ta": "கல்வெட்டு ஆண்டு (Inscription Year)", "color": "#263238"},
}

KNOWN_PREDICATES = [
    {"pattern": r"கட்டினார்|கட்டி முடித்தார்|கட்டிய", "rel": "கட்டியது (BUILT)", "inverse": "கட்டப்பட்டது (BUILT_BY)"},
    {"pattern": r"இயற்றினார்|இயற்றிய|தொகுத்தோனே|அருளிய", "rel": "இயற்றியவர் (AUTHORED)", "inverse": "இயற்றப்பட்டது (AUTHORED_BY)"},
    {"pattern": r"அமைந்துள்ள|அமைந்த|உள்ளது|தலைநகரம்|நகரில்", "rel": "அமைந்துள்ள இடம் (LOCATED_IN)", "inverse": "கொண்டுள்ளது (CONTAINS)"},
    {"pattern": r"ஆட்சி|மன்னன்|ஆண்ட", "rel": "ஆட்சி செய்தது (RULED)", "inverse": "ஆளப்பட்டது (RULED_BY)"},
    {"pattern": r"உரை எழுதிய|உரையாசிரியர்|உரை", "rel": "உரை எழுதியவர் (COMMENTED_BY)", "inverse": "உரை நூல் (COMMENTARY_OF)"},
    {"pattern": r"அதிகாரங்களைக் கொண்டுள்ளது|பகுக்கப்பட்டு|கொண்டுள்ளது", "rel": "கொண்டுள்ள பகுதி (CONTAINS_PART)", "inverse": "உட்பிரிவு (PART_OF)"},
    {"pattern": r"தம்பியான|மகன்|மகள்", "rel": "குடும்ப உறவு (KINSHIP)", "inverse": "உறவு (RELATED)"},
]


# =====================================================================
# 🔍 Heritage Entity Extraction
# =====================================================================
def extract_heritage_entities(document_text: str) -> List[Dict[str, Any]]:
    """
    Extracts known and structurally discovered entities from manuscript text.
    Preserves exact references and line occurrences.
    """
    if not document_text:
        return []

    norm_text = unicodedata.normalize("NFC", document_text)
    sentences = tamil_nlp.segment_sentences(norm_text)
    extracted_entities = {}

    for name, meta in KNOWN_HERITAGE_ENTITIES.items():
        occurrences = []
        for s_idx, sent in enumerate(sentences, start=1):
            if name in sent:
                occurrences.append(s_idx)

        if occurrences:
            extracted_entities[name] = {
                "id": name,
                "name": name,
                "type": meta["type"],
                "label_ta": meta["label_ta"],
                "color": meta["color"],
                "frequency": len(occurrences),
                "sentence_indices": occurrences,
            }

    # Dynamic extraction for year / king / title markers
    # e.g., கி.பி. 1010, கி.மு. 300
    year_matches = re.finditer(r"(கி\.பி\.|கி\.மு\.)\s*\d{2,4}", norm_text)
    for m in year_matches:
        yr = m.group(0).strip()
        if yr not in extracted_entities:
            occs = [i for i, s in enumerate(sentences, 1) if yr in s]
            extracted_entities[yr] = {
                "id": yr,
                "name": yr,
                "type": "ERA",
                "label_ta": "காலக் குறிப்பு (Year/Era)",
                "color": "#263238",
                "frequency": len(occs),
                "sentence_indices": occs,
            }

    # Filter out redundant substrings when a more specific longer entity is present
    filtered_entities = {}
    sorted_names = sorted(extracted_entities.keys(), key=len, reverse=True)
    kept_names = []
    for nm in sorted_names:
        is_sub = any(nm in longer and nm != longer for longer in kept_names if extracted_entities[nm]["type"] == extracted_entities[longer]["type"])
        if not is_sub:
            kept_names.append(nm)
            filtered_entities[nm] = extracted_entities[nm]

    return list(filtered_entities.values())


# =====================================================================
# 🔗 Relationship Identification with Evidence
# =====================================================================
def extract_heritage_relationships(
    document_text: str,
    entities: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Identifies relationships between co-occurring entities within sentences
    and marks whether each relationship is directly source-supported or contextual.
    """
    if not document_text or not entities:
        return []

    norm_text = unicodedata.normalize("NFC", document_text)
    sentences = tamil_nlp.segment_sentences(norm_text)
    relationships = []
    seen_pairs: Set[Tuple[str, str, str]] = set()

    # Map entities by sentence
    ent_by_sent: Dict[int, List[Dict[str, Any]]] = {}
    for ent in entities:
        for s_idx in ent["sentence_indices"]:
            ent_by_sent.setdefault(s_idx, []).append(ent)

    # 1. Direct Intra-Sentence Relationship Extraction (Source-Supported)
    for s_idx, sent_entities in ent_by_sent.items():
        if len(sent_entities) < 2:
            continue

        sent_text = sentences[s_idx - 1] if s_idx <= len(sentences) else ""

        # Test pairs
        for i in range(len(sent_entities)):
            for j in range(i + 1, len(sent_entities)):
                e1 = sent_entities[i]
                e2 = sent_entities[j]

                # Check predicate patterns
                rel_label = "தொடர்புடையது (RELATED)"
                for pred in KNOWN_PREDICATES:
                    if re.search(pred["pattern"], sent_text):
                        # Determine direction
                        if e1["type"] in ("PERSON", "ERA") and e2["type"] in ("WORK", "LOCATION", "CONCEPT"):
                            rel_label = pred["rel"]
                        elif e2["type"] in ("PERSON", "ERA") and e1["type"] in ("WORK", "LOCATION", "CONCEPT"):
                            rel_label = pred["inverse"]
                        else:
                            rel_label = pred["rel"]
                        break

                pair_key = (e1["id"], e2["id"], rel_label)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    relationships.append({
                        "source": e1["id"],
                        "target": e2["id"],
                        "source_type": e1["type"],
                        "target_type": e2["type"],
                        "relationship": rel_label,
                        "evidence_level": "உறுதியான ஆவணச் சான்று (Source-Supported Direct Evidence)",
                        "is_direct_evidence": True,
                        "sentence_number": s_idx,
                        "supporting_passage": sent_text,
                    })

    # 2. Contextual Document-Level Links (Contextual Inference)
    # If two prominent entities exist in the same document but not in the same sentence
    if len(entities) >= 2 and len(relationships) < 3:
        for i in range(min(4, len(entities))):
            for j in range(i + 1, min(4, len(entities))):
                e1 = entities[i]
                e2 = entities[j]
                pair_key = (e1["id"], e2["id"], "ஒரே ஆவணத்தில் குறிப்பிடப்பட்டுள்ளது (CO_OCCURS)")
                if pair_key not in seen_pairs and not any(
                    (r["source"] == e1["id"] and r["target"] == e2["id"]) or (r["source"] == e2["id"] and r["target"] == e1["id"])
                    for r in relationships
                ):
                    seen_pairs.add(pair_key)
                    relationships.append({
                        "source": e1["id"],
                        "target": e2["id"],
                        "source_type": e1["type"],
                        "target_type": e2["type"],
                        "relationship": "சுவடிப் பின்னணித் தொடர்பு (Document Context)",
                        "evidence_level": "சூழல் அறிவு (Contextual Heritage Inference)",
                        "is_direct_evidence": False,
                        "sentence_number": e1["sentence_indices"][0] if e1["sentence_indices"] else 1,
                        "supporting_passage": f"இரு கூறுகளும் '{document_text[:80]}...' எனும் சுவடியில் இடம்பெற்றுள்ளன.",
                    })

    return relationships


# =====================================================================
# 🕸️ Interactive Visual Knowledge Graph Builder (HTML5 / SVG)
# =====================================================================
def generate_interactive_graph_html(
    entities: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
    width: int = 700,
    height: int = 440,
) -> str:
    """
    Renders an interactive, responsive SVG graph with nodes, labels,
    curved connector edges, and tooltip inspection cards.
    """
    if not entities:
        return (
            "<div style='padding:20px; text-align:center; color:#888; background:#1e1e24; border-radius:8px;'>"
            "ஆவணத்தில் அறிவு வரைபடத்திற்கான கூறுகள் கண்டறியப்படவில்லை (No graph entities found in current text)."
            "</div>"
        )

    # Compute node coordinates in a circular/elliptical layout
    import math
    n = len(entities)
    cx, cy = width / 2, height / 2
    rx, ry = min(width, height) * 0.38, min(width, height) * 0.34

    coords = {}
    for idx, ent in enumerate(entities):
        angle = (2 * math.pi * idx) / max(n, 1) - (math.pi / 2)
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        coords[ent["id"]] = (round(x, 1), round(y, 1))

    # Build SVG edges
    edge_svgs = []
    for rel in relationships:
        s_id = rel["source"]
        t_id = rel["target"]
        if s_id in coords and t_id in coords:
            x1, y1 = coords[s_id]
            x2, y2 = coords[t_id]
            # Dash style: solid for direct evidence, dashed for contextual inference
            stroke_dash = "none" if rel.get("is_direct_evidence") else "5,5"
            stroke_color = "#FFB300" if rel.get("is_direct_evidence") else "#78909C"
            stroke_width = "2.5" if rel.get("is_direct_evidence") else "1.5"

            # Midpoint for label
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            rel_text = html.escape(rel["relationship"].split("(")[0].strip())

            edge_svgs.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" '
                f'stroke-width="{stroke_width}" stroke-dasharray="{stroke_dash}" stroke-opacity="0.8"/>\n'
                f'<text x="{mx}" y="{my - 5}" fill="#E0E0E0" font-size="10" font-family="sans-serif" '
                f'text-anchor="middle" background="#121212">{rel_text}</text>'
            )

    # Build SVG nodes
    node_svgs = []
    for ent in entities:
        x, y = coords[ent["id"]]
        color = ent.get("color", "#1565C0")
        name = html.escape(ent["name"])
        lbl = html.escape(ent.get("label_ta", ent["type"]))
        radius = 24 if ent.get("frequency", 1) > 1 else 20

        node_svgs.append(
            f'<g class="graph-node" style="cursor:pointer;">\n'
            f'  <circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" stroke="#FFFFFF" stroke-width="2" />\n'
            f'  <text x="{x}" y="{y + 36}" fill="#FFFFFF" font-size="12" font-weight="bold" font-family="sans-serif" text-anchor="middle">{name}</text>\n'
            f'  <text x="{x}" y="{y + 50}" fill="#B0BEC5" font-size="9" font-family="sans-serif" text-anchor="middle">{lbl}</text>\n'
            f'  <title>{name} ({lbl})&#10;குறிப்பிடப்பட்ட எண்ணிக்கை: {ent.get("frequency", 1)}</title>\n'
            f'</g>'
        )

    svg_content = f"""
    <div style="background: linear-gradient(135deg, #181924 0%, #1e2230 100%); border: 1px solid #33394d; border-radius: 12px; padding: 15px; overflow-x: auto; text-align: center;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 11px; color: #BBB;">
        <span>🟡 <b>தடித்த கோடு:</b> நேரடி ஆவணச் சான்று (Source-Supported)</span>
        <span>⚪ <b>புள்ளி கோடு:</b> சூழல் அறிவுத் தொடர்பு (Contextual Inference)</span>
        <span>🔵 <b>மொத்தக் கூறுகள்:</b> {len(entities)} | <b>தொடர்புகள்:</b> {len(relationships)}</span>
      </div>
      <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="max-width: 100%; height: auto;">
        <!-- Edges -->
        {''.join(edge_svgs)}
        <!-- Nodes -->
        {''.join(node_svgs)}
      </svg>
    </div>
    """
    return svg_content


# =====================================================================
# 📊 High-Level Explorer Controller
# =====================================================================
def run_knowledge_explorer(document_text: str) -> Dict[str, Any]:
    """Runs end-to-end entity and relationship extraction for the knowledge explorer."""
    entities = extract_heritage_entities(document_text)
    relationships = extract_heritage_relationships(document_text, entities)
    graph_html = generate_interactive_graph_html(entities, relationships)

    return {
        "success": True,
        "total_entities": len(entities),
        "total_relationships": len(relationships),
        "entities": entities,
        "relationships": relationships,
        "graph_html": graph_html,
        "structured_graph": {
            "nodes": [{"id": e["id"], "type": e["type"], "label": e["name"]} for e in entities],
            "edges": [{"source": r["source"], "target": r["target"], "rel": r["relationship"]} for r in relationships],
        },
    }


# Standard alias for compatibility
def build_document_knowledge_graph(document_text: str, document_title: str = "") -> Dict[str, Any]:
    return run_knowledge_explorer(document_text)
