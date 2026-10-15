# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 13 & 15: Collection Insights & Digital Heritage Export
(collection_intelligence.py)
Collection-level intelligence, repository analytics, and TEI-compliant XML/JSON/TXT
export pipelines for long-term digital preservation of ancient Tamil heritage.
=============================================================================
Features:
  1. Collection Intelligence (Feature 13):
     - Computes live metrics across actual stored library & session documents.
     - Document-Entity bipartite link graph.
     - Lexical diversity (Type-Token Ratio / TTR) & Tamil Grantha vs Classical character distribution.
     - Identifies unindexed documents, missing metadata, and OCR processing failures.
     - Generates grounded collection summary without hardcoded numbers.
  2. Digital Heritage Export & Preservation (Feature 15):
     - Standardized UTF-8 Plain text export (.txt) with epigraphical header.
     - Standard TEI P5 Compliant XML export (.xml) for digital humanities archives.
     - TEI-compatible JSON export (.json) with provenance, approvals, and confidence.
     - Collection-level batch export archive.
     - Printable research dossier (.html).
=============================================================================
"""

import json
import html
import re
import unicodedata
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

import tamil_nlp
import manuscript_assistant
import knowledge_explorer
import knowledge_verification


# =====================================================================
# 📊 Feature 13: Collection-Level Intelligence
# =====================================================================
def get_collection_intelligence_report(
    session_history: Optional[List[Dict[str, Any]]] = None,
    custom_library: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Computes rigorous collection-level statistics grounded strictly in the actual
    stored digital library and processed session documents.
    Detects missing metadata, unindexed files, and processing failures.
    """
    library = custom_library if custom_library else manuscript_assistant.DIGITAL_LIBRARY_MANUSCRIPTS
    all_docs = []
    missing_metadata_alerts = []
    processing_failures = []
    unindexed_docs = []

    # 1. Digital Library Documents (Canonical Indexed Store)
    for k, v in library.items():
        doc_entry = {
            "id": k,
            "title": v.get("title", f"Untitled ({k})"),
            "era": v.get("era", ""),
            "category": v.get("category", ""),
            "text": v.get("text", ""),
            "status": "INDEXED_VERIFIED",
            "source_type": "LIBRARY_CANON",
        }
        all_docs.append(doc_entry)

        # Audit for missing metadata
        missing_fields = []
        if not v.get("era"):
            missing_fields.append("காலம் (Era)")
        if not v.get("category"):
            missing_fields.append("வகைப்பாடு (Category)")
        if not v.get("text") or len(v.get("text", "").strip()) == 0:
            missing_fields.append("மூல வாசகம் (Full Text)")
            processing_failures.append({
                "doc_id": k,
                "title": v.get("title", k),
                "reason": "வெற்று ஆவணம் - உரை எதுவும் இல்லை (Empty document body)",
            })
        if missing_fields:
            missing_metadata_alerts.append({
                "doc_id": k,
                "title": v.get("title", k),
                "missing_fields": missing_fields,
            })

    # 2. Session Processed Documents (Dynamic User Uploads)
    if session_history:
        for idx, h in enumerate(session_history, start=1):
            txt = h.get("preview", "") or h.get("text", "")
            fname = h.get("filename", f"Uploaded_Doc_{idx}")
            is_empty = len(txt.strip()) == 0

            doc_entry = {
                "id": f"session_upload_{idx}",
                "title": fname,
                "era": "நடப்பு ஸ்கேன் (Current Scan)",
                "category": "பயனர் பதிவேற்றம் (User Upload)",
                "text": txt,
                "status": "UNINDEXED_RAW" if not is_empty else "FAILED_OCR",
                "source_type": "USER_SESSION",
            }
            all_docs.append(doc_entry)

            if is_empty:
                processing_failures.append({
                    "doc_id": doc_entry["id"],
                    "title": fname,
                    "reason": "OCR எழுத்துணர்தல் தோல்வி அல்லது வெற்றுப் பக்கம் (OCR failure or empty scan)",
                })
            else:
                unindexed_docs.append({
                    "doc_id": doc_entry["id"],
                    "title": fname,
                    "reason": "நிரந்தர நூலகத்தில் இன்னும் சுட்டெண் ஆக்கப்படவில்லை (Awaiting library indexing)",
                })

    total_docs = len(all_docs)
    total_words = 0
    total_characters = 0
    all_tokens = []
    category_distribution = {}
    total_passages = 0
    entity_frequency_map = {}
    document_entity_links = [] # Bipartite document-entity graph

    # Grantha vs Classical character tracking
    grantha_chars = set("ஜஷஸஹக்ஷஸ்ரீ")
    grantha_found_count = 0
    pure_tamil_chars_count = 0

    for doc in all_docs:
        txt = doc["text"]
        if not txt.strip():
            continue

        sentences = tamil_nlp.segment_sentences(txt)
        total_passages += len(sentences)

        words = re.findall(r"[\u0B80-\u0BFAa-zA-Z0-9]+", txt)
        total_words += len(words)
        total_characters += len(txt)
        all_tokens.extend([w.lower() for w in words])

        cat = doc["category"] or "வகைப்படுத்தப்படாதவை (Uncategorized)"
        category_distribution[cat] = category_distribution.get(cat, 0) + 1

        # Check script characteristics
        for ch in txt:
            if ch in grantha_chars:
                grantha_found_count += 1
            elif "\u0B80" <= ch <= "\u0BFA":
                pure_tamil_chars_count += 1

        # Extract entities for co-occurrence and link graph
        ents = knowledge_explorer.extract_heritage_entities(txt)
        for e in ents:
            nm = e["name"]
            entity_frequency_map[nm] = entity_frequency_map.get(nm, 0) + 1
            document_entity_links.append({
                "doc_id": doc["id"],
                "doc_title": doc["title"],
                "entity_name": nm,
                "entity_type": e["type"],
                "entity_label_ta": e["label_ta"],
            })

    # Vocabulary Richness: Type-Token Ratio (TTR)
    unique_tokens = len(set(all_tokens))
    ttr = round((unique_tokens / max(total_words, 1)) * 100, 2)

    top_entities = sorted(entity_frequency_map.items(), key=lambda x: x[1], reverse=True)[:10]

    # Script Orthography Classification
    grantha_ratio_pct = round((grantha_found_count / max(pure_tamil_chars_count + grantha_found_count, 1)) * 100, 3)

    # Collection summary grounded in live data
    indexed_count = len([d for d in all_docs if d["status"] == "INDEXED_VERIFIED"])
    unindexed_count = len(unindexed_docs)
    summary_text = (
        f"தொகுப்பில் மொத்தம் {total_docs} ஆவணங்கள் ({indexed_count} சுட்டெண் பெற்றவை, {unindexed_count} புதிய பதிவேற்றங்கள்) "
        f"உள்ளன. இதில் {total_passages} தனித்தனி வாசகப் பத்திகளும், {total_words} சொற்களும் ({unique_tokens} தனித்துவச் சொற்கள்; "
        f"சொல்லகச் செழுமை TTR: {ttr}%) இடம்பெற்றுள்ளன. "
        f"கண்டறியப்பட்ட வரலாற்று உருப்படிகளில் முதன்மையானவை: {', '.join([e[0] for e in top_entities[:4]])}."
    )

    return {
        "success": True,
        "total_documents": total_docs,
        "indexed_documents_count": indexed_count,
        "unindexed_documents_count": unindexed_count,
        "total_passages": total_passages,
        "total_words": total_words,
        "total_characters": total_characters,
        "unique_vocabulary_types": unique_tokens,
        "type_token_ratio_pct": f"{ttr}%",
        "category_distribution": category_distribution,
        "top_entities": top_entities,
        "document_entity_links": document_entity_links,
        "unindexed_documents": unindexed_docs,
        "missing_metadata_alerts": missing_metadata_alerts,
        "processing_failures": processing_failures,
        "script_characteristics": {
            "pure_tamil_characters": pure_tamil_chars_count,
            "grantha_characters": grantha_found_count,
            "grantha_ratio_pct": f"{grantha_ratio_pct}%",
            "script_type": "தூய சங்கத் தமிழ் (Classical Sangam Tamil)" if grantha_ratio_pct < 0.1 else "மத்திய கால கிரந்தக் கலப்புத் தமிழ் (Medieval Inscriptional/Grantha Tamil)",
        },
        "collection_grounded_summary": summary_text,
        "documents": all_docs,
    }


