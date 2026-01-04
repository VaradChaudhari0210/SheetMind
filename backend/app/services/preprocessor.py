import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import os

# Configure Tesseract path for Windows (adjust if installed elsewhere)
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                # If no text found, try OCR on the page image
                try:
                    img = page.to_image(resolution=300)
                    page_img = img.original
                    ocr_text = pytesseract.image_to_string(page_img)
                    if ocr_text:
                        text += ocr_text + "\n"
                except Exception as e:
                    print(f"OCR failed for page: {e}")
                    continue
    print(text.strip())
    return text.strip()

def extract_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def extract_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string()

def extract_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string()

def extract_content(file_path, file_type):
    file_type_lower = file_type.lower()
    
    if "pdf" in file_type_lower:
        return extract_from_pdf(file_path)
    elif "image" in file_type_lower or "png" in file_type_lower or "jpeg" in file_type_lower or "jpg" in file_type_lower:
        return extract_from_image(file_path)
    elif "csv" in file_type_lower:
        return extract_from_csv(file_path)
    elif "spreadsheet" in file_type_lower or "excel" in file_type_lower or "xlsx" in file_path.lower() or "xls" in file_path.lower():
        return extract_from_excel(file_path)
    else:
        return None    