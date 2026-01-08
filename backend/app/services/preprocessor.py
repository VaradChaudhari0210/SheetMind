import os
import cv2
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import pandas as pd


# =========================
# Configuration
# =========================

# Poppler path (required for PDF to image conversion on Windows)
POPPLER_PATH = r'C:\Program Files\poppler\Library\bin'

# Tesseract OCR path (required for OCR on Windows)
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set Tesseract path
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
else:
    print(f"Warning: Tesseract not found at {TESSERACT_CMD}")


# =========================
# Utility Functions
# =========================
def is_text_based_pdf(pdf_path: str) -> bool:
    """
    Check whether PDF contains an embedded text layer
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    return True
    except Exception:
        pass
    return False


def preprocess_image_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Image preprocessing to improve OCR accuracy
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    gray = cv2.medianBlur(gray, 3)

    # Adaptive threshold for tables
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh


def ocr_image(image: np.ndarray) -> str:
    """
    Run OCR on preprocessed image
    """
    config = "--psm 6"
    text = pytesseract.image_to_string(image, config=config)
    return text


def clean_ocr_text(text: str) -> str:
    """
    Cleanup OCR artifacts
    """
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


# =========================
# Core Pipeline
# =========================
def extract_from_text_pdf(pdf_path: str) -> str:
    """
    Extract text from text-based PDFs
    """
    text_chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

    return "\n".join(text_chunks)


def extract_from_scanned_pdf(pdf_path: str) -> str:
    """
    Extract text from scanned PDFs using OCR
    """
    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    extracted_text = []

    for idx, page in enumerate(pages):
        page_np = np.array(page)
        processed = preprocess_image_for_ocr(page_np)
        text = ocr_image(processed)
        text = clean_ocr_text(text)

        if text:
            extracted_text.append(text)

    return "\n\n".join(extracted_text)


# =========================
# Public API
# =========================
def preprocess_pdf(pdf_path: str) -> dict:
    """
    Main entry point used by the API / worker
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    print(f"FILE PATH: {pdf_path}")
    print(f"EXISTS: {os.path.exists(pdf_path)}")

    if is_text_based_pdf(pdf_path):
        print("✔ Text-based PDF detected")
        content = extract_from_text_pdf(pdf_path)
        source = "text"
    else:
        print("⚠ No text layer found. Using OCR...")
        content = extract_from_scanned_pdf(pdf_path)
        source = "ocr"

    if not content.strip():
        raise ValueError("No content could be extracted from the file")

    return {
        "source": source,
        "content": content
    }


def extract_content(file_path: str, file_type: str) -> str:
    """
    Legacy API for backward compatibility.
    Routes different file types to appropriate extractors.
    """
    import pandas as pd
    
    file_type_lower = file_type.lower()
    
    # PDF files
    if "pdf" in file_type_lower:
        result = preprocess_pdf(file_path)
        return result["content"]
    
    # Image files
    elif any(ext in file_type_lower for ext in ["image", "png", "jpeg", "jpg"]):
        image = Image.open(file_path)
        image_np = np.array(image)
        processed = preprocess_image_for_ocr(image_np)
        text = ocr_image(processed)
        return clean_ocr_text(text)
    
    # CSV files
    elif "csv" in file_type_lower:
        df = pd.read_csv(file_path)
        return df.to_string()
    
    # Excel files
    elif any(ext in file_type_lower for ext in ["spreadsheet", "excel", "xlsx", "xls"]) or \
         file_path.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
        return df.to_string()
    
    else:
        return None


# =========================
# CLI Testing
# =========================
if __name__ == "__main__":
    pdf = "storage/uploads/datasheet_1.pdf"

    try:
        result = preprocess_pdf(pdf)
        print("\n--- EXTRACTION SOURCE ---")
        print(result["source"])
        print("\n--- EXTRACTED CONTENT ---")
        print(result["content"][:2000])
    except Exception as e:
        print("ERROR:", str(e))
