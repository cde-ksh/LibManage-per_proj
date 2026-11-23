import shutil
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

from backend.upload_file import get_file, get_destination
from backend.classifier.classification import classify_document
from backend.extractor.text_extractor import extract_text
from backend.memory.memory import find_rule


# Dynamic base directory relative to the repository / backend
BASE_DIR = Path(__file__).resolve().parent / "filemanager"

RESUME_DIR = BASE_DIR / "resume"
IMAGES_DIR = BASE_DIR / "images"
CERTIFICATE_DIR = BASE_DIR / "certificates"
MARKSHEET_DIR = BASE_DIR / "marksheets"
PROJECT_DIR = BASE_DIR / "projects"
PRESENTATION_DIR = BASE_DIR / "presentations"
REPORT_DIR = BASE_DIR / "reports"
ARCHIVE_DIR = BASE_DIR / "archives"
OTHER_DIR = BASE_DIR / "other"


FOLDERS = {
    "resume": RESUME_DIR,
    "certificate": CERTIFICATE_DIR,
    "certificates": CERTIFICATE_DIR,
    "image": IMAGES_DIR,
    "images": IMAGES_DIR,
    "marksheet": MARKSHEET_DIR,
    "marksheets": MARKSHEET_DIR,
    "project": PROJECT_DIR,
    "projects": PROJECT_DIR,
    "presentation": PRESENTATION_DIR,
    "presentations": PRESENTATION_DIR,
    "report": REPORT_DIR,
    "reports": REPORT_DIR,
    "archive": ARCHIVE_DIR,
    "archives": ARCHIVE_DIR,
    "other": OTHER_DIR
}


IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"
}

PRESENTATION_EXTENSIONS = {
    ".pptx", ".ppt"
}

ARCHIVE_EXTENSIONS = {
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"
}


def put_file(file_path, dest_loca=None):
    source = Path(file_path)

    if not source.is_file():
        raise FileNotFoundError(
            f"File does not exist: {source}"
        )

    # Priority 1: User-provided destination
    if dest_loca is not None:
        destination_folder = Path(dest_loca)

    else:
        # Priority 2: Previously saved memory rule
        rem_dest = find_rule(source.name)

        if rem_dest is not None:
            destination_folder = Path(rem_dest)

        else:

            extension = source.suffix.lower()

            # Priority 3: Direct routing for presentations
            if extension in PRESENTATION_EXTENSIONS:
                document_type = "presentation"

            # Priority 4: Direct routing for archives
            elif extension in ARCHIVE_EXTENSIONS:
                document_type = "archives"

            # Priority 5: OCR and ML classification for images
            elif extension in IMAGE_EXTENSIONS:
                try:
                    text = extract_text(str(source))

                    if isinstance(text, str) and text.strip():
                        document_type = classify_document(text)
                    else:
                        document_type = "image"

                except Exception as exc:
                    logger.warning(
                        "Could not extract text from image %s: %s: %s. "
                        "Routing to images.",
                        source.name,
                        type(exc).__name__,
                        exc
                    )
                    document_type = "image"

            # Priority 6: ML classification for other supported documents
            else:
                try:
                    text = extract_text(str(source))
                    document_type = classify_document(text)

                except Exception as exc:
                    logger.warning(
                        "Could not process %s: %s: %s. "
                        "Routing to other.",
                        source.name,
                        type(exc).__name__,
                        exc
                    )
                    document_type = "other"

            destination_folder = FOLDERS.get(
                document_type,
                OTHER_DIR
            )

    # Create destination directory if it does not exist
    destination_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = destination_folder / source.name

    # Prevent accidental overwriting
    if destination.exists():
        raise FileExistsError(
            f"A file with this name already exists: {destination}"
        )

    # Move file safely
    shutil.move(
        str(source),
        str(destination)
    )

    return destination


if __name__ == "__main__":
    uploaded_file = get_file()
    destination = get_destination()

    moved_file = put_file(
        uploaded_file,
        destination
    )

    print(f"File moved successfully to: {moved_file}")
