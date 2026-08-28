from upload_file import get_file
from put_to_respective_folder import put_file
from extractor.text_extractor import extract_text
from classifier.classification import classify_document

def main():
    file_path = get_file()

    text = extract_text(file_path)

    document_type = classify_document(text)
    print(f"Document type: {document_type}")

    moved_file = put_file(file_path, )