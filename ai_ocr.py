r"""
Tamil Heritage AI - Standalone AI OCR Module (ai_ocr.py)
=========================================================
A self-contained, user-friendly AI OCR module for digitising historical
Tamil books and manuscripts using fine-tuned Hugging Face Vision Transformers.

Model Architecture:
  Repository: sabaridsnfuji/Tamil_Offline_Handwritten_OCR
  Architecture: VisionEncoderDecoderModel (ViT-Base + Tamil-RoBERTa)
  Weight Size: ~639.2 MB (Safe for 4 GB VRAM; runs smoothly on CPU)
  License: Apache 2.0 (Open-Source)

Supported Formats:
  - Images: JPG, JPEG, PNG, WEBP, BMP, TIFF (via PIL or file path)
  - Documents: PDF (via extract_tamil_text_from_pdf using PyMuPDF)

PowerShell Quick Start:
  # In PowerShell:
  Set-Location "$env:USERPROFILE\OneDrive\Documents\TamilHeritageAI"
  py .\ai_ocr.py ".\samples\sample_tamil.jpg"
  py .\ai_ocr.py "C:\full\path\to\your\tamil-image.jpg"
"""[1:]

import os
import sys
import time
import io
from pathlib import Path
from typing import Union, List, Optional, Dict, Any

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Validate dependencies
try:
    from PIL import Image, ImageOps, ImageEnhance, UnidentifiedImageError
    import numpy as np
    import torch
    from transformers import (
        AutoImageProcessor,
        AutoTokenizer,
        TrOCRProcessor,
        VisionEncoderDecoderModel,
    )
except ImportError as imp_err:
    raise ImportError(
        f"Missing required dependency for AI OCR: {imp_err}.\n"
        "Please run: py -m pip install -r requirements.txt"
    ) from imp_err

# Optional PyMuPDF import for PDF support
try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Model and Tokenizer Repository Identifiers
MODEL_REPO_ID = "sabaridsnfuji/Tamil_Offline_Handwritten_OCR"
TOKENIZER_REPO_ID = "d42kw01f/Tamil-RoBERTa"
ENCODER_REPO_ID = "google/vit-base-patch16-224-in21k"
CLOUD_VLM_ID = "sair390/tamil-ocr-qwen25vl"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".pdf"}


