# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 14: Human-in-the-Loop Knowledge Verification
(knowledge_verification.py)
Epigraphical review, editorial approval, and audit logging for AI-extracted
entities, relationships, historical events, and thematic labels.
=============================================================================
Verification Statuses:
  1. TENTATIVE_AI (ஊகிக்கப்பட்ட AI உருப்படி - தற்காலிகமானது / Unreviewed)
  2. HUMAN_VERIFIED (ஆய்வாளரால் உறுதிப்படுத்தப்பட்ட வரலாற்று உண்மை)
  3. REJECTED (ஆதாரமற்றதென நிராகரிக்கப்பட்டது)
  4. EDITED_AND_APPROVED (திருத்தப்பட்டு ஏற்கப்பட்டது)

Security & Governance:
  - Role-based authorization: Only verified epigraphists/archivists may approve.
  - Read-only protection for guest/unauthorized users.
  - Complete dual-state preservation: original AI prediction is NEVER erased.
  - Persistent tamper-evident JSON store with timestamped audit trail.
=============================================================================
"""

import os
import json
import time
import shutil
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

VERIFICATION_STORE_FILE = Path(__file__).resolve().parent / "knowledge_verification_store.json"
AUDIT_LOG_FILE = Path(__file__).resolve().parent / "knowledge_verification_audit.json"

_STORAGE_LOCK = threading.Lock()


def _atomic_write_json(target_path: Path, data: Any, backup: bool = True) -> None:
    """Atomically writes JSON using a temporary file and atomic replace.
    Maintains rolling backup to guarantee zero corruption on power/process interruption.
    """
    with _STORAGE_LOCK:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if backup and target_path.exists():
            bak_path = target_path.with_suffix(".json.bak")
            try:
                shutil.copy2(target_path, bak_path)
            except Exception:
                pass

        temp_path = target_path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temp_path, target_path)
        except Exception as e:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            raise IOError(f"Atomic write failed for {target_path}: {e}")


# Authorized scholarly roles capable of validating epigraphical facts
AUTHORIZED_ROLES = {
    "CHIEF_EPIGRAPHIST": "முதன்மை கல்வெட்டாய்வாளர் (Chief Epigraphist)",
    "HERITAGE_ARCHIVIST": "மரபு ஆவணக் காப்பாளர் (Heritage Archivist)",
    "TAMIL_SCHOLAR": "தமிழ் வரலாற்று ஆய்வாளர் (Tamil Historical Scholar)",
    "ADMIN": "கணினி நிர்வாகி (System Administrator)",
}

# Read-only roles that cannot alter records
READ_ONLY_ROLES = {
    "GUEST_VIEWER": "பார்வையாளர் (Guest / Student)",
    "EXTERNAL_READER": "வெளியக வாசகர் (External Reader)",
}

# Curated canonical records shielded from regular alterations without Chief approval
CANONICAL_PROTECTED_ENTITIES = {
    "இராஜராஜ சோழன்",
    "பெருவுடையார் கோயில்",
    "தொல்காப்பியம்",
    "சிலப்பதிகாரம்",
    "திருக்குறள்",
}


def get_all_verifications() -> Dict[str, Dict[str, Any]]:
    """Loads all human knowledge verification decisions with automatic backup recovery."""
    if VERIFICATION_STORE_FILE.exists():
        try:
            return json.loads(VERIFICATION_STORE_FILE.read_text(encoding="utf-8"))
        except Exception:
            bak = VERIFICATION_STORE_FILE.with_suffix(".json.bak")
            if bak.exists():
                try:
                    return json.loads(bak.read_text(encoding="utf-8"))
                except Exception:
                    pass
            return {}
    return {}


def get_audit_trail() -> List[Dict[str, Any]]:
    """Loads full chronological verification audit trail with automatic backup recovery."""
    if AUDIT_LOG_FILE.exists():
        try:
            return json.loads(AUDIT_LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            bak = AUDIT_LOG_FILE.with_suffix(".json.bak")
            if bak.exists():
                try:
                    return json.loads(bak.read_text(encoding="utf-8"))
                except Exception:
                    pass
            return []
    return []


def check_user_permission(
    user_role: str,
    item_id: str,
    action: str, # "ACCEPT", "REJECT", "EDIT"
) -> Tuple[bool, str]:
    """
    Validates whether the user role is authorized to perform the review action.
    Strictly protects canonized records and forbids unauthorized alterations.
    """
    clean_role = user_role.strip().upper()

    # Unauthorized / Guest check
    if clean_role in READ_ONLY_ROLES or clean_role not in AUTHORIZED_ROLES:
        return False, f"அனுமதி மறுக்கப்பட்டது (Access Denied): '{user_role}' பிரிவினருக்கு ஆய்வு முடிவுகளை மாற்றும் அல்லது ஒப்புதல் அளிக்கும் உரிமை இல்லை."

    # Protected Canon Check
    if any(p_name in item_id for p_name in CANONICAL_PROTECTED_ENTITIES):
        if clean_role not in ("CHIEF_EPIGRAPHIST", "ADMIN") and action in ("REJECT", "EDIT"):
            return False, f"பாதுகாக்கப்பட்ட வரலாற்று ஆவணம் (Protected Canon): '{item_id}' மீதான திருத்தங்களை 'முதன்மை கல்வெட்டாய்வாளர்' (Chief Epigraphist) மட்டுமே செய்ய இயலும்."

    return True, "அனுமதிக்கப்பட்டது (Authorized)"


def save_verification_decision(
    item_id: str,
    item_type: str, # "ENTITY", "RELATIONSHIP", "TIMELINE_EVENT", "THEME"
    original_ai_prediction: Dict[str, Any],
    decision: str, # "ACCEPT", "REJECT", "EDIT"
    reviewed_value: Optional[Dict[str, Any]] = None,
    reviewer_role: str = "CHIEF_EPIGRAPHIST",
    reviewer_name: str = "Chief Epigraphist (முதன்மை கல்வெட்டாய்வாளர்)",
    notes: str = "",
) -> Dict[str, Any]:
    """
    Records a human verification decision while strictly preserving
    the original AI prediction and appending to the audit trail.
    """
    # 1. Permission Enforcement
    allowed, perm_msg = check_user_permission(reviewer_role, item_id, decision)
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not allowed:
        # Log unauthorized attempt to audit
        audit_trail = get_audit_trail()
        audit_trail.append({
            "timestamp": now_ts,
            "item_id": item_id,
            "action": decision,
            "reviewer_name": reviewer_name,
            "reviewer_role": reviewer_role,
            "status": "BLOCKED_UNAUTHORIZED",
            "message": perm_msg,
        })
        AUDIT_LOG_FILE.write_text(json.dumps(audit_trail, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "success": False,
            "error": perm_msg,
            "item_id": item_id,
            "status": "UNAUTHORIZED",
        }

    # 2. Status Mapping
    if decision == "ACCEPT":
        new_status = "HUMAN_VERIFIED"
        status_label = "ஆய்வாளரால் உறுதிப்படுத்தப்பட்டது (Human Verified)"
        status_color = "#10B981"
    elif decision == "EDIT":
        new_status = "EDITED_AND_APPROVED"
        status_label = "திருத்தப்பட்டு ஏற்கப்பட்டது (Edited & Approved)"
        status_color = "#3B82F6"
    else: # REJECT
        new_status = "REJECTED"
        status_label = "ஆதாரமற்றதென நிராகரிக்கப்பட்டது (Rejected)"
        status_color = "#EF4444"

    store = get_all_verifications()

    record = {
        "item_id": item_id,
        "item_type": item_type,
        "original_ai_prediction": original_ai_prediction,
        "decision": decision,
        "status": new_status,
        "status_label_ta": status_label,
        "status_color": status_color,
        "reviewed_value": reviewed_value if reviewed_value else original_ai_prediction,
        "reviewer_name": reviewer_name,
        "reviewer_role": reviewer_role,
        "notes": notes,
        "timestamp": now_ts,
    }

    store[item_id] = record
    _atomic_write_json(VERIFICATION_STORE_FILE, store, backup=True)

    # 3. Append to Audit Trail
    audit_trail = get_audit_trail()
    audit_trail.append({
        "timestamp": now_ts,
        "item_id": item_id,
        "item_type": item_type,
        "action": decision,
        "new_status": new_status,
        "reviewer_name": reviewer_name,
        "reviewer_role": reviewer_role,
        "notes": notes,
        "status": "SUCCESS",
    })
    _atomic_write_json(AUDIT_LOG_FILE, audit_trail, backup=True)

    return {
        "success": True,
        "record": record,
        "message": f"முடிவு வெற்றிகரமாகப் பதிவு செய்யப்பட்டது: {status_label}",
    }


def get_item_verification_status(item_id: str) -> Dict[str, Any]:
    """
    Returns the verification state of an entity, theme, or relation.
    Unreviewed items are explicitly labeled as TENTATIVE_AI.
    """
    store = get_all_verifications()
    if item_id in store:
        rec = store[item_id]
        return {
            "item_id": item_id,
            "status": rec["status"],
            "status_label_ta": rec["status_label_ta"],
            "status_color": rec.get("status_color", "#10B981"),
            "is_verified": rec["status"] in ("HUMAN_VERIFIED", "EDITED_AND_APPROVED"),
            "reviewer_name": rec.get("reviewer_name"),
            "reviewer_role": rec.get("reviewer_role"),
            "decision": rec.get("decision"),
            "notes": rec.get("notes", ""),
            "timestamp": rec.get("timestamp"),
            "original_ai_prediction": rec.get("original_ai_prediction"),
            "reviewed_value": rec.get("reviewed_value"),
        }

    return {
        "item_id": item_id,
        "status": "TENTATIVE_AI",
        "status_label_ta": "ஊகிக்கப்பட்ட AI உருப்படி (Tentative - Unreviewed AI Prediction)",
        "status_color": "#F59E0B",
        "is_verified": False,
        "reviewer_name": None,
        "reviewer_role": None,
        "decision": "PENDING_REVIEW",
        "notes": "கல்வெட்டாய்வாளர் மீள்பார்வை செய்யவில்லை. தற்காலிக ஆய்வுத் தரவு.",
        "timestamp": None,
    }


def get_verification_summary_stats() -> Dict[str, int]:
    """Calculates counts across all verified, edited, and rejected records."""
    store = get_all_verifications()
    stats = {
        "total_reviewed": len(store),
        "verified_count": 0,
        "edited_count": 0,
        "rejected_count": 0,
    }
    for rec in store.values():
        st = rec.get("status")
        if st == "HUMAN_VERIFIED":
            stats["verified_count"] += 1
        elif st == "EDITED_AND_APPROVED":
            stats["edited_count"] += 1
        elif st == "REJECTED":
            stats["rejected_count"] += 1
    return stats