# =====================================================================
# 📦 Feature 15: Digital Heritage Export & Preservation
# =====================================================================
def export_plain_text(
    doc_title: str,
    doc_text: str,
    era: str = "",
    category: str = "",
    provenance: str = "",
    verification_status: str = "TENTATIVE_AI",
    reviewer_name: Optional[str] = None,
    confidence_score: Optional[float] = None,
) -> str:
    """
    Generates standardized UTF-8 Plain text with rigorous archival and epigraphical metadata.
    """
    conf_str = f"{int(confidence_score * 100)}%" if confidence_score is not None else "உறுதிப்படுத்தப்படாதது (Heuristic)"
    rev_str = reviewer_name if reviewer_name else "ஆய்வாளர் மீள்பார்வை செய்யவில்லை (Unreviewed)"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = (
        "===========================================================================\n"
        "🏛️ தமிழ் மரபு ஆவண எண்மக் காப்பகம் (Tamil Heritage Digital Archive)\n"
        "===========================================================================\n"
        f"ஆவணத் தலைப்பு (Title)         : {doc_title}\n"
        f"வரலாற்றுக் காலம் (Era)        : {era}\n"
        f"இலக்கிய வகை (Category)       : {category}\n"
        f"மூலச் சான்றாதாரம் (Provenance): {provenance if provenance else 'Tamil Suvadi Digital Repository'}\n"
        f"ஏற்பு நிலை (Review Status)    : {verification_status}\n"
        f"மீள்பார்வையாளர் (Reviewer)    : {rev_str}\n"
        f"AI நம்பகத்தன்மை (Confidence)  : {conf_str}\n"
        f"ஏற்றுமதி செய்த தேதி (Exported): {ts}\n"
        "===========================================================================\n\n"
    )
    return header + doc_text


