from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    file_content = Column(LargeBinary, nullable=False)
    file_path = Column(String, nullable=False)
    
    # Foreign key to the user who uploaded this file
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # Relationship to the user
    user = relationship("User")
    # Relationship to subscriptions derived from this file
    subscriptions = relationship("Subscription", back_populates="uploaded_file")

    # Remove the relationship to User
    # owner = relationship("User", back_populates="uploaded_files") 