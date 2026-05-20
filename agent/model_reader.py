import json
from pathlib import Path

def read_model(pbip_path: str) -> dict:
    model_path = Path(pbip_path) / "model.bim"
    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)
    return model

def get_tables(pbip_path: str) -> list:
    model = read_model(pbip_path)
    tables = []
    for table in model["model"]["tables"]:
        # Skip hidden system tables
        if table["name"].startswith("DateTableTemplate") or \
           table["name"].startswith("LocalDateTable"):
            continue
        columns = [c["name"] for c in table.get("columns", [])]
        measures = [m["name"] for m in table.get("measures", [])]
        tables.append({
            "name": table["name"],
            "columns": columns,
            "measures": measures
        })
    return tables

def get_model_summary(pbip_path: str) -> str:
    tables = get_tables(pbip_path)
    summary = "Your Power BI model contains:\n"
    for t in tables:
        summary += f"\nTable: {t['name']}\n"
        summary += f"  Columns : {', '.join(t['columns'])}\n"
        if t['measures']:
            summary += f"  Measures: {', '.join(t['measures'])}\n"
    return summary

def get_context_for_prompt(pbip_path: str) -> str:
    tables = get_tables(pbip_path)
    context = "Available tables and columns in the Power BI model:\n"
    for t in tables:
        context += f"- Table '{t['name']}': columns = {', '.join(t['columns'])}\n"
        if t['measures']:
            context += f"  Existing measures = {', '.join(t['measures'])}\n"
    return context