from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

load_dotenv()

def _reformat_messages(messages: list):
    """
    Reformat messages for Gemini.

    Args:
        messages: The list of messages provided in the request.

    Returns:
        tuple: (system_instruction, contents_list)
    """
    
    system_instruction = None
    contexts = []

    for message in messages:
        if message["role"] == "system":
            system_instruction = message["content"]
        else:
            context = types.Content(
                parts=[types.Part(text=message["content"])],
                role=message["role"],
            )
            contexts.append(context)

    return system_instruction, contexts


def save_grounding(response) -> str | None:
    """ Validate grounding metadata """
    candidate = response.candidates[0]
    metadata = getattr(candidate, "grounding_metadata", None)
    
    if metadata and metadata.grounding_chunks:
        chunk = metadata.grounding_chunks[0]
        if hasattr(chunk, "retrieved_context") and chunk.retrieved_context:
            return chunk.retrieved_context.text
        
    return None
        
class Gemini:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self.api_key = os.environ["GEMINI_API_KEY"]
        
        if not self.api_key:
            raise ValueError("Set api key in .env file of pass an valid api key")
        try: 
            self.client = genai.Client(api_key=self.api_key)
            
        except Exception as e:
            raise ValueError(f"Failed to connect to Gemini: {str(e)}")
    
    
    def generate_response(self, messages: list | str, **args):
        response_format = args.get("response_format")
        
        config_params: dict[str, any] = {}
        
        system_instruction, context = _reformat_messages(messages)
        
        if system_instruction:
            config_params["system_instruction"] = system_instruction
            
        if response_format is not None and response_format["type"] == "json_object":
            config_params["response_mime_type"] = "application/json"
            if "response_schema" in response_format:
                config_params["response_schema"] = response_format["response_schema"]
                
        tool = args.get("tool")

        if tool:
            config_params["tools"] = [tool]
        
        config = types.GenerateContentConfig(**config_params)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=context,
                config=config
            )
            
            # check if text in response format
            if hasattr(response, "text"):
                grounding = save_grounding(response)
                return {
                    "response": response.text,
                    "grounding_metadata": grounding
                }
            
            # check if candidate in response format
            elif hasattr(response, "candidate") and response.candidates():
                grounding = save_grounding(response)
                return {
                    "response": response.candidates[0].content.parts[0].text,
                    "grounding_metadata": grounding
                }
            
            else:
                raise ValueError("No valid response from Gemini")
        
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")