from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import tempfile
import logging
import uuid
import shutil

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}}
)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# File storage functions
def save_file(file_id: str, file_path: str):
    """Save file to persistent storage"""
    new_path = os.path.join(UPLOAD_DIR, f"{file_id}.xlsx")
    shutil.copy2(file_path, new_path)
    os.unlink(file_path)  # Remove the temporary file
    return new_path

def get_file_path(file_id: str) -> str:
    """Get file path from persistent storage"""
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.xlsx")
    return file_path if os.path.exists(file_path) else None

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Generate a unique file ID using UUID
        file_id = str(uuid.uuid4())
        
        # Store the file in persistent storage
        file_path = save_file(file_id, temp_file_path)
        logger.info(f"File uploaded and saved at {file_path} with ID {file_id}")

        return {"message": "File uploaded successfully", "file_id": file_id}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail="Error uploading file")

@router.get("/files/{file_id}")
async def get_file(file_id: str):
    try:
        # Retrieve the file path using the file ID
        file_path = get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")

        # Return the file path
        return {"file_path": file_path}
    except Exception as e:
        logger.error(f"Error retrieving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving file")