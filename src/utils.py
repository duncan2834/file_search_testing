from google import genai
from google.genai import types
from src.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def extract_markdown_from_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                "You are an expert in parsing scientific tables. "
                "Your task is to convert the table in the image into a complete, single Markdown-formatted table."
                "Ensure every cell's content is preserved **exactly as seen, including special characters and text like 'n =', 'Ref.', or ranges (e.g., '0.5–2.1')**. "
                "The table has **hierarchical headers**. "
                "You MUST combine all levels of hierarchical headers into a single, descriptive header row, using a clear separator (e.g., ' / '). **CRITICALLY: Remove all footnote/superscript characters (e.g., ᵃ, ᵇ, ᶜ) from the column headers** for optimal query performance. "
                "For rows with **sparse data** (where many cells are empty), you must preserve **empty Markdown cells** (e.g., `| |`) to maintain correct column alignment across the entire table. "
                "CRITICALLY: Output **ONLY** the complete, non-redundant Markdown table. "
                "DO NOT include the image's footnotes or explanatory text."
                "Output **ONLY** the complete Markdown table (no explanation, no surrounding text, no triple backticks)."
            ],
        )
        return response.text.strip() if response.text else ""

def normalize_string(text:str) -> str:
    text = text.replace(' ', '')
    text = text.replace('–', '-') 
    return text.lower()

def evaluate_answer(predicted: str, expected: str) -> bool:
    return normalize_string(expected) in normalize_string(predicted)

def ask_question(markdown_table: str, question: str) -> str:
    prompt = f"""
        You are given the following table in Markdown format:

        {markdown_table}

        Answer this question using ONLY the information in the table:
        {question}

        **Crucial Formatting Rules:**
        1. **Single Cell (CRITICAL DETAIL PRESERVATION):** If the answer is found in a single cell (e.g., 'n = 89', 'Ref.', '3251 ± 584', or **'37(10%)'**), your response MUST be the **exact content of that cell**. You **must not omit** parentheses, percentages (%), units, plus/minus signs (±), or any descriptive text.
        2. **OR and CI (COMBINATION):** If the question asks for an **Odds Ratio (OR)**, **Relative Risk (RR)**, or similar measure with its **Confidence Interval (CI)**, you MUST combine the values from the separate OR and CI cells into the format: **OR(CI_start–CI_end)**, using the exact values from the table (e.g., '1.4(0.6–3.2)').
        3. **Final Output:** YOUR RESPONSE MUST BE ONLY the exact content determined by rules 1 or 2. DO NOT include any conversational phrases, prefixes, or suffixes.

        If the answer is not in the table, say "NOT FOUND".
        """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip() if response.text else ""