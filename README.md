# LibManage V1.0.0 — Intelligent Document Organizer

LibManage is an automated, intelligent document management and organization utility designed to sort local incoming files into structured directories. It combines explicit user overrides, persistent memory rules, file-extension dispatching, multi-format text extraction, optical character recognition (OCR), and machine-learning text classification.

---

## 1. Project Overview

Manual file sorting is repetitive, error-prone, and inconsistent. LibManage automates file intake and organization through a multi-tier routing pipeline:
- Respects explicit user destination overrides when provided.
- Remembers user keyword preferences via a persistent memory rules file.
- Directs images, presentations, and archives straight to dedicated folders.
- Ingests text documents, extracts plain text from multiple container formats, and applies machine-learning classification.
- Protects files against accidental data overwrite and falls back safely to an `other/` directory when documents are unsupported or corrupted.

---

## 2. Features

- **Local File Organization**: Automatically ingests files and moves them into organized category subdirectories.
- **User-Specified Destination**: Prioritizes manual destination input when specified by the user.
- **Memory-Based Keyword Routing**: Substring, case-insensitive keyword rules stored in `rules.json` override automatic classification.
- **Extension-Based Routing**:
  - Images (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tiff`, `.gif`) $\rightarrow$ `images/`
  - Presentations (`.pptx`, `.ppt`) $\rightarrow$ `presentations/`
  - Archives (`.zip`, `.tar`, `.gz`, `.bz2`, `.7z`, `.rar`) $\rightarrow$ `archives/`
- **Machine Learning Classification**: TF-IDF n-gram vectorizer with balanced Logistic Regression classifying text documents into `resume/`, `certificates/`, `marksheets/`, `reports/`, and `projects/`.
- **Multi-Format Text Extraction**:
  - **PDF**: Multi-page text extraction via PyMuPDF.
  - **DOCX / DOC**: Conversion via Pandoc with a native `python-docx` fallback.
  - **PPTX**: Text extraction across slides, shapes, text frames, and tables via `python-pptx`.
  - **CSV & TXT**: Plain-text parsing with UTF-8 encoding support.
- **Image OCR**: Extracts readable text from images using Tesseract OCR and Pillow.
- **Duplicate Filename Collision Protection**: Strictly raises `FileExistsError` to prevent overwriting existing files at the destination.
- **Failure Logging and Safe Fallback**: Unextractable, unsupported, or corrupted files log a warning and fall back safely to `other/`.

---

## 3. Technology Stack

- **Language**: Python 3.10+ (Verified on Python 3.13)
- **Machine Learning**: `scikit-learn`, `pandas`
- **Document Processing**: `PyMuPDF`, `python-docx`, `python-pptx`, `pypandoc`
- **Computer Vision & OCR**: `Pillow`, `pytesseract`
- **Testing**: `pytest`
- **External Binaries**: `pandoc`, `tesseract`

---

## 4. Project Structure

```
LibManage/
├── backend/
│   ├── classifier/
│   │   ├── classification.py          # TF-IDF + Logistic Regression pipeline
│   │   └── training_data.csv          # Labeled training dataset (120 records)
│   ├── extractor/
│   │   └── text_extractor.py          # PDF, DOCX, PPTX, OCR, CSV extractors
│   ├── filemanager/                   # Destination storage directories
│   ├── memory/
│   │   └── memory.py                  # Memory rule management & search
│   ├── main.py                        # Programmatic & CLI entry point
│   ├── put_to_respective_folder.py    # Hierarchical routing engine
│   └── upload_file.py                 # File ingestion & path validation
├── tests/
│   ├── generate_test_data.py          # Synthetic document generation
│   ├── test_classification.py         # Classifier unit tests
│   ├── test_file_routing.py           # Priority routing & safety tests
│   ├── test_integration.py            # End-to-end integration tests
│   ├── test_memory.py                 # Memory persistence tests
│   ├── test_text_extractor.py         # Extraction and OCR tests
│   └── test_upload_file.py            # CLI input validation tests
├── .gitignore                         # Excludes user files, test data, and caches
├── README.md                          # Project documentation
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development & testing dependencies
├── rules.json.example                 # Distributable template for memory rules
└── rules.json                         # Local user memory configuration (git-ignored)
```

---

## 5. System Requirements

- **Python**: Version 3.10 to 3.13
- **Pandoc**: Document conversion utility (version 3.0+)
- **Tesseract OCR**: Optical character recognition engine (version 5.0+)

### System Package Installation

**On macOS (using Homebrew):**
```bash
brew install pandoc tesseract
```

**On Linux (Ubuntu / Debian):**
```bash
sudo apt-get update
sudo apt-get install -y pandoc tesseract-ocr
```

---

## 6. Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd LibManage
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Upgrade pip and install production dependencies:**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. **Install development/testing dependencies (optional, for running tests):**
   ```bash
   python -m pip install -r requirements-dev.txt
   ```

5. **Initialize memory rules configuration:**
   If `rules.json` does not exist at the project root, copy the template:
   ```bash
   cp rules.json.example rules.json
   ```
   *(If not manually initialized, LibManage will automatically create it from `rules.json.example` on first execution).*

---

## 7. Running the Application

### Interactive CLI Mode
Run the intake workflow from the repository root:
```bash
python -m backend.main
```
You will be prompted to enter the path of the file to import and an optional target destination:
```
Import your file: /path/to/invoice.pdf
Enter your destination (press Enter to skip):
File moved to: /Users/.../backend/filemanager/other/invoice.pdf
```

### Programmatic Python API
LibManage provides a clean Python function for embedding into other scripts:
```python
from backend.main import organize

# Automatic routing (Memory -> Extension -> ML Classifier -> other/)
moved_path = organize("samples/resume.pdf")
print(f"File moved to: {moved_path}")

# Explicit destination override
custom_path = organize("samples/notes.docx", destination="my_custom_folder")
print(f"File moved to: {custom_path}")
```

---

## 8. Memory Rules Configuration

LibManage allows you to define keyword rules that take precedence over the machine learning classifier.

### How It Works
- Rules are stored in `rules.json` at the project root.
- Matching is **case-insensitive** and searches for **substrings** within the filename.
  - *Example*: A rule with keyword `"DBMS"` will match `dbms_lecture_4.pdf`, `Unit3_DBMS_Notes.docx`, and `Advanced_DBMS.pptx`.
- Matches route directly to the specified destination directory without triggering text extraction or ML classification.

### Template & Local User State
- [`rules.json.example`](rules.json.example): The distributable template tracked in Git.
- [`rules.json`](rules.json): The active runtime configuration file containing local paths. It is excluded by `.gitignore` to protect personal directory structures from accidental commits.

---

## 9. Testing

Run the automated test suite using `pytest`:

```bash
python -m pytest tests/ -v
```

To run a specific test suite:
```bash
python -m pytest tests/test_file_routing.py -v
python -m pytest tests/test_classification.py -v
python -m pytest tests/test_text_extractor.py -v
```

---

## 10. Current Limitations (V1.0.0)

- **Classifier Categories**: The machine learning model is trained on five document categories: `resume`, `certificate`, `marksheet`, `project`, and `report`.
- **Unrecognized Document Fallback**: Unrecognized document types (such as invoices, letters, or study notes) without explicit memory rules or extensions will route to `other/` or one of the trained categories based on closest vocabulary features.
- **Real-World Calibration**: Classification accuracy is established on synthetic and verified sample documents; large-scale noisy real-world document evaluations are planned for subsequent releases.
- **Scope**: Cloud storage synchronization (e.g. Google Drive), web dashboards, and frontend interfaces are outside the scope of V1.
