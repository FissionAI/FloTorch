import os
from PyPDF2 import PdfReader
import logging
from io import StringIO
# Avoid importing PyMuPDF (fitz) at module import time to prevent DLL errors on Windows.

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        logger.info(f"Extracting text from PDF: {file_path}")
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        logger.info("Text extraction from PDF successful.")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise

def extract_text_from_pdf_pymudf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF if available; falls back to PyPDF2."""
    try:
        logger.info(f"Extracting text from PDF (PyMuPDF preferred): {file_path}")
        try:
            import fitz  # local import to avoid DLL load at module import time
        except Exception as imp_err:
            logger.warning(f"PyMuPDF unavailable ({imp_err}); falling back to PyPDF2")
            return extract_text_from_pdf(file_path)

        doc = fitz.open(file_path)
        text_buffer = StringIO()
        for page in doc:
            page_text = page.get_text() or ""
            text_buffer.write(page_text)

        logger.info("Text extraction from PDF successful (PyMuPDF).")
        text = text_buffer.getvalue()
        text_buffer.close()
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF via PyMuPDF: {e}; using PyPDF2 fallback")
        return extract_text_from_pdf(file_path)
    
def process_pdf_from_folder(file_path: str) -> str:
    "Extract text from all files in a folder"
    try:
        text_data = []
        for file in os.listdir(file_path):
            file_text = extract_text_from_pdf(os.path.join(file_path, file))
            text_data.append(file_text)
        logger.info(f"Extracted text from all files. Number of files: {len(text_data)}")
        return text_data
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise