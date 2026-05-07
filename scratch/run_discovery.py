import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from discovery_engine import DiscoveryEngine

file_path = r"C:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\46566_FCL_TRANSPORTES GRUPO CALICHE_contract.xlsx"
engine = DiscoveryEngine()
try:
    results = engine.process_excel(file_path)
    for name, sheet_res in results.items():
        print(f"\n================ SHEET: {name} ================")
        print("Metadata:", sheet_res.get("metadata"))
        tables = sheet_res.get("tables", [])
        print(f"Number of tables found: {len(tables)}")
        for idx, t in enumerate(tables, 1):
            print(f"  Table {idx}: {t.get('table_name')} ({t.get('range')})")
            print(f"    Headers: {t.get('headers')}")
            print(f"    Data rows count: {len(t.get('data', []))}")
            if len(t.get('data', [])) > 0:
                print(f"    Sample Row: {t.get('data')[0]}")
except Exception as e:
    print("Error:", e)
