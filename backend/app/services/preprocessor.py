import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import os
import cv2
import numpy as np
from pdf2image import convert_from_path

# ------------------ TESSERACT CONFIG ------------------
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

# ------------------ IMAGE PREPROCESSING ------------------
def preprocess_image(pil_image):
    """
    Improves OCR accuracy for scanned PDFs / tables
    """
    img = np.array(pil_image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive thresholding works well for scanned tables
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    return thresh

# ------------------ PDF EXTRACTION ------------------
def extract_from_pdf(file_path):
    extracted_text = ""

    # 1️⃣ First attempt: text-based PDF
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                extracted_text += page_text + "\n"

    # If text was found, return early
    if extracted_text.strip():
        print("✔ Extracted using PDF text layer")
        return extracted_text.strip()

    # 2️⃣ Fallback: scanned PDF → images → OCR
    print("⚠ No text layer found. Using OCR...")

    try:
        pages = convert_from_path(file_path, dpi=300)

        for page_img in pages:
            processed_img = preprocess_image(page_img)
            ocr_text = pytesseract.image_to_string(
                processed_img,
                config="--psm 6"
            )
            extracted_text += ocr_text + "\n"

    except Exception as e:
        print(f"OCR failed: {e}")

    return extracted_text.strip()

# ------------------ IMAGE EXTRACTION ------------------
def extract_from_image(file_path):
    image = Image.open(file_path)
    processed_img = preprocess_image(image)
    return pytesseract.image_to_string(processed_img, config="--psm 6")

# ------------------ CSV EXTRACTION ------------------
def extract_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string(index=False)

# ------------------ EXCEL EXTRACTION ------------------
def extract_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string(index=False)

# ------------------ MAIN ROUTER ------------------
def extract_content(file_path, file_type):
    file_type_lower = file_type.lower()

    if "pdf" in file_type_lower:
        print("FILE PATH:", file_path)
        print("EXISTS:", os.path.exists(file_path))
        return extract_from_pdf(file_path)

    elif any(ext in file_type_lower for ext in ["image", "png", "jpeg", "jpg"]):
        return extract_from_image(file_path)

    elif "csv" in file_type_lower:
        return extract_from_csv(file_path)

    elif any(ext in file_type_lower for ext in ["spreadsheet", "excel", "xlsx", "xls"]):
        return extract_from_excel(file_path)

    else:
        return None
