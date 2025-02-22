from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import tempfile
import logging
import uuid

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    responses={404: {"description": "Not found"}}
)
logger = logging.getLogger(__name__)

# In-memory storage for file paths
file_storage = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Generate a unique file ID using UUID
        file_id = str(uuid.uuid4())
        
        # Store the file path in memory
        file_storage[file_id] = temp_file_path

        logger.info(f"File uploaded and saved temporarily at {temp_file_path} with ID {file_id}")

        return {"message": "File uploaded successfully", "file_id": file_id}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading file")

@router.get("/files/{file_id}")
async def get_file(file_id: str):
    try:
        # Retrieve the file path using the file ID
        temp_file_path = file_storage.get(file_id)
        if not temp_file_path or not os.path.exists(temp_file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Return the file path or process the file as needed
        return {"file_path": temp_file_path}
    except Exception as e:
        logger.error(f"Error retrieving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving file") 