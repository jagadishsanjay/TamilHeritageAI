"""
Tamil Heritage AI – OCR Engine Module
Provides Tesseract OCR baseline, local Hugging Face AI OCR (Vision Transformer + RoBERTa),
optional Hugging Face Inference API integration, PDF rendering via PyMuPDF, and image preprocessing.
"""

import os
import sys
import time
import difflib
import io
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pymupdf
import torch
from transformers import (
    AutoImageProcessor,
    AutoTokenizer,
    TrOCRProcessor,
    VisionEncoderDecoderModel,
)

# Standard default Tesseract installation paths on Windows
TESSERACT_DEFAULT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\jagad\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

LOCAL_AI_MODEL_ID = "sabaridsnfuji/Tamil_Offline_Handwritten_OCR"
TOKENIZER_ID = "d42kw01f/Tamil-RoBERTa"
ENCODER_ID = "google/vit-base-patch16-224-in21k"


def get_system_hardware_info() -> Dict[str, Any]:
    """Inspects available hardware (CPU, GPU, VRAM) and returns diagnostic details."""
    import platform as _platform
    cuda_available = torch.cuda.is_available()
    device_name = "CPU"
    total_vram_gb = 0.0

    if cuda_available:
        try:
            device_name = torch.cuda.get_device_name(0)
            total_vram_gb = round(
                torch.cuda.get_device_properties(0).total_memory / (1024**3), 2
            )
        except Exception:
            device_name = "CUDA Compatible GPU"
            total_vram_gb = 4.0

    # Determine runtime label
    if cuda_available:
        runtime_label = f"GPU ({device_name})"
    else:
        runtime_label = "CPU (உள்ளூர் நினைவகம் / Local RAM)"

    # active_device key: "gpu" if CUDA, else "cpu"
    active_device = "gpu" if cuda_available else "cpu"

    return {
        "cuda_available": cuda_available,
        "device_name": device_name,
        # 'active_device' is the key app.py reads for display
        "active_device": active_device,
        "runtime_label": runtime_label,
        "total_vram_gb": total_vram_gb,
        "torch_version": torch.__version__,
        "python_version": sys.version.split()[0],
        "os_name": _platform.system(),
        "os_version": _platform.release(),
    }


def find_tesseract_binary(custom_path: Optional[str] = None) -> Optional[str]:
    """Locates the tesseract executable on Windows."""
    if custom_path and os.path.exists(custom_path):
        return custom_path

    # Check known paths
    for p in TESSERACT_DEFAULT_PATHS:
        if os.path.exists(p):
            return p

    # Check system PATH
    import shutil
    path_in_env = shutil.which("tesseract")
    if path_in_env and os.path.exists(path_in_env):
        return path_in_env

    return None


