import pytest
from pathlib import Path
from backend.extractor.text_extractor import (
    extract_text,
    extract_pdf_text,
    extract_docx_text,
    extract_pptx_text,
    extract_img_text
)

TEST_DATA_DIR = Path(__file__).resolve().parent / "test_data"


def test_extract_pdf_success():
    pdf_path = TEST_DATA_DIR / "resume_sample.pdf"
    text = extract_text(str(pdf_path))
    assert isinstance(text, str)
    assert "John Doe" in text
    assert "Software Engineer" in text


def test_extract_docx_success():
    docx_path = TEST_DATA_DIR / "report_sample.docx"
    text = extract_text(str(docx_path))
    assert isinstance(text, str)
    assert "ORGANIZATIONAL PERFORMANCE REPORT" in text or "Performance" in text


def test_extract_pptx_success():
    pptx_path = TEST_DATA_DIR / "technical_report_sample.pptx"
    text = extract_text(str(pptx_path))
    assert isinstance(text, str)
    assert len(text) > 0
    assert "TECHNICAL REPORT" in text.upper() or "ARCHITECTURE" in text.upper()


def test_extract_png_ocr_success():
    png_path = TEST_DATA_DIR / "certificate_ocr.png"
    text = extract_text(str(png_path))
    assert isinstance(text, str)
    # OCR output should detect certificate / achievement
    text_lower = text.lower()
    assert any(w in text_lower for w in ["certificate", "achievement", "alex", "morgan", "python"])


def test_extract_jpeg_ocr_success():
    jpg_path = TEST_DATA_DIR / "resume_ocr.jpg"
    text = extract_text(str(jpg_path))
    assert isinstance(text, str)
    assert len(text) > 50


def test_extract_webp_ocr_success():
    webp_path = TEST_DATA_DIR / "report_ocr.webp"
    text = extract_text(str(webp_path))
    assert isinstance(text, str)
    assert len(text) > 30


def test_extract_spaces_in_filename_pdf():
    pdf_path = TEST_DATA_DIR / "John Doe Senior Engineer Resume.pdf"
    text = extract_text(str(pdf_path))
    assert "John Doe" in text


def test_extract_spaces_in_filename_docx():
    docx_path = TEST_DATA_DIR / "Q4 Financial Operational Report 2025.docx"
    text = extract_text(str(docx_path))
    assert len(text) > 50


def test_missing_file_raises():
    missing = TEST_DATA_DIR / "non_existent_file.pdf"
    with pytest.raises(FileNotFoundError):
        extract_text(str(missing))


def test_unsupported_extension_bin_raises():
    bin_path = TEST_DATA_DIR / "unsupported.bin"
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(str(bin_path))


def test_unsupported_extension_exe_raises():
    exe_path = TEST_DATA_DIR / "unsupported.exe"
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(str(exe_path))


def test_blank_pdf_no_text():
    blank_pdf = TEST_DATA_DIR / "no_text_blank.pdf"
    text = extract_text(str(blank_pdf))
    assert text.strip() == ""


def test_blank_image_no_text():
    blank_png = TEST_DATA_DIR / "no_text_blank.png"
    text = extract_text(str(blank_png))
    assert text.strip() == ""


def test_extract_gif_ocr():
    gif_path = TEST_DATA_DIR / "invoice_ocr.gif"
    text = extract_text(str(gif_path))
    assert isinstance(text, str)
    assert len(text) > 0


def test_extract_csv_text():
    csv_path = TEST_DATA_DIR / "resume_sample.csv"
    text = extract_text(str(csv_path))
    assert isinstance(text, str)
    assert len(text) > 0
    assert "John Doe" in text or "RowID" in text


def test_empty_files_handling():
    # Empty (0-byte) files should return empty string cleanly rather than crashing with unhandled exceptions
    for empty_name in ["empty.pdf", "empty.docx", "empty.pptx", "empty.png", "empty.txt"]:
        empty_file = TEST_DATA_DIR / empty_name
        text = extract_text(str(empty_file))
        assert text == "", f"Expected empty text for {empty_name}, got: {text}"
