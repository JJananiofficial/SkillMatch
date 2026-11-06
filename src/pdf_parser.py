from pypdf import PdfReader
import logging

def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts text from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
        return text.strip()
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
        return ""
