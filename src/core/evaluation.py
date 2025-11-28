import json
import logging
import time
from src.core.prompt import EVALUATION_PROMPT, EVALUATION_USER_PROMPT
from src.core.llm import Gemini
from src.core.file_search import FileSearchStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

def generate_answer_from_store(
    file_search_store: FileSearchStore,
    genai: Gemini,
    question: str
) -> dict[str, str]:
    """ Load questions, generate answers with file_search_store and save """
        
    logger.info(f"Answering {question} ...")
    start = time.perf_counter()
    
    result = file_search_store.query(
        question=question,
        genai=genai
    )
    
    generated_answer = result.get("response", "")
    grounding_metadata = result.get("grounding_metadata", "")
    
    end = time.perf_counter()
    runtime = end - start
    
    logger.info(f"Runtime: {runtime}")
    logger.info(f"Answer: {generated_answer}")
    
    result = {
        "question": question,
        "answer": generated_answer,
        "runtime": runtime,
        "grounding_metadata": grounding_metadata,
        "note": "" # note what to add, change, ask,...
    }
    time.sleep(15)


def evaluate_answer(
    question: str,
    ground_truth_answer: str,
    generated_answer: str,
    genai: Gemini
) -> dict[str, str]:
    """ Evaluating answer generated from file search """
    messages = [
        {
            "role": "system",
            "content": EVALUATION_PROMPT
        },
        {
            "role": "user",
            "content": EVALUATION_USER_PROMPT.format(
                question=question,
                ground_truth_answer=ground_truth_answer,
                generated_answer=generated_answer
            )
        }
    ]
    
    return genai.generate_response(
        messages=messages
    )


def evaluate_answers(
    ground_truth_qa_path: str,
    generated_qa_path: str,
    output_dir: str,
    genai: Gemini
):
    with open(ground_truth_qa_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
        
    with open(generated_qa_path, 'r', encoding='utf-8') as f:
        generated = json.load(f)
        
    generated_pairs = {item["question"]: item["answer"] for item in generated}
    
    results: list[dict[str, any]] = []
    
    for gt_pair in ground_truth:
        question = gt_pair["question"]
        ground_truth_answer = gt_pair["answer"]
        generated_answer = generated_pairs.get(question)
        
        result = evaluate_answer(
            question=question,
            ground_truth_answer=ground_truth_answer,
            generated_answer=generated_answer,
            genai=genai
        )
        
        score = result.get("response", "")
        
        results.append({
            "question": question,
            "gt_answer": ground_truth_answer,
            "generated_answer": generated_answer,
            "score": json.loads(score)
        })
        time.sleep(15)
        
    with open(output_dir, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)