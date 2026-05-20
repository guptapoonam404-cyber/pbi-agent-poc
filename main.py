from agent.intent_detector import detect_intent
from agent.model_reader import get_model_summary, get_context_for_prompt, get_tables
from agent.dax_generator import generate_dax_with_context
from agent.pbip_writer import add_measure_to_model
from agent.measure_tools import list_measures, delete_measure
from agent.visual_creator import add_visual_to_report

# ─── CONFIG ──────────────────────────────────────
PBIP_PATH = r"C:\Users\P0605227\pbi-agent-poc\pbip_sample\SalesModel.SemanticModel"
# ─────────────────────────────────────────────────

session_log = []  # memory of this session

def handle_prompt(user_prompt: str):
    print(f"\n Thinking...")

    # Step 1: Detect intent
    intent_data = detect_intent(user_prompt)
    intent = intent_data["intent"]
    table_name = intent_data["table_name"]

    print(f" Intent detected: {intent}")

    # Step 2: Route to the right tool
    if intent in ["generate_dax", "generate_both"]:
        context = get_context_for_prompt(PBIP_PATH)
        print(" Generating DAX with model context...")
        dax_output = generate_dax_with_context(
            business_requirement=user_prompt,
            table_name=table_name,
            model_context=context
        )
        print(f"\n Generated DAX:\n{dax_output}\n")

        # Parse and write
        if "=" in dax_output:
            parts = dax_output.split("=", 1)
            measure_name = parts[0].strip()
            dax_expression = parts[1].strip()
        else:
            measure_name = "AgentMeasure"
            dax_expression = dax_output

        success = add_measure_to_model(
            PBIP_PATH, table_name, measure_name, dax_expression
        )
        if success:
            print(f" Measure '{measure_name}' written to Power BI!")
            session_log.append(f"Generated: {measure_name}")

            # Auto create card visual
            REPORT_PATH = r"C:\Users\P0605227\pbi-agent-poc\pbip_sample\SalesModel.Report"
            from agent.visual_creator import add_visual_to_report
            result = add_visual_to_report(
                REPORT_PATH, "card", measure_name, table_name
            )
            print(f" Visual: {result}")
            session_log.append(f"Visual: card for {measure_name}")
        else:
            print(" Could not write measure. Check table name.")

    elif intent == "list_tables":
        print("\n Your Power BI model:\n")
        print(get_model_summary(PBIP_PATH))

    elif intent == "list_measures":
        print("\n" + list_measures(PBIP_PATH))

    elif intent == "delete_measure":
        measure_name = intent_data.get("measure_name", "")
        if not measure_name:
            measure_name = input(" Which measure to delete? Type name: ").strip()
        result = delete_measure(PBIP_PATH, measure_name)
        print(f"\n {result}")
        session_log.append(f"Deleted: {measure_name}")

    elif intent == "explain_model":
        tables = get_tables(PBIP_PATH)
        print(f"\n Your model has {len(tables)} table(s):")
        for t in tables:
            print(f"\n  Table: {t['name']}")
            print(f"  Columns : {', '.join(t['columns'])}")
            if t['measures']:
                print(f"  Measures: {', '.join(t['measures'])}")

    else:
        print(" I didn't understand that. Try:")
        print("   'calculate total sales'        → generates DAX")
        print("   'show me all tables'            → lists model tables")
        print("   'what measures exist'           → lists measures")
        print("   'delete measure TotalSales'     → removes a measure")
        print("   'explain my model'              → describes structure")


def run_agent():
    print("\n" + "="*55)
    print("  Power BI Agent — ready!")
    print("  Type your instruction in plain English.")
    print("  Type 'history' to see this session's log.")
    print("  Type 'exit' to quit.")
    print("="*55 + "\n")

    while True:
        try:
            user_input = input(" You: ").strip()

            if not user_input:
                continue
            elif user_input.lower() == "exit":
                print("\n Goodbye! Refresh Power BI Desktop to see changes.")
                break
            elif user_input.lower() == "history":
                if session_log:
                    print("\n Session log:")
                    for i, entry in enumerate(session_log, 1):
                        print(f"  {i}. {entry}")
                else:
                    print(" Nothing done yet this session.")
            else:
                handle_prompt(user_input)

        except KeyboardInterrupt:
            print("\n\n Agent stopped.")
            break

if __name__ == "__main__":
    run_agent()