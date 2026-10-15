# தமிழ்ச்சுவடி AI — Tamil Heritage Preservation Platform
### Phase 5: Final Production-Ready Integration & Architectural Reference

**தமிழ்ச்சுவடி AI** (Tamil Heritage AI) is an enterprise-grade digital humanities and preservation platform engineered specifically for ancient Tamil printed texts, stone inscriptions (கல்வெட்டுகள்), copper plate grants (செப்பேடுகள்), and weathered palm-leaf manuscripts (ஓலைச்சுவடிகள்).

The platform pairs a high-throughput **Dual OCR Engine** (classical Tesseract LSTM + Hugging Face Vision Transformer `TrOCR: ViT-Base + Tamil-RoBERTa`) with **18 fully integrated AI heritage capabilities**, organized into **12 primary heritage navigation sections**, featuring role-based access control, tamper-evident audit logging, and zero-hallucination epigraphical grounding.

---

## 🏛️ System Architecture

```
                                    +------------------------------------------------------+
                                    |         Uploaded Document (Images / PDFs)           |
                                    +--------------------------+---------------------------+
                                                               |
                                            +------------------v------------------+
                                            |   Feature 14: Image Preprocessing   |
                                            | (Grayscale, Contrast, Denoise, Otsu)|
                                            +------------------+------------------+
                                                               |
                                            +------------------+------------------+
                                            |                                     |
                             +--------------v--------------+       +--------------v--------------+
                             |     Tesseract OCR Engine    |       |    TrOCR Vision Transformer  |
                             |   (Layout & image_to_data)  |       |  (ViT-Base + Tamil-RoBERTa) |
                             +--------------+--------------+       +--------------+--------------+
                                            |                                     |
                                            +------------------+------------------+
                                                               |
                                            +------------------v------------------+
                                            |    Feature 4: Dual OCR Comparison   |
                                            | (Similarity Ratio, Char/Word Diffs) |
                                            +------------------+------------------+
                                                               |
                                            +------------------v------------------+
                                            |    Feature 12: Editable Workspace   |
                                            |    (UTF-8 TXT & JSON Provenance)    |
                                            +------------------+------------------+
                                                               |
    +----------------------------------------------------------+----------------------------------------------------------+
    |                                                          |                                                          |
+---v---------------------------+  +---------------------------v---+  +---------------------------v---+  +----------------v---------------------------+
| F1: OCR Text Correction       |  | F2: Unicode Normalization     |  | F3: OCR Confidence & Review   |  | F5: Tamil Text Cleanup                    |
| (Error detection + Suggestion)|  | (Canonical NFC + Split Vowels)|  | (Authentic Tesseract matrix)  |  | (Spaces, hyphens, scan noise artifacts)   |
+-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------------------+
    |                                                          |                                                          |
+---v---------------------------+  +---------------------------v---+  +---------------------------v---+  +----------------v---------------------------+
| F6: Paragraph Reconstruction  |  | F7: Ancient Term Preservation |  | F8: Mixed Tamil-English       |  | F9: In-Document Search                    |
| (Flowing prose from scans)    |  | (Sangam terminology protection|  | (Bilingual & numerals support)|  | (Fast query match with highlighted text)  |
+-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------------------+
    |                                                          |                                                          |
+---v---------------------------+  +---------------------------v---+  +---------------------------v---+  +----------------v---------------------------+
| F10: Batch OCR Processing     |  | F11: PDF Page-wise OCR        |  | F13: OCR Processing History   |  | F15: AI Text Analysis                     |
| (Multi-file queue & export)   |  | (Page selection & rendering)  |  | (Audit log, reload, clear)    |  | (Local frequency NLP & extractive summary)|
+-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------------------+
                                                               |
                                    +--------------------------v---------------------------+
                                    |       15 ADVANCED HERITAGE INTELLIGENCE TABS         |
                                    +------------------------------------------------------+
```

---

## 🏛️ 12 Core Platform Sections

