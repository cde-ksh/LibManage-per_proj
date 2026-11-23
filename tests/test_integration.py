import pytest
import shutil
from pathlib import Path
from unittest.mock import patch

import backend.main as main_module
import backend.upload_file as upload_module
import backend.put_to_respective_folder as put_module
import backend.memory.memory as memory_module

TEST_DATA_DIR = Path(__file__).resolve().parent / "test_data"


@pytest.fixture
def integrated_env(tmp_path, monkeypatch):
    fm_dir = tmp_path / "filemanager"
    fm_dir.mkdir(parents=True, exist_ok=True)

    other_dir = fm_dir / "other"
    folders = {
        "resume": fm_dir / "resume",
        "certificate": fm_dir / "certificates",
        "image": fm_dir / "images",
        "marksheet": fm_dir / "marksheets",
        "project": fm_dir / "projects",
        "presentation": fm_dir / "presentations",
        "report": fm_dir / "reports",
        "archives": fm_dir / "archives",
        "other": other_dir
    }

    monkeypatch.setattr(upload_module, "BASE_DIR", fm_dir)
    monkeypatch.setattr(put_module, "BASE_DIR", fm_dir)
    monkeypatch.setattr(put_module, "OTHER_DIR", other_dir)
    monkeypatch.setattr(put_module, "FOLDERS", folders)

    rules_file = tmp_path / "test_rules.json"
    monkeypatch.setattr(memory_module, "MEMORY_FILE", rules_file)

    staging = tmp_path / "staging"
    staging.mkdir(parents=True, exist_ok=True)

    return {
        "base_dir": fm_dir,
        "folders": folders,
        "staging": staging,
        "rules_file": rules_file
    }


def test_workflow_manual_destination(integrated_env, capsys):
    src = integrated_env["staging"] / "manual_test.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src)

    with patch("builtins.input", side_effect=[str(src), "manual_vault"]):
        main_module.main()

    out = capsys.readouterr().out
    assert "File moved to:" in out
    expected_file = integrated_env["base_dir"] / "manual_vault" / "manual_test.pdf"
    assert expected_file.exists()
    assert not src.exists()


def test_workflow_automatic_ml_classification(integrated_env, capsys):
    src = integrated_env["staging"] / "auto_resume.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src)

    with patch("builtins.input", side_effect=[str(src), ""]):
        main_module.main()

    out = capsys.readouterr().out
    assert "File moved to:" in out
    expected_file = integrated_env["folders"]["resume"] / "auto_resume.pdf"
    assert expected_file.exists()
    assert not src.exists()


def test_workflow_memory_routing(integrated_env, capsys):
    # Register rule
    memory_module.add_rule("CHEMISTRY", str(integrated_env["base_dir"] / "chem_notes"))

    src = integrated_env["staging"] / "CHEMISTRY_Lab_Report.pdf"
    shutil.copy(TEST_DATA_DIR / "research_report_sample.pdf", src)

    with patch("builtins.input", side_effect=[str(src), ""]):
        main_module.main()

    out = capsys.readouterr().out
    assert "File moved to:" in out
    expected_file = integrated_env["base_dir"] / "chem_notes" / "CHEMISTRY_Lab_Report.pdf"
    assert expected_file.exists()
    assert not src.exists()


def test_workflow_missing_input_file(integrated_env):
    missing_path = integrated_env["staging"] / "not_there.pdf"

    with patch("builtins.input", side_effect=[str(missing_path), ""]):
        with pytest.raises(FileNotFoundError):
            main_module.main()


def test_workflow_duplicate_destination_file(integrated_env):
    src1 = integrated_env["staging"] / "dup_doc.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src1)

    with patch("builtins.input", side_effect=[str(src1), ""]):
        main_module.main()

    # Second copy to cause collision
    src2 = integrated_env["staging"] / "dup_doc.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src2)

    with patch("builtins.input", side_effect=[str(src2), ""]):
        with pytest.raises(FileExistsError):
            main_module.main()
