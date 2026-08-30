from pathlib import Path

BASE_DIR = Path("/Users/kshiraj/Desktop/LibManage/backend/filemanager")

def get_file():
    file = Path(input("Import your file: "))
    if not file.is_file():
        raise FileNotFoundError("File not exists...")
    
    return file

def get_destination():
    dest = input("Enter your destination: ").strip()
    if not dest:
        destination = None
    else:
        destination = BASE_DIR / dest
        if not destination.exists():
            destination.mkdir(parents=True, exist_ok=True)

    return destination
