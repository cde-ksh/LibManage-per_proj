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


def add_rule(keyword, destination):
    existing_rules = load_rules()

    for rule in existing_rules["rules"]:
        if rule["keyword"].lower() == keyword.lower():
            return rule

    rule = {
        "keyword": keyword,
        "destination": str(destination)
    }

    existing_rules["rules"].append(rule)

    # Persist the updated rules
    with open(MEMORY_FILE, "w") as f:
        json.dump(existing_rules, f, indent=4)

    return rule


def find_rule(keyword):
    existing_rules = load_rules()
    for rule in existing_rules["rules"]:
        if rule["keyword"].lower() in keyword.lower():
            return rule["destination"]
    return None
        

if __name__ == "__main__":

    print(add_rule("DBMS", "/Documents/DBMS"))
    print(add_rule("Python", "/Documents/Python"))

    print("\nAll rules:")
    print(load_rules())

    print("\nFind DBMS:")
    print(find_rule("DBMS_Unit_4.pdf"))

    print("\nFind unknown:")
    print(find_rule("unknown.pdf"))