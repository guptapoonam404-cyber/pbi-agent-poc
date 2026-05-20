import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_dax(prompt: str, model: str = "llama3.1") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"].strip()

def generate_dax_with_context(
    business_requirement: str,
    table_name: str,
    model_context: str,
    model: str = "llama3.1"
) -> str:
    prompt = f"""
You are a Power BI DAX expert. 

{model_context}

Generate a single DAX measure for this requirement:
Business requirement: {business_requirement}
Table to use: {table_name}

Rules:
- Use ONLY the column names that exist in the model above
- Return ONLY the DAX code, nothing else
- Format: MeasureName = <DAX expression>
- No explanation, no markdown, just the DAX line

DAX measure:
"""
    return generate_dax(prompt, model)

