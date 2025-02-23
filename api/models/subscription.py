from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    estimated_next_date = Column(Date, nullable=True)
    
    # Foreign key to the user who owns this subscription
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # Relationship to the user
    user = relationship("User", back_populates="subscriptions")
    
    # Foreign key to the uploaded file that generated this subscription
    file_id = Column(Integer, ForeignKey('uploaded_files.id'), nullable=False)
    # Relationship to the uploaded file
    uploaded_file = relationship("UploadedFile", back_populates="subscriptions")