The interface is structured into 12 dedicated, Chola-heritage-styled sections:

| # | Section Name (Tamil / English) | Primary Purpose & Features |
|:---:|---|---|
| **1** | **🏛️ முகப்பு (Home)** | Chola architectural hero banner, live platform metrics, 1-Click Interactive Showcase presets (Thanjavur, Silappadikaram, Tolkappiyam), and navigation roadmap. |
| **2** | **📑 நூல்களை டிஜிட்டல் மயமாக்குதல் (Digitization & Dual OCR)** | Multi-format upload (JPG, PNG, WEBP, PDF, Word DOCX, TXT), preprocessing (grayscale, contrast, denoise), dual OCR comparison, and word-level confidence. |
| **3** | **✍️ OCR உரைத் திருத்தம் (OCR Correction Review)** | Side-by-side human-in-the-loop proofreading, CER/WER diff highlighting, and separate immutable storage of corrections. |
| **4** | **🤖 AI கையெழுத்துப் பிரதி உதவியாளர் (Manuscript Assistant)** | Evidence-grounded bilingual Q&A, exact passage citation cards, confidence scores, and strict zero-hallucination refusal for unsupported claims. |
| **5** | **🕸️ அறிவு வரைபடம் (Knowledge Explorer)** | Named Entity Recognition (Persons, Places, Works, Dynasties, Concepts), entity-relation triples, and source evidence inspector. |
| **6** | **🔎 பொருள் சார்ந்த தேடல் (Semantic Search)** | Meaning-based semantic vector retrieval across manuscripts with TF-IDF fallback, query expansion, and highlighted excerpts. |
| **7** | **⚖️ பிரதி ஒப்பீடு (Variant Comparison)** | Apparatus criticus AI, line-by-line alignment, Levenshtein distance, and orthographic vs substantive variation classification. |
| **8** | **⏳ வரலாற்றுக் காலவரிசை (Historical Timeline)** | Extracted chronology of Sangam, Chola, Pandiya, and Pallava eras with historical certainty markers and source links. |
| **9** | **🔊 தமிழ் குரல் வாசிப்பு (Smart Voice Reading)** | Natural Google Neural Tamil voice synthesis (gTTS), speed control (0.8x study mode to 1.25x), and in-memory `io.BytesIO` audio streaming. |
| **10** | **🔬 மதிப்பீடு மற்றும் சரிபார்ப்பு (Evaluation & Verification)** | Real empirical benchmark metrics (CER, WER, Precision@k) + Human-in-the-Loop knowledge claim verification store with atomic writes. |
| **11** | **📚 டிஜிட்டல் நூலகம் (Digital Library & Canon)** | Digital Library browser, Cross-Manuscript Discovery (thematic affinities & shared motifs), and Tamil Literary Theme Analyzer. |
| **12** | **🛡️ பாதுகாப்பு மற்றும் அமைப்புகள் (Security & Admin)** | Role-Based Access Control (RBAC), multi-lingual prompt injection defense tester, 5 Core NLP lab tools, and session audit history. |

---

## 💻 Hardware & Software Requirements

- **Operating System:** Windows 10 / 11, Linux (Ubuntu 20.04+), or macOS
- **Python Version:** Python 3.10 to Python 3.14 (Tested on Python 3.14.8)
- **Memory (RAM):** 8 GB minimum (16 GB recommended for batch Vision Transformer OCR)
- **Processor / GPU:**
  - CPU: Intel Core i5 / AMD Ryzen 5 or higher
  - GPU (Optional): NVIDIA RTX (CUDA supported, e.g. RTX 3050 4GB); automatic CPU fallback supported
- **External Dependencies:**
  - Tesseract OCR v5.0+ with `tam` (Tamil) and `eng` (English) traineddata packs

---

## ⚙️ Installation and Startup Guide

### 1. Clone or Open the Workspace
```powershell
cd c:\Users\jagad\OneDrive\Documents\TamilHeritageAI
```

