from google.genai import types
import time
import os
from src.core.llm import Gemini
from src.core.prompt import FILE_SEARCH_INSTRUCTION
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


class FileSearchStore:
    def __init__(self, genai: Gemini, display_name: str):
        if not isinstance(display_name, str) or not display_name.strip():
            raise ValueError("display_name must be a non-empty string.")
        
        self.display_name = display_name
        self.store = None
        
        if not self._load_existing_store(genai=genai):
            # If not exist, create one
            logger.info(f"Creating File Search Store...")
            self._create_store(genai=genai)
            
        self.file_search_tool = types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[self.store.name]
            )
        )
    
    def _load_existing_store(self, genai: Gemini) -> bool:
        """ Load store if it already existed """
        for store in genai.client.file_search_stores.list():
            if store.display_name == self.display_name:
                logger.info(f"Store {self.display_name} existed.")
                self.store = genai.client.file_search_stores.get(name=store.name)
                return True
            
        return False
          
          
    def _create_store(self, genai: Gemini):
        """ Create new file search store """
        self.store = genai.client.file_search_stores.create(config={"display_name": self.display_name})
        
        
    def upload_file(self, file_path: str, genai: Gemini, display_name: str):
        """ Upload file to file search store """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"File {file_path} adding to search store...")
        operation = genai.client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=self.store.name,
            config={
                "display_name": display_name,
            }
        )
            
        while not operation.done:
            time.sleep(5)
            operation = genai.client.operations.get(operation)
        
    
    def query(self, question: str, genai: Gemini) -> str:
        """ Asking about files with file search store """
        messages = [
            {
                "role": "system", 
                "content": FILE_SEARCH_INSTRUCTION
            },
            {
                "role": "user", 
                "content": question
            }
        ]
        
        return genai.generate_response(
            messages=messages,
            tool=self.file_search_tool
        )
        