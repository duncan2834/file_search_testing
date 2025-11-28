from src.core.llm import Gemini

genai = Gemini()

def get_genai() -> Gemini:
    """ Dependency to init gemini service instance once """
    return genai