def resolve_image_path(path_input: Union[str, Path]) -> Path:
    r"""
    Robustly resolves an image path on Windows / PowerShell / CMD:
    - Strips surrounding quotes (' or ") and extra whitespace.
    - Resolves absolute Windows paths (e.g. C:\... or C:/...).
    - Resolves paths containing spaces.
    - Resolves relative paths against the Current Working Directory (CWD).
    - Resolves relative paths against the script's directory if run from another folder.
    - Checks common subdirectories like 'samples/'.
    - Validates supported formats (JPG, JPEG, PNG, WEBP, BMP, TIFF, PDF).
    - Raises a clear, helpful FileNotFoundError or IsADirectoryError explaining how to provide a valid path.
    """
    if isinstance(path_input, Path):
        raw_str = str(path_input)
    elif isinstance(path_input, str):
        raw_str = path_input
    else:
        raise TypeError(f"Expected file path string or Path, got: {type(path_input).__name__}")

    clean_str = raw_str.strip().strip("'\"").strip()
    if not clean_str:
        raise ValueError("Image file path cannot be empty. Please provide a path to an image file.")

    target = Path(clean_str)

    # 1. Directory check
    if target.is_dir():
        msg = (
            f"\n[ERROR] Specified path is a directory, not an image file:\n"
            f"  '{target.resolve()}'\n\n"
            f"Please specify an image file, for example:\n"
            f"  py .\\ai_ocr.py \"{(target / 'your-tamil-image.jpg')}\""
        )
        raise IsADirectoryError(msg)

    # 2. Direct check: absolute path or relative to current working directory (CWD)
    try:
        if target.is_file():
            if target.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise ValueError(
                    f"\n[ERROR] Unsupported file extension '{target.suffix}'.\n"
                    f"Supported formats: JPG, JPEG, PNG, WEBP, BMP, TIFF, PDF."
                )
            return target.resolve()
    except (ValueError, IsADirectoryError):
        raise
    except Exception:
        pass

    # 3. If relative path, check relative to the script's directory
    script_dir = Path(__file__).resolve().parent
    if not target.is_absolute():
        script_relative = script_dir / clean_str
        try:
            if script_relative.is_file():
                if script_relative.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    raise ValueError(
                        f"\n[ERROR] Unsupported file extension '{script_relative.suffix}'.\n"
                        f"Supported formats: JPG, JPEG, PNG, WEBP, BMP, TIFF, PDF."
                    )
                return script_relative.resolve()
        except (ValueError, IsADirectoryError):
            raise
        except Exception:
            pass

        # 4. Check in a 'samples' subdirectory relative to script directory
        samples_script = script_dir / "samples" / clean_str
        try:
            if samples_script.is_file():
                return samples_script.resolve()
        except Exception:
            pass

        # 5. Check in a 'samples' subdirectory relative to CWD
        samples_cwd = Path.cwd() / "samples" / clean_str
        try:
            if samples_cwd.is_file():
                return samples_cwd.resolve()
        except Exception:
            pass

    # File not found: build a friendly, actionable diagnostic error message
    if target.is_absolute():
        resolved_full = target.resolve()
        msg = (
            f"\n[ERROR] Image file does not exist at absolute path:\n"
            f"  '{resolved_full}'\n\n"
            f"Troubleshooting tips:\n"
            f"  1. Check for typos in the filename or folder names.\n"
            f"  2. In PowerShell, make sure paths with spaces are enclosed in quotes:\n"
            f"       py .\\ai_ocr.py \"{resolved_full}\"\n"
            f"  3. Test whether the file exists using PowerShell:\n"
            f"       Test-Path \"{clean_str}\"\n"
        )
    else:
        cwd_attempt = (Path.cwd() / target).resolve()
        script_attempt = (script_dir / target).resolve()
        msg = (
            f"\n[ERROR] Image file does not exist: '{clean_str}'\n\n"
            f"Full paths checked:\n"
            f"  1. Current working directory: '{cwd_attempt}'\n"
            f"  2. Script directory:          '{script_attempt}'\n\n"
            f"How to provide a valid image path in PowerShell:\n"
            f"  - If the image is in your current folder:\n"
            f"      py .\\ai_ocr.py \".\\{target.name if target.name else 'your-tamil-image.jpg'}\"\n"
            f"  - Using an absolute path:\n"
            f"      py .\\ai_ocr.py \"C:\\full\\path\\to\\your\\tamil-image.jpg\"\n"
            f"  - Check available images in the current folder:\n"
            f"      Get-ChildItem -Include *.jpg,*.jpeg,*.png,*.webp -Name\n"
        )
    raise FileNotFoundError(msg)


