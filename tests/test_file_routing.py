
import pytest
import shutil
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import backend.put_to_respective_folder as put_module
import backend.memory.memory as memory_module

TEST_DATA_DIR = Path(__file__).resolve().parent / "test_data"


@pytest.fixture
def routing_env(tmp_path, monkeypatch):
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

    monkeypatch.setattr(put_module, "BASE_DIR", fm_dir)
    monkeypatch.setattr(put_module, "OTHER_DIR", other_dir)
    monkeypatch.setattr(put_module, "FOLDERS", folders)

    # Isolated memory rules file
    rules_file = tmp_path / "test_rules.json"
    monkeypatch.setattr(memory_module, "MEMORY_FILE", rules_file)

    return {
        "base_dir": fm_dir,
        "folders": folders,
        "rules_file": rules_file,
        "staging": tmp_path / "staging"
    }


def test_priority_1_explicit_destination(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "custom_doc.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src)

    explicit_dest = routing_env["base_dir"] / "user_chosen_dir"
    result = put_module.put_file(str(src), explicit_dest)

    assert result == explicit_dest / "custom_doc.pdf"
    assert result.exists()
    assert not src.exists()


def test_priority_2_memory_rule(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    dest_rule = routing_env["base_dir"] / "special_dbms"
    memory_module.add_rule("DBMS", str(dest_rule))

    src = staging / "DBMS_Lecture_Notes.pdf"
    shutil.copy(TEST_DATA_DIR / "academic_assignment_sample.pdf", src)

    result = put_module.put_file(str(src), None)

    assert result == dest_rule / "DBMS_Lecture_Notes.pdf"
    assert result.exists()
    assert not src.exists()


def test_image_with_ocr_text_routes_by_classification(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "photo.png"
    shutil.copy(TEST_DATA_DIR / "certificate_ocr.png", src)

    result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["certificate"] / "photo.png"
    assert result.exists()
    assert not src.exists()


def test_image_without_extractable_text_routes_to_images(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "ordinary_photo.png"

    # Create a blank image without readable text.
    Image.new("RGB", (200, 200), color="white").save(src)

    result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["image"] / "ordinary_photo.png"
    assert result.exists()
    assert not src.exists()


def test_priority_3_presentation_extension_routing(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "slides.pptx"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pptx", src)

    result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["presentation"] / "slides.pptx"
    assert result.exists()
    assert not src.exists()


def test_priority_4_zip_archive_routing(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "archive_bundle.zip"
    shutil.copy(TEST_DATA_DIR / "multi_file_archive.zip", src)

    result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["archives"] / "archive_bundle.zip"
    assert result.exists()
    assert not src.exists()


def test_priority_6_fallback_for_unsupported_extension(routing_env, caplog):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "binary_payload.bin"
    shutil.copy(TEST_DATA_DIR / "unsupported.bin", src)

    with caplog.at_level("WARNING"):
        result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["other"] / "binary_payload.bin"
    assert result.exists()
    assert not src.exists()
    assert "Could not process binary_payload.bin" in caplog.text


def test_priority_6_fallback_for_corrupted_file(routing_env, caplog):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "broken_corrupted.pdf"
    shutil.copy(TEST_DATA_DIR / "corrupted.pdf", src)

    with caplog.at_level("WARNING"):
        result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["other"] / "broken_corrupted.pdf"
    assert result.exists()
    assert not src.exists()
    assert "Could not process broken_corrupted.pdf" in caplog.text


def test_priority_5_ml_classification_resume(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "candidate.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src)

    result = put_module.put_file(str(src), None)

    assert result == routing_env["folders"]["resume"] / "candidate.pdf"
    assert result.exists()
    assert not src.exists()


def test_duplicate_filename_protection(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src1 = staging / "candidate.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src1)
    put_module.put_file(str(src1), None)

    src2 = staging / "candidate.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src2)

    with pytest.raises(
        FileExistsError,
        match="A file with this name already exists"
    ):
        put_module.put_file(str(src2), None)

    dest_file = routing_env["folders"]["resume"] / "candidate.pdf"
    assert dest_file.exists()


def test_missing_source_file_raises(routing_env):
    missing = routing_env["staging"] / "does_not_exist.pdf"

    with pytest.raises(FileNotFoundError, match="File does not exist"):
        put_module.put_file(str(missing), None)


def test_destination_directory_creation_on_the_fly(routing_env):
    staging = routing_env["staging"]
    staging.mkdir()

    src = staging / "new_target.pdf"
    shutil.copy(TEST_DATA_DIR / "resume_sample.pdf", src)

    non_existent_folder = (
        routing_env["base_dir"] / "deep" / "nested" / "folder"
    )
    assert not non_existent_folder.exists()

    result = put_module.put_file(str(src), non_existent_folder)

    assert non_existent_folder.exists()
    assert result.exists()
