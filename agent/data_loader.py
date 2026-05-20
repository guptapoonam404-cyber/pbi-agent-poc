import json
import uuid
from pathlib import Path

def load_csv_to_model(pbip_path: str, csv_path: str, table_name: str) -> str:
    import csv
    
    # Read CSV file
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    
    if not rows:
        return "CSV file is empty!"
    
    print(f" Read {len(rows)} rows, {len(columns)} columns from {csv_path}")
    
    # Build column definitions for model.bim
    col_defs = []
    for col in columns:
        # Detect data type from first row
        sample = rows[0][col]
        try:
            int(sample.replace(",", ""))
            dtype = "int64"
        except:
            try:
                float(sample.replace(",", ""))
                dtype = "double"
            except:
                dtype = "string"

        col_defs.append({
            "name": col,
            "dataType": dtype,
            "lineageTag": str(uuid.uuid4()),
            "sourceColumn": col,
            "summarizeBy": "none" if dtype == "string" else "sum",
            "annotations": [
                {"name": "SummarizationSetBy", "value": "Automatic"}
            ]
        })

    # Build new table definition
    new_table = {
        "name": table_name,
        "lineageTag": str(uuid.uuid4()),
        "columns": col_defs,
        "measures": [],
        "partitions": [
            {
                "name": table_name,
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": build_m_expression(csv_path, columns)
                }
            }
        ],
        "annotations": [
            {"name": "PBI_NavigationStepName", "value": "Navigation"},
            {"name": "PBI_ResultType", "value": "Table"}
        ]
    }

    # Load model and replace/add table
    model_path = Path(pbip_path) / "model.bim"
    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    # Remove existing table with same name
    model["model"]["tables"] = [
        t for t in model["model"]["tables"]
        if t["name"] != table_name
    ]
    model["model"]["tables"].append(new_table)

    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    return f"Table '{table_name}' loaded with {len(rows)} rows and columns: {', '.join(columns)}"


def build_m_expression(csv_path: str, columns: list) -> str:
    safe_path = csv_path.replace("\\", "\\\\")
    return [
        f'let',
        f'    Source = Csv.Document(File.Contents("{safe_path}"), ',
        f'        [Delimiter=",", Columns={len(columns)}, ',
        f'        Encoding=1252, QuoteStyle=QuoteStyle.None]),',
        f'    promoted = Table.PromoteHeaders(Source, ',
        f'        [PromoteAllScalars=true])',
        f'in',
        f'    promoted'
    ]