class TamilAIOCR:
    """
    Standalone Tamil AI OCR Engine.
    Handles image validation, rotation, multi-line slicing, and transformer inference.
    Supports automatic GPU detection with CPU fallback and thread-safe caching.
    """

    def __init__(
        self,
        model_id: str = MODEL_REPO_ID,
        device_preference: Optional[str] = "auto",
        auto_slice: bool = True,
    ):
        """
        Initialize the AI OCR engine.

        Args:
            model_id: Hugging Face model repository ID.
            device_preference: 'auto' (detects CUDA, falls back to CPU), 'cuda', or 'cpu'.
            auto_slice: If True, uses adaptive horizontal line slicing for multi-line scans.
        """
        self.model_id = model_id
        self.auto_slice = auto_slice
        self.device = self._resolve_device(device_preference)
        self.processor: Optional[TrOCRProcessor] = None
        self.model: Optional[VisionEncoderDecoderModel] = None
        self.load_time: float = 0.0
        self.last_inference_time: float = 0.0

        # Load pipeline weights
        self._load_pipeline()

    def get_info(self) -> Dict[str, Any]:
        """Returns diagnostic metadata about the loaded model and hardware."""
        return {
            "model_id": self.model_id,
            "architecture": "VisionEncoderDecoderModel (ViT-Base + Tamil-RoBERTa)",
            "device": self.device,
            "torch_version": torch.__version__,
            "load_time_seconds": self.load_time,
            "auto_slice": self.auto_slice,
        }

    def _resolve_device(self, preference: Optional[str]) -> str:
        """Determines whether to execute on CUDA GPU or CPU."""
        if preference == "cuda" and torch.cuda.is_available():
            return "cuda"
        if preference == "cpu":
            return "cpu"
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _load_pipeline(self):
        """Loads processor and model weights from local cache or Hugging Face Hub."""
        start_time = time.perf_counter()
        try:
            feature_extractor = AutoImageProcessor.from_pretrained(ENCODER_REPO_ID)
            tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_REPO_ID)
            self.processor = TrOCRProcessor(
                image_processor=feature_extractor, tokenizer=tokenizer
            )

            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_id)
            self.model.to(self.device)
            self.model.eval()

            self.load_time = round(time.perf_counter() - start_time, 2)

        except torch.cuda.OutOfMemoryError:
            print("Warning: GPU out of memory. Automatically falling back to CPU...")
            torch.cuda.empty_cache()
            self.device = "cpu"
            self.model = VisionEncoderDecoderModel.from_pretrained(self.model_id)
            self.model.to("cpu")
            self.model.eval()
            self.load_time = round(time.perf_counter() - start_time, 2)

        except Exception as exc:
            raise RuntimeError(
                f"Failed to load AI OCR model '{self.model_id}': {exc}\n"
                "Ensure internet access on first use to download model weights into cache."
            ) from exc

    def validate_and_preprocess_image(
        self,
        image_input: Union[str, Path, bytes, Image.Image],
        to_grayscale: bool = False,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        scale: float = 1.0,
    ) -> Image.Image:
        """
        Validates input format, corrects EXIF rotation, and applies basic enhancements.
        Supports JPG, JPEG, PNG, WEBP, BMP, and TIFF.
        Raises FileNotFoundError, ValueError, or TypeError if invalid.
        """
        img: Image.Image

        if isinstance(image_input, Image.Image):
            img = image_input.copy()
        elif isinstance(image_input, bytes):
            try:
                img = Image.open(io.BytesIO(image_input))
            except UnidentifiedImageError:
                raise ValueError("Byte data is not a recognized image format.")
        elif isinstance(image_input, (str, Path)):
            resolved_path = resolve_image_path(image_input)
            try:
                img = Image.open(resolved_path)
            except UnidentifiedImageError:
                raise ValueError(
                    f"File '{resolved_path}' is not a valid image format (supported: JPG, JPEG, PNG, WEBP, TIFF, BMP)."
                )
            except Exception as err:
                raise ValueError(f"Unable to read image '{resolved_path}': {err}")
        else:
            raise TypeError(
                f"Expected PIL Image, file path string, Path, or bytes, got: {type(image_input).__name__}"
            )

        # 1. Correct EXIF rotation if present (e.g. mobile photos of book pages)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 2. Ensure RGB mode
        img = img.convert("RGB")

        # 3. Optional enhancement filters
        if to_grayscale:
            img = img.convert("L").convert("RGB")

        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)

        if scale != 1.0:
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        return img

    def _slice_lines(
        self, image: Image.Image, min_line_height: int = 15, threshold: Optional[int] = None
    ) -> List[Image.Image]:
        """
        Segments a multi-line document image into individual horizontal text lines
        using adaptive horizontal projection profiling. Automatically adapts to
        dark palm leaves, antique parchment, and scanned books.
        """
        gray = image.convert("L")
        np_img = np.array(gray)

        if threshold is None or threshold == 240:
            p15 = float(np.percentile(np_img, 15))
            p85 = float(np.percentile(np_img, 85))
            thresh_val = (p15 + p85) / 2.0
            thresh_val = min(max(thresh_val, 40), 235)
        else:
            thresh_val = threshold

        binary = np_img < thresh_val
        h_proj = np.sum(binary, axis=1)

        in_line = False
        start_y = 0
        line_boxes = []
        min_ink = max(4, int(image.width * 0.012))

        for y, val in enumerate(h_proj):
            if val > min_ink and not in_line:
                in_line = True
                start_y = y
            elif val <= min_ink and in_line:
                in_line = False
                if (y - start_y) >= min_line_height:
                    line_boxes.append((start_y, y))

        if in_line and (len(h_proj) - start_y) >= min_line_height:
            line_boxes.append((start_y, len(h_proj)))

        # Fallback if no distinct lines were found
        if not line_boxes:
            return [image]

        slices = []
        width, height = image.size
        for start_y, end_y in line_boxes:
            pad = 4
            sy = max(0, start_y - pad)
            ey = min(height, end_y + pad)
            crop_box = (0, sy, width, ey)
            line_crop = image.crop(crop_box)
            slices.append(line_crop)

        return slices

    def extract_text(
        self,
        image_input: Union[str, Path, bytes, Image.Image],
        max_new_tokens: int = 64,
        to_grayscale: bool = False,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        scale: float = 1.0,
    ) -> str:
        """
        Extracts Tamil text from an image.
        Returns the recognized Tamil text as a single string.
        Raises FileNotFoundError, ValueError, TypeError if input is invalid.
        """
        img = self.validate_and_preprocess_image(
            image_input,
            to_grayscale=to_grayscale,
            contrast=contrast,
            sharpness=sharpness,
            scale=scale,
        )
        result = self.extract_detailed(img, max_new_tokens=max_new_tokens)
        if not result["success"]:
            raise RuntimeError(f"OCR Inference Failed: {result['error']}")
        return result["text"]

    def extract_detailed(
        self,
        image_input: Union[str, Path, bytes, Image.Image],
        max_new_tokens: int = 64,
        to_grayscale: bool = False,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        scale: float = 1.0,
        batch_size: int = 4,
    ) -> Dict[str, Any]:
        """
        Extracts Tamil text and returns structured execution metadata.
        Uses batching, torch.inference_mode, and Unicode normalization.
        """
        if self.model is None or self.processor is None:
            return {
                "text": "",
                "model_id": self.model_id,
                "elapsed_seconds": 0.0,
                "device_used": self.device,
                "success": False,
                "error": "OCR model is not loaded.",
                "line_count": 0,
                "char_count": 0,
                "word_count": 0,
            }

        start_time = time.perf_counter()
        try:
            img = self.validate_and_preprocess_image(
                image_input,
                to_grayscale=to_grayscale,
                contrast=contrast,
                sharpness=sharpness,
                scale=scale,
            )
        except (FileNotFoundError, IsADirectoryError, ValueError, TypeError) as val_err:
            elapsed = round(time.perf_counter() - start_time, 3)
            return {
                "text": "",
                "model_id": self.model_id,
                "elapsed_seconds": elapsed,
                "device_used": self.device,
                "success": False,
                "error": str(val_err),
                "line_count": 0,
                "char_count": 0,
                "word_count": 0,
            }

        try:
            # Downscale oversized images maintaining aspect ratio
            max_dim = max(img.width, img.height)
            if max_dim > 2048:
                ratio = 2048.0 / max_dim
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            segments = self._slice_lines(img) if self.auto_slice else [img]
            recognized_lines = []
            inf_ctx = torch.inference_mode() if hasattr(torch, "inference_mode") else torch.no_grad()

            with inf_ctx:
                for i in range(0, len(segments), batch_size):
                    batch_imgs = segments[i : i + batch_size]
                    pixel_values = self.processor(
                        images=batch_imgs, return_tensors="pt"
                    ).pixel_values.to(self.device)

                    generated_ids = self.model.generate(
                        pixel_values, max_new_tokens=max_new_tokens
                    )

                    decoded_batch = self.processor.batch_decode(
                        generated_ids, skip_special_tokens=True
                    )
                    for decoded in decoded_batch:
                        dec_strip = decoded.strip()
                        if dec_strip:
                            # Re-compose split vowel signs and normalize
                            import unicodedata
                            dec_norm = unicodedata.normalize("NFC", dec_strip)
                            dec_norm = dec_norm.replace("\u0BC6\u0BBE", "\u0BCA").replace("\u0BC7\u0BBE", "\u0BCB")
                            recognized_lines.append(dec_norm)

            elapsed = round(time.perf_counter() - start_time, 3)
            self.last_inference_time = elapsed
            full_text = "\n".join(recognized_lines)

            return {
                "text": full_text,
                "model_id": self.model_id,
                "elapsed_seconds": elapsed,
                "device_used": self.device,
                "success": True,
                "error": None,
                "line_count": len(segments),
                "char_count": len(full_text),
                "word_count": len(full_text.split()) if full_text else 0,
            }


        except torch.cuda.OutOfMemoryError:
            print("CUDA OutOfMemory detected during inference. Retrying on CPU...")
            torch.cuda.empty_cache()
            self.model.to("cpu")
            self.device = "cpu"
            return self.extract_detailed(
                img,
                max_new_tokens=max_new_tokens,
                to_grayscale=False,
                contrast=1.0,
                sharpness=1.0,
                scale=1.0,
            )
        except Exception as exc:
            elapsed = round(time.perf_counter() - start_time, 3)
            self.last_inference_time = elapsed
            return {
                "text": "",
                "model_id": self.model_id,
                "elapsed_seconds": elapsed,
                "device_used": self.device,
                "success": False,
                "error": f"Inference execution failed: {str(exc)}",
                "line_count": 0,
                "char_count": 0,
                "word_count": 0,
            }

    def extract_from_pdf(
        self,
        pdf_input: Union[str, Path, bytes],
        page_number: int = 0,
        dpi: int = 200,
        max_new_tokens: int = 64,
    ) -> Dict[str, Any]:
        """
        Renders a single PDF page into high-resolution memory bytes using PyMuPDF
        and runs OCR without loading the full document into RAM.
        """
        if not PYMUPDF_AVAILABLE:
            return {
                "text": "",
                "model_id": self.model_id,
                "elapsed_seconds": 0.0,
                "device_used": self.device,
                "success": False,
                "error": "PyMuPDF is not installed. Run: py -m pip install pymupdf",
                "line_count": 0,
                "char_count": 0,
                "word_count": 0,
            }

        try:
            if isinstance(pdf_input, (str, Path)):
                resolved_pdf = resolve_image_path(pdf_input)
                doc = pymupdf.open(str(resolved_pdf))
            elif isinstance(pdf_input, bytes):
                doc = pymupdf.open(stream=pdf_input, filetype="pdf")
            else:
                raise TypeError("PDF input must be a file path string or bytes.")

            if page_number < 0 or page_number >= len(doc):
                doc.close()
                return {
                    "text": "",
                    "model_id": self.model_id,
                    "elapsed_seconds": 0.0,
                    "device_used": self.device,
                    "success": False,
                    "error": f"Invalid page number {page_number}. Document contains {len(doc)} pages.",
                    "line_count": 0,
                    "char_count": 0,
                    "word_count": 0,
                }

            page = doc[page_number]
            zoom = dpi / 72.0
            matrix = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()

            return self.extract_detailed(img, max_new_tokens=max_new_tokens)

        except Exception as pdf_err:
            return {
                "text": "",
                "model_id": self.model_id,
                "elapsed_seconds": 0.0,
                "device_used": self.device,
                "success": False,
                "error": f"Failed to render PDF page: {str(pdf_err)}",
                "line_count": 0,
                "char_count": 0,
                "word_count": 0,
            }


