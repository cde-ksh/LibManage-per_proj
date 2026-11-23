from pathlib import Path
import json

PROJECT_DIR = Path(__file__).resolve().parents[2]
# Root-level rules.json is the single canonical source of truth for memory rules
MEMORY_FILE = PROJECT_DIR / "rules.json"
EXAMPLE_FILE = PROJECT_DIR / "rules.json.example"
FILE_MANAGER_DIRECTORY = PROJECT_DIR / "backend" / "filemanager"


def init_rules_if_missing():
    """Initializes canonical root rules.json from template if missing."""
    canonical_root = PROJECT_DIR / "rules.json"
    if not canonical_root.exists() and EXAMPLE_FILE.exists():
        with open(EXAMPLE_FILE, "r") as f:
            data = json.load(f)
        with open(canonical_root, "w") as f:
            json.dump(data, f, indent=4)
        return data
    return None


def load_rules(rules_file=None):
    if rules_file is None:
        init_rules_if_missing()
        target = MEMORY_FILE
    else:
        target = Path(rules_file)

    if target.exists():
        with open(target, "r") as f:
            data = json.load(f)
    else:
        data = {"rules": []}

    return data


def add_rule(keyword, destination, rules_file=None):
    target = Path(rules_file) if rules_file is not None else MEMORY_FILE
    existing_rules = load_rules(target)

    for rule in existing_rules.get("rules", []):
        if rule["keyword"].lower() == keyword.lower():
            return rule

    rule = {
        "keyword": keyword,
        "destination": str(destination)
    }

    if "rules" not in existing_rules:
        existing_rules["rules"] = []

    existing_rules["rules"].append(rule)

    # Persist the updated rules
    with open(target, "w") as f:
        json.dump(existing_rules, f, indent=4)

    return rule


def find_rule(keyword, rules_file=None):
    target = Path(rules_file) if rules_file is not None else MEMORY_FILE
    existing_rules = load_rules(target)
    for rule in existing_rules.get("rules", []):
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
