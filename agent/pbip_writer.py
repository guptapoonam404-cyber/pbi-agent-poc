import json
import uuid
from pathlib import Path

def add_measure_to_model(pbip_path: str, table_name: str,
                          measure_name: str, dax_expression: str):

    model_path = Path(pbip_path) / "model.bim"
    print(f"\n Reading model from: {model_path}")

    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    tables = model["model"]["tables"]
    print(f" Tables found: {[t['name'] for t in tables]}")

    target_table = None
    for table in tables:
        if table["name"].strip().lower() == table_name.strip().lower():
            target_table = table
            break

    if not target_table:
        print(f" Table '{table_name}' not found!")
        print(f" Available: {[t['name'] for t in tables]}")
        return False

    print(f" Table '{table_name}' found!")

    if "measures" not in target_table:
        target_table["measures"] = []

    # Remove if already exists
    target_table["measures"] = [
        m for m in target_table["measures"]
        if m["name"] != measure_name
    ]

    # Generate unique lineageTag every time
    new_measure = {
        "name": measure_name,
        "expression": dax_expression,
        "lineageTag": str(uuid.uuid4())
    }
    target_table["measures"].append(new_measure)

    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    print(f" Measure '{measure_name}' written to model.bim!")
    return True