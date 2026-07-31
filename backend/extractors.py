import io
import fitz
from docx import Document


def extract_from_pdf(file_bytes: bytes) -> str:
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    return text


def extract_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        return extract_from_pdf(file_bytes)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_from_docx(file_bytes)
    elif content_type == "text/plain":
        return extract_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")