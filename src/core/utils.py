import json


def avg_runtime(gen_path: str):
    with open(gen_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    runtime_list = [result["runtime"] for result in results]
    
    return sum(runtime_list) / len(runtime_list)