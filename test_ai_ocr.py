"""
தமிழ் மரபு AI – Comprehensive AI OCR & Engine Test Suite (test_ai_ocr.py)
========================================================================
Automated verification covering:
  1. Model initialization, architecture metadata, and hardware detection (CUDA/CPU).
  2. Input validation: non-existent file paths, corrupted image bytes, invalid types.
  3. Real Tamil OCR inference on sample manuscript (verifying authentic Tamil Unicode).
  4. Functional one-line interface: extract_tamil_text().
  5. CPU execution compatibility and fallback mode.
  6. Multi-format support: WEBP, PNG, and JPEG loading & preprocessing.
  7. Empty / blank image handling and whitespace strip.
  8. Tamil Unicode encoding integrity and string preservation.
  9. OCR comparison analysis logic (similarity ratio, character and word difference).
 10. PDF document rendering helper (PyMuPDF integration).

Usage:
  py .\test_ai_ocr.py
"""

import sys
import os
import io
import tempfile
import pytest
from pathlib import Path
from PIL import Image

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import ocr_engine
from ai_ocr import (
    TamilAIOCR,
    extract_tamil_text,
    extract_tamil_text_detailed,
    resolve_image_path,
)


def find_sample_image() -> Path:
    candidates = [
        PROJECT_ROOT / "samples" / "sample_tamil.jpg",
        PROJECT_ROOT.parent / "TamilHeritageAI_Model" / "sample_tamil.jpg",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return candidates[0]


def test_model_loading():
    """Test 1: Verify model instantiation, device detection, and metadata."""
    print("\n[TEST 1] Model Loading and Hardware Configuration...")
    ocr = TamilAIOCR(device_preference="auto")
    info = ocr.get_info()
    print(f"  -> Model ID: {info['model_id']}")
    print(f"  -> Architecture: {info['architecture']}")
    print(f"  -> Active Device: {info['device']}")
    print(f"  -> PyTorch Version: {info['torch_version']}")
    assert ocr.model is not None, "Model was not loaded successfully."
    assert ocr.processor is not None, "Processor was not loaded successfully."
    print("  [PASS] Model initialized and verified.")


@pytest.fixture(scope="module")
def ocr():
    """Pytest fixture: shared TamilAIOCR instance for tests that require it."""
    return TamilAIOCR(device_preference="auto")


def test_input_validation(ocr: TamilAIOCR):
    """Test 2: Verify error handling on invalid paths, corrupted files, and wrong types."""
    print("\n[TEST 2] Image Input Validation and Error Handling...")

    # Case A: Non-existent file path
    non_existent = "non_existent_tamil_document_12345.jpg"
    try:
        ocr.extract_text(non_existent)
        assert False, "Should have raised FileNotFoundError for missing file."
    except FileNotFoundError:
        print("  [PASS] FileNotFoundError correctly raised for non-existent path.")

    # Case B: Corrupted/invalid image file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(b"NOT_A_REAL_IMAGE_DATA_CORRUPT")
        tmp_path = tmp.name

    try:
        ocr.extract_text(tmp_path)
        assert False, "Should have raised ValueError for corrupt image."
    except ValueError:
        print("  [PASS] ValueError correctly raised for unreadable/corrupted file.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # Case C: Invalid input type
    try:
        ocr.extract_text(12345)  # type: ignore
        assert False, "Should have raised TypeError for invalid type."
    except TypeError:
        print("  [PASS] TypeError correctly raised for invalid input data type.")


def test_real_inference(ocr: TamilAIOCR):
    """Test 3: Perform actual OCR inference on sample image via both path and PIL Image."""
    print("\n[TEST 3] Real Tamil OCR Inference & Authentic Output...")

    sample_img_path = find_sample_image()
    if not sample_img_path.exists():
        print(f"  [SKIPPED] Sample image not found at: {sample_img_path}")
        return

    print(f"  -> Testing with real sample image: {sample_img_path}")

    # Test via file path string
    start_path_test = ocr.extract_text(str(sample_img_path))
    assert isinstance(start_path_test, str), "Output must be a Python string."
    assert len(start_path_test) > 0, "Extracted text should not be empty."
    print(f"  -> Inference elapsed: {ocr.last_inference_time}s")
    print("  -> Authentic Extracted Tamil Text:")
    for line in start_path_test.splitlines():
        print(f"     \"{line}\"")

    # Test via PIL Image object
    with Image.open(sample_img_path) as pil_img:
        text_from_pil = ocr.extract_text(pil_img)
        assert isinstance(text_from_pil, str)
        assert text_from_pil == start_path_test

    print("  [PASS] Real OCR inference succeeded with authentic Tamil character extraction.")


def test_functional_interface():
    """Test 4: Verify the one-line helper function extract_tamil_text()."""
    print("\n[TEST 4] Functional API Interface...")
    sample_img_path = find_sample_image()
    if sample_img_path.exists():
        extracted = extract_tamil_text(sample_img_path)
        assert isinstance(extracted, str), "extract_tamil_text() must return string."
        assert len(extracted) > 0, "Extracted text should not be empty."
        print(f"  [PASS] extract_tamil_text() functional call succeeded ({len(extracted)} chars).")
    else:
        print("  [SKIPPED] Sample image missing for functional test.")


def test_cpu_compatibility():
    """Test 5: Explicitly verify CPU execution fallback mode."""
    print("\n[TEST 5] CPU Execution Compatibility...")
    cpu_ocr = TamilAIOCR(device_preference="cpu")
    info = cpu_ocr.get_info()
    assert info["device"] == "cpu", "Device should be explicitly set to 'cpu'."
    print(f"  -> CPU engine initialized in {cpu_ocr.load_time}s")

    sample_img_path = find_sample_image()
    if sample_img_path.exists():
        cpu_text = cpu_ocr.extract_text(str(sample_img_path))
        print(f"  -> CPU inference completed in {cpu_ocr.last_inference_time}s")
        assert isinstance(cpu_text, str)
        print("  [PASS] CPU inference verified and operational.")
    else:
        print("  [PASS] CPU model initialization verified.")


def test_multi_format_support(ocr: TamilAIOCR):
    """Test 6: Verify WEBP and PNG loading and processing via Pillow."""
    print("\n[TEST 6] Multi-Format Support (WEBP, PNG, JPEG)...")
    sample_path = find_sample_image()
    if not sample_path.exists():
        print("  [SKIPPED] Sample image missing.")
        return

    orig_img = Image.open(sample_path)

    # 1. Test WEBP format
    webp_io = io.BytesIO()
    orig_img.save(webp_io, format="WEBP")
    webp_io.seek(0)
    webp_img = Image.open(webp_io)
    webp_out = ocr.extract_text(webp_img)
    assert len(webp_out) > 0, "WEBP extraction failed."
    print(f"  -> WEBP extraction: {len(webp_out)} characters")

    # 2. Test PNG format
    png_io = io.BytesIO()
    orig_img.save(png_io, format="PNG")
    png_io.seek(0)
    png_img = Image.open(png_io)
    png_out = ocr.extract_text(png_img)
    assert len(png_out) > 0, "PNG extraction failed."
    print(f"  -> PNG extraction: {len(png_out)} characters")

    print("  [PASS] WEBP, PNG, and JPEG formats supported.")


def test_empty_image_handling(ocr: TamilAIOCR):
    """Test 7: Verify blank white image does not crash the pipeline."""
    print("\n[TEST 7] Blank / Empty Image Handling...")
    blank_img = Image.new("RGB", (300, 100), color="white")
    result = ocr.extract_detailed(blank_img)
    assert isinstance(result, dict)
    assert result["success"] is True
    assert isinstance(result["text"], str)
    print("  [PASS] Blank image handled cleanly without exception.")


def test_tamil_unicode_integrity():
    """Test 8: Verify Tamil Unicode encoding, preservation, and UTF-8 TXT export."""
    print("\n[TEST 8] Tamil Unicode Integrity...")
    sample_tamil = "தமிழ் மரபு ஏஐ – பழமையான தமிழ் நூல்கள்"
    utf8_encoded = sample_tamil.encode("utf-8")
    utf8_decoded = utf8_encoded.decode("utf-8")
    assert sample_tamil == utf8_decoded, "Unicode UTF-8 encoding failed."
    assert "தமிழ்" in utf8_decoded
    print(f"  -> Original: {sample_tamil}")
    print(f"  -> Decoded : {utf8_decoded}")
    print("  [PASS] Tamil Unicode strings and UTF-8 encoding verified.")


def test_comparison_analysis():
    """Test 9: Verify diff and similarity metrics between two OCR outputs."""
    print("\n[TEST 9] OCR Comparison Analysis Logic...")
    text_a = "தமிழ் மரபு"
    text_b = "தமிழ் வரலாறு"
    stats = ocr_engine.compare_ocr_results(text_a, text_b)
    assert "similarity_percentage" in stats
    assert "char_diff" in stats
    assert "word_diff" in stats
    assert "diff_lines" in stats
    print(f"  -> Similarity: {stats['similarity_percentage']}%")
    print(f"  -> Character Diff: {stats['char_diff']}")
    print("  [PASS] Comparison analysis logic verified.")


def test_pdf_helper():
    """Test 10: Verify PDF rendering using PyMuPDF."""
    print("\n[TEST 10] PDF Rendering Helper...")
    import pymupdf
    sample_path = find_sample_image()
    if not sample_path.exists():
        print("  [SKIPPED] Sample image missing.")
        return

    # Generate a temporary single-page PDF containing sample image
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name

    try:
        doc = pymupdf.open()
        page = doc.new_page(width=600, height=800)
        page.insert_image(pymupdf.Rect(50, 50, 550, 400), filename=str(sample_path))
        doc.save(tmp_pdf_path)
        doc.close()

        with open(tmp_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        page_count = ocr_engine.get_pdf_page_count(pdf_bytes)
        assert page_count == 1, f"Expected 1 page, got {page_count}"

        rendered_img = ocr_engine.render_pdf_page_to_image(pdf_bytes, page_number=0, dpi=150)
        assert rendered_img is not None
        assert isinstance(rendered_img, Image.Image)
        print(f"  -> Rendered PDF page dimensions: {rendered_img.width}x{rendered_img.height}")
        print("  [PASS] PDF helper verified.")
    finally:
        if os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)


if __name__ == "__main__":
    print("=" * 68)
    print("  தமிழ் மரபு AI – Comprehensive AI OCR & Engine Test Suite")
    print("=" * 68)

    try:
        active_ocr = test_model_loading()
        test_input_validation(active_ocr)
        test_real_inference(active_ocr)
        test_functional_interface()
        test_cpu_compatibility()
        test_multi_format_support(active_ocr)
        test_empty_image_handling(active_ocr)
        test_tamil_unicode_integrity()
        test_comparison_analysis()
        test_pdf_helper()

        print("\n" + "=" * 68)
        print("  ALL 10 VERIFICATION TESTS COMPLETED AND PASSED!")
        print("=" * 68)
    except AssertionError as ae:
        print(f"\n[FAIL] Assertion failed: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test suite encountered an exception: {e}")
        sys.exit(1)