### 2. Verify Python & Virtual Environment
Ensure Python 3.10+ is installed:
```powershell
py --version
```
*(Optional but recommended)* Create and activate a dedicated virtual environment:
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies
Install core application dependencies:
```powershell
py -m pip install -r requirements.txt
```

### 4. Verify Tesseract OCR Installation
Verify that Tesseract OCR is available in your PATH:
```powershell
tesseract --version
```
Ensure Tamil language support is installed:
```powershell
tesseract --list-langs
# Output must include 'tam' and 'eng'
```
*If Tesseract is not in your PATH on Windows, install from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and ensure `C:\Program Files\Tesseract-OCR` is added to your Environment PATH.*

### 5. Launch the Streamlit Web Application
Run the Streamlit server:
```powershell
py -m streamlit run app.py --server.port=8501
```

Open your browser and navigate to:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🔐 Environment Variables Configuration

The platform operates out of the box with zero required external credentials, guaranteeing zero vendor lock-in and complete privacy for rare cultural heritage. Optional environment variables may be configured as needed:

| Variable | Default Value | Description |
|---|---|---|
| `PYTHONIOENCODING` | `utf-8` | **Recommended on Windows:** Ensures stdout/stderr stream handles Tamil Unicode without `cp1252` encoding errors. |
| `TESSDATA_PREFIX` | System default | Optional path to custom directory containing Tesseract `.traineddata` files. |
| `HF_TOKEN` | *None (Optional)* | Hugging Face Access Token for downloading gated Vision Transformer models or avoiding rate limits. |
| `AI_DEVICE` | `auto` | Set to `cuda` to force GPU acceleration, or `cpu` to enforce CPU inference. |
| `STREAMLIT_SERVER_PORT` | `8501` | Local port for Streamlit web server. |

> [!IMPORTANT]
> **Zero Hardcoded Secrets Policy:** No API keys, passwords, or cloud credentials are hardcoded into the source code. All file stores (`knowledge_verification_store.json`, `experiments_log.json`) are self-contained locally.

---

## 🧠 AI Provider & Model Configuration

| Component | Provider / Architecture | Specific Model / Checkpoint | Fallback Mechanism |
|---|---|---|---|
| **Dual OCR (Baseline)** | Tesseract OCR v5 LSTM Engine | `tam.traineddata` + `eng.traineddata` | Standard PSM 3/6 layout analysis with word-level confidence |
| **Dual OCR (Advanced)** | Hugging Face Transformers | `sabaridsnfuji/Tamil_Offline_Handwritten_OCR` (Vision Transformer `google/vit-base-patch16-224-in21k` + `d42kw01f/Tamil-RoBERTa`) | Automatic graceful fallback to Tesseract baseline when GPU memory is constrained |
| **Voice Reading (TTS)** | Google Neural Voice Engine | `gTTS` (Tamil locale `ta`, `co.in` tld) | Chunked sequential streaming (150-char limit) with 0.8x slow study mode; clean offline diagnostic message |
| **Semantic Search** | Local TF-ISF & Ontological Clustering | 7 Classical Historical Clusters (Monuments, Dynasties, Grammar, Epics, Geography, Chronology) | Deterministic lexical matching; zero remote API latency |
| **Grounded Assistant** | Rule-Guided Extractive Synthesizer | Contextual Sentence Alignment with Exact Lexical Match | Guaranteed refusal response upon insufficient evidence |

---

## 🗄️ Database & Persistent Storage Requirements

The platform uses lightweight, transactional, file-based JSON stores designed for cultural archives without requiring complex database server deployments (no PostgreSQL, MySQL, or MongoDB services required):

1. **`knowledge_verification_store.json`**:
   - Stores human-in-the-loop review statuses (`APPROVED`, `REJECTED`, `FLAGGED_FOR_EXPERT`, `PENDING_REVIEW`).
   - Automatically created in the application root on first review.
