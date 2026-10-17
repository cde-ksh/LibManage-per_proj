from pathlib import Path
import json

PROJECT_DIR = Path(__file__).resolve().parents[2]
MEMORY_FILE = PROJECT_DIR / "rules.json"
FILE_MANAGER_DIRECTORY = PROJECT_DIR / "backend" / "filemanager"


def load_rules():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

    else:
        data = {"rules": []}

    return data
    





def rem_rule(keyword, destination):
    rule = {
        "keyword": keyword,
        "destination": destination
    }

    with open(MEMORY_FILE, "w") as f:
        json.dump(rule, f, indent=4)
