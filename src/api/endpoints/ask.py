from fastapi import Depends, APIRouter
from pydantic import BaseModel, Field
from src.core.llm import Gemini
from src.core.file_search import FileSearchStore
from src.core.dependencies import get_genai

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Answer from LLM using file search tool")
    grounding_metatdata: str = Field(..., description="Citation for the answer in docs")

router = APIRouter()

@router.post("/ask", response_model=ChatResponse)
async def ask(question: str, display_name: str, genai: Gemini = Depends(get_genai)):
    """ Ask questions about files in a filesearchstore """
    file_search_store = FileSearchStore(genai=genai, display_name=display_name)
    
    response = file_search_store.query(
        question=question,
        genai=genai
    )
    
    return ChatResponse(
        answer=response["response"],
        grounding_metatdata=response["grounding_metadata"]
    )