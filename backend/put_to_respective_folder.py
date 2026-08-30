import shutil
from pathlib import Path
from backend.upload_file import get_file

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

def put_file(file_path, document_type):
    destination_folder = FOLDERS[document_type]
    destination_folder.mkdir(parents=True, exist_ok=True)
    destination = destination_folder / Path(file_path).name
    
    shutil.move(str(file_path), str(destination))

    return destination    
    

if __name__ == "__main__":
    uploaded_file = get_file()
    moved_file = put_file(uploaded_file)

    print(f"File moved successfully to: {moved_file}")