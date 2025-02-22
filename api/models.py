from sqlalchemy import Column, Integer, String
from .database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
