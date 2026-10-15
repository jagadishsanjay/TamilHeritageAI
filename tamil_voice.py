"""
தமிழ்ச்சுவடி AI – Smart Tamil Voice Engine (tamil_voice.py)
===========================================================
High-fidelity Text-to-Speech (TTS) engine for ancient Tamil manuscripts, books,
and heritage documents.

Key Capabilities:
 1. Reads actual Tamil OCR output or user-edited text aloud using authentic Tamil voices.
 2. Chunking engine for long historical documents preserving sentence order and Tamil Unicode.
 3. Dual-mode network diagnostic (detects online vs offline capabilities).
 4. Transparent reporting of voice engines and graceful fallbacks.
 5. Speech speed controls (Normal 1.0x and Study/Slow 0.8x).
"""

import os
import io
import re
import time
import socket
import unicodedata
from typing import Dict, List, Optional, Tuple, Any

import gtts


# =====================================================================
# Network & Voice Engine Diagnostics
# =====================================================================

def is_internet_available(host: str = "translate.google.com", port: int = 443, timeout: float = 3.0) -> bool:
    """Checks whether connection to TTS endpoint is reachable."""
    try:
        socket.setdefaulttimeout(timeout)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.gaierror, OSError):
        return False


def check_voice_engine_status() -> Dict[str, Any]:
    """
    Detects available Tamil voice engines, checks offline vs online status,
    and inspects Windows SAPI voices for local Tamil packs.
    """
    online = is_internet_available()

    # Check Windows SAPI voices
    sapi_voices = []
    sapi_has_tamil = False
    try:
        import subprocess
        ps_cmd = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + '|' + $_.VoiceInfo.Culture.Name }"
        )
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.strip().splitlines():
                if "|" in line:
                    v_name, v_cult = line.strip().split("|", 1)
                    sapi_voices.append({"name": v_name, "culture": v_cult})
                    if v_cult.lower().startswith("ta"):
                        sapi_has_tamil = True
    except Exception:
        pass

    if online:
        engine_desc = "Google Neural Tamil Voice (gTTS - தமிழ் மொழிக்குரல்)"
        status_msg = "உண்மையான தமிழ் குரல் இயந்திரம் தயார் நிலையில் உள்ளது (Genuine Tamil Voice Ready)."
    else:
        engine_desc = "இணைய இணைப்பு தேவை (Internet Connection Required)"
        if sapi_has_tamil:
            status_msg = "விண்டோஸ் ஆஃப்லைன் தமிழ் குரல் கண்டறியப்பட்டது."
        else:
            status_msg = (
                "இணைய இணைப்பு இல்லை. கணினியில் விண்டோஸ் தமிழ் குரல் பேக் நிறுவப்படவில்லை "
                "(தற்போது ஆங்கில குரல்கள் மட்டுமே உள்ளன; அவை தமிழ் எழுத்துக்களை சரியாக வாசிக்க இயலாது). "
                "உண்மையான தமிழ் குரல் கேட்க இணையத்தை இணைக்கவும்."
            )

    return {
        "engine_name": engine_desc,
        "is_offline": False,
        "requires_internet": True,
        "internet_connected": online,
        "supported_language": "ta (தமிழ்)",
        "sapi_tamil_available": sapi_has_tamil,
        "sapi_voices_count": len(sapi_voices),
        "status_message": status_msg,
    }


# =====================================================================
# Tamil Text Preprocessing & Chunking
# =====================================================================

def clean_text_for_voice(text: str) -> str:
    """
    Standardizes Tamil Unicode for smooth voice synthesis,
    strips non-pronounceable OCR artifacts and control characters.
    """
    if not text:
        return ""
    # Normalize NFC
    t = unicodedata.normalize("NFC", text)
    # Remove control and zero-width characters
    t = re.sub(r"[\u200B-\u200D\uFEFF]", "", t)
    # Remove OCR bounding noise like boxes, hashes, dangling punctuation
    t = re.sub(r"[#_~*<>=\[\]{}|\\]", " ", t)
    # Collapse multiple whitespaces
    t = re.sub(r"[ \t]+", " ", t)
    return t.strip()


def chunk_tamil_text_for_voice(text: str, max_chunk_chars: int = 500) -> List[str]:
    """
    Splits long Tamil documents into natural syntactic chunks based on
    sentence delimiters without losing reading order or truncating words.
    """
    cleaned = clean_text_for_voice(text)
    if not cleaned:
        return []

    # Split into sentences or stanzas
    raw_sentences = re.split(r"(?<=[.!?|॥])\s+|\n+", cleaned)
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_len = 0

    for sent in raw_sentences:
        s_strip = sent.strip()
        if not s_strip:
            continue

        if current_len + len(s_strip) + 1 <= max_chunk_chars:
            current_chunk.append(s_strip)
            current_len += len(s_strip) + 1
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [s_strip]
            current_len = len(s_strip)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks if chunks else [cleaned]


