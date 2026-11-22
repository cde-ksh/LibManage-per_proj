import shutil
from pathlib import Path
from backend.upload_file import get_file, get_destination
from backend.classifier.classification import classify_document
from backend.extractor.text_extractor import extract_text
from backend.memory.memory import find_rule

BASE_DIR = Path("/Users/kshiraj/Desktop/LibManage/backend/filemanager")
RESUME_DIR = BASE_DIR / "resume"
IMAGES_DIR = BASE_DIR / "images"
CERTIFICATE_DIR = BASE_DIR / "certificates"
MARKSHEET_DIR = BASE_DIR / "marksheets"
PROJECT_DIR = BASE_DIR / "projects"
OTHER_DIR = BASE_DIR / "other"

FOLDERS = {
    "resume": RESUME_DIR,
    "certificate": CERTIFICATE_DIR,
    "image": IMAGES_DIR,
    "marksheet": MARKSHEET_DIR,
    "project": PROJECT_DIR,
    "other": OTHER_DIR
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def put_file(file_path, dest_loca):
    source = Path(file_path)

    if dest_loca is not None:
        destination_folder = Path(dest_loca)
    
    else:
        rem_dest = find_rule(source.name)
        if rem_dest is not None:
            destination_folder = Path(rem_dest)
        else: 
            text = extract_text(file_path)
            document_type = classify_document(text)
            destination_folder = FOLDERS[document_type]

            destination_folder.mkdir(parents=True, exist_ok=True)

            destination = destination_folder / source.name

            return destination
        



if __name__ == "__main__":
    uploaded_file = get_file()
    destination = get_destination()
    moved_file = put_file(uploaded_file, destination)

    print(f"File moved successfully to: {moved_file}")