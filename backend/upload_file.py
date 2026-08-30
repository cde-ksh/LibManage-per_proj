from pathlib import Path
def get_file():
    file = Path(input("Import your file: "))
    if not file.exists():
        raise FileNotFoundError("File not exists...")
    
    return file

