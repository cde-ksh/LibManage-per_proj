import json
import pytest
from pathlib import Path
import backend.memory.memory as memory_module


@pytest.fixture
def temp_rules_file(tmp_path, monkeypatch):
    rules_file = tmp_path / "test_rules.json"
    monkeypatch.setattr(memory_module, "MEMORY_FILE", rules_file)
    return rules_file


def test_load_rules_missing_file(temp_rules_file):
    assert not temp_rules_file.exists()
    data = memory_module.load_rules()
    assert data == {"rules": []}


def test_load_rules_existing_file(temp_rules_file):
    initial_content = {
        "rules": [
            {"keyword": "DBMS", "destination": "/custom/DBMS"}
        ]
    }
    temp_rules_file.write_text(json.dumps(initial_content, indent=4))

    data = memory_module.load_rules()
    assert len(data["rules"]) == 1
    assert data["rules"][0]["keyword"] == "DBMS"
    assert data["rules"][0]["destination"] == "/custom/DBMS"


def test_load_rules_malformed_json(temp_rules_file):
    temp_rules_file.write_text("{ this is malformed json :")
    with pytest.raises(json.JSONDecodeError):
        memory_module.load_rules()


def test_load_rules_empty_file(temp_rules_file):
    temp_rules_file.write_text("")
    with pytest.raises(json.JSONDecodeError):
        memory_module.load_rules()


def test_add_rule_creates_file_and_persists(temp_rules_file):
    rule = memory_module.add_rule("Python", "/custom/Python")
    assert rule["keyword"] == "Python"
    assert rule["destination"] == "/custom/Python"
    assert temp_rules_file.exists()

    data = memory_module.load_rules()
    assert len(data["rules"]) == 1
    assert data["rules"][0] == rule


def test_add_rule_duplicate_prevention(temp_rules_file):
    memory_module.add_rule("DBMS", "/custom/DBMS_1")
    # Attempt to add exact duplicate
    second = memory_module.add_rule("DBMS", "/custom/DBMS_2")

    assert second["destination"] == "/custom/DBMS_1"
    data = memory_module.load_rules()
    assert len(data["rules"]) == 1


def test_add_rule_duplicate_case_insensitive(temp_rules_file):
    memory_module.add_rule("MACHINE_LEARNING", "/custom/ML")
    # Attempt to add lower case variant
    second = memory_module.add_rule("machine_learning", "/custom/Other_ML")

    assert second["destination"] == "/custom/ML"
    data = memory_module.load_rules()
    assert len(data["rules"]) == 1


def test_find_rule_exact_match(temp_rules_file):
    memory_module.add_rule("Biology", "/custom/Biology")
    dest = memory_module.find_rule("Biology")
    assert dest == "/custom/Biology"


def test_find_rule_substring_match(temp_rules_file):
    memory_module.add_rule("DBMS", "/custom/DBMS")
    dest = memory_module.find_rule("DBMS_Unit_4_Lecture_Notes.pdf")
    assert dest == "/custom/DBMS"


def test_find_rule_case_insensitive_lookup(temp_rules_file):
    memory_module.add_rule("Calculus", "/custom/Math")
    dest = memory_module.find_rule("advanced_calculus_homework.pdf")
    assert dest == "/custom/Math"


def test_find_rule_unknown_keyword(temp_rules_file):
    memory_module.add_rule("History", "/custom/History")
    dest = memory_module.find_rule("random_unrelated_filename.pdf")
    assert dest is None


def test_persistence_across_multiple_operations(temp_rules_file):
    memory_module.add_rule("Algebra", "/custom/Algebra")
    memory_module.add_rule("Geometry", "/custom/Geometry")

    reloaded = memory_module.load_rules()
    assert len(reloaded["rules"]) == 2
    keywords = [r["keyword"] for r in reloaded["rules"]]
    assert "Algebra" in keywords
    assert "Geometry" in keywords


def test_canonical_rules_path_points_to_root():
    # Verify root-level rules.json is canonical and existing user rules are intact
    root_file = memory_module.PROJECT_DIR / "rules.json"
    assert root_file.exists()
    assert root_file.name == "rules.json"
    assert root_file.parent == memory_module.PROJECT_DIR

    data = memory_module.load_rules(root_file)
    keywords = [r["keyword"] for r in data.get("rules", [])]
    assert "DBMS" in keywords
    assert "Python" in keywords


def test_init_rules_from_example_template(tmp_path, monkeypatch):
    # Verify safe initialization from template when root rules.json does not exist
    fake_project = tmp_path / "project"
    fake_project.mkdir()
    fake_example = fake_project / "rules.json.example"
    fake_example.write_text(json.dumps({"rules": [{"keyword": "Example", "destination": "/test"}]}))
    fake_root = fake_project / "rules.json"

    monkeypatch.setattr(memory_module, "PROJECT_DIR", fake_project)
    monkeypatch.setattr(memory_module, "MEMORY_FILE", fake_root)
    monkeypatch.setattr(memory_module, "EXAMPLE_FILE", fake_example)

    assert not fake_root.exists()
    data = memory_module.load_rules()
    assert fake_root.exists()
    assert data["rules"][0]["keyword"] == "Example"
