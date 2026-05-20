import json
import uuid
from pathlib import Path

def create_card_visual(measure_name: str, table_name: str, 
                        x: int, y: int) -> dict:
    visual_name = str(uuid.uuid4())[:8]
    config = {
        "name": visual_name,
        "layouts": [{
            "id": 0,
            "position": {
                "x": x, "y": y, "z": 0,
                "height": 150, "width": 250,
                "tabOrder": 1000
            }
        }],
        "singleVisual": {
            "visualType": "card",
            "drillFilterOtherVisuals": True,
            "projections": {
                "Values": [{"queryRef": f"{table_name}.{measure_name}",
                            "active": True}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "s", "Entity": table_name, "Type": 0}],
                "Select": [{
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": measure_name
                    },
                    "Name": f"{table_name}.{measure_name}"
                }]
            },
            "vcObjects": {
                "title": [{
                    "properties": {
                        "text": {
                            "expr": {"Literal": {
                                "Value": f"'{measure_name}'"
                            }}
                        }
                    }
                }]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 0,
        "width": 250, "height": 150,
        "config": json.dumps(config),
        "filters": "[]",
        "query": "{}",
        "dataTransforms": "{}"
    }


def create_bar_chart_visual(measure_name: str, table_name: str,
                             category_column: str, x: int, y: int) -> dict:
    visual_name = str(uuid.uuid4())[:8]
    config = {
        "name": visual_name,
        "layouts": [{
            "id": 0,
            "position": {
                "x": x, "y": y, "z": 0,
                "height": 300, "width": 420,
                "tabOrder": 2000
            }
        }],
        "singleVisual": {
            "visualType": "barChart",
            "drillFilterOtherVisuals": True,
            "projections": {
                "Category": [{"queryRef": f"{table_name}.{category_column}"}],
                "Y": [{"queryRef": f"{table_name}.{measure_name}",
                       "active": True}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "s", "Entity": table_name, "Type": 0}],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "s"}},
                            "Property": category_column
                        },
                        "Name": f"{table_name}.{category_column}"
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "s"}},
                            "Property": measure_name
                        },
                        "Name": f"{table_name}.{measure_name}"
                    }
                ]
            },
            "vcObjects": {
                "title": [{
                    "properties": {
                        "text": {
                            "expr": {"Literal": {
                                "Value": f"'{measure_name} by {category_column}'"
                            }}
                        }
                    }
                }]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 0,
        "width": 420, "height": 300,
        "config": json.dumps(config),
        "filters": "[]",
        "query": "{}",
        "dataTransforms": "{}"
    }


def add_visual_to_report(report_path: str, visual_type: str,
                          measure_name: str, table_name: str,
                          category_column: str = None) -> str:
    report_json_path = Path(report_path) / "report.json"

    if not report_json_path.exists():
        return f"report.json not found at {report_json_path}"

    with open(report_json_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    sections = report.get("sections", [])
    if not sections:
        return "No pages found in report!"

    page = sections[0]
    if "visualContainers" not in page:
        page["visualContainers"] = []

    # Calculate position based on existing visuals
    existing = page["visualContainers"]
    count    = len(existing)
    x_pos    = (count % 3) * 280 + 20
    y_pos    = (count // 3) * 200 + 20

    # Create the right visual type
    if visual_type == "card":
        visual = create_card_visual(measure_name, table_name, x_pos, y_pos)
    else:
        cat_col = category_column or "ProductID"
        visual  = create_bar_chart_visual(
            measure_name, table_name, cat_col, x_pos, y_pos
        )

    page["visualContainers"].append(visual)
    report["sections"] = sections

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return (f"✅ {visual_type} visual for '{measure_name}' "
            f"added to report page!")