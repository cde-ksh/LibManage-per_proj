import pymupdf
import pypandoc
from pathlib import Path
from PIL import Image
import pytesseract
from pptx import Presentation

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff",
    ".gif"
}


def extract_pdf_text(file_path):
    try:
        with pymupdf.open(file_path) as doc:
            text = chr(12).join([page.get_text() for page in doc])
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text from {file_path}: {e}") from e


def extract_docx_text(file_path):
    try:
        text = pypandoc.convert_file(str(file_path), "plain")
        return text
    except Exception:
        # Fallback to python-docx if pandoc fails
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(paragraphs)
        except Exception as e:
            raise ValueError(f"Failed to extract DOCX text from {file_path}: {e}") from e


def extract_img_text(file_path):
    try:
        with Image.open(file_path) as image:
            text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract image text from {file_path}: {e}") from e


def extract_pptx_text(file_path):
    try:
        presentation = Presentation(file_path)
        text = []
        for slide in presentation.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text.append(shape.text)
                if shape.has_table:
                    for row in shape.table.rows:
                        for cell in row.cells:
                            text.append(cell.text)
        return "\n".join(text)
    except Exception as e:
        raise ValueError(f"Failed to extract PPTX text from {file_path}: {e}") from e


def extract_plain_text(file_path):
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        raise ValueError(f"Failed to extract text from {file_path}: {e}") from e


def extract_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Clean handling for empty (0-byte) files
    if file_path.stat().st_size == 0:
        return ""

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension in {".docx", ".doc"}:
        return extract_docx_text(file_path)

    elif extension in IMAGE_EXTENSIONS:
        return extract_img_text(file_path)

    elif extension == ".pptx":
        return extract_pptx_text(file_path)

    elif extension in {".csv", ".txt"}:
        return extract_plain_text(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension or 'no extension'}"
        )