# --- Singleton Cache & Functional Interface ---
_GLOBAL_OCR_ENGINE: Optional[TamilAIOCR] = None


def get_ocr_engine(device_preference: Optional[str] = "auto") -> TamilAIOCR:
    """Returns a shared, cached TamilAIOCR instance to avoid repeated model loading."""
    global _GLOBAL_OCR_ENGINE
    if _GLOBAL_OCR_ENGINE is None:
        _GLOBAL_OCR_ENGINE = TamilAIOCR(device_preference=device_preference)
    return _GLOBAL_OCR_ENGINE


def load_tamil_ai_model(device_override: Optional[str] = "auto") -> Dict[str, Any]:
    """Helper for Streamlit and external modules to load and cache the AI model pipeline."""
    try:
        engine = get_ocr_engine(device_preference=device_override)
        return {
            "success": True,
            "engine": engine,
            "model": engine.model,
            "processor": engine.processor,
            "device": engine.device,
            "load_time": engine.load_time,
            "model_id": engine.model_id,
            "error": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "engine": None,
            "model": None,
            "processor": None,
            "device": "cpu",
            "load_time": 0.0,
            "model_id": MODEL_REPO_ID,
            "error": str(exc),
        }


def extract_tamil_text_ai(
    image: Union[str, Path, bytes, Image.Image],
    model: Optional[VisionEncoderDecoderModel] = None,
    processor: Optional[TrOCRProcessor] = None,
    device: Optional[str] = "auto",
    auto_slice: bool = True,
    max_new_tokens: int = 64,
) -> Dict[str, Any]:
    """Helper for Streamlit app.py to run AI OCR inference."""
    engine = get_ocr_engine(device_preference=device)
    engine.auto_slice = auto_slice
    return engine.extract_detailed(image, max_new_tokens=max_new_tokens)