2. **`knowledge_verification_audit.json`**:
   - Append-only, tamper-evident audit ledger recording every epigraphical decision, user role, ISO timestamp, and diff.
3. **`experiments_log.json`**:
   - Persistent ledger for evaluation benchmarks, CER/WER runs, and model parameters.

---

## 📄 Supported File Formats

### Input Formats (Ingestion)
- **Images:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff` (high-resolution palm leaf scans, temple rubbings, and printed editions)
- **PDF Documents:** `.pdf` (single-page or multi-page documents rasterized at archival resolution via PyMuPDF)
- **Word Documents:** `.docx` (authentic XML extraction using standard Python library with manuscript preview rendering)
- **Plain Text / Transcriptions:** `.txt` (UTF-8 encoded transcriptions and epigraphical field notes)

### Output Formats (Digital Heritage Export)
- **UTF-8 Plain Text (`.txt`):** Canonical NFC normalized text preserving Tamil Unicode.
- **TEI P5 XML (`.xml`):** International Standard Text Encoding Initiative XML with manuscript headers, facsimile references, and metadata.
- **TEI JSON (`.json`):** Structured JSON representation with document provenance, passage divisions, and confidence metrics.
- **HTML Research Dossier (`.html`):** Standalone, printable research report with embedded styling, metadata, and passage breakdowns.
- **Batch Preservation Archive (`.zip`):** Compressed archive containing all processed files in plain text and TEI formats.

---

## 🧪 Comprehensive Test Suites & Verification

The repository includes 5 comprehensive test suites covering unit, functional, research, and end-to-end integration criteria:

```powershell
# 1. Master E2E Integration Suite (Phase 5 - All 12 Acceptance Criteria)
py test_e2e_integration.py

# 2. Phase 4 Advanced Intelligence Suite (Features 11, 12, 13, 14, 15)
py test_phase4_features.py

# 3. Phase 3 Research-Level AI Suite (Features 7, 8, 9, 10)
py test_phase3_features.py

# 4. Phase 2 Advanced AI Upgrade Suite (Features 4, 5, 6)
py test_phase2_features.py

# 5. Master Upgrade Test Suite (Features 1, 2, 3 + OCR Preservation)
py test_master_upgrade.py
```

### Actual Test Execution Output Summary
```
===========================================================================
🏆 test_e2e_integration.py: 12/12 STEPS PASSED 100%
  • Step 1: Server Health & Connectivity (HTTP 200 OK)
  • Step 2 & 3: Dual OCR Execution (Tesseract + TrOCR Vision Transformer)
  • Step 4: Tamil Unicode Normalization & Decomposed Vowels
  • Step 5: AI Manuscript Assistant (Grounded Q&A + Anti-Hallucination)
  • Step 6: Semantic Concept Search Across Manuscripts
  • Step 7: Tamil Knowledge Explorer (NER + Relational Graph)
  • Step 8: Smart Tamil Voice Reading (gTTS Synthesis & Chunking)
  • Step 9: Manuscript Variant Comparison & Timeline Explorer
  • Step 10: OCR Proofreading Review, Source Trust & TEI Export
  • Step 11: Role-Based Access Control & Tamper-Evident Audit
  • Step 12: Graceful Interception of Edge Cases & Invalid Inputs
