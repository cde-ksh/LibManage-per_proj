from backend.upload_file import get_file
from backend.put_to_respective_folder import put_file
from backend.extractor.text_extractor import extract_text
from backend.classifier.classification import classify_document

def main():
    file_path = get_file()

    text = extract_text(file_path)

    document_type = classify_document(text)
    print(f"Document type: {document_type}")

    moved_file = put_file(file_path, document_type)

    print(f"File moved to: {moved_file}")


if __name__ == "__main__":
    main()