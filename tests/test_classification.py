import pytest
from backend.classifier.classification import classify_document, predict_document, model


def test_classify_empty_string():
    assert classify_document("") == "other"


def test_classify_whitespace_only():
    assert classify_document("   \n\t  ") == "other"


def test_classify_none_input():
    assert classify_document(None) == "other"


def test_classify_non_string():
    assert classify_document(12345) == "other"
    assert classify_document(["list", "of", "text"]) == "other"


def test_predict_document_empty():
    res = predict_document("")
    assert res["category"] == "other"
    assert res["confidence"] == 0.0
    assert res["probabilities"] == {}


def test_predict_document_valid():
    sample_resume = "Software Engineer with experience in Python, FastAPI, Docker, and SQL."
    res = predict_document(sample_resume)
    assert "category" in res
    assert "confidence" in res
    assert "probabilities" in res
    assert isinstance(res["confidence"], float)
    assert res["category"] in model.classes_
    # Sum of probabilities should be approximately 1.0
    total_prob = sum(res["probabilities"].values())
    assert pytest.approx(total_prob, abs=1e-2) == 1.0


def test_classify_clear_resume():
    text = "John Doe Curriculum Vitae Education B.S. Computer Science Experience Python Software Developer"
    pred = classify_document(text)
    assert pred == "resume"


def test_classify_clear_certificate():
    text = "Certificate of Completion awarded to student for successfully completing machine learning course"
    pred = classify_document(text)
    assert pred == "certificate"


def test_classify_clear_marksheet():
    text = "Student Examination Marksheet Roll Number Subject Code Marks Grade Total SGPA CGPA"
    pred = classify_document(text)
    assert pred == "marksheet"


def test_report_classification_behavior():
    # Reports should classify as report
    report_text = (
        "Investigative report detailing the sequence of events, forensic evidence collected, "
        "and conclusions regarding an organizational incident."
    )
    res = predict_document(report_text)
    assert res["category"] == "report"
    assert res["confidence"] > 0.25


def test_known_categories_coverage():
    expected_categories = {"certificate", "marksheet", "project", "report", "resume"}
    assert set(model.classes_) == expected_categories
