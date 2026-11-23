import os
import csv
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw
import docx
from pptx import Presentation
import pymupdf

DATA_DIR = Path(__file__).resolve().parent / "test_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TEXT_SAMPLES = {
    "resume": (
        "John Doe - Senior Software Engineer\n"
        "Email: john.doe@example.com | Phone: (555) 019-2834 | Location: San Francisco, CA\n\n"
        "PROFESSIONAL SUMMARY\n"
        "Experienced Senior Software Engineer with 8+ years designing and scaling distributed backend systems "
        "and data processing pipelines. Proficient in Python, Go, PostgreSQL, Docker, and Kubernetes.\n\n"
        "TECHNICAL SKILLS\n"
        "Languages: Python, Go, JavaScript, C++, SQL\n"
        "Frameworks: FastAPI, Flask, Django, PyTorch, Scikit-learn\n"
        "Infrastructure: Docker, Kubernetes, AWS, GCP, CI/CD, Terraform\n\n"
        "WORK EXPERIENCE\n"
        "TechCorp Inc. - Senior Software Engineer (2021 - Present)\n"
        "- Architected high-throughput microservices handling 50k requests per second.\n"
        "- Reduced latency by 35% through query optimization and distributed caching.\n\n"
        "Startup Innovations - Software Engineer (2018 - 2021)\n"
        "- Developed REST APIs and automated ETL pipelines in Python.\n\n"
        "EDUCATION\n"
        "Bachelor of Science in Computer Science - University of California, Berkeley (2014 - 2018)\n"
        "Certifications: AWS Certified Solutions Architect Associate"
    ),
    "certificate": (
        "CERTIFICATE OF ACHIEVEMENT\n\n"
        "This certificate is proudly presented to\n"
        "JANE SMITH\n\n"
        "for successfully completing the Professional Machine Learning and Deep Learning Specialization.\n"
        "Demonstrating excellence in natural language processing, computer vision, and model deployment.\n\n"
        "Date of Issuance: October 15, 2025\n"
        "Certificate ID: CERT-ML-2025-9981\n"
        "Authorized Signature: Dr. Alan Turing, Director of AI Education"
    ),
    "marksheet": (
        "STATE UNIVERSITY - SEMESTER EXAMINATION MARKSHEET\n\n"
        "Student Name: Alex Johnson\n"
        "Roll Number: CS-2024-8841\n"
        "Program: Bachelor of Technology in Computer Science\n"
        "Semester: VI (Spring 2025)\n\n"
        "Course Code | Course Title                   | Credits | Grade | Marks Obtained | Max Marks\n"
        "CS-601      | Database Management Systems   | 4       | A     | 88             | 100\n"
        "CS-602      | Machine Learning Fundamentals | 4       | A+    | 94             | 100\n"
        "CS-603      | Computer Networks             | 4       | A     | 85             | 100\n"
        "CS-604      | Software Engineering          | 3       | B+    | 79             | 100\n"
        "CS-605      | Web Technologies Lab          | 2       | A+    | 96             | 100\n\n"
        "Total Marks Obtained: 442 / 500\n"
        "Semester GPA (SGPA): 9.20\n"
        "Cumulative GPA (CGPA): 8.95\n"
        "Result: PASS WITH DISTINCTION"
    ),
    "report": (
        "ANNUAL ORGANIZATIONAL PERFORMANCE REPORT\n\n"
        "Executive Summary:\n"
        "This annual report presents an overview of the key operations, strategic initiatives, "
        "and departmental achievements for the fiscal year 2025. Across all business units, "
        "operational efficiency increased by 18%, driven by workflow automation and infrastructure upgrades.\n\n"
        "Financial Overview:\n"
        "Total revenue reached $42.5M, representing a 14% year-over-year increase. "
        "Operational expenses remained within projected budget margins.\n\n"
        "Key Accomplishments:\n"
        "- Deployed modernized document classification and archive indexing system.\n"
        "- Expanded customer support reach across three new international territories.\n\n"
        "Conclusion & Outlook:\n"
        "The organization is well-positioned for sustainable growth in the upcoming fiscal cycle."
    ),
    "investigative_report": (
        "INCIDENT INVESTIGATION REPORT\n\n"
        "Incident Reference: INV-2025-SEC-042\n"
        "Subject: Unauthorized Database Query Anomaly\n"
        "Date of Investigation: November 12, 2025\n"
        "Investigator: Cyber Forensics Team\n\n"
        "1. Sequence of Events:\n"
        "At 02:14 UTC, telemetry detected repeated elevated database read requests from an unauthenticated IP.\n\n"
        "2. Forensic Analysis & Evidence Collected:\n"
        "Audit log inspection, packet traces, and session token analysis indicate a brute-force credential attempt. "
        "No customer data was exfiltrated; rate limiting halted the session after 47 attempts.\n\n"
        "3. Findings & Corrective Action:\n"
        "The vulnerable endpoint was secured with mandatory API key rotation and stricter IP throttling."
    ),
    "research_report": (
        "RESEARCH REPORT: MULTIMODAL FEATURE EXTRACTION FOR DOCUMENT ANALYSIS\n\n"
        "Abstract:\n"
        "This research report investigates empirical performance bounds of hybrid TF-IDF and transformer-based "
        "representations for unstructured document classification. We examine vocabulary density, sublinear scaling, "
        "and n-gram tokenization across diverse technical corpora.\n\n"
        "Methodology:\n"
        "Experiments were conducted on 5,000 heterogeneous text artifacts utilizing stratified 5-fold cross validation. "
        "A Logistic Regression classifier with balanced class weighting was utilized as baseline.\n\n"
        "Results & Discussion:\n"
        "The experimental evaluation demonstrated an overall F1-score of 0.94, confirming that bi-gram feature capture "
        "significantly mitigates domain ambiguity.\n\n"
        "Conclusion: Hybrid extraction yields high recall with low computational inference overhead."
    ),
    "technical_report": (
        "TECHNICAL REPORT: ARCHITECTURE AND HIGH-AVAILABILITY CLUSTER DESIGN\n\n"
        "Document ID: TR-2025-08\n"
        "System: Distributed File Sorting and Ingestion Service (LibManage)\n\n"
        "System Architecture:\n"
        "The storage ingestion cluster consists of three stateless worker nodes behind an NGINX load balancer. "
        "Asynchronous file processing utilizes task queues with persistent Redis storage.\n\n"
        "Performance Benchmarking:\n"
        "- Average document ingestion latency: 45 ms\n"
        "- Peak throughput: 1,200 documents/minute\n"
        "- Memory footprint: 180MB per worker process\n\n"
        "Failover & Disaster Recovery:\n"
        "Automated health checks trigger instance restarts within 5 seconds of failure detection."
    ),
    "academic_assignment": (
        "ACADEMIC ASSIGNMENT: DISTRIBUTED SYSTEMS ALGORITHMS\n\n"
        "Course: CS-702 Distributed Computing\n"
        "Assignment Number: 4\n"
        "Student Name: Emily Davis (ID: 902184)\n"
        "Professor: Dr. Marcus Vance\n\n"
        "Question 1: Explain the leader election mechanism in the Raft consensus protocol.\n"
        "Answer: Raft uses randomized election timeouts to elect a cluster leader. When followers do not receive "
        "heartbeats from the current leader within the timeout window, they transition to Candidate state and "
        "request votes from peers. A candidate obtaining a majority of votes becomes the new leader.\n\n"
        "Question 2: Compare Paxos and Raft in terms of understandability and state machine safety.\n"
        "Answer: While theoretically equivalent in safety, Raft decomposes consensus into leader election, "
        "log replication, and safety, making practical implementation substantially more tractable."
    ),
    "project_documentation": (
        "PROJECT DOCUMENTATION: LIBMANAGE V1 AUTOMATED FILE MANAGEMENT SYSTEM\n\n"
        "Project Overview:\n"
        "LibManage is an intelligent file organization utility that classifies incoming documents "
        "using rule-based heuristics, extension filtering, and machine learning text classification.\n\n"
        "Module Architecture:\n"
        "- backend.upload_file: Handles file path acquisition and destination folder verification.\n"
        "- backend.memory: Persists custom user routing rules in rules.json.\n"
        "- backend.extractor: Extracts plain text from PDF, DOCX, PPTX, and image formats.\n"
        "- backend.classifier: Uses TF-IDF and Logistic Regression to categorize documents.\n"
        "- backend.put_to_respective_folder: Routes documents safely without data loss.\n\n"
        "Installation & Deployment:\n"
        "Execute 'pip install -r requirements.txt' and start the pipeline using 'python backend/main.py'."
    ),
    "notes": (
        "STUDY NOTES: DATABASE SYSTEMS CONCURRENCY CONTROL\n\n"
        "Date: October 24, 2025\n"
        "Lecture 14 Notes - Dr. Robinson\n\n"
        "- ACID Properties: Atomicity, Consistency, Isolation, Durability.\n"
        "- Isolation Levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable.\n"
        "- Concurrency Anomalies: Dirty Reads, Non-repeatable Reads, Phantom Reads.\n"
        "- Two-Phase Locking (2PL): Growing phase (acquire locks), Shrinking phase (release locks).\n"
        "Strict 2PL prevents cascading aborts by holding exclusive locks until transaction commit."
    ),
    "invoice": (
        "COMMERCIAL INVOICE\n\n"
        "Invoice Number: INV-2025-0982\n"
        "Invoice Date: November 18, 2025\n"
        "Payment Due Date: December 18, 2025\n\n"
        "Billed To:\n"
        "Acme Enterprise Solutions\n"
        "100 Corporate Plaza, Suite 400\n"
        "New York, NY 10001\n\n"
        "Description                              | Qty | Unit Price | Total Amount\n"
        "Software Engineering Consulting (Hours)  | 40  | $150.00    | $6,000.00\n"
        "Cloud Architecture Review                | 1   | $2,500.00  | $2,500.00\n"
        "Server Maintenance Retainer              | 1   | $1,000.00  | $1,000.00\n\n"
        "Subtotal: $9,500.00\n"
        "Tax (8.25%): $783.75\n"
        "Total Balance Due: $10,283.75\n\n"
        "Payment Terms: Net 30. Wire transfer details: First National Bank, Routing: 021000021."
    ),
    "letter": (
        "FORMAL LETTER OF RECOMMENDATION\n\n"
        "November 15, 2025\n\n"
        "To the Admissions Committee,\n"
        "School of Engineering and Applied Sciences\n\n"
        "Dear Members of the Committee,\n\n"
        "It is my distinct privilege to write this letter of recommendation on behalf of Emily Davis. "
        "During her tenure as a Research Assistant in our Systems Laboratory, Emily demonstrated remarkable "
        "analytical rigor, deep technical acumen, and exceptional dedication to empirical inquiry.\n\n"
        "She consistently authored meticulous documentation, designed comprehensive testing frameworks, and "
        "collaborated effectively with fellow researchers. I recommend her without reservation.\n\n"
        "Sincerely,\n"
        "Dr. Robert Vance, Professor of Computer Science"
    ),
    "miscellaneous": (
        "COMPANY CAFETERIA WEEKLY MENU & ANNOUNCEMENTS\n\n"
        "Weekly Lunch Specials (November 17 - November 21):\n"
        "Monday: Roasted Mediterranean Vegetable Bowl with Quinoa.\n"
        "Tuesday: Slow-cooked Chicken Tacos with Cilantro Lime Rice.\n"
        "Wednesday: Wild Mushroom Risotto with Truffle Oil.\n"
        "Thursday: Thai Green Curry with Tofu and Jasmine Rice.\n"
        "Friday: Artisan Margherita Pizza and Caesar Salad.\n\n"
        "Notice: The cafeteria will close early at 2:00 PM this Friday for annual maintenance."
    )
}

