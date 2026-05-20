import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def detect_intent(user_prompt: str) -> dict:
    classification_prompt = f"""
You are an intent classifier for a Power BI agent.

Classify this user message into EXACTLY one of these intents:
- generate_dax : user wants to create a new DAX measure
- list_tables  : user wants to see tables and columns in the model
- list_measures: user wants to see existing measures
- delete_measure: user wants to delete/remove a measure
- explain_model: user wants to understand the model structure
- unknown      : none of the above

Also extract:
- table_name: which table to use (if mentioned, else "Sales")
- measure_name: name of measure to delete (only for delete_measure)

User message: "{user_prompt}"

Reply in this exact format, nothing else:
INTENT: <intent>
TABLE: <table_name>
MEASURE: <measure_name>
"""
    payload = {
        "model": "llama3.1",
        "prompt": classification_prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    result = response.json()["response"].strip()

    # Parse result
    intent = "unknown"
    table = "Sales"
    measure = ""

    for line in result.split("\n"):
        if line.startswith("INTENT:"):
            intent = line.replace("INTENT:", "").strip()
        elif line.startswith("TABLE:"):
            table = line.replace("TABLE:", "").strip()
        elif line.startswith("MEASURE:"):
            measure = line.replace("MEASURE:", "").strip()

    return {
        "intent": intent,
        "table_name": table,
        "measure_name": measure,
        "original_prompt": user_prompt
    }