_VOICE_SYNTHESIS_CACHE: Dict[Tuple[str, bool, str], Dict[str, Any]] = {}


def synthesize_tamil_speech(
    text: str,
    slow: bool = False,
    tld: str = "co.in",
) -> Dict[str, Any]:
    """
    Synthesizes authentic Tamil speech from actual OCR text or user input.
    Caches synthesized audio in memory to avoid repeated network requests on Streamlit reruns.
    """
    cleaned = clean_text_for_voice(text)
    if not cleaned:
        return {
            "success": False,
            "error": "வாசிப்பதற்கு உரை காலியாக உள்ளது (Text to read is empty).",
            "audio_bytes": None,
            "duration_est_seconds": 0.0,
            "word_count": 0,
            "char_count": 0,
            "chunks_count": 0,
        }

    # Verify that text contains pronounceable Tamil or English letters
    has_letters = bool(re.search(r"[\u0B80-\u0BFFA-Za-z]", cleaned))
    if not has_letters:
        return {
            "success": False,
            "error": "உரையில் வாசிக்கக்கூடிய தமிழ் அல்லது ஆங்கில எழுத்துக்கள் இல்லை (No readable letters found).",
            "audio_bytes": None,
            "duration_est_seconds": 0.0,
            "word_count": 0,
            "char_count": len(cleaned),
            "chunks_count": 0,
        }

    # Check cache to avoid duplicate network requests on Streamlit reruns
    cache_key = (cleaned, slow, tld)
    if cache_key in _VOICE_SYNTHESIS_CACHE:
        cached_result = _VOICE_SYNTHESIS_CACHE[cache_key].copy()
        cached_result["from_cache"] = True
        return cached_result

    # Check network connectivity
    if not is_internet_available():
        return {
            "success": False,
            "error": (
                "இணைய இணைப்பு கிடைக்கவில்லை (No Internet Connection). "
                "உண்மையான தமிழ் குரல் இயந்திரம் (Google Neural Tamil TTS) இயங்குவதற்கு இணைய இணைப்பு தேவைப்படுகிறது. "
                "உங்கள் இணைய இணைப்பை சரிபார்த்து மீண்டும் முயற்சிக்கவும்."
            ),
            "audio_bytes": None,
            "duration_est_seconds": 0.0,
            "word_count": len(cleaned.split()),
            "char_count": len(cleaned),
            "chunks_count": 0,
        }

    try:
        t0 = time.time()
        # gTTS natively handles Tamil with authentic prosody and pronunciation
        tts = gtts.gTTS(text=cleaned, lang="ta", slow=slow, tld=tld)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_data = fp.getvalue()
        elapsed = round(time.time() - t0, 2)

        words = cleaned.split()
        # Rough duration estimate: ~120 words per minute (normal), ~90 wpm (slow)
        wpm = 90.0 if slow else 130.0
        dur_est = round((len(words) / wpm) * 60.0, 1)

        result_dict = {
            "success": True,
            "audio_bytes": audio_data,
            "audio_format": "audio/mp3",
            "elapsed_seconds": elapsed,
            "duration_est_seconds": max(1.0, dur_est),
            "word_count": len(words),
            "char_count": len(cleaned),
            "engine": "Google Neural Tamil Voice (gTTS)",
            "voice_language": "Tamil (தமிழ் - இந்தியா)",
            "speed": "மெதுவான வாசிப்பு (0.8x)" if slow else "இயல்பான வேகம் (1.0x)",
            "is_offline": False,
            "error": None,
            "from_cache": False,
        }
        _VOICE_SYNTHESIS_CACHE[cache_key] = result_dict
        return result_dict

    except Exception as e:
        err_msg = str(e)
        if "Failed to connect" in err_msg or "timed out" in err_msg:
            friendly_err = "குரல் சேவையகத்துடன் இணைக்க முடியவில்லை. தயவுசெய்து இணைய இணைப்பைச் சரிபார்க்கவும்."
        else:
            friendly_err = f"குரல் உருவாக்குவதில் பிழை: {err_msg}"
        return {
            "success": False,
            "error": friendly_err,
            "audio_bytes": None,
            "duration_est_seconds": 0.0,
            "word_count": len(cleaned.split()),
            "char_count": len(cleaned),
            "chunks_count": 0,
        }
