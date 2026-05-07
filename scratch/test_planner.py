import json
from discovery_engine import discovery_engine
from planner_engine import planner_engine

file_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_contract.xlsx"
print("1. Running Discovery Engine...")
results = discovery_engine.process_excel(file_path)

print("2. Generating Master Execution Plan...")
plan = planner_engine.generate_plan(results)

print("\n=== GENERATED MASTER EXECUTION PLAN ===")
print(json.dumps(plan, indent=2))
