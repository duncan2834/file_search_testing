from fastapi import Depends, APIRouter, File, UploadFile, HTTPException, status
import os
from src.core.file_search import FileSearchStore
from src.core.llm import Gemini
from src.core.dependencies import get_genai

    
router = APIRouter()

@router.post("/upload")
async def upload_file(
    display_name: str,
    file: UploadFile = File(..., description="File uploaded for Gemini File Search Tool"),
    genai: Gemini = Depends(get_genai)
) -> str:
    """ Upload file to file search stores with store display name and file """
    
    file_path = f"./data/{file.filename}"
    
    try:
        contents = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        file_search_store = FileSearchStore(genai=genai, display_name=display_name)
        
        file_search_store.upload_file(
            file_path=file_path,
            genai=genai,
            display_name=display_name
        )
        
        return f"File {file.filename} uploaded."
    
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {e}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)