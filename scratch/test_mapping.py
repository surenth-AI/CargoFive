import json
from discovery_engine import discovery_engine
from planner_engine import planner_engine
from mapping_engine import mapping_engine

file_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_contract.xlsx"
print("1. Running Discovery Engine...")
workbook_data = discovery_engine.process_excel(file_path)

print("2. Generating Master Execution Plan...")
plan = planner_engine.generate_plan(workbook_data)
schedule = plan.get('schedule', [])

print("\n--- EXECUTING SCHEDULED TASKS ---")
for task in schedule:
    task_id = task.get('task_id')
    region_name = task.get('region_name')
    primary_sheet = task.get('primary_sheet')
    print(f"\n> Executing {task_id}: {region_name} (Sheet: {primary_sheet})...")
    try:
        mapped_rows = mapping_engine.process_task(task, workbook_data)
        print(f"  Result: {len(mapped_rows)} rows mapped.")
        if len(mapped_rows) > 0:
            charges = set(r.get('CHARGE') for r in mapped_rows)
            print(f"  Charges found: {charges}")
    except Exception as e:
        print(f"  Error executing task: {e}")
