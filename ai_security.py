# -*- coding: utf-8 -*-
"""
Tamil Heritage AI Security and Access Control.
Provides role verification and query safety checks.
"""

from typing import Dict, Tuple, Any

ROLE_PERMISSIONS: Dict[str, Dict[str, bool]] = {
    "CHIEF_EPIGRAPHIST": {
        "read_documents": True,
        "run_ocr": True,
        "edit_ocr": True,
        "approve_knowledge": True,
        "reject_knowledge": True,
        "export_preservation": True,
        "manage_system": True,
    },
    "HERITAGE_ARCHIVIST": {
        "read_documents": True,
        "run_ocr": True,
        "edit_ocr": True,
        "approve_knowledge": True,
        "reject_knowledge": False,
        "export_preservation": True,
        "manage_system": False,
    },
    "TAMIL_SCHOLAR": {
        "read_documents": True,
        "run_ocr": True,
        "edit_ocr": True,
        "approve_knowledge": False,
        "reject_knowledge": False,
        "export_preservation": True,
        "manage_system": False,
    },
    "GUEST_VIEWER": {
        "read_documents": True,
        "run_ocr": False,
        "edit_ocr": False,
        "approve_knowledge": False,
        "reject_knowledge": False,
        "export_preservation": False,
        "manage_system": False,
    },
}

ROLE_TITLES: Dict[str, str] = {
    "CHIEF_EPIGRAPHIST": "முதன்மை கல்வெட்டாய்வாளர் (Chief Epigraphist)",
    "HERITAGE_ARCHIVIST": "ஆவணக் காப்பாளர் (Heritage Archivist)",
    "TAMIL_SCHOLAR": "தமிழ் ஆய்வாளர் (Tamil Scholar)",
    "GUEST_VIEWER": "பார்வையாளர் (Guest / Student - Read-only)",
}

BLOCKLIST_SUBSTRINGS = [
    "system prompt",
    "reveal key",
    "secret token",
    "மறந்துவிடு",
    "ரகசியங்களை வெளியிடு",
]


def check_permission(role: str, action: str) -> Tuple[bool, str]:
    clean_role = (role or "GUEST_VIEWER").strip().upper()
    perms = ROLE_PERMISSIONS.get(clean_role, ROLE_PERMISSIONS["GUEST_VIEWER"])
    if perms.get(action, False):
        return True, f"அனுமதி உண்டு: {ROLE_TITLES.get(clean_role, clean_role)} -> {action}"
    return False, f"அனுமதி மறுக்கப்பட்டது: {ROLE_TITLES.get(clean_role, clean_role)} -> {action}"


def validate_query_safety(query: str) -> Dict[str, Any]:
    if not query or not str(query).strip():
        return {"safe": True, "message": "வெற்று வினா"}
    q_lower = str(query).lower()
    for token in BLOCKLIST_SUBSTRINGS:
        if token in q_lower:
            return {
                "safe": False,
                "message": "பாதுகாப்பு எச்சரிக்கை: AI வழிகாட்டுதல்களை மீறும் உள்ளீடு தடுக்கப்பட்டது (Safety Guardrail).",
            }
    return {"safe": True, "message": "உள்ளீடு பாதுகாப்பானது."}