===========================================================================
```

---

## 🎭 Step-by-Step Repeatable Demonstration Workflow

To conduct a live, evidence-grounded demonstration:

### Step 1: Launch Application
```powershell
py -m streamlit run app.py --server.port=8501
```
Open **[http://localhost:8501](http://localhost:8501)**. Ensure the role selector in the sidebar is set to **`CHIEF_EPIGRAPHIST`** or **`TAMIL_SCHOLAR`**.

### Step 2: Select or Upload a Document
- In the sidebar, select **"தஞ்சைப் பெரிய கோயில் கல்வெட்டு (Brihadisvara Temple Inscription)"** from the Digital Library, or upload `samples/sample_tamil.jpg`.
- Observe the loaded document preview, transcription, and metadata.

### Step 3: Run Dual OCR Workflow
- Click **"Run OCR Extraction"** under the main Dual OCR panel.
- Inspect the side-by-side comparison between **Tesseract OCR Baseline** and **TrOCR Vision Transformer**.
- Review the word-level confidence scores and sequence similarity percentage.

### Step 4: Ask an Evidence-Grounded Question (Tab 1)
- Navigate to **"Tab 1: AI Manuscript Assistant"**.
- Enter the query: `"தஞ்சைப் பெரிய கோயிலைக் கட்டியது யார்?"` *(Who built the Thanjavur Big Temple?)*.
- Click **"கேள்வி கேள் (Ask Assistant)"**.
- **Verified Output:**
  > **ஆவணச் சான்றின்படி:**
  > *"ஸ்வஸ்திஸ்ரீ திருநிலமளந்த முதலாம் இராஜராஜ சோழன் கி.பி. 1010 ஆம் ஆண்டு தஞ்சைப் பெரிய கோயிலைக் கட்டி முடித்தார்."*
  > **சான்றுப் பகுதி:** Passage #1 | **நம்பகத்தன்மை:** 100%

### Step 5: Verify Anti-Hallucination Refusal (Tab 1)
- In Tab 1, enter an ungrounded query: `"அசோகர் எந்த போரில் வெற்றி பெற்றார்?"` *(In which war did Ashoka win?)*.
- **Verified Output:**
  > *மன்னிக்கவும், கேட்கப்பட்ட கேள்விக்கான போதுமான சான்றுகள் இந்த ஆவணத்தில் காணப்படவில்லை (Sufficient evidence to answer this question was not found in the selected manuscript text).*
  > *(The system strictly refuses to fabricate an answer).*

### Step 6: Execute Semantic Conceptual Search (Tab 2)
- Navigate to **"Tab 2: Semantic Manuscript Search"**.
- Enter bilingual query: `"king chola empire"` or Tamil query: `"பெருவுடையார் கோயில் விமானம்"`.
- Observe rank-1 retrieval of the Brihadisvara Temple Inscription with highlighted semantic concept matches (`விமானம்`, `தட்சிண மேரு`, `பெருவுடையார்`).

### Step 7: Experience Smart Tamil Voice Reading (Tab 7)
- Navigate to **"Tab 7: Smart Tamil Voice Reading"**.
- Select **"இயல்பான வேகம் (1.0x Normal)"** or **"கற்றல் முறை (0.8x Slow Study Mode)"**.
- Click **"ஒலி வடிவில் கேட்க (Listen Now)"** to listen to the neural synthesized Tamil voice.

### Step 8: Verify Epigraphist Review & Audit Logging (Tab 14)
- Navigate to **"Tab 14: Epigraphist Review"**.
- Select an entity or claim, record a correction (e.g. changing an entity type to `HISTORICAL_MONARCH`), and click **"சான்றளித்து உறுதிசெய் (Approve with Epigraphical Certification)"**.
- Switch the sidebar role to **`GUEST_VIEWER`** and verify that modification controls are cleanly disabled (read-only enforcement).
- Inspect the live audit log showing the user role, timestamp, and modification diff.

---

## 🛠️ Common Errors and Troubleshooting

### 1. Windows Terminal Unicode Encoding (`UnicodeEncodeError: 'charmap' codec can't encode characters`)
- **Cause:** Windows PowerShell / CMD defaults to legacy `cp1252` encoding.
- **Solution:** Set Python's IO encoding to UTF-8 before running scripts:
  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  ```
  *(All test scripts and `app.py` already include automatic `sys.stdout.reconfigure(encoding="utf-8")` safety guards).*

### 2. Tesseract Not Found (`pytesseract.pytesseract.TesseractNotFoundError`)
- **Cause:** Tesseract executable is not located in the system PATH.
- **Solution:** Add `C:\Program Files\Tesseract-OCR` to your Environment Variables PATH, or set `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"` in `ocr_engine.py`.

