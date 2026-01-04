import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Datasheet, ExtractedContent
from app.services.preprocessor import extract_content

UPLOAD_DIR = "storage/uploads"
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/process/{datasheet_id}")
def process_datasheet(datasheet_id:int, db: Session = Depends(get_db)):
    datasheet = db.query(Datasheet).filter(Datasheet.id == datasheet_id).first()
    if not datasheet:
        raise HTTPException(status_code=404, detail="Datasheet not found")

    file_path = os.path.join(UPLOAD_DIR,datasheet.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {datasheet.filename}")
    
    extracted_text = extract_content(file_path, datasheet.file_type)

    if extracted_text is None:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No content could be extracted from the file")
    
    content = ExtractedContent(
        datasheet_id = datasheet.id,
        content_type = "text",
        content = extracted_text
    )

    datasheet.status = "processed"
    db.add(content)
    db.commit()
    db.refresh(content)

    return {
        "datasheet_id": datasheet.id,
        "status": "processed",
        "content_length": len(extracted_text)
    }