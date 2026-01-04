from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Datasheet(Base):
    __tablename__ = "datasheets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String,nullable=False)
    status = Column(String,default="uploaded")
    uploaded_at = Column(DateTime,default = datetime.utcnow)