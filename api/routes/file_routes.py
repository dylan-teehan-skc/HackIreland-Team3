from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models import UploadedFile
from api.database import get_db
import logging

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}}
)
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_id = str(db.query(UploadedFile).count() + 1)
        file_path = f"temp_{file_id}.xlsx"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        new_file = UploadedFile(file_path=file_path)
        db.add(new_file)
        db.commit()

        logger.info(f"File uploaded successfully with ID {new_file.id}")
        return {"message": "File uploaded successfully", "file_id": new_file.id}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error") 