def create_pdf(path: Path, text: str):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), text, fontsize=10)
    doc.save(str(path))
    doc.close()

def create_docx(path: Path, text: str, title: str = "Document"):
    doc = docx.Document()
    doc.add_heading(title, 0)
    for para in text.split("\n\n"):
        if para.strip():
            doc.add_paragraph(para.strip())
    doc.save(str(path))

def create_pptx(path: Path, text: str, title: str = "Presentation"):
    prs = Presentation()
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    body_shape = slide.shapes.placeholders[1]
    body_shape.text = text[:800]
    prs.save(str(path))

def create_image(path: Path, text: str, fmt: str = "PNG"):
    img = Image.new("RGB", (1000, 500), color="white")
    draw = ImageDraw.Draw(img)
    lines = text.split("\n")[:12]
    y = 30
    for line in lines:
        if line.strip():
            draw.text((30, y), line.strip()[:60], fill="black")
            y += 30
    img.save(str(path), format=fmt)

def create_csv(path: Path, text: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["RowID", "ContentLine"])
        for i, line in enumerate(text.split("\n")):
            if line.strip():
                writer.writerow([i + 1, line.strip()])

def create_zip(path: Path, files_to_zip: list):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files_to_zip:
            if file_path.exists():
                zf.write(file_path, arcname=file_path.name)

