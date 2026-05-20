import json
from pathlib import Path

PBIP_PATH = ""  # set from main agent

def list_measures(pbip_path: str) -> str:
    model_path = Path(pbip_path) / "model.bim"
    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    result = "Existing measures in your model:\n"
    found = False
    for table in model["model"]["tables"]:
        measures = table.get("measures", [])
        if measures:
            found = True
            result += f"\nTable: {table['name']}\n"
            for m in measures:
                result += f"  - {m['name']} = {m['expression'][:60]}...\n"

    if not found:
        result = "No measures found in the model yet."
    return result

def delete_measure(pbip_path: str, measure_name: str) -> str:
    model_path = Path(pbip_path) / "model.bim"
    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    deleted = False
    for table in model["model"]["tables"]:
        before = len(table.get("measures", []))
        table["measures"] = [
            m for m in table.get("measures", [])
            if m["name"].lower() != measure_name.lower()
        ]
        if len(table.get("measures", [])) < before:
            deleted = True

    if deleted:
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(model, f, indent=2)
        return f"Measure '{measure_name}' deleted successfully!"
    else:
        return f"Measure '{measure_name}' not found in the model."