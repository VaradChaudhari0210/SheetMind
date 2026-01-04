import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Datasheet

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
def upload_datasheet(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR,file.filename)

    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    
    datasheet = Datasheet(
        filename = file.filename,
        file_type = file.content_type,
        status="uploaded"
    )
    db.add(datasheet)
    db.commit()
    db.refresh(datasheet)

    return{
        "id":datasheet.id,
        "filename":datasheet.filename,
        "status":datasheet.status
    }