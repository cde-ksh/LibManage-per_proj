import pytest
from pathlib import Path
from unittest.mock import patch
import backend.upload_file as upload_module


@pytest.fixture
def temp_workspace(tmp_path, monkeypatch):
    fm_dir = tmp_path / "filemanager"
    fm_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(upload_module, "BASE_DIR", fm_dir)
    return fm_dir


def test_get_file_valid(tmp_path):
    test_file = tmp_path / "sample.pdf"
    test_file.write_text("dummy content")

    with patch("builtins.input", return_value=str(test_file)):
        result = upload_module.get_file()

    assert result == test_file
    assert result.is_file()


def test_get_file_with_whitespace(tmp_path):
    test_file = tmp_path / "sample space.pdf"
    test_file.write_text("dummy content")

    with patch("builtins.input", return_value=f"  {test_file}  "):
        result = upload_module.get_file()

    assert result == test_file


def test_get_file_not_found(tmp_path):
    missing_file = tmp_path / "missing.pdf"

    with patch("builtins.input", return_value=str(missing_file)):
        with pytest.raises(FileNotFoundError, match="File not exists"):
            upload_module.get_file()


def test_get_destination_skipped(temp_workspace):
    with patch("builtins.input", return_value=""):
        result = upload_module.get_destination()

    assert result is None


def test_get_destination_provided(temp_workspace):
    with patch("builtins.input", return_value="my_custom_folder"):
        result = upload_module.get_destination()

    expected_path = temp_workspace / "my_custom_folder"
    assert result == expected_path
    assert expected_path.is_dir()


def test_get_destination_with_whitespace(temp_workspace):
    with patch("builtins.input", return_value="   finance_docs   "):
        result = upload_module.get_destination()

    expected_path = temp_workspace / "finance_docs"
    assert result == expected_path
    assert expected_path.is_dir()
