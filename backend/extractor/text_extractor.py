import pymupdf, pypandoc
from pathlib import Path
from PIL import Image
import pytesseract

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff"
}


def extract_pdf_text(file_path):
    with pymupdf.open(file_path) as doc:
        text = chr(12).join([page.get_text() for page in doc])

    return text

def extract_docx_text(file_path):
    text = pypandoc.convert_file(str(file_path), "plain")

    return text

def extract_img_text(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)

    return text

def extract_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension in {".docx", ".doc"}:
        return extract_docx_text(file_path)
    
    elif extension in IMAGE_EXTENSIONS:
        return extract_img_text(file_path)
    
    else:
        raise ValueError(
            f"Unsupported file type: {extension or 'no extension'}"
        )

