import shutil
from pathlib import Path
from backend.upload_file import get_file

BASE_DIR = Path("/Users/kshiraj/Desktop/LibManage/backend")
RESUME_DIR = BASE_DIR / "resume"
IMAGES_DIR = BASE_DIR / "images"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def put_file(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")
    
    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    if file_path.suffix.lower() == ".pdf":
        destination = RESUME_DIR / file_path.name

    elif file_path.suffix.lower() in IMAGE_EXTENSIONS:
        destination = IMAGES_DIR / file_path.name
    
    else:
        raise ValueError(
            f"Unsupported file type: {file_path.suffix or 'no extension'}"
        )
    shutil.move(str(file_path), str(destination))

    return destination


if __name__ == "__main__":
    uploaded_file = get_file()
    moved_file = put_file(uploaded_file)

    print(f"File moved successfully to: {moved_file}")