def verify_tesseract(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Checks if Tesseract is installed and configured, and lists available languages.
    Returns status dictionary with version and language details.
    """
    exe_path = find_tesseract_binary(custom_path)
    if not exe_path:
        return {
            "installed": False,
            "path": None,
            "version": None,
            "languages": [],
            "tamil_available": False,
            "error": "Tesseract executable not found. Please install Tesseract-OCR at C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        }

    try:
        pytesseract.pytesseract.tesseract_cmd = exe_path
        version = str(pytesseract.get_tesseract_version())
        languages = pytesseract.get_languages()
        has_tam = "tam" in languages

        return {
            "installed": True,
            "path": exe_path,
            "version": version,
            "languages": languages,
            "tamil_available": has_tam,
            "error": None if has_tam else "Tamil language data ('tam.traineddata') is missing from tessdata folder.",
        }
    except Exception as e:
        return {
            "installed": True,
            "path": exe_path,
            "version": None,
            "languages": [],
            "tamil_available": False,
            "error": f"Error communicating with Tesseract: {str(e)}",
        }


def run_tesseract_ocr(
    image: Image.Image,
    lang: str = "tam",
    tesseract_path: Optional[str] = None,
    psm: int = 3,
) -> Dict[str, Any]:
    """
    Executes Tesseract OCR on a PIL Image.
    Returns extracted text, execution time in seconds, and status.
    """
    if image is None:
        return {
            "text": "",
            "elapsed_seconds": 0.0,
            "success": False,
            "error": "Invalid input: image object is None or empty.",
            "char_count": 0,
            "word_count": 0,
        }

    exe_path = find_tesseract_binary(tesseract_path)
    if not exe_path:
        return {
            "text": "",
            "elapsed_seconds": 0.0,
            "success": False,
            "error": "Tesseract executable path is not configured.",
        }

    pytesseract.pytesseract.tesseract_cmd = exe_path
    config = f"--psm {psm}"

    start_time = time.perf_counter()
    try:
        raw_text = pytesseract.image_to_string(image, lang=lang, config=config)
        cleaned_text = raw_text.strip()
        psm_used = psm

        # If standard auto-page segmentation (PSM 3) found nothing, try PSM 6 (uniform block)
        if not cleaned_text and psm == 3:
            try:
                fallback_text = pytesseract.image_to_string(
                    image, lang=lang, config="--psm 6"
                ).strip()
                if fallback_text:
                    cleaned_text = fallback_text
                    psm_used = 6
            except Exception:
                pass

        elapsed = time.perf_counter() - start_time

        if cleaned_text:
            import unicodedata
            import re
            cleaned_text = unicodedata.normalize("NFC", cleaned_text)
            # Re-compose split vowel signs (ெ + ா -> ொ, ே + ா -> ோ, ெ + ௗ -> ௌ)
            cleaned_text = (
                cleaned_text.replace("\u0BC6\u0BBE", "\u0BCA")
                .replace("\u0BC7\u0BBE", "\u0BCB")
                .replace("\u0BC6\u0BD7", "\u0BCC")
            )
            # Clean zero-width control characters that Tesseract can inject
            cleaned_text = re.sub(r"[\u200B-\u200D\uFEFF]", "", cleaned_text).strip()

        return {
            "text": cleaned_text,
            "elapsed_seconds": round(elapsed, 3),
            "success": True,
            "error": None
            if cleaned_text
            else "எழுத்துக்கள் எதுவும் கண்டறியப்படவில்லை (No text detected by Tesseract OCR).",
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split()) if cleaned_text else 0,
            "psm_used": psm_used,
        }

    except pytesseract.TesseractError as te:
        elapsed = time.perf_counter() - start_time
        return {
            "text": "",
            "elapsed_seconds": round(elapsed, 3),
            "success": False,
            "error": f"Tesseract OCR Error: {str(te)}",
            "char_count": 0,
            "word_count": 0,
            "psm_used": psm,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {
            "text": "",
            "elapsed_seconds": round(elapsed, 3),
            "success": False,
            "error": f"Unexpected OCR failure: {str(e)}",
            "char_count": 0,
            "word_count": 0,
        }


_GLOBAL_AI_OCR_PIPELINE: Dict[str, Any] = {}


def load_ai_ocr_pipeline(device_mode: str = "auto") -> Dict[str, Any]:
    """
    Loads the fine-tuned Tamil VisionEncoderDecoder OCR model and TrOCR processor.
    Uses cached pipeline in memory if already loaded to avoid 639MB reload overhead.
    """
    global _GLOBAL_AI_OCR_PIPELINE

    if device_mode == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    elif device_mode == "cuda" and torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    # Reuse cached pipeline if valid and device matches
    if _GLOBAL_AI_OCR_PIPELINE and _GLOBAL_AI_OCR_PIPELINE.get("success"):
        if _GLOBAL_AI_OCR_PIPELINE.get("device") == device:
            return _GLOBAL_AI_OCR_PIPELINE

    start_load = time.perf_counter()
    try:
        # Load feature extractor and tokenizer
        feature_extractor = AutoImageProcessor.from_pretrained(ENCODER_ID)
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_ID)
        processor = TrOCRProcessor(
            image_processor=feature_extractor, tokenizer=tokenizer
        )

        # Load VisionEncoderDecoder model
        model = VisionEncoderDecoderModel.from_pretrained(LOCAL_AI_MODEL_ID)
        model.to(device)
        model.eval()

        elapsed = time.perf_counter() - start_load
        pipeline = {
            "success": True,
            "model": model,
            "processor": processor,
            "device": device,
            "load_time_seconds": round(elapsed, 2),
            "model_id": LOCAL_AI_MODEL_ID,
            "error": None,
        }
        _GLOBAL_AI_OCR_PIPELINE = pipeline
        return pipeline
    except Exception as e:
        elapsed = time.perf_counter() - start_load
        return {
            "success": False,
            "model": None,
            "processor": None,
            "device": device,
            "load_time_seconds": round(elapsed, 2),
            "model_id": LOCAL_AI_MODEL_ID,
            "error": f"Failed to load AI OCR model: {str(e)}",
        }


def slice_image_into_lines(
    image: Image.Image, min_line_height: int = 14, threshold: Optional[int] = None
) -> List[Image.Image]:
    """
    Slices a multi-line document image into individual horizontal text lines
    using adaptive horizontal projection profiling.
    Automatically adapts to palm-leaf manuscripts and dark parchment backgrounds.
    """
    if image is None:
        return []

    gray = image.convert("L")
    arr = np.array(gray)

    # Adaptive foreground threshold computation for historical manuscripts
    if threshold is None or threshold == 240:
        p15 = float(np.percentile(arr, 15))
        p85 = float(np.percentile(arr, 85))
        thresh_val = (p15 + p85) / 2.0
        thresh_val = min(max(thresh_val, 40), 235)
    else:
        thresh_val = threshold

    binary = (arr < thresh_val).astype(np.int32)
    h_proj = np.sum(binary, axis=1)

    min_ink = max(4, int(image.width * 0.012))
    lines = []
    in_line = False
    start_y = 0

    for y, count in enumerate(h_proj):
        # A line begins when ink density exceeds threshold
        if count > min_ink and not in_line:
            in_line = True
            start_y = max(0, y - 3)
        elif count <= min_ink and in_line:
            in_line = False
            end_y = min(arr.shape[0], y + 3)
            if end_y - start_y >= min_line_height:
                lines.append(image.crop((0, start_y, image.width, end_y)))

    if in_line and (arr.shape[0] - start_y >= min_line_height):
        lines.append(image.crop((0, start_y, image.width, arr.shape[0])))

    return lines if lines else [image]


def run_ai_ocr_inference(
    image: Image.Image,
    model: VisionEncoderDecoderModel,
    processor: TrOCRProcessor,
    device: str = "cpu",
    auto_slice_lines: bool = True,
    max_new_tokens: int = 64,
    batch_size: int = 4,
) -> Dict[str, Any]:
    """
    Runs genuine Hugging Face AI OCR inference with batching, torch.inference_mode,
    and Unicode postprocessing to preserve fine Tamil compound characters.
    """
    if image is None:
        return {
            "text": "",
            "elapsed_seconds": 0.0,
            "success": False,
            "error": "Input image is None or empty.",
            "char_count": 0,
            "word_count": 0,
            "lines_processed": 0,
        }

    start_time = time.perf_counter()
    try:
        rgb_image = image.convert("RGB")

        # Downscale oversized images maintaining aspect ratio to prevent CPU thrashing
        max_dim = max(rgb_image.width, rgb_image.height)
        if max_dim > 2048:
            ratio = 2048.0 / max_dim
            new_size = (int(rgb_image.width * ratio), int(rgb_image.height * ratio))
            rgb_image = rgb_image.resize(new_size, Image.Resampling.LANCZOS)

        lines_to_process = (
            slice_image_into_lines(rgb_image) if auto_slice_lines else [rgb_image]
        )

        extracted_lines = []
        inference_ctx = torch.inference_mode() if hasattr(torch, "inference_mode") else torch.no_grad()

        with inference_ctx:
            for i in range(0, len(lines_to_process), batch_size):
                batch_imgs = lines_to_process[i : i + batch_size]
                pixel_values = processor(
                    images=batch_imgs, return_tensors="pt"
                ).pixel_values.to(device)

                generated_ids = model.generate(
                    pixel_values, max_new_tokens=max_new_tokens
                )
                decoded_batch = processor.batch_decode(
                    generated_ids, skip_special_tokens=True
                )
                for dec in decoded_batch:
                    dec_clean = dec.strip()
                    if dec_clean:
                        # Post-process canonical NFC normalization
                        import unicodedata
                        dec_nfc = unicodedata.normalize("NFC", dec_clean)
                        # Re-compose split vowel signs (ெ + ா -> ொ, ே + ா -> ோ)
                        dec_nfc = dec_nfc.replace("\u0BC6\u0BBE", "\u0BCA").replace("\u0BC7\u0BBE", "\u0BCB")
                        extracted_lines.append(dec_nfc)

        elapsed = time.perf_counter() - start_time
        full_text = "\n".join(extracted_lines).strip()

        return {
            "text": full_text,
            "elapsed_seconds": round(elapsed, 3),
            "success": True,
            "error": None if full_text else "No text recognized by AI OCR model.",
            "char_count": len(full_text),
            "word_count": len(full_text.split()) if full_text else 0,
            "lines_processed": len(lines_to_process),
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {
            "text": "",
            "elapsed_seconds": round(elapsed, 3),
            "success": False,
            "error": f"AI OCR inference error: {str(e)}",
            "char_count": 0,
            "word_count": 0,
            "lines_processed": 0,
        }



def check_ai_model_status() -> Dict[str, Any]:
    """
    Inspects whether the local Vision Transformer model weights are physically
    available in the local cache without initiating network downloads.
    """
    try:
        import huggingface_hub
        model_path = huggingface_hub.try_to_load_from_cache(LOCAL_AI_MODEL_ID, "model.safetensors")
        is_ready = bool(model_path and os.path.isfile(model_path))
        return {
            "model_id": LOCAL_AI_MODEL_ID,
            "architecture": "VisionEncoderDecoder (ViT-Base + Tamil-RoBERTa)",
            "cached_locally": is_ready,
            "status": "ready" if is_ready else "not_cached",
            "status_label": "✅ தயார் (Local Cache)" if is_ready else "⚠️ பதிவிறக்கம் தேவை (Not in cache)",
            "local_path": model_path if is_ready else None,
        }
    except Exception as e:
        return {
            "model_id": LOCAL_AI_MODEL_ID,
            "architecture": "VisionEncoderDecoder (ViT-Base + Tamil-RoBERTa)",
            "cached_locally": False,
            "status": "error",
            "status_label": f"பிழை: {str(e)}",
            "local_path": None,
        }


def run_hf_cloud_inference(
    image: Image.Image,
    model_id: str = "sair390/tamil-ocr-qwen25vl",
    hf_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calls the Hugging Face Serverless Inference API for large vision-language models
    like Qwen2.5-VL with secure token handling and clear status classification.
    """
    token = hf_token or os.environ.get("HF_TOKEN")
    if not token or not token.strip():
        return {
            "text": "",
            "elapsed_seconds": 0.0,
            "success": False,
            "error": "Hugging Face Access Token missing. Provide a valid token in the sidebar to use Cloud Vision models.",
        }

    try:
        import requests
    except ImportError:
        return {
            "text": "",
            "elapsed_seconds": 0.0,
            "success": False,
            "error": "The 'requests' library is required for Hugging Face Cloud Inference.",
        }

    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token.strip()}"}

    # Save image to in-memory bytes
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    image_bytes = buffer.read()

    start_time = time.perf_counter()
    try:
        response = requests.post(api_url, headers=headers, data=image_bytes, timeout=45)
        elapsed = round(time.perf_counter() - start_time, 3)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = (
                    result[0].get("generated_text")
                    or result[0].get("summary_text")
                    or str(result[0])
                )
            elif isinstance(result, dict):
                text = result.get("generated_text") or str(result)
            else:
                text = str(result)

            return {
                "text": text.strip(),
                "elapsed_seconds": elapsed,
                "success": True,
                "error": None,
                "char_count": len(text.strip()),
                "word_count": len(text.strip().split()),
            }
        elif response.status_code in (401, 403):
            return {
                "text": "",
                "elapsed_seconds": elapsed,
                "success": False,
                "error": "HF API Authentication Failed (HTTP 401/403): Invalid or expired access token.",
                "char_count": 0,
                "word_count": 0,
            }
        elif response.status_code == 429:
            return {
                "text": "",
                "elapsed_seconds": elapsed,
                "success": False,
                "error": "HF API Rate Limit Exceeded (HTTP 429): Please wait before sending additional requests.",
                "char_count": 0,
                "word_count": 0,
            }
        elif response.status_code == 503:
            return {
                "text": "",
                "elapsed_seconds": elapsed,
                "success": False,
                "error": "HF Serverless Model is currently spinning up (HTTP 503). Please retry in 20-30 seconds.",
                "char_count": 0,
                "word_count": 0,
            }
        else:
            return {
                "text": "",
                "elapsed_seconds": elapsed,
                "success": False,
                "error": f"HF Cloud API returned HTTP status {response.status_code}.",
                "char_count": 0,
                "word_count": 0,
            }
    except requests.exceptions.Timeout:
        elapsed = round(time.perf_counter() - start_time, 3)
        return {
            "text": "",
            "elapsed_seconds": elapsed,
            "success": False,
            "error": "Cloud API request timed out (45s). Local AI OCR is recommended for offline or slower connections.",
            "char_count": 0,
            "word_count": 0,
        }
    except Exception as e:
        elapsed = round(time.perf_counter() - start_time, 3)
        return {
            "text": "",
            "elapsed_seconds": elapsed,
            "success": False,
            "error": f"Cloud API request error: {str(e)}",
            "char_count": 0,
            "word_count": 0,
        }