### 3. Missing Tamil Traineddata (`tam.traineddata`)
- **Cause:** Tesseract was installed without Tamil language pack.
- **Solution:** Download `tam.traineddata` from [tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata) and place it into `C:\Program Files\Tesseract-OCR\tessdata\`.

### 4. GPU Out-of-Memory with TrOCR
- **Cause:** Large images processed with Vision Transformer on GPUs with less than 4GB VRAM.
- **Solution:** The platform automatically splits manuscripts into horizontal line crops and falls back to CPU inference or Tesseract baseline seamlessly when CUDA memory limits are reached.

### 5. Network Timeout during Voice Reading (gTTS)
- **Cause:** Temporary network latency reaching Google TTS endpoints.
- **Solution:** The voice reading module includes automatic offline diagnostics, audio caching, and graceful error alerts without crashing the application.

---

## 📜 Epigraphical & Technical Disclaimers

1. **Epigraphical Similarity Disclaimer:** Textual and conceptual connections discovered across manuscripts indicate shared thematic motifs or vocabulary and **never prove common authorship, direct historical influence, or genealogical dependence**.
2. **AI Interpretation Transparency:** All thematic categorizations and conceptual groupings generated by AI models are explicitly labeled as `[AI-Generated Interpretation - Not Historical Dogma]` and require epigraphist certification.
3. **Dual-State Preservation:** Original raw OCR transcriptions and AI predictions are never overwritten or discarded; human revisions are recorded as separate attested layers in the archival JSON and TEI audit trail.
4. **Heritage Shield:** Ancient Tamil classical vocabulary from Sangam poetry and Tolkappiyam are protected from automated modern spellchecking alterations.

---

## 📁 Repository File Map

```
TamilHeritageAI/
├── app.py                         # Main Streamlit heritage application (15 tabs)
├── cross_manuscript_discovery.py   # Feature 11 & 12: Cross-Manuscript Discovery & Literary Themes
├── collection_intelligence.py     # Feature 13 & 15: Collection Insights & TEI Export Preservation
├── knowledge_verification.py      # Feature 14: Epigraphist Review & Audit Logging Store
├── ai_evaluation.py               # Feature 7 & 10: AI Evaluation Metrics & Experiment Tracking
├── ocr_review_workflow.py         # Feature 8: Human-in-the-Loop OCR Proofreading & Classical Shield
├── source_trust_layer.py          # Feature 9: Source Traceability & Claim Audit Layer
├── semantic_search.py             # Feature 4: Meaning-based Conceptual Search
├── manuscript_variant_ai.py       # Feature 5: Manuscript Variant Comparison AI
├── timeline_explorer.py           # Feature 6: Historical Chronology & Timeline Explorer
├── manuscript_assistant.py        # Feature 1: Evidence-grounded Q&A Assistant
├── knowledge_explorer.py          # Feature 2: Named Entity Recognition & Knowledge Graph
├── tamil_voice.py                 # Feature 3: Smart Tamil Neural Voice (gTTS)
├── ocr_engine.py                  # Dual OCR Engine (Tesseract + TrOCR + Image Processing)
├── ai_ocr.py                      # Hugging Face Vision Transformer Model Interface
├── tamil_nlp.py                   # Tamil Unicode Normalization, Tokenization & Morphology
├── test_e2e_integration.py        # Phase 5 Master E2E Integration Suite (100% PASS)
├── test_phase4_features.py        # Test suite for Features 11–15 (100% PASS)
├── test_phase3_features.py        # Test suite for Features 7–10 (100% PASS)
├── test_phase2_features.py        # Test suite for Features 4–6 (100% PASS)
├── test_master_upgrade.py         # Test suite for Features 1–3 (100% PASS)
├── requirements.txt               # Production dependencies
└── README.md                      # Complete Architectural & Operational Guide
```
