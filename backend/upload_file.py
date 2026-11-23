from pathlib import Path

# Dynamic base directory relative to the repository / backend
BASE_DIR = Path(__file__).resolve().parent / "filemanager"

def get_file():
    file = Path(input("Import your file: ").strip()).expanduser()
    if not file.is_file():
        raise FileNotFoundError(f"File not exists: {file}")
    return file

def get_destination():
    dest = input("Enter your destination (press Enter to skip): ").strip()
    if not dest:
        return None
    destination = BASE_DIR / dest
    destination.mkdir(parents=True, exist_ok=True)
    return destination
