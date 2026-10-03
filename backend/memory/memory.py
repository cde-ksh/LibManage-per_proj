import json

MEMORY_FILE = "rules.json"

def rem_rule(keyword, destination):
    rule = {
        "keyword": keyword,
        "destination": destination
    }

    with open(MEMORY_FILE, "w") as f:
        json.dump(rule, f, indent=4)