def sauvola_binarize(img: Image.Image, window_size: int = 25, k: float = 0.2, r: float = 128.0) -> Image.Image:
    """
    Genuine Sauvola adaptive binarization for historical palm-leaf manuscripts and aged books.
    Computes local threshold: T(x, y) = mean * (1 + k * (std / R - 1))
    """
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)

    # Local mean using PIL BoxBlur
    mean_img = gray.filter(ImageFilter.BoxBlur(window_size // 2))
    mean_arr = np.array(mean_img, dtype=np.float32)

    # Mean absolute deviation as standard deviation proxy for speed and stability
    dev_arr = np.abs(arr - mean_arr)
    dev_img = Image.fromarray(dev_arr.astype(np.uint8)).filter(ImageFilter.BoxBlur(window_size // 2))
    std_arr = np.array(dev_img, dtype=np.float32) * 1.2533

    threshold = mean_arr * (1.0 + k * ((std_arr / r) - 1.0))
    bin_arr = np.where(arr > threshold, 255, 0).astype(np.uint8)
    return Image.fromarray(bin_arr).convert("RGB")


def preprocess_image(
    image: Image.Image,
    to_grayscale: bool = False,
    contrast_factor: float = 1.0,
    sharpness_factor: float = 1.0,
    scale_factor: float = 1.0,
    denoise: bool = False,
    binarize: bool = False,
) -> Image.Image:
    """Applies user-selected enhancement filters to improve historical manuscript readability."""
    if image is None:
        return None
    img = image.copy()

    if to_grayscale:
        img = img.convert("L").convert("RGB")

    if denoise:
        img = img.filter(ImageFilter.MedianFilter(size=3))

    if contrast_factor != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)

    if sharpness_factor != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness_factor)

    if binarize:
        img = sauvola_binarize(img)

    if scale_factor != 1.0:
        new_width = max(int(img.width * scale_factor), 10)
        new_height = max(int(img.height * scale_factor), 10)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return img




def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Returns the total number of pages in the uploaded PDF."""
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 0


def render_pdf_page_to_image(
    pdf_bytes: bytes, page_number: int = 0, dpi: int = 200
) -> Optional[Image.Image]:
    """
    Renders a single PDF page into a high-resolution PIL Image using PyMuPDF.
    Avoids loading full documents into memory.
    """
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        if page_number < 0 or page_number >= len(doc):
            doc.close()
            return None

        page = doc[page_number]
        # Calculate zoom factor from DPI (default PDF is 72 dpi)
        zoom = dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    except Exception as e:
        print(f"Error rendering PDF page: {e}")
        return None



def compare_ocr_results(text1: str, text2: str) -> Dict[str, Any]:
    """
    Compares two OCR outputs using SequenceMatcher and diff analysis.
    Explicitly clarifies that differences do not indicate which output is ground truth.
    """
    matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity_ratio = round(matcher.ratio() * 100, 1)

    words1 = text1.split()
    words2 = text2.split()

    # Generate unified diff lines
    diff_lines = list(
        difflib.unified_diff(
            text1.splitlines(),
            text2.splitlines(),
            fromfile="Tesseract OCR",
            tofile="AI Model OCR",
            lineterm="",
        )
    )

    return {
        "similarity_percentage": similarity_ratio,
        "char_diff": abs(len(text1) - len(text2)),
        "word_diff": abs(len(words1) - len(words2)),
        "diff_lines": diff_lines,
    }


# =====================================================================
# Integrated 15 Tamil Heritage AI Features (Re-exported for seamless access)
# =====================================================================
try:
    from tamil_ai_features import (
        correct_tamil_ocr_text,
        correct_tamil_text,
        normalize_tamil_unicode,
        extract_ocr_confidence,
        compare_dual_ocr,
        compare_manuscript_versions,
        cleanup_tamil_text,
        reconstruct_paragraphs,
        preserve_ancient_tamil_terms,
        explain_ancient_tamil,
        process_mixed_tamil_english,
        search_in_digitized_text,
        semantic_tamil_search,
        process_batch_ocr,
        process_pdf_page_wise,
        export_recognized_text,
        manage_ocr_history,
        preprocess_heritage_image,
        enhance_manuscript_image,
        analyze_tamil_text,
        extract_vault_knowledge,
        synthesize_tamil_speech,
        translate_tamil_english,
        process_tamil_inscription,
        extract_history_timeline,
        analyze_preservation_history,
        generate_knowledge_graph,
        simplify_tamil_text,
    )
except ImportError:
    pass


def extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    """Extracts plain text from DOCX document bytes using standard library."""
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
            if "word/document.xml" not in z.namelist():
                return ""
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for p in tree.iterfind(".//w:p", ns):
                texts = [node.text for node in p.iterfind(".//w:t", ns) if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception:
        return ""


def render_text_as_manuscript_image(
    text: str,
    title: Optional[Any] = None,
    width: int = 1000,
    min_height: int = 400,
    **kwargs: Any,
) -> Image.Image:
    """
    Renders text onto a simulated antique parchment background for UI preview.
    Supports title header, arbitrary kwargs, and Tamil Unicode rendering safely.
    """
    from PIL import ImageDraw, ImageFont

    # Handle backwards compatibility if caller passed integer width as 2nd positional arg
    if isinstance(title, int):
        width = title
        title = kwargs.get("title", None)

    # Check kwargs for potential overrides
    if "title" in kwargs and title is None:
        title = kwargs["title"]
    if "width" in kwargs:
        try:
            width = int(kwargs["width"])
        except (ValueError, TypeError):
            pass
    if "min_height" in kwargs:
        try:
            min_height = int(kwargs["min_height"])
        except (ValueError, TypeError):
            pass

    header_text = (
        str(title).strip()
        if title
        else "தமிழ்ச்சுவடி எண்ம ஆவணம் (Tamil Heritage Digital Manuscript)"
    )

    # Attempt to load Unicode font for Tamil script rendering
    title_font = None
    body_font = None
    for font_path in [
        r"C:\Windows\Fonts\Nirmala.ttc",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
    ]:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, 18)
                body_font = ImageFont.truetype(font_path, 16)
                break
            except Exception:
                pass

    lines = [line.strip() for line in (text or "").splitlines() if line.strip()][:25]
    line_height = 36
    calc_height = max(min_height, len(lines) * line_height + 120)
    img = Image.new("RGB", (width, calc_height), color=(38, 24, 16))
    draw = ImageDraw.Draw(img)

    # Antique parchment borders
    draw.rectangle([15, 15, width - 15, calc_height - 15], outline=(115, 79, 39), width=2)
    draw.rectangle([22, 22, width - 22, calc_height - 22], outline=(212, 175, 55), width=1)
    draw.rectangle([25, 25, width - 25, 65], fill=(26, 16, 10))

    # Header title
    if title_font:
        draw.text((40, 36), header_text, fill=(212, 175, 55), font=title_font)
    else:
        draw.text((40, 36), header_text, fill=(212, 175, 55))

    # Manuscript content lines
    y_pos = 90
    for line in lines:
        disp_line = line[:80] + ("..." if len(line) > 80 else "")
        if body_font:
            draw.text((45, y_pos), disp_line, fill=(245, 232, 208), font=body_font)
        else:
            draw.text((45, y_pos), disp_line, fill=(245, 232, 208))
        y_pos += line_height

    return img



