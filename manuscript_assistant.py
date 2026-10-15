# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Feature 1: AI Manuscript Assistant (manuscript_assistant.py)
Evidence-Grounded AI Assistant for Tamil Manuscripts & Inscriptions
=============================================================================
Features:
  1. Digital Library of Authentic Tamil Manuscripts & Palm-leaf Inscriptions.
  2. Grounded Passage Retrieval across document sentences/verses.
  3. Bilingual Answers: Authentic Tamil response + English historical context.
  4. Evidence Citation Panel: Exact passage numbers, original quotes, confidence.
  5. Anti-Hallucination Guarantee: Refuses to fabricate facts if evidence is absent.
  6. Preserves original extracted/OCR text unchanged.
=============================================================================
"""

import re
import unicodedata
from typing import Dict, List, Any, Optional, Tuple

import tamil_nlp

# =====================================================================
# 🏛️ Digital Library of Curated Authentic Tamil Manuscripts
# =====================================================================
DIGITAL_LIBRARY_MANUSCRIPTS: Dict[str, Dict[str, Any]] = {
    "tolkappiyam": {
        "id": "tolkappiyam",
        "title": "தொல்காப்பியம் பாயிரச் சுவடி (Tolkappiyam Palm-Leaf)",
        "era": "சங்க காலம் (Sangam Era - c. 3rd Century BCE)",
        "category": "இலக்கணம் (Grammar & Linguistics)",
        "description": "தமிழ் மொழியின் மிகத் தொன்மையான இலக்கண நூலான தொல்காப்பியத்தின் சிறப்புப் பாயிரச் சுவடிப் பகுதி.",
        "text": (
            "வடவேங்கடம் தென்குமரி ஆயிடைத் தமிழ்கூறும் நல்லுலகத்து வழக்குஞ் செய்யுளு மாயிரு முதலின் எழுத்துஞ் சொல்லும் பொருளும் நாடி. "
            "செந்தமிழியற்கை சிவணிய நிலத்தொடு முந்துநூல் கண்டு முறைப்பட எண்ணிப் புலம் தொகுத்தோனே தொல்காப்பியன். "
            "தொல்காப்பியம் தமிழ் மொழியின் மிகத் தொன்மையான இலக்கண நூலாகும். "
            "இந்நூல் எழுத்து, சொல், பொருள் ஆகிய மூன்று பெரும் அதிகாரங்களைக் கொண்டுள்ளது. "
            "ஒவ்வொரு அதிகாரமும் ஒன்பது இயல்களாகப் பகுக்கப்பட்டு மொத்தம் இருபத்தேழு இயல்களைக் கொண்டுள்ளது. "
            "பொருள் அதிகாரத்தில் தமிழர் தம் அகவாழ்க்கை மற்றும் புறவாழ்க்கை நெறிகள் விரிவாக விளக்கப்பட்டுள்ளன."
        ),
    },
    "thanjavur_inscription": {
        "id": "thanjavur_inscription",
        "title": "தஞ்சைப் பெரிய கோயில் கல்வெட்டு (Brihadisvara Temple Inscription)",
        "era": "கி.பி. 1010 (Imperial Chola Dynasty - 11th Century CE)",
        "category": "கல்வெட்டு (Epigraphy & History)",
        "description": "முதலாம் இராஜராஜ சோழன் தஞ்சை இராஜராஜேஸ்வரம் (பெரிய கோயில்) கட்டியதை விவரிக்கும் கல்வெட்டுப் பதிவு.",
        "text": (
            "ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டி முடித்தார். "
            "இக்கோயிலின் மூலவர் பெருவுடையார் என்றும் விமானம் தட்சிண மேரு என்றும் கல்வெட்டுகளில் குறிப்பிடப்பட்டுள்ளது. "
            "கோயிலின் தலைமைத் தச்சராக வீரசோழன் குஞ்சர மல்லன் எனும் குஞ்சரமல்லன் இராஜராஜப் பெருந்தச்சன் நியமிக்கப்பட்டார். "
            "சோழர்களின் ஆட்சிக் காலத்தில் தமிழகத்தில் கலை, இலக்கியம், சிற்பம் மற்றும் கடல் வணிகம் உச்சத்தை எட்டின. "
            "இக்கோயிலுக்கு அளித்த பொன், வெள்ளி, செப்புப் பாத்திரங்கள் மற்றும் நெல் கொடைகள் அனைத்தும் கல்வெட்டில் பொறிக்கப்பட்டுள்ளன."
        ),
    },
    "silappadikaram": {
        "id": "silappadikaram",
        "title": "சிலப்பதிகாரம் கானல்வரி ஏடு (Silappadikaram Kanalvari)",
        "era": "கி.பி. 2-5 ஆம் நூற்றாண்டு (Post-Sangam Epic Era)",
        "category": "காப்பியம் (Classical Epic)",
        "description": "இளங்கோவடிகள் இயற்றிய சிலப்பதிகாரக் காப்பியத்தின் பூம்புகார் கடற்கரை கானல்வரிப் பாடல் சுவடி.",
        "text": (
            "சிலப்பதிகாரம் ஐம்பெருங் காப்பியங்களில் முதன்மையான தமிழ் இலக்கியக் காப்பியமாகும். "
            "இந்நூலை சேர மன்னன் செங்குட்டுவனின் தம்பியான இளங்கோவடிகள் இயற்றினார். "
            "பூம்புகார் நகரில் செல்வந்தர் மாசாத்துவான் மகனான கோவலனும் மாநாய்கன் மகளான கண்ணகியும் வாழ்ந்து வந்தனர். "
            "காவிரிப்பூம்பட்டினக் கடற்கரையில் மாதவி பாடிய கானல்வரிப் பாடலால் ஏற்பட்ட ஊடலால் கோவலன் கண்ணகியுடன் மதுரை நோக்கிப் புறப்பட்டான். "
            "அரசியல் பிழைத்தோர்க்கு அறங்கூற்றாவதூஉம் உரைசால் பத்தினியை உயர்ந்தோர் ஏத்தலும் ஊழ்வினை உருத்துவந்து ஊட்டும் என்பதும் இதன் முப்பெரும் உண்மைகள்."
        ),
    },
    "tirukkural_commentary": {
        "id": "tirukkural_commentary",
        "title": "திருக்குறள் பரிமேலழகர் உரை ஏடு (Tirukkural Palm-leaf)",
        "era": "செம்மொழி இலக்கியம் & இடைக்கால உரை (Classical Ethics)",
        "category": "நீதி இலக்கியம் (Ethics & Philosophy)",
        "description": "திருவள்ளுவர் அருளிய திருக்குறளுக்கு பரிமேலழகர் எழுதிய பழமையான சுவடி உரைப் பதிவு.",
        "text": (
            "திருக்குறள் உலகப் பொதுமறை என்று போற்றப்படும் மிகச் சிறந்த தமிழ் அறநூலாகும். "
            "இந்நூலை இயற்றியவர் தெய்வப் புலவர் திருவள்ளுவர் ஆவார். "
            "திருக்குறள் அறத்துப்பால், பொருட்பால், காமத்துப்பால் என்ற முப்பால்களாகப் பிரிக்கப்பட்டு 133 அதிகாரங்களையும் 1330 குறட்பாக்களையும் கொண்டுள்ளது. "
            "திருக்குறளுக்கு உரை எழுதிய பதின்மருள் பரிமேலழகரின் உரையே தலைசிறந்ததாக அறிஞர்களால் ஏற்றுக்கொள்ளப்பட்டுள்ளது. "
            "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு என்பது இந்நூலின் முதல் குறட்பா ஆகும்."
        ),
    },
}


# =====================================================================
# 🔍 Tamil Morphological Stemming & Agglutinative Word Matcher
# =====================================================================
TAMIL_INFLECTION_SUFFIXES = [
    # Multi-char case markers & postpositions
    "களிலிருந்து", "களினுடைய", "களுக்கு", "களினால்",
    "இலிருந்து", "இனிடமிருந்து", "உடைய", "இடமிருந்து",
    "களின்", "களை", "களால்", "களில்", "களோடு", "களுடன்",
    "த்தினால்", "த்தோடு", "த்துடன்", "த்துக்கு", "த்தின்", "த்தை", "த்தால்",
    "த்தினார்", "க்கிறார்", "க்கின்றார்", "ப்பார்", "த்தார்",
    "இயற்றினார்", "இயற்றப்பட்ட", "செய்தார்",
    "இருந்தார்", "இருந்தனர்", "இருந்தது",
    "உக்கு", "இக்கு", "க்கு", "ஆல்", "இன்", "இல்", "கண்",
    "அவர்", "ஆளர்", "ஆர்கள்", "ஆர்", "ஆன்", "ஆள்", "அனர்", "இயவர்", "வர்",
    "இய", "செய்த", "பட்ட", "படும்", "கின்ற", "கிற", "ினார்", "ந்தார்", "ட்டார்", "ற்றார்",
    "ங்களாக", "அங்களாக", "ப்பட்டுள்ளது", "ப்பட்டது",
    "கள்", "ஐ", "ன்", "ம்", "து"
]


def extract_tamil_stem(w: str) -> str:
    """Extracts core Tamil stem by stripping common inflectional suffixes."""
    w_clean = unicodedata.normalize("NFC", w.strip().lower())
    for sfx in TAMIL_INFLECTION_SUFFIXES:
        if w_clean.endswith(sfx) and len(w_clean) - len(sfx) >= 3:
            w_clean = w_clean[:-len(sfx)]
            break
    if w_clean.endswith("்") and len(w_clean) > 3:
        w_clean = w_clean[:-1]
    return w_clean


def match_tamil_words(w1: str, w2: str) -> bool:
    """
    Robust comparison for Tamil agglutinative forms.
    Returns True if w1 and w2 match exactly, share a root stem, or share a long common prefix.
    """
    if not w1 or not w2:
        return False
    w1_low = w1.lower()
    w2_low = w2.lower()
    if w1_low == w2_low or w1_low in w2_low or w2_low in w1_low:
        return True
    s1 = extract_tamil_stem(w1_low)
    s2 = extract_tamil_stem(w2_low)
    if s1 == s2 or s1.startswith(s2) or s2.startswith(s1):
        return True
    if len(s1) >= 4 and len(s2) >= 4:
        cp_len = 0
        for c1, c2 in zip(s1, s2):
            if c1 == c2:
                cp_len += 1
            else:
                break
        if cp_len >= 4:
            return True
    import difflib
    return difflib.SequenceMatcher(None, w1_low, w2_low).ratio() >= 0.72


# =====================================================================
# 🔍 Passage Segmentation & Intent Detection
# =====================================================================
def get_manuscript_passages(doc_text: str) -> List[Dict[str, Any]]:
    """Splits manuscript into numbered, non-empty passages preserving exact text."""
    raw_sentences = tamil_nlp.segment_sentences(doc_text)
    passages = []
    for idx, s in enumerate(raw_sentences, start=1):
        clean_s = s.strip()
        if clean_s:
            passages.append({
                "passage_number": idx,
                "text": clean_s,
                "word_count": len(clean_s.split()),
            })
    return passages


def detect_question_intent(question: str) -> List[str]:
    """Detects historical question intents (person, location, time, work, definition)."""
    q_norm = unicodedata.normalize("NFC", question.lower())
    intents = []

    if re.search(r"யார்|எவர்|யாருடைய|ஆசிரியர்|புலவர்|மன்னன்|தச்சர்|தலைவர்|இயற்றிய|எழுதிய|பாடிய|who|author|creator|writer", q_norm):
        intents.append("person")
    if re.search(r"எங்கு|எங்குள்ளது|இடம்|நகரம்|நாடு|ஆறு|கோயில்|where|location", q_norm):
        intents.append("location")
    if re.search(r"எப்போது|ஆண்டு|நூற்றாண்டு|காலம்|தேதி|when|year|era", q_norm):
        intents.append("time")
    if re.search(r"என்ன|விளக்குக|பொருள்|அதிகாரம்|பெயர்|நூல்|காப்பியம்|what|which", q_norm):
        intents.append("concept")
    if re.search(r"எத்தனை|எண்ணிக்கை|how many", q_norm):
        intents.append("count")

    return intents if intents else ["general"]


# =====================================================================
# 🤖 Evidence-Grounded Query Engine
# =====================================================================
def ask_manuscript_assistant(
    document_text: str,
    question: str,
    document_title: str = "தேர்ந்தெடுக்கப்பட்ட சுவடி ஆவணம்",
    target_language: str = "ta",
) -> Dict[str, Any]:
    """
    Retrieves evidence passages and formulates grounded answers.
    Never hallucinates: if confidence is low, clearly states evidence was not found.
    Treats instructions embedded in uploaded manuscripts strictly as passive text.
    """
    # Auto-detect if caller passed (question, document_text)
    if document_text and question and len(document_text) < 120 and len(question) > len(document_text):
        document_text, question = question, document_text

    if not document_text or not document_text.strip():
        return {
            "success": False,
            "found": False,
            "answer_tamil": "ஆவணத்தில் வாசிக்கக்கூடிய உரை இல்லை (Document text is empty).",
            "explanation_english": "Please provide or OCR a manuscript first.",
            "supporting_passages": [],
            "confidence": 0.0,
            "document_title": document_title,
        }

    q_clean = question.strip()
    if not q_clean:
        return {
            "success": False,
            "found": False,
            "answer_tamil": "தயவுசெய்து ஆவணம் குறித்த ஒரு கேள்வியை உள்ளிடவும் (Please enter a question).",
            "explanation_english": "Question prompt was empty.",
            "supporting_passages": [],
            "confidence": 0.0,
            "document_title": document_title,
        }

    # Prompt injection mitigation: Sanitize any prompt jailbreak phrasing from influencing pipeline
    sanitized_q = re.sub(
        r"(?i)\b(ignore previous instructions|system prompt|jailbreak|disregard earlier instructions)\b",
        "",
        q_clean,
    ).strip()
    if not sanitized_q:
        sanitized_q = q_clean

    passages = get_manuscript_passages(document_text)
    if not passages:
        return {
            "success": False,
            "found": False,
            "answer_tamil": "ஆவணத்தில் வாக்கியங்கள் கண்டறியப்படவில்லை.",
            "explanation_english": "No readable sentences detected in the document.",
            "supporting_passages": [],
            "confidence": 0.0,
            "document_title": document_title,
        }

    # Extract keywords from question
    q_words = re.findall(r"[\u0B80-\u0BFAa-zA-Z0-9]+", sanitized_q.lower())
    # Exclude common Tamil question/wh-words so they don't dilute base_score
    _QUESTION_WORDS = {
        "யார்", "என்ன", "எங்கு", "எப்போது", "எப்படி", "ஏன்",
        "எத்தனை", "எவ்வளவு", "எவ்வாறு", "எந்த", "எவர்",
        "எவை", "எது", "எடு", "எம்மை",
    }
    q_keywords = [
        w for w in q_words
        if w not in tamil_nlp.TAMIL_STOPWORDS
        and w not in tamil_nlp.ENGLISH_STOPWORDS
        and len(w) > 1
        and w not in _QUESTION_WORDS
    ]
    if not q_keywords:
        q_keywords = [w for w in q_words if len(w) > 1]

    intents = detect_question_intent(sanitized_q)

    # Score each passage
    scored_passages = []
    for p in passages:
        p_text = p["text"]
        p_lower = p_text.lower()
        p_tokens = re.findall(r"[\u0B80-\u0BFAa-zA-Z0-9]+", p_lower)
        matched_kw = []

        for kw in q_keywords:
            if kw in p_lower:
                matched_kw.append(kw)
            elif any(match_tamil_words(kw, pw) for pw in p_tokens):
                matched_kw.append(kw)

        if not matched_kw:
            continue

        base_score = len(matched_kw) / max(len(q_keywords), 1)

        # Intent heuristic bonus: ONLY apply if at least 50% of the question keywords matched!
        intent_bonus = 0.0
        if base_score >= 0.5:
            if "person" in intents and re.search(r"தொல்காப்பியன்|சோழன்|இளங்கோவடிகள்|திருவள்ளுவர்|கோவலன்|கண்ணகி|தச்சன்|மன்னன்|புலவர்|ஆசிரியர்|இயற்றினார்|கட்டினார்", p_text):
                intent_bonus += 0.2
            if "time" in intents and re.search(r"\d{3,4}|கி\.பி|கி\.மு|ஆண்டு|நூற்றாண்டு|காலம்", p_text):
                intent_bonus += 0.2
            if "location" in intents and re.search(r"தஞ்சை|வேங்கடம்|குமரி|பூம்புகார்|மதுரை|காவிரி|கோயில்|நகர்", p_text):
                intent_bonus += 0.2
            if "count" in intents and re.search(r"மூன்று|ஒன்பது|இருபத்தேழு|133|1330|பதின்மர்", p_text):
                intent_bonus += 0.2

        total_score = min(1.0, base_score + intent_bonus)
        scored_passages.append({
            "passage_number": p["passage_number"],
            "text": p_text,
            "score": round(total_score, 3),
            "base_score": round(base_score, 3),
            "matched_keywords": matched_kw,
            "document_title": document_title,
        })

    # Sort descending by score
    scored_passages.sort(key=lambda x: (x["score"], x["base_score"]), reverse=True)

    # Refusal responses in target language
    refusal_map = {
        "ta": "மன்னிக்கவும், கேட்கப்பட்ட கேள்விக்கான போதுமான சான்றுகள் இந்த ஆவணத்தில் காணப்படவில்லை (Sufficient evidence was not found in the manuscript).",
        "en": "Sorry, sufficient evidence to answer this question was not found in the selected manuscript text (Anti-Hallucination Guarantee).",
        "hi": "क्षमा करें, चयनित पांडुलिपि में इस प्रश्न का उत्तर देने के लिए पर्याप्त साक्ष्य नहीं मिले (Anti-Hallucination Guarantee)।",
        "te": "క్షమించండి, ఎంచుకున్న తాళపత్రంలో ఈ ప్రశ్నకు తగిన ఆధారాలు లభించలేదు.",
        "kn": "ಕ್ಷಮಿಸಿ, ಆಯ್ಕೆಮಾಡಿದ ಹಸ್ತಪ್ರತಿಯಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ಸಾಕಷ್ಟು ಪುರಾವೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
        "ml": "ക്ഷമിക്കണം, ഈ ചോദ്യത്തിന് ഉത്തരം നൽകാൻ ആവശ്യമായ തെളിവുകൾ കണ്ടെത്തിയില്ല.",
        "bn": "দুঃখিত, নির্বাচিত পাণ্ডুলিপিতে এই প্রশ্নের উত্তর দেওয়ার মতো পর্যাপ্ত প্রমাণ পাওয়া যায়নি।",
        "mr": "क्षमस्व, निवडलेल्या हस्तलिखितामध्ये या प्रश्नाचे उत्तर देण्यासाठी पुरेसा पुरावा आढळला नाही.",
        "ur": "معذرت، منتخب کردہ مخطوطے میں اس سوال کا جواب دینے کے لیے کافی شواہد نہیں ملے۔",
    }

    # Threshold check: Must meet minimum confidence and substantive keyword evidence
    if not scored_passages or scored_passages[0]["score"] < 0.40 or scored_passages[0]["base_score"] < 0.45:
        refusal_msg = refusal_map.get(target_language, refusal_map["en"])
        return {
            "success": True,
            "found": False,
            "answer_tamil": refusal_msg,
            "explanation_english": (
                "The assistant is strictly evidence-grounded and does not invent facts. "
                "The queried information is not stated in the processed manuscript."
            ),
            "supporting_passages": [],
            "confidence": scored_passages[0]["score"] if scored_passages else 0.0,
            "document_title": document_title,
            "intents": intents,
        }


    top_passage = scored_passages[0]
    supporting_list = scored_passages[:3]

    # Formulate verified answers: Always keep manuscript evidence in authentic Tamil
    evidence_quote = f"\"{top_passage['text']}\""
    
    # Prefix grounded statement in target language
    pref_map = {
        "ta": "ஆவணச் சான்றின்படி:",
        "en": "According to authentic manuscript evidence:",
        "hi": "प्रामाणिक पांडुलिपि साक्ष्य के अनुसार:",
        "te": "ప్రామాణిక తాళపత్ర ఆధారాల ప్రకారం:",
        "kn": "ಹಸ್ತಪ್ರತಿ ಸಾಕ್ಷ್ಯಾಧಾರದ ಪ್ರಕಾರ:",
        "ml": "ഗ്രന്ഥ തെളിവുകൾ പ്രകാരം:",
        "bn": "পাণ্ডুলিপি প্রমাণ অনুসারে:",
        "mr": "हस्तलिखित पुराव्यानुसार:",
        "ur": "مخطوطہ کے مستند شواہد کے مطابق:",
        "sa": "पाण्डुलिपि-प्रमाणानुसारेण:",
    }
    intro = pref_map.get(target_language, pref_map["ta"])
    ans_tamil = f"{intro}\n\n{evidence_quote}"
    
    # Formulate contextual English explanation
    eng_expl = (
        f"Grounded directly in passage #{top_passage['passage_number']} of '{document_title}'. "
        f"Key evidence terms matched: {', '.join(top_passage['matched_keywords'])} "
        f"(Confidence: {int(top_passage['score'] * 100)}%)."
    )

    return {
        "success": True,
        "found": True,
        "answer_tamil": ans_tamil,
        "explanation_english": eng_expl,
        "supporting_passages": supporting_list,
        "confidence": top_passage["score"],
        "confidence_percentage": f"{int(top_passage['score'] * 100)}%",
        "document_title": document_title,
        "intents": intents,
    }


# Standard alias for backward compatibility and clean API design
answer_manuscript_question = ask_manuscript_assistant
