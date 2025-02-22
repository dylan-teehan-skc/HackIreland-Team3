from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship
from .base import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)
    file_path = Column(String, nullable=False)

    # Remove the relationship to User
    # owner = relationship("User", back_populates="uploaded_files") 