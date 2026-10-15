# -*- coding: utf-8 -*-
"""
=============================================================================
தமிழ்ச்சுவடி AI – Indian Multilingual Architecture (i18n.py)
Supports the 22 Scheduled Languages of the Republic of India + English
=============================================================================
Features:
  1. Centralized registry of India's 22 Eighth Schedule Languages + English (23 total).
  2. Native script representation and language metadata (direction LTR/RTL, code).
  3. Seamless t(key, lang) lookup with graceful cascade: lang -> en -> ta -> key.
  4. Preserves manuscript text in authentic classical Tamil while adapting UI.
  5. Responsive language selector widget preserving all session state.
  6. Transparent AI capability reporting for each language.
=============================================================================
"""

import streamlit as st
from typing import Dict, Any, Optional, List

# =====================================================================
# 1. Official 22 Eighth Schedule Languages of India + English (23 Total)
# =====================================================================
SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "script": "Latin",
        "direction": "ltr",
        "flag": "🌐",
        "ocr_supported": True,
        "tts_supported": True,
        "assistant_supported": True,
    },
    "ta": {
        "code": "ta",
        "name": "Tamil",
        "native_name": "தமிழ்",
        "script": "Tamil",
        "direction": "ltr",
        "flag": "🏛️",
        "ocr_supported": True,
        "tts_supported": True,
        "assistant_supported": True,
    },
    "hi": {
        "code": "hi",
        "name": "Hindi",
        "native_name": "हिन्दी",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "te": {
        "code": "te",
        "name": "Telugu",
        "native_name": "తెలుగు",
        "script": "Telugu",
        "direction": "ltr",
        "flag": "🏛️",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "kn": {
        "code": "kn",
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "script": "Kannada",
        "direction": "ltr",
        "flag": "🏛️",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "ml": {
        "code": "ml",
        "name": "Malayalam",
        "native_name": "മലയാളം",
        "script": "Malayalam",
        "direction": "ltr",
        "flag": "🏛️",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "bn": {
        "code": "bn",
        "name": "Bengali",
        "native_name": "বাংলা",
        "script": "Bengali",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "mr": {
        "code": "mr",
        "name": "Marathi",
        "native_name": "मराठी",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "gu": {
        "code": "gu",
        "name": "Gujarati",
        "native_name": "ગુજરાતી",
        "script": "Gujarati",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "pa": {
        "code": "pa",
        "name": "Punjabi",
        "native_name": "ਪੰਜਾਬੀ",
        "script": "Gurmukhi",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "or": {
        "code": "or",
        "name": "Odia",
        "native_name": "ଓଡ଼ିଆ",
        "script": "Odia",
        "direction": "ltr",
        "flag": "🏛️",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "as": {
        "code": "as",
        "name": "Assamese",
        "native_name": "অসমীয়া",
        "script": "Bengali-Assamese",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "ur": {
        "code": "ur",
        "name": "Urdu",
        "native_name": "اردو",
        "script": "Perso-Arabic",
        "direction": "rtl",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "sa": {
        "code": "sa",
        "name": "Sanskrit",
        "native_name": "संस्कृतम्",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🕉️",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": True,
    },
    "ne": {
        "code": "ne",
        "name": "Nepali",
        "native_name": "नेपाली",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "kok": {
        "code": "kok",
        "name": "Konkani",
        "native_name": "कोंकणी",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "mni": {
        "code": "mni",
        "name": "Manipuri (Meitei)",
        "native_name": "মৈতৈলোন্ (Meitei)",
        "script": "Bengali / Meetei Mayek",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "mai": {
        "code": "mai",
        "name": "Maithili",
        "native_name": "मैथिली",
        "script": "Devanagari / Tirhuta",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "sat": {
        "code": "sat",
        "name": "Santali",
        "native_name": "ᱥᱟᱱᱛᱟᱲᱤ (Santali)",
        "script": "Ol Chiki",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "ks": {
        "code": "ks",
        "name": "Kashmiri",
        "native_name": "کٲشُر (Kashmiri)",
        "script": "Perso-Arabic / Devanagari",
        "direction": "rtl",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "doi": {
        "code": "doi",
        "name": "Dogri",
        "native_name": "डोगरी (Dogri)",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "brx": {
        "code": "brx",
        "name": "Bodo",
        "native_name": "बर' (Bodo)",
        "script": "Devanagari",
        "direction": "ltr",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
    "sd": {
        "code": "sd",
        "name": "Sindhi",
        "native_name": "سنڌي / सिन्धी",
        "script": "Perso-Arabic / Devanagari",
        "direction": "rtl",
        "flag": "🇮🇳",
        "ocr_supported": False,
        "tts_supported": False,
        "assistant_supported": False,
    },
}

# =====================================================================
# 2. Centralized Multi-Lingual Translation Dictionary
# =====================================================================
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Application Title & Subtitle
    "app_title": {
        "en": "📜 Tamil Suvadi AI — Ancient Tamil Manuscripts Digitization & AI Preservation",
        "ta": "📜 தமிழ் மரபு AI — பழமையான தமிழ் நூல்கள் எண்மமாக்கம்",
        "hi": "📜 तमिल सुवड़ी एआई — प्राचीन तमिल पांडुलिपियों का डिजिटलीकरण एवं संरक्षण",
        "te": "📜 తమిళ్ సువడి AI — ప్రాచీన తమిళ తాళపత్ర గ్రంథాల డిజిటలైజేషన్",
        "kn": "📜 ತಮಿಳು ಸುವಡಿ AI — ಪ್ರಾಚೀನ ತಮಿಳು ಹಸ್ತಪ್ರತಿಗಳ ಡಿಜಿಟಲೀಕರಣ",
        "ml": "📜 തമിഴ് സുവടി AI — പുരാതന തമിഴ് താളിയോല ഗ്രന്ഥ ഡിജിറ്റൈസേഷൻ",
        "bn": "📜 তামিল সুবড়ি এআই — প্রাচীন তামিল পাণ্ডুলিপির ডিজিটাইজেশন ও সংরক্ষণ",
        "mr": "📜 तमिळ सुवडी एआय — प्राचीन तमिळ हस्तलिखितांचे डिजिटायझेशन",
        "gu": "📜 તમિલ સુવડી AI — પ્રાચીન તમિલ હસ્તપ્રતોનું ડિજિટાઈઝેશન",
        "pa": "📜 ਤਮਿਲ ਸੁਵੜੀ AI — ਪੁਰਾਤਨ ਤਮਿਲ ਹੱਥ-ਲਿਖਤਾਂ ਦਾ ਡਿਜੀਟਾਈਜ਼ੇਸ਼ਨ",
        "or": "📜 ତାମିଲ ସୁବଡ଼ି AI — ପ୍ରାଚୀନ ତାମିଲ ତାଳପତ୍ର ପାଣ୍ଡୁଲିପି ଡିଜିଟାଇଜେସନ୍",
        "ur": "📜 تمل سووڈی AI — قدیم تمل مخطوطات کی ڈیجیٹائزیشن اور تحفظ",
        "sa": "📜 तमिल सुवडी AI — प्राचीन तमिल पाण्डुलिपीनां डिजिटलीकरणम्",
    },
    "app_subtitle": {
        "en": "Preserving Ancient Palm-Leaf Manuscripts, Inscriptions & Rare Texts with Vision Transformer OCR & Grounded AI",
        "ta": "பழமையான ஓலைச்சுவடிகள், கல்வெட்டுகள் மற்றும் அரிய நூல்களை இரட்டை OCR மற்றும் சான்று-சார்ந்த AI உடன் பாதுகாக்கும் தளம்",
        "hi": "विज़न ट्रांसफार्मर ओसीआर और साक्ष्य-आधारित एआई के साथ प्राचीन पांडुलिपियों और शिलालेखों का संरक्षण",
        "te": "విజన్ ట్రాన్స్ఫార్మర్ OCR మరియు ఆధారిత AI తో ప్రాచీన తాళపత్ర గ్రంథాల పరిరక్షణ",
        "kn": "ವಿಷನ್ ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್ OCR ಮತ್ತು ಆಧಾರಿತ AI ನೊಂದಿಗೆ ಪ್ರಾಚೀನ ಹಸ್ತಪ್ರತಿಗಳ ಸಂರಕ್ಷಣೆ",
        "ml": "വിഷൻ ട്രാൻസ്ഫോർമർ ഒസിആറും തെളിവ് അധിഷ്ഠിത എഐയും ഉപയോഗിച്ച് പുരാതന ഗ്രന്ഥങ്ങൾ സംരക്ഷിക്കുന്നു",
        "bn": "ভিশন ট্রান্সফরমার ওসিআর এবং প্রমাণ-ভিত্তিক এআই দিয়ে প্রাচীন পাণ্ডুলিপি সংরক্ষণ",
        "mr": "व्हिजन ट्रान्सफॉर्मर ओसीआर आणि पुरावा-आधारित एआय सह प्राचीन हस्तलिखितांचे संरक्षण",
        "ur": "ویژن ٹرانسفارمر OCR اور شواہد پر مبنی AI کے ساتھ قدیم مخطوطات کا تحفظ",
    },

    # --- 12 PRIMARY NAVIGATION TABS (All 23 Languages) ---
    "tab_home": {
        "en": "🏛️ Home",
        "ta": "🏛️ முகப்பு (Home)",
        "hi": "🏛️ मुख्य पृष्ठ (Home)",
        "te": "🏛️ ముఖ్యాంశాలు (Home)",
        "kn": "🏛️ ಮುಖಪುಟ (Home)",
        "ml": "🏛️ പ്രധാനം (Home)",
        "bn": "🏛️ প্রচ্ছদ (Home)",
        "mr": "🏛️ मुख्य पान (Home)",
        "gu": "🏛️ મુખ્ય પૃષ્ઠ (Home)",
        "pa": "🏛️ ਮੁੱਖ ਪੰਨਾ (Home)",
        "or": "🏛️ ମୁଖ୍ୟ ପୃଷ୍ଠା (Home)",
        "as": "🏛️ মূল পৃষ্ঠা (Home)",
        "ur": "🏛️ ہوم پیج (Home)",
        "sa": "🏛️ मुखपृष्ठम् (Home)",
        "ne": "🏛️ गृहपृष्ठ (Home)",
        "kok": "🏛️ मुख्य पान (Home)",
        "mni": "🏛️ য়ুম্ফম্ (Home)",
        "mai": "🏛️ मुख्य पृष्ठ (Home)",
        "sat": "🏛️ ᱢᱩᱞ ᱥᱟᱦᱴᱟ (Home)",
        "ks": "🏛️ اہم صفحہ (Home)",
        "doi": "🏛️ मुख पृष्ठ (Home)",
        "brx": "🏛️ गाहाय बिखं (Home)",
        "sd": "🏛️ مکھیو صفحو (Home)",
    },
    "tab_digitize": {
        "en": "📑 Digitize & Dual OCR",
        "ta": "📑 நூல்களை டிஜிட்டல் மயமாக்குதல் (Digitization & OCR)",
        "hi": "📑 डिजिटलीकरण एवं दोहरा OCR",
        "te": "📑 డిజిటలైజేషన్ & ద్వంద్వ OCR",
        "kn": "📑 ಡಿಜಿಟಲೀಕರಣ & ಡ್ಯುಯಲ್ OCR",
        "ml": "📑 ഡിജിറ്റൈസേഷൻ & ഇരട്ട OCR",
        "bn": "📑 ডিজিটাইজেশন ও ডুয়াল OCR",
        "mr": "📑 डिजिटायझेशन व दुहेरी OCR",
        "gu": "📑 ડિજિટાઈઝેશન અને ડ્યુઅલ OCR",
        "pa": "📑 ਡਿਜੀਟਾਈਜ਼ੇਸ਼ਨ ਅਤੇ ਦੋਹਰਾ OCR",
        "or": "📑 ଡିଜିଟାଇଜେସନ୍ ଏବଂ ଦ୍ୱୈତ OCR",
        "as": "📑 ডিজিটাইজেচন আৰু ডুৱেল OCR",
        "ur": "📑 ڈیجیٹائزیشن اور ڈوئل OCR",
        "sa": "📑 डिजिटलीकरणं द्वैध-OCR च",
        "ne": "📑 डिजिटलीकरण र दोहोरो OCR",
        "kok": "📑 डिजिटायझेशन आनी दुहेरी OCR",
        "mni": "📑 দিজিতাইজেশন অমসুং দুয়েল OCR",
        "mai": "📑 डिजिटलीकरण आ दोहरा OCR",
        "sat": "📑 ᱰᱤᱡᱤᱴᱟᱭᱤᱡᱮᱥᱚᱱ ᱟᱨ OCR",
        "ks": "📑 ڈیجیٹائزیشن تہٕ ڈوئل OCR",
        "doi": "📑 डिजिटलीकरण ते दोहरा OCR",
        "brx": "📑 दिजिताइजेसन आरो दबाइल OCR",
        "sd": "📑 ڊيجيٽائيزيشن ۽ ٻٽو OCR",
    },
    "tab_correction": {
        "en": "✍️ OCR Text Correction",
        "ta": "✍️ OCR உரைத் திருத்தம் (OCR Correction)",
        "hi": "✍️ ओसीआर पाठ सुधार (Correction)",
        "te": "✍️ OCR వచన సవరణ (Correction)",
        "kn": "✍️ OCR ಪಠ್ಯ ತಿದ್ದುಪಡಿ",
        "ml": "✍️ OCR ടെക്സ്റ്റ് തിരുത്തൽ",
        "bn": "✍️ ওসিআর পাঠ্য সংশোধন",
        "mr": "✍️ ओसीआर मजकूर दुरुस्ती",
        "gu": "✍️ OCR ટેક્સ્ટ સુધારણા",
        "pa": "✍️ OCR ਪਾਠ ਸੋਧ",
        "or": "✍️ OCR ପାଠ ସଂଶୋଧନ",
        "as": "✍️ OCR পাঠ্য সংশোধন",
        "ur": "✍️ OCR متن کی تصحیح",
        "sa": "✍️ OCR पाठ्यशोधनम्",
        "ne": "✍️ ओसीआर पाठ सुधार",
        "kok": "✍️ ओसीआर मजकूर सुदारणा",
        "mni": "✍️ OCR তেক্সট শেম্বা",
        "mai": "✍️ ओसीआर पाठ संशोधन",
        "sat": "✍️ OCR ᱚᱞ ᱥᱩᱫᱷᱨᱟᱹᱣ",
        "ks": "✍️ OCR متن درستی",
        "doi": "✍️ ओसीआर पाठ सुधार",
        "brx": "✍️ ओसिआर फराय बिथोन",
        "sd": "✍️ OCR متن جي درستگي",
    },
    "tab_assistant": {
        "en": "🤖 AI Manuscript Assistant",
        "ta": "🤖 AI கையெழுத்துப் பிரதி உதவியாளர் (Assistant)",
        "hi": "🤖 एआई पांडुलिपि सहायक",
        "te": "🤖 AI తాళపత్ర సహాయకుడు",
        "kn": "🤖 AI ಹಸ್ತಪ್ರತಿ ಸಹಾಯಕ",
        "ml": "🤖 AI ഗ്രന്ഥ സഹായി",
        "bn": "🤖 এআই পাণ্ডুলিপি সহকারী",
        "mr": "🤖 एआय हस्तलिखित सहाय्यक",
        "gu": "🤖 AI હસ્તપ્રત સહાયક",
        "pa": "🤖 AI ਹੱਥ-ਲਿਖਤ ਸਹਾਇਕ",
        "or": "🤖 AI ପାଣ୍ଡୁଲିପି ସହାୟକ",
        "as": "🤖 AI পাণ্ডুলিপি সহায়ক",
        "ur": "🤖 AI مخطوطہ معاون",
        "sa": "🤖 AI पाण्डुलिपि-सहायकः",
        "ne": "🤖 एआई पाण्डुलिपि सहायक",
        "kok": "🤖 एआय हस्तलिखित सहाय्यक",
        "mni": "🤖 AI লাইরিক সহকারী",
        "mai": "🤖 एआई पाण्डुलिपि सहायक",
        "sat": "🤖 AI ᱚᱞ-ᱯᱚᱛᱚᱵ ᱜᱚᱲᱚᱭᱤᱡ",
        "ks": "🤖 AI مخطوطہ مددگار",
        "doi": "🤖 एआई पाण्डुलिपि सहायक",
        "brx": "🤖 AI लाइसाम बिथोन",
        "sd": "🤖 AI قلمي نسخي وارو مددگار",
    },
    "tab_explorer": {
        "en": "🕸️ Knowledge Explorer",
        "ta": "🕸️ அறிவு வரைபடம் (Knowledge Explorer)",
        "hi": "🕸️ ज्ञान अन्वेषक एवं ग्राफ",
        "te": "🕸️ జ్ఞాన చిత్రపట అన్వేషకుడు",
        "kn": "🕸️ ಜ್ಞಾನ ನಕ್ಷೆ ಎಕ್ಸ್‌ಪ್ಲೋರರ್",
        "ml": "🕸️ വിജ്ഞാന ഭൂപടം",
        "bn": "🕸️ জ্ঞান মানচিত্র এক্সপ্লোরার",
        "mr": "🕸️ ज्ञान आलेख अन्वेषक",
        "gu": "🕸️ જ્ઞાન આલેખ એક્સપ્લોરર",
        "pa": "🕸️ ਗਿਆਨ ਨਕਸ਼ਾ ਐਕਸਪਲੋਰਰ",
        "or": "🕸️ ଜ୍ଞାନ ମାନଚିତ୍ର ଅନୁସନ୍ଧାନକାରୀ",
        "as": "🕸️ জ্ঞান মানচিত্ৰ অন্বেষক",
        "ur": "🕸️ نالج ایکسپلورر اور گراف",
        "sa": "🕸️ ज्ञान-मानचित्र-अन्वेषकः",
        "ne": "🕸️ ज्ञान नक्सा अन्वेषक",
        "kok": "🕸️ गिन्यान आलेख सोदक",
        "mni": "🕸️ লৌশিং মেপ এক্সপ্লোরার",
        "mai": "🕸️ ज्ञान मानचित्र अन्वेषक",
        "sat": "🕸️ ᱜᱮᱭᱟᱱ ᱱᱚᱠᱥᱟ ᱯᱟᱱᱛᱮ",
        "ks": "🕸️ علم گراف ایکسپلورر",
        "doi": "🕸️ ज्ञान नक्शा अन्वेषक",
        "brx": "🕸️ गियान नक्सा नायगिरि",
        "sd": "🕸️ علمي گراف ۽ ڳولا",
    },
    "tab_semantic": {
        "en": "🔎 Semantic Search",
        "ta": "🔎 பொருள் சார்ந்த தேடல் (Semantic Search)",
        "hi": "🔎 अर्थ-आधारित खोज (Semantic Search)",
        "te": "🔎 భావార్థ శోధన (Semantic Search)",
        "kn": "🔎 ಅರ್ಥ ಆಧಾರಿತ ಹುಡುಕಾಟ",
        "ml": "🔎 അർത്ഥാധിഷ്ഠിത തിരച്ചിൽ",
        "bn": "🔎 অর্থ-ভিত্তিক অনুসন্ধান",
        "mr": "🔎 अर्थ-आधारित शोध",
        "gu": "🔎 અર્થ-આધારિત શોધ",
        "pa": "🔎 ਅਰਥ-ਅਧਾਰਿਤ ਖੋਜ",
        "or": "🔎 ଅର୍ଥ-ଭିତ୍ତିକ ସନ୍ଧାନ",
        "as": "🔎 অৰ্থ-ভিত্তিক অনুসন্ধান",
        "ur": "🔎 معنی خیز تلاش (Semantic Search)",
        "sa": "🔎 अर्थाधारित-अन्वेषणम्",
        "ne": "🔎 अर्थ-आधारित खोज",
        "kok": "🔎 अर्थ-आदारीत सोद",
        "mni": "🔎 অর্থ য়ুম্ফম্ ওইবা থীবা",
        "mai": "🔎 अर्थ-आधारित खोज",
        "sat": "🔎 ᱢᱮᱱᱮᱛ-ᱟᱱᱟᱜ ᱥᱮᱸᱫᱽᱨᱟ",
        "ks": "🔎 معنی خیز ژھانڈ",
        "doi": "🔎 अर्थ-अधारत खोज",
        "brx": "🔎 ओंथि-फारसे नायगिर",
        "sd": "🔎 معنوي ڳولا",
    },
    "tab_variant": {
        "en": "⚖️ Variant Comparison",
        "ta": "⚖️ பிரதி ஒப்பீடு (Variant Comparison)",
        "hi": "⚖️ पाठ तुलना एवं भिन्नता (Variant AI)",
        "te": "⚖️ తాళపత్ర పోలిక & భేదాలు",
        "kn": "⚖️ ಆವೃತ್ತಿ ಹೋಲಿಕೆ & ವ್ಯತ್ಯಾಸ",
        "ml": "⚖️ വകഭേദ താരതമ്യം",
        "bn": "⚖️ রূপান্তর তুলনা ও পার্থক্য",
        "mr": "⚖️ आवृत्ती तुलना व भेद",
        "gu": "⚖️ આવૃત્તિ સરખામણી",
        "pa": "⚖️ ਰੂਪਾਂਤਰ ਤੁਲਨਾ",
        "or": "⚖️ ରୂପାନ୍ତର ତୁଳନା",
        "as": "⚖️ ৰূপান্তৰ তুলনা",
        "ur": "⚖️ نسخوں کا تقابل (Variant AI)",
        "sa": "⚖️ पाण्डुलिपि-पाठभेद-तुलना",
        "ne": "⚖️ संस्करण तुलना",
        "kok": "⚖️ आवृत्ती तुलना",
        "mni": "⚖️ শক্লোন চাংদম্নবা",
        "mai": "⚖️ पाठभेद तुलना",
        "sat": "⚖️ ᱨᱩᱯ ᱛᱩᱞᱟᱹᱡᱚᱠᱷᱟ",
        "ks": "⚖️ نسخن ہند تقابل",
        "doi": "⚖️ रूप भेद तुलना",
        "brx": "⚖️ महर रुजुनाय",
        "sd": "⚖️ نسخن جي ڀيٽ",
    },
    "tab_timeline": {
        "en": "⏳ Historical Timeline",
        "ta": "⏳ வரலாற்றுக் காலவரிசை (Historical Timeline)",
        "hi": "⏳ ऐतिहासिक समयरेखा (Timeline)",
        "te": "⏳ చారిత్రక కాలక్రమం",
        "kn": "⏳ ಐತಿಹಾಸಿಕ ಕಾಲರೇಖೆ",
        "ml": "⏳ ചരിത്ര കാലഗണന",
        "bn": "⏳ ঐতিহাসিক সময়রেখা",
        "mr": "⏳ ऐतिहासिक कालरेषा",
        "gu": "⏳ ઐતિહાસિક સમયરેખા",
        "pa": "⏳ ਇਤਿਹਾਸਕ ਸਮਾਂ-ਰੇਖਾ",
        "or": "⏳ ଐତିହାସିକ ସମୟରେଖା",
        "as": "⏳ ঐতিহাসিক সময়ৰেখা",
        "ur": "⏳ تاریخی ٹائم لائن",
        "sa": "⏳ ऐतिहासिक-कालक्रमः",
        "ne": "⏳ ऐतिहासिक समयरेखा",
        "kok": "⏳ ऐतिहासीक कालवळ",
        "mni": "⏳ পুৱারীগী মতমগী পরিং",
        "mai": "⏳ ऐतिहासिक कालक्रम",
        "sat": "⏳ ᱱᱟᱜᱟᱢ ᱚᱠᱛᱚ-ᱜᱟᱨ",
        "ks": "⏳ تٲریخی وقت لائن",
        "doi": "⏳ ऐतिहासिक समें-रेखा",
        "brx": "⏳ जारिमिन सम-फार",
        "sd": "⏳ تاريخي وقت جو ڏيک",
    },
    "tab_voice": {
        "en": "🔊 Smart Voice Reading",
        "ta": "🔊 தமிழ் குரல் வாசிப்பு (Smart Voice Reading)",
        "hi": "🔊 तमिल वाणी वाचन (Voice Reading)",
        "te": "🔊 తమిళ స్వర పఠనం",
        "kn": "🔊 ತಮಿಳು ಧ್ವನಿ ವಾಚನ",
        "ml": "🔊 തമിഴ് ശബ്ദ വായന",
        "bn": "🔊 তামিল কণ্ঠ পাঠ",
        "mr": "🔊 तमिळ वाणी वाचन",
        "gu": "🔊 તમિલ વાણી વાંચન",
        "pa": "🔊 ਤਮਿਲ ਅਵਾਜ਼ ਪਾਠ",
        "or": "🔊 ତାମିଲ କଣ୍ଠ ପଠନ",
        "as": "🔊 তামিল ধ্বনি পঠন",
        "ur": "🔊 تمل صوتی قرأت (Voice Reading)",
        "sa": "🔊 तमिल-वाणी-वाचनम्",
        "ne": "🔊 तमिल वाणी वाचन",
        "kok": "🔊 तमिळ आवाज वाचन",
        "mni": "🔊 তামিল খোন্থোক পাবা",
        "mai": "🔊 तमिल वाणी वाचन",
        "sat": "🔊 ᱛᱟᱢᱤᱞ ᱟᱲᱟᱝ ᱯᱟᱲᱦᱟᱣ",
        "ks": "🔊 تمل آواز پرن",
        "doi": "🔊 तमिल आवाज पाठ",
        "brx": "🔊 तामिल राव फरायनाय",
        "sd": "🔊 تمل آوازي پڙهڻي",
    },
    "tab_eval_verify": {
        "en": "🔬 Evaluation & Verification",
        "ta": "🔬 மதிப்பீடு மற்றும் சரிபார்ப்பு (Evaluation & Verification)",
        "hi": "🔬 मूल्यांकन एवं मानव सत्यापन",
        "te": "🔬 మూల్యాంకనం & ధృవీకరణ",
        "kn": "🔬 ಮೌಲ್ಯಮಾಪನ & ಪರಿಶೀಲನೆ",
        "ml": "🔬 മൂല്യനിർണ്ണയം & സ്ഥിരീകരണം",
        "bn": "🔬 মূল্যায়ন ও মানব যাচাইকরণ",
        "mr": "🔬 मूल्यांकन आणि मानवी पडताळणी",
        "gu": "🔬 મૂલ્યાંકન અને ચકાસણી",
        "pa": "🔬 ਮੁਲਾਂਕਣ ਅਤੇ ਪੜਤਾਲ",
        "or": "🔬 ମୂଲ୍ୟାଙ୍କନ ଏବଂ ଯାଞ୍ଚ",
        "as": "🔬 মূল্যায়ন আৰু পৰীক্ষণ",
        "ur": "🔬 جانچ اور تصدیق (Evaluation & Verification)",
        "sa": "🔬 मूल्याङ्कनं प्रमाणिकरणं च",
        "ne": "🔬 मूल्याङ्कन र प्रमाणीकरण",
        "kok": "🔬 मोलमापणी आनी खात्री",
        "mni": "🔬 য়েংশিনবা অমসুং চৎনহনবা",
        "mai": "🔬 मूल्यांकन आ प्रमाणीकरण",
        "sat": "🔬 ᱵᱤᱰᱟᱹᱣ ᱟᱨ ᱥᱟᱹᱨᱤᱭᱟᱹᱛ",
        "ks": "🔬 جانچ تہٕ تصدیق",
        "doi": "🔬 मूल्यांकन ते तस्दीक",
        "brx": "🔬 आनजाद आरो थारथि",
        "sd": "🔬 جاچ ۽ تصديق",
    },
    "tab_library": {
        "en": "📚 Digital Library & Canon",
        "ta": "📚 டிஜிட்டல் நூலகம் (Digital Library & Canon)",
        "hi": "📚 डिजिटल पुस्तकालय एवं संग्रह",
        "te": "📚 డిజిటల్ గ్రంథాలయం",
        "kn": "📚 ಡಿಜಿಟಲ್ ಗ್ರಂಥಾಲಯ",
        "ml": "📚 ഡിജിറ്റൽ ലൈബ്രറി",
        "bn": "📚 ডিজিটাল লাইব্রেরি ও সংকলন",
        "mr": "📚 डिजिटल ग्रंथालय व संग्रह",
        "gu": "📚 ડિજિટલ પુસ્તકાલય",
        "pa": "📚 ਡਿਜੀਟਲ ਲਾਇਬ੍ਰੇਰੀ",
        "or": "📚 ଡିଜିଟାଲ୍ ପାଠାଗାର",
        "as": "📚 ডিজিটেল পুথিভঁৰাল",
        "ur": "📚 ڈیجیٹل کتب خانہ اور ذخیرہ",
        "sa": "📚 डिजिटल-पुस्तकालयः",
        "ne": "📚 डिजिटल पुस्तकालय",
        "kok": "📚 डिजिटल वाचनालय",
        "mni": "📚 দিজিতাল লাইরিকশং",
        "mai": "📚 डिजिटल पुस्तकालय",
        "sat": "📚 ᱰᱤᱡᱤᱴᱟᱞ ᱯᱚᱛᱚᱵ ᱜᱟᱲ",
        "ks": "📚 ڈیجیٹل لائبریشن",
        "doi": "📚 डिजिटल पुस्तकालय",
        "brx": "📚 दिजिताल बिजाबख'था",
        "sd": "📚 ڊيجيٽل لائبريري",
    },
    "tab_security_admin": {
        "en": "🛡️ Security & Admin",
        "ta": "🛡️ பாதுகாப்பு மற்றும் அமைப்புகள் (Security & Admin)",
        "hi": "🛡️ सुरक्षा, शासन एवं सेटिंग्स",
        "te": "🛡️ భద్రత & నిర్వాహణ",
        "kn": "🛡️ ಭದ್ರತೆ & ಆಡಳಿತ",
        "ml": "🛡️ സുരക്ഷ & ക്രമീകരണങ്ങൾ",
        "bn": "🛡️ নিরাপত্তা ও প্রশাসন",
        "mr": "🛡️ सुरक्षा आणि प्रशासन",
        "gu": "🛡️ સુરક્ષા અને સેટિંગ્સ",
        "pa": "🛡️ ਸੁਰੱਖਿਆ ਅਤੇ ਪ੍ਰਬੰਧਨ",
        "or": "🛡️ ସୁରକ୍ଷା ଏବଂ ପ୍ରଶାସନ",
        "as": "🛡️ নিৰাপত্তা আৰু প্ৰশাসন",
        "ur": "🛡️ سیکورٹی اور ایڈمن سیٹنگز",
        "sa": "🛡️ सुरक्षा प्रशासनं च",
        "ne": "🛡️ सुरक्षा र प्रशासन",
        "kok": "🛡️ सुरक्षीतता आनी प्रशासन",
        "mni": "🛡️ ঙাক-শেন অমসুং ওফিস",
        "mai": "🛡️ सुरक्षा आ प्रशासन",
        "sat": "🛡️ ᱨᱩᱠᱷᱤᱭᱟᱹ ᱟᱨ ᱥᱟᱥᱚᱱ",
        "ks": "🛡️ حفاظت تہٕ ایڈمن",
        "doi": "🛡️ सुरक्षा ते प्रबंध",
        "brx": "🛡️ रैखा आरो खुंथाय",
        "sd": "🛡️ سيڪيورٽي ۽ انتظاميه",
    },

    # --- UI Elements & Action Buttons ---
    "language_selector_label": {
        "en": "🌐 Interface Language (భారతీయ భాషలు / Indian Languages):",
        "ta": "🌐 இடைமுக மொழி (22 இந்திய மொழிகள் + English):",
        "hi": "🌐 इंटरफ़ेस भाषा (22 अनुसूचित भाषाएँ + English):",
        "te": "🌐 ఇంటర్ఫేస్ భాష (22 భారతీయ భాషలు + English):",
        "kn": "🌐 ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ (22 ಭಾರತೀಯ ಭಾಷೆಗಳು + English):",
        "ml": "🌐 ഇന്റർഫേസ് ഭാഷ (22 ഔദ്യോഗിക ഭാഷകൾ + English):",
        "bn": "🌐 ইন্টারফেস ভাষা (২২টি ভারতীয় ভাষা + English):",
        "mr": "🌐 इंटरफेस भाषा (२२ भारतीय भाषा + English):",
        "ur": "🌐 انٹرفیس زبان (22 ہندوستانی زبانیں + English):",
        "sa": "🌐 अन्तर्मुख-भाषा (२२ भारतीय-भाषाः + English):",
    },
    "archive_controls": {
        "en": "🏛️ Archive Controls",
        "ta": "🏛️ களஞ்சியக் கட்டுப்பாடுகள் (Archive Controls)",
        "hi": "🏛️ अभिलेखागार नियंत्रण (Archive Controls)",
        "te": "🏛️ ఆర్కైవ్ నియంత్రణలు",
        "kn": "🏛️ ದಾಖಲೆ ನಿಯಂತ್ರಣಗಳು",
        "ml": "🏛️ ആർക്കൈവ് നിയന്ത്രണങ്ങൾ",
        "bn": "🏛️ সংরক্ষণাগার নিয়ন্ত্রণ",
        "mr": "🏛️ अभिलेखागार नियंत्रणे",
        "ur": "🏛️ آرکائیو کنٹرولز",
    },
    "ocr_mode_label": {
        "en": "Select OCR Engine:",
        "ta": "OCR முறையைத் தேர்ந்தெடுக்கவும்:",
        "hi": "ओसीआर इंजन का चयन करें:",
        "te": "OCR మోడ్‌ను ఎంచుకోండి:",
        "kn": "OCR ವಿಧಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "ml": "OCR രീതി തിരഞ്ഞെടുക്കുക:",
        "bn": "ওসিআর মোড নির্বাচন করুন:",
        "mr": "ओसीआर पद्धत निवडा:",
        "ur": "OCR موڈ منتخب کریں:",
    },
    "scholar_role_label": {
        "en": "User Scholar Role (RBAC):",
        "ta": "பயனர் உரிமை நிலை (User Access Level):",
        "hi": "विद्वान भूमिका (RBAC):",
        "te": "పండిత పాత్ర (RBAC):",
        "kn": "ವಿದ್ವಾಂಸರ ಪಾತ್ರ (RBAC):",
        "ml": "ഉപയോക്തൃ പദവി (RBAC):",
        "bn": "ব্যবহারকারী ভূমিকা (RBAC):",
        "mr": "वापरकर्ता भूमिका (RBAC):",
        "ur": "صارف کا کردار (RBAC):",
    },
    "upload_panel_title": {
        "en": "📄 Upload Document (Images, PDF, Word DOCX, TXT)",
        "ta": "📄 ஆவணத்தைப் பதிவேற்றவும் (Upload Document)",
        "hi": "📄 दस्तावेज़ अपलोड करें (Images, PDF, Word DOCX, TXT)",
        "te": "📄 పత్రాన్ని అప్‌లోడ్ చేయండి (Images, PDF, DOCX, TXT)",
        "kn": "📄 ದಾಖಲೆಯನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "ml": "📄 പ്രമാണം അപ്‌ലോഡ് ചെയ്യുക",
        "bn": "📄 নথি আপলোড করুন",
        "mr": "📄 दस्तऐवज अपलोड करा",
        "ur": "📄 دستاویز اپ لوڈ کریں",
    },
    "btn_load_sample": {
        "en": "📜 Load Sample Manuscript",
        "ta": "📜 மாதிரி ஆவணம் (Load Sample)",
        "hi": "📜 नमूना पांडुलिपि लोड करें",
        "te": "📜 నమూనా పత్రాన్ని లోడ్ చేయండి",
        "kn": "📜 ಮಾದರಿ ದಾಖಲೆಯನ್ನು ಲೋಡ್ ಮಾಡಿ",
        "ml": "📜 മാതൃകാ രേഖ ലോഡ് ചെയ്യുക",
        "bn": "📜 নমুনা পাণ্ডুলিপি লোড করুন",
        "mr": "📜 नमुना दस्तऐवज लोड करा",
        "ur": "📜 نمونہ دستاویز لوڈ کریں",
    },
    "btn_clear_doc": {
        "en": "🗑️ Clear Document",
        "ta": "🗑️ ஆவணத்தை அழிக்கவும் (Clear)",
        "hi": "🗑️ दस्तावेज़ हटाएं (Clear)",
        "te": "🗑️ పత్రాన్ని తొలగించండి",
        "kn": "🗑️ ತೆರವುಗೊಳಿಸಿ (Clear)",
        "ml": "🗑️ മായ്‌ക്കുക (Clear)",
        "bn": "🗑️ পরিষ্কার করুন",
        "mr": "🗑️ हटवा (Clear)",
        "ur": "🗑️ دستاویز صاف کریں",
    },
    "btn_run_ocr": {
        "en": "🔍 Run Tamil Dual OCR Engine",
        "ta": "🔍 OCR உரையை பிரித்தெடு (Run OCR)",
        "hi": "🔍 तमिल ओसीआर निष्पादित करें",
        "te": "🔍 OCR ప్రారంభించండి",
        "kn": "🔍 OCR ಚಲಾಯಿಸಿ",
        "ml": "🔍 OCR പ്രക്രിയ ആരംഭിക്കുക",
        "bn": "🔍 ওসিআর চালান",
        "mr": "🔍 ओसीआर चालवा",
        "ur": "🔍 OCR کا عمل شروع کریں",
    },
    "live_stats_title": {
        "en": "Live Heritage Preservation Metrics",
        "ta": "களஞ்சிய நேரலை புள்ளிவிவரங்கள்",
        "hi": "लाइव विरासत संरक्षण मेट्रिक्स",
        "te": "ప్రత్యక్ష పురావస్తు గణాంకాలు",
        "kn": "ಲೈವ್ ಪರಂಪರೆ ಸಂರಕ್ಷಣಾ ಅಂಕಿಅಂಶಗಳು",
        "ml": "തത്സമയ പൈതൃക സ്ഥിതിവിവരക്കണക്കുകൾ",
        "bn": "লাইভ ঐতিহ্য সংরক্ষণ মেট্রিক্স",
        "mr": "थेट वारसा संवर्धन मेट्रिक्स",
        "ur": "لائیو ہیریٹیج تحفظ میٹرکس",
    },
    "stat_canon_docs": {
        "en": "📜 Canonical Manuscripts",
        "ta": "📜 களஞ்சியச் சுவடிகள் (Canon)",
        "hi": "📜 प्रमाणित पांडुलिपियाँ",
        "te": "📜 ప్రామాణిక గ్రంథాలు",
        "kn": "📜 ಪ್ರಮಾಣಿತ ಹಸ್ತಪ್ರತಿಗಳು",
        "ml": "📜 ആധികാരിക ഗ്രന്ഥങ്ങൾ",
        "bn": "📜 প্রামাণ্য পাণ্ডুলিপি",
        "mr": "📜 प्रामाणिक हस्तलिखिते",
        "ur": "📜 مستند مخطوطات",
    },
    "stat_ai_subsystems": {
        "en": "🧠 Verified AI Subsystems",
        "ta": "🧠 AI நுண்ணறிவுத் திறன்கள்",
        "hi": "🧠 सत्यापित एआई उपप्रणालियाँ",
        "te": "🧠 ధృవీకరించిన AI ఉపవ్యవస్థలు",
        "kn": "🧠 ಪರಿಶೀಲಿಸಿದ AI ವ್ಯವಸ್ಥೆಗಳು",
        "ml": "🧠 സ്ഥിരീകരിച്ച AI സിസ്റ്റങ്ങൾ",
        "bn": "🧠 যাচাইকৃত এআই সিস্টেম",
        "mr": "🧠 सत्यापित एआय प्रणाल्या",
        "ur": "🧠 تصدیق شدہ AI سسٹمز",
    },
    "stat_source_traceability": {
        "en": "🛡️ Evidence Traceability",
        "ta": "🛡️ சான்று நம்பகத்தன்மை",
        "hi": "🛡️ साक्ष्य प्रामाणिकता (100%)",
        "te": "🛡️ ఆధార విశ్వసనీయత",
        "kn": "🛡️ ಸಾಕ್ಷ್ಯಾಧಾರ ವಿಶ್ವಾಸಾರ್ಹತೆ",
        "ml": "🛡️ തെളിവ് ആധികാരികത",
        "bn": "🛡️ প্রমাণ নির্ভরযোগ্যতা",
        "mr": "🛡️ पुरावा विश्वासार्हता",
        "ur": "🛡️ ثبوتی صداقت",
    },
    "stat_dual_engines": {
        "en": "⚡ Dual OCR Engines",
        "ta": "⚡ இரட்டை OCR இயந்திரங்கள்",
        "hi": "⚡ दोहरा ओसीआर इंजन",
        "te": "⚡ ద్వంద్వ OCR ఇంజిన్లు",
        "kn": "⚡ ಡ್ಯುಯಲ್ OCR ಎಂಜಿನ್",
        "ml": "⚡ ഇരട്ട OCR എഞ്ചിനുകൾ",
        "bn": "⚡ ডুয়াল ওসিআর ইঞ্জিন",
        "mr": "⚡ दुहेरी ओसीआर इंजिन",
        "ur": "⚡ دوہری OCR انجن",
    },
    "lang_capability_notice": {
        "en": "ℹ️ <b>Language Architecture Notice:</b> Interface translated into {lang}. The underlying epigraphical texts and OCR/Voice engines operate authentically on original Tamil manuscripts to preserve historical fidelity.",
        "ta": "ℹ️ <b>மொழித் தகவல்:</b> இடைமுகம் {lang} மொழியில் காட்டப்படுகிறது. சுவடியின் மூல வாசகங்களும் OCR/குரல் இயந்திரங்களும் வரலாற்றின் நம்பகத்தன்மையைப் பாதுகாக்க அசல் தமிழ் வடிவிலேயே இயங்குகின்றன.",
        "hi": "ℹ️ <b>भाषा सूचना:</b> इंटरफ़ेस {lang} में अनुवादित है। ऐतिहासिक प्रामाणिकता बनाए रखने के लिए मूल पांडुलिपि पाठ और ओसीआर/वाणी मॉडल प्रामाणिक तमिल में कार्य करते हैं।",
        "te": "ℹ️ <b>భాషా సమాచారం:</b> ఇంటర్‌ఫేస్ {lang} లో అనువదించబడింది. చారిత్రక ప్రామాణికత కొరకు మూల వ్రాతప్రతులు మరియు OCR/స్వర నమూనాలు తమిళంలోనే పనిచేస్తాయి.",
        "kn": "ℹ️ <b>ಭಾಷಾ ಮಾಹಿತಿ:</b> ಇಂಟರ್ಫೇಸ್ {lang} ನಲ್ಲಿ ಅನುವಾದಗೊಂಡಿದೆ. ಮೂಲ ಹಸ್ತಪ್ರತಿಗಳು ತಮಿಳಿನಲ್ಲಿಯೇ ಸುರಕ್ಷಿತವಾಗಿವೆ.",
        "ml": "ℹ️ <b>ഭാഷാ അറിയിപ്പ്:</b> ഇന്റർഫേസ് {lang} ഭാഷയിലാണ്. യഥാർത്ഥ ഗ്രന്ഥങ്ങൾ തമിഴിൽ തന്നെ സംരക്ഷിക്കപ്പെടുന്നു.",
        "bn": "ℹ️ <b>ভাষা নোটিশ:</b> ইন্টারফেসটি {lang} ভাষায় প্রদর্শিত হচ্ছে। ঐতিহাসিক সত্যতা বজায় রাখতে মূল পাণ্ডুলিপি পাঠ তামিলে সংরক্ষিত।",
        "mr": "ℹ️ <b>भाषा सूचना:</b> इंटरफेस {lang} मध्ये अनुवादित आहे. मूळ हस्तलिखित पाठ तमिळमध्येच राहील.",
        "ur": "ℹ️ <b>زبان کی اطلاع:</b> انٹرفیس کا ترجمہ {lang} میں کیا گیا ہے۔ تاریخی درستگی برقرار رکھنے کے لیے بنیادی مخطوطہ تمل میں ہی رہے گا۔",
    },
}


# =====================================================================
# 3. Translation Helper Function
# =====================================================================
def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Retrieves the translation for `key` in the requested or session language.
    Cascade order: requested lang -> 'en' -> 'ta' -> key.
    Supports kwargs string interpolation.
    """
    if not lang:
        try:
            lang = st.session_state.get("app_language", "ta")
        except Exception:
            lang = "ta"
            
    # Clean language code
    lang = (lang or "ta").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "ta"
        
    translations_for_key = TRANSLATIONS.get(key, {})
    
    # Cascade lookup
    text = translations_for_key.get(lang)
    if not text:
        text = translations_for_key.get("en")
    if not text:
        text = translations_for_key.get("ta")
    if not text:
        text = key
        
    # Format with kwargs if provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
            
    return text


def get_current_language() -> str:
    """Returns the currently active language code from session state."""
    try:
        return st.session_state.get("app_language", "ta")
    except Exception:
        return "ta"


def is_rtl(lang: Optional[str] = None) -> bool:
    """Returns True if the language uses Right-to-Left writing direction."""
    code = lang if lang else get_current_language()
    meta = SUPPORTED_LANGUAGES.get(code, {})
    return meta.get("direction", "ltr") == "rtl"


# =====================================================================
# 4. Prominent & Responsive Language Selector Component
# =====================================================================
def render_language_selector(sidebar: bool = False, key_suffix: str = ""):
    """
    Renders an accessible language selector for India's 22 Scheduled Languages + English.
    Preserves all uploaded files, OCR outputs, and workflow states across language switches.
    """
    if "app_language" not in st.session_state:
        st.session_state.app_language = "ta"
        
    current_code = st.session_state.app_language
    codes = list(SUPPORTED_LANGUAGES.keys())
    
    def format_lang_option(code: str) -> str:
        info = SUPPORTED_LANGUAGES[code]
        flag = info.get("flag", "🌐")
        native = info.get("native_name", "")
        english_name = info.get("name", "")
        if code == "en":
            return f"{flag} {english_name}"
        elif code == "ta":
            return f"{flag} {native} ({english_name})"
        else:
            return f"{flag} {native} · {english_name}"
            
    current_idx = codes.index(current_code) if current_code in codes else codes.index("ta")
    
    label = t("language_selector_label", current_code)
    
    selected_code = st.selectbox(
        label,
        options=codes,
        index=current_idx,
        format_func=format_lang_option,
        key=f"lang_selector_widget_{'side' if sidebar else 'top'}_{key_suffix}",
        help="Select any of the 22 Eighth Schedule Languages of India or English. Original manuscript texts remain in authentic Tamil.",
    )
    
    if selected_code != st.session_state.app_language:
        st.session_state.app_language = selected_code
        st.rerun()


def render_language_capability_badge():
    """Renders a transparent capability status card for the current language."""
    cur_lang = get_current_language()
    info = SUPPORTED_LANGUAGES.get(cur_lang, SUPPORTED_LANGUAGES["ta"])
    lang_name = f"{info.get('native_name')} ({info.get('name')})"
    notice = t("lang_capability_notice", cur_lang, lang=lang_name)
    
    st.markdown(
        f"""
        <div style="background: rgba(212, 175, 55, 0.08); border: 1px solid #734F27; border-radius: 6px; padding: 10px 14px; margin-bottom: 14px; font-size: 0.88rem; color: #E0C9A6;">
            {notice}
        </div>
        """,
        unsafe_allow_html=True,
    )
