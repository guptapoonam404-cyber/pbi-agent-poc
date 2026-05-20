def build_dax_prompt(business_requirement: str, table_name: str) -> str:
    return f"""
You are a Power BI DAX expert.
Generate a single DAX measure for this requirement:

Business requirement: {business_requirement}
Table name: {table_name}

Rules:
- Return ONLY the DAX code, nothing else
- Use proper DAX syntax
- Format: MeasureName = <DAX expression>

DAX measure:
"""