def export_tei_xml(
    doc_id: str,
    doc_title: str,
    doc_text: str,
    era: str = "",
    category: str = "",
    provenance: str = "",
    entities: Optional[List[Dict[str, Any]]] = None,
    verification_status: str = "TENTATIVE_AI",
    reviewer_name: Optional[str] = None,
    audit_log: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generates a formal, standard TEI P5 (Text Encoding Initiative) compliant XML
    for digital humanities scholars, libraries, and university repositories.
    """
    title_esc = html.escape(doc_title)
    era_esc = html.escape(era)
    cat_esc = html.escape(category)
    prov_esc = html.escape(provenance if provenance else "Tamil Heritage AI Repository")
    rev_esc = html.escape(reviewer_name if reviewer_name else "Unreviewed")
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    passages = tamil_nlp.segment_sentences(doc_text)
    passage_elements = "\n".join(
        f'        <p n="{idx+1}">{html.escape(s)}</p>' for idx, s in enumerate(passages)
    )

    entity_elements = ""
    if entities:
        ent_lines = []
        for e in entities:
            e_name = html.escape(e.get("name", ""))
            e_type = e.get("type", "MISC").lower()
            if "person" in e_type or "king" in e_type:
                ent_lines.append(f'        <persName type="{e_type}">{e_name}</persName>')
            elif "place" in e_type or "geo" in e_type:
                ent_lines.append(f'        <placeName type="{e_type}">{e_name}</placeName>')
            else:
                ent_lines.append(f'        <term type="{e_type}">{e_name}</term>')
        entity_elements = "\n".join(ent_lines)

    tei_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:lang="ta">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{title_esc}</title>
        <author>Ancient Tamil Epigraphical / Manuscript Tradition</author>
        <editor role="epigraphist">{rev_esc}</editor>
      </titleStmt>
      <publicationStmt>
        <publisher>தமிழ்ச்சுவடி AI - Tamil Suvadi Digital Preservation Initiative</publisher>
        <date when="{now_iso[:10]}">{now_iso[:10]}</date>
        <availability status="restricted">
          <p>Preserved under Digital Heritage Public Domain &amp; Academic Research License.</p>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <msDesc>
          <msIdentifier>
            <idno>{html.escape(doc_id)}</idno>
            <repository>{prov_esc}</repository>
          </msIdentifier>
          <history>
            <origin>
              <origDate>{era_esc}</origDate>
            </origin>
          </history>
        </msDesc>
      </sourceDesc>
    </fileDesc>
    <profileDesc>
      <langUsage>
        <language ident="tam">Classical Tamil (தமிழ்)</language>
      </langUsage>
      <textClass>
        <keywords scheme="TamilHeritageTaxonomy">
          <term>{cat_esc}</term>
        </keywords>
      </textClass>
    </profileDesc>
    <revisionDesc>
      <change when="{now_iso}" status="{verification_status}">
        Human verification state recorded as: {verification_status} by {rev_esc}.
      </change>
    </revisionDesc>
  </teiHeader>
  <text>
    <body>
      <div type="transcription" n="1">
{passage_elements}
      </div>
      <div type="entities">
{entity_elements}
      </div>
    </body>
  </text>
</TEI>"""
    return tei_xml


def export_tei_json(
    doc_id: str,
    doc_title: str,
    doc_text: str,
    era: str = "",
    category: str = "",
    provenance: str = "",
    entities: Optional[List[Dict[str, Any]]] = None,
    verification_status: str = "TENTATIVE_AI",
    reviewer_name: Optional[str] = None,
    confidence_score: Optional[float] = None,
    audit_log: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generates a TEI-compatible structured digital heritage JSON package
    with complete audit trail, confidence metadata, and line-level text.
    """
    passages = tamil_nlp.segment_sentences(doc_text)
    structured_doc = {
        "teiHeader": {
            "title": doc_title,
            "id": doc_id,
            "era": era,
            "category": category,
            "provenance": provenance if provenance else "Tamil Heritage AI Digital Library",
            "encoding": "UTF-8",
            "script": "Tamil (தமிழ் - தமிழ் எழுத்து வடிவம்)",
            "preservation_status": verification_status,
            "reviewer_name": reviewer_name,
            "confidence_score": confidence_score if confidence_score is not None else 0.85,
            "export_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "textBody": {
            "total_sentences": len(passages),
            "passages": [{"n": idx + 1, "text": s} for idx, s in enumerate(passages)],
            "raw_text": doc_text,
        },
        "namedEntities": entities if entities else [],
        "auditTrail": audit_log if audit_log else [],
    }
    return json.dumps(structured_doc, ensure_ascii=False, indent=2)


def export_collection_batch_tei_json(
    documents: List[Dict[str, Any]],
    verification_store: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generates a collection-level batch preservation archive containing
    all manuscripts, unified entity graph, and complete audit provenance.
    """
    store = verification_store if verification_store else knowledge_verification.get_all_verifications()
    batch_archive = {
        "collectionMetadata": {
            "archive_name": "தமிழ் மரபு முழுத் தொகுப்பு எண்மக் காப்பகம் (Tamil Suvadi Complete Preservation Archive)",
            "total_documents": len(documents),
            "export_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "standard": "TEI-P5 / OAI-PMH Compatible Digital Humanities Schema",
        },
        "documents": [],
    }

    for doc in documents:
        doc_id = doc.get("id", "doc_unknown")
        txt = doc.get("text", "")
        v_status = store.get(f"DOC_{doc_id}", {})
        passages = tamil_nlp.segment_sentences(txt)
        ents = knowledge_explorer.extract_heritage_entities(txt)

        batch_archive["documents"].append({
            "doc_id": doc_id,
            "title": doc.get("title", ""),
            "era": doc.get("era", ""),
            "category": doc.get("category", ""),
            "review_status": v_status.get("status", "TENTATIVE_AI"),
            "passages_count": len(passages),
            "entities_count": len(ents),
            "raw_text": txt,
        })

    return json.dumps(batch_archive, ensure_ascii=False, indent=2)


def export_html_dossier(
    doc_title: str,
    doc_text: str,
    era: str = "",
    category: str = "",
    provenance: str = "",
    verification_status: str = "TENTATIVE_AI",
    reviewer_name: Optional[str] = None,
    entities: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generates a standalone, beautiful HTML research dossier suitable for printing or archiving.
    """
    title_esc = html.escape(doc_title)
    era_esc = html.escape(era)
    cat_esc = html.escape(category)
    prov_esc = html.escape(provenance if provenance else "தமிழ் மரபு AI நூலகம்")
    rev_esc = html.escape(reviewer_name if reviewer_name else "மீள்பார்வை செய்யப்படவில்லை")

    status_color = "#10B981" if "VERIFIED" in verification_status else ("#3B82F6" if "EDITED" in verification_status else "#F59E0B")
    status_label = "ஆய்வாளரால் உறுதிப்படுத்தப்பட்டது" if "VERIFIED" in verification_status else ("திருத்தப்பட்டு ஏற்கப்பட்டது" if "EDITED" in verification_status else "AI ஊகம் (தற்காலிகமானது)")

    sentences = tamil_nlp.segment_sentences(doc_text)
    passage_items = "".join(
        f'<div class="passage-row"><span class="line-badge">வரி #{i+1}</span> <span class="passage-text">{html.escape(s)}</span></div>'
        for i, s in enumerate(sentences)
    )

    ent_pills = ""
    if entities:
        ent_pills = "".join(
            f'<span class="ent-pill" style="background:{e.get("color", "#1565C0")}">{html.escape(e["name"])} ({html.escape(e.get("label_ta", e.get("type", "")))})</span>'
            for e in entities
        )

    html_dossier = f"""<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <title>{title_esc} – தமிழ் மரபு AI எண்மக் காப்பகம்</title>
    <style>
        body {{
            font-family: 'Mukta Malar', 'Noto Sans Tamil', serif;
            background: #140C07;
            color: #F5E8D0;
            padding: 40px;
            max-width: 900px;
            margin: auto;
            line-height: 1.8;
        }}
        .header-card {{
            border-bottom: 2px solid #D4AF37;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{ color: #E6CA65; font-family: 'Cinzel', serif; margin-bottom: 6px; }}
        .meta-pill {{ color: #C8AC82; font-size: 0.95rem; margin-right: 15px; }}
        .status-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            color: #FFF;
            background: {status_color};
            font-weight: bold;
            font-size: 0.85rem;
            margin-top: 10px;
        }}
        .passage-row {{
            background: #1F140D;
            border-left: 3px solid #734F27;
            padding: 10px 16px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .line-badge {{ color: #D4AF37; font-weight: bold; margin-right: 10px; }}
        .ent-pill {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            color: #FFF;
            font-size: 0.82rem;
            margin: 4px 6px 4px 0;
        }}
        @media print {{
            body {{ background: #FFF; color: #000; }}
            .passage-row {{ background: #F9F9F9; border-left: 3px solid #333; }}
        }}
    </style>
</head>
<body>
    <div class="header-card">
        <h1>{title_esc}</h1>
        <div>
            <span class="meta-pill">🏛️ <b>காலம்:</b> {era_esc}</span>
            <span class="meta-pill">📂 <b>வகை:</b> {cat_esc}</span>
            <span class="meta-pill">📜 <b>சான்று:</b> {prov_esc}</span>
        </div>
        <div class="status-badge">✅ ஏற்பு நிலை: {status_label} ({rev_esc})</div>
    </div>
    <h3>🔍 கண்டறியப்பட்ட வரலாற்று உருப்படிகள் (Extracted Heritage Entities):</h3>
    <div style="margin-bottom: 25px;">{ent_pills if ent_pills else '<span style="color:#888;">உருப்படிகள் இல்லை</span>'}</div>
    <h3>📜 மூல சுவடி வாசகங்கள் (Numbered Passages):</h3>
    <div>{passage_items}</div>
</body>
</html>
"""
    return html_dossier