def generate_all():
    print(f"Generating synthetic test dataset in {DATA_DIR}...")

    # 1. Standard format documents for each category
    for cat_name, content in TEXT_SAMPLES.items():
        # PDF
        create_pdf(DATA_DIR / f"{cat_name}_sample.pdf", content)
        # DOCX
        create_docx(DATA_DIR / f"{cat_name}_sample.docx", content, title=cat_name.replace("_", " ").title())
        # PPTX
        create_pptx(DATA_DIR / f"{cat_name}_sample.pptx", content, title=cat_name.replace("_", " ").title())
        # CSV
        create_csv(DATA_DIR / f"{cat_name}_sample.csv", content)

    # 2. Image formats (JPEG, PNG, WEBP, GIF) with readable text for OCR
    ocr_text = (
        "Certificate of Achievement awarded to Alex Morgan for outstanding "
        "performance in Python Software Development."
    )
    create_image(DATA_DIR / "certificate_ocr.png", ocr_text, fmt="PNG")
    create_image(DATA_DIR / "resume_ocr.jpg", TEXT_SAMPLES["resume"], fmt="JPEG")
    create_image(DATA_DIR / "report_ocr.webp", TEXT_SAMPLES["report"], fmt="WEBP")
    create_image(DATA_DIR / "invoice_ocr.gif", TEXT_SAMPLES["invoice"], fmt="GIF")

    # 3. Empty documents (0-byte)
    (DATA_DIR / "empty.pdf").write_bytes(b"")
    (DATA_DIR / "empty.docx").write_bytes(b"")
    (DATA_DIR / "empty.pptx").write_bytes(b"")
    (DATA_DIR / "empty.png").write_bytes(b"")
    (DATA_DIR / "empty.csv").write_bytes(b"")
    (DATA_DIR / "empty.zip").write_bytes(b"")
    (DATA_DIR / "empty.txt").write_bytes(b"")

    # 4. Corrupted documents (malformed binary headers)
    (DATA_DIR / "corrupted.pdf").write_bytes(b"%PDF-1.4\nTRUNCATED_AND_CORRUPTED_BYTES_HERE\x00\xff\xfe")
    (DATA_DIR / "corrupted.docx").write_bytes(b"PK\x03\x04CORRUPTED_DOCX_HEADER_INVALID_ZIP_ARCHIVE")
    (DATA_DIR / "corrupted.pptx").write_bytes(b"PK\x03\x04CORRUPTED_PPTX_HEADER_INVALID_ZIP")
    (DATA_DIR / "corrupted.png").write_bytes(b"\x89PNG\r\n\x1a\nCORRUPTED_IMAGE_BYTES_STREAM")
    (DATA_DIR / "corrupted.zip").write_bytes(b"PK\x03\x04CORRUPTED_ZIP_STREAM_NOT_A_VALID_ARCHIVE")

    # 5. Unsupported file formats
    (DATA_DIR / "unsupported.bin").write_bytes(b"\x00\x01\x02\x03\x04\x05\x06\x07")
    (DATA_DIR / "unsupported.exe").write_bytes(b"MZ\x90\x00\x03\x00\x00\x00")
    (DATA_DIR / "unsupported.xyz").write_text("This is an arbitrary unsupported file format.")

    # 6. Documents with no extractable text
    # PDF with blank page (no text elements)
    blank_pdf = pymupdf.open()
    blank_pdf.new_page()
    blank_pdf.save(str(DATA_DIR / "no_text_blank.pdf"))
    blank_pdf.close()

    # Image with pure white background, no text drawn
    blank_img = Image.new("RGB", (400, 300), color="white")
    blank_img.save(str(DATA_DIR / "no_text_blank.png"))

    # DOCX with no paragraphs
    blank_doc = docx.Document()
    blank_doc.save(str(DATA_DIR / "no_text_blank.docx"))

    # 7. Documents with misleading filenames
    # Named resume.pdf, but contains report content
    create_pdf(DATA_DIR / "misleading_resume_name_but_report.pdf", TEXT_SAMPLES["report"])
    # Named certificate.docx, but contains project documentation
    create_docx(DATA_DIR / "misleading_certificate_name_but_project.docx", TEXT_SAMPLES["project_documentation"])
    # Named marksheet.pdf, but contains letter
    create_pdf(DATA_DIR / "misleading_marksheet_name_but_letter.pdf", TEXT_SAMPLES["letter"])

    # 8. Documents with similar content but different categories
    # Project Report (mentions both project and report)
    create_pdf(
        DATA_DIR / "similar_content_project_vs_report.pdf",
        "Project Report on Distributed Autonomous Systems. Problem Statement: Design a resilient system. "
        "Methodology: We developed software architecture and evaluated latency. Results & Findings: High availability achieved."
    )
    # Assignment Report (mentions assignment and report)
    create_docx(
        DATA_DIR / "similar_content_assignment_vs_report.docx",
        "Student Assignment Report. Course CS-301. The purpose of this assignment report is to examine "
        "concurrency bottlenecks and report the findings with recommendations."
    )
    # Annual Financial Audit Report (mentions audit, financial, report)
    create_pdf(
        DATA_DIR / "similar_content_audit_report.pdf",
        "Internal Audit Report for Q4. The audit team examined financial records, expense vouchers, "
        "and compliance filings. Discrepancies noted in invoice reconciliation."
    )

    # 9. Files with spaces in filenames
    create_pdf(DATA_DIR / "John Doe Senior Engineer Resume.pdf", TEXT_SAMPLES["resume"])
    create_docx(DATA_DIR / "Q4 Financial Operational Report 2025.docx", TEXT_SAMPLES["report"])
    create_pptx(DATA_DIR / "Architecture Strategy Review 2025.pptx", TEXT_SAMPLES["technical_report"])
    create_image(DATA_DIR / "Jane Smith Certificate of Excellence.png", TEXT_SAMPLES["certificate"], fmt="PNG")

    # 10. Large documents for performance testing
    # Large PDF (50 pages)
    large_pdf = pymupdf.open()
    for page_num in range(50):
        p = large_pdf.new_page()
        p.insert_text((50, 72), f"Page {page_num + 1}\n\n" + TEXT_SAMPLES["technical_report"])
    large_pdf.save(str(DATA_DIR / "large_document_50_pages.pdf"))
    large_pdf.close()

    # Large DOCX (100 paragraphs)
    large_docx = docx.Document()
    large_docx.add_heading("Large Performance Benchmark Document", 0)
    for i in range(100):
        large_docx.add_paragraph(f"Paragraph {i+1}: " + TEXT_SAMPLES["research_report"])
    large_docx.save(str(DATA_DIR / "large_document_100_paragraphs.docx"))

    # 11. ZIP archives containing multiple sample files
    sample_files_for_zip = [
        DATA_DIR / "resume_sample.pdf",
        DATA_DIR / "certificate_sample.docx",
        DATA_DIR / "report_sample.csv"
    ]
    create_zip(DATA_DIR / "multi_file_archive.zip", sample_files_for_zip)

    # 12. Staging duplicate filename for collision test
    dup_dir = DATA_DIR / "duplicate_staging"
    dup_dir.mkdir(parents=True, exist_ok=True)
    create_pdf(dup_dir / "John Doe Senior Engineer Resume.pdf", TEXT_SAMPLES["resume"])

    total_files = len(list(DATA_DIR.rglob("*")))
    print(f"Generated {total_files} synthetic test files successfully in {DATA_DIR}.")

if __name__ == "__main__":
    generate_all()