def extract_via_hf_cloud_api(
    image: Image.Image,
    model_id: str = "sair390/tamil-ocr-qwen25vl",
    hf_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to query Hugging Face Inference API for large vision-language models."""
    import ocr_engine
    return ocr_engine.run_hf_cloud_inference(image, model_id=model_id, hf_token=hf_token)


def extract_tamil_text(
    image: Union[str, Path, bytes, Image.Image],
    device: Optional[str] = "auto",
) -> str:
    """
    User-friendly one-line function to extract Tamil text from an image.
    Accepts file path (JPG, JPEG, PNG, WEBP), Path object, bytes, or PIL Image.
    Returns extracted text as a UTF-8 Python string.
    """
    engine = get_ocr_engine(device_preference=device)
    return engine.extract_text(image)


def extract_tamil_text_detailed(
    image: Union[str, Path, bytes, Image.Image],
    device: Optional[str] = "auto",
) -> Dict[str, Any]:
    """
    Extracts Tamil text and returns structured metadata including processing time,
    device used, line count, and character statistics.
    """
    engine = get_ocr_engine(device_preference=device)
    return engine.extract_detailed(image)


def extract_tamil_text_from_pdf(
    pdf_input: Union[str, Path, bytes],
    page_number: int = 0,
    dpi: int = 200,
    device: Optional[str] = "auto",
) -> str:
    """
    Renders a specific page of a PDF document using PyMuPDF and extracts Tamil text.
    """
    engine = get_ocr_engine(device_preference=device)
    res = engine.extract_from_pdf(pdf_input, page_number=page_number, dpi=dpi)
    if not res["success"]:
        raise RuntimeError(res["error"])
    return res["text"]


# =====================================================================
# Integrated 15 Tamil Heritage AI Features (Re-exported for convenient access)
# =====================================================================
try:
    from tamil_ai_features import (
        correct_tamil_text,
        explain_ancient_tamil,
        synthesize_tamil_speech,
        semantic_tamil_search,
        enhance_manuscript_image,
        translate_tamil_english,
        extract_ocr_confidence,
        chat_with_document,
        extract_vault_knowledge,
        process_tamil_inscription,
        extract_history_timeline,
        compare_manuscript_versions,
        analyze_preservation_history,
        generate_knowledge_graph,
        simplify_tamil_text,
    )
except ImportError:
    pass


# --- Direct Command-Line Execution ---

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].lower() in ("-h", "--help", "/?"):
        print("\n=== Tamil Heritage AI - AI OCR Command Line ===")
        print("Usage in PowerShell:")
        print("  1. Absolute image path:")
        print("     py .\\ai_ocr.py \"C:\\full\\path\\to\\your\\tamil-image.jpg\"")
        print("  2. Relative image path:")
        print("     py .\\ai_ocr.py \".\\your-tamil-image.jpg\"")
        print("  3. PDF page extraction:")
        print("     py .\\ai_ocr.py \"document.pdf\" 0\n")
        print("Run from any directory using the script's full path:")
        print(f"  py \"{Path(__file__).resolve()}\" \"C:\\path\\to\\image.jpg\"\n")
        sys.exit(0 if (len(sys.argv) >= 2 and sys.argv[1].lower() in ("-h", "--help", "/?")) else 1)

    file_arg = sys.argv[1].strip().strip("'\"").strip()
    page_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print(f"Checking input file: {file_arg}")

    # Validate file path BEFORE loading the model to give instant feedback (0.01s)
    resolved_path: Optional[Path] = None
    try:
        resolved_path = resolve_image_path(file_arg)
        print(f"Resolved input path: {resolved_path}")
    except (FileNotFoundError, IsADirectoryError, ValueError) as path_err:
        print(str(path_err))
        sys.exit(1)
    except Exception as p_err:
        print(f"\n[ERROR] Invalid path: {p_err}")
        sys.exit(1)

    # Initialize engine and run inference
    print("Loading AI OCR model and running inference...")
    engine = get_ocr_engine()

    if resolved_path.suffix.lower() == ".pdf":
        output = engine.extract_from_pdf(resolved_path, page_number=page_arg)
    else:
        output = engine.extract_detailed(resolved_path)

    if output["success"]:
        print("\n--- Extracted Tamil Text ---")
        print(output["text"] if output["text"] else "[No text detected in image]")
        print("----------------------------")
        print(f"Inference Time: {output['elapsed_seconds']}s | Device: {output['device_used']} | Lines: {output['line_count']}")
    else:
        print(f"\n[ERROR] OCR Inference Failed: {output['error']}")
        sys.exit(1)
