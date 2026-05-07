import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import openpyxl
from discovery_engine import DiscoveryEngine

file_path = r"C:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\46566_FCL_TRANSPORTES GRUPO CALICHE_contract.xlsx"
wb = openpyxl.load_workbook(file_path, data_only=True)
engine = DiscoveryEngine()

# Let's test EXP BARCELONA
sheet_name = "EXP BARCELONA"
sheet = wb[sheet_name]
merged_map = engine._get_merged_cells_map(sheet)
sheet_data = engine._extract_sheet_data(sheet, merged_map)

print(f"Sheet Data size: {len(sheet_data)} rows")

# Let's see the prompt and the raw response
def json_serial(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)

prompt = f"""
You are a world-class data structure specialist. I have an Excel sheet named '{sheet_name}'.

Your task:
1. Find ALL distinct data tables in the provided data snippet.
2. Identify the EXACT boundaries (Excel range like A1:G2500).
3. Identify the logical headers for each table.
4. FIND TABLE NAME: Look for a title or name in the rows immediately ABOVE the table headers. 
   - Mostly, tables have names like "Import Customer Service" or "Sales Report 2024".
   - Use the actual name found in the sheet if present.
   - ONLY if no name is found in the sheet, generate a highly relevant one.
5. Resolve Merged Cells: If a column is [MERGED], it belongs to the cell to its left.

CRITICAL: DO NOT return the data rows. ONLY return the metadata.

Return the result STRICTLY as a JSON array:
[
    {{
        "range": "A1:G2500",
        "headers": ["Header 1", "Header 2", ...],
        "table_name": "Actual Name from Sheet or Relevant Name",
        "type": "Table Description",
        "start_row": 1, 
        "end_row": 2500,
        "start_col": "A",
        "end_col": "G"
    }}
]

Sheet Data Snippet (with [MERGED] tokens):
{json.dumps(sheet_data[:300], default=json_serial)} 
"""

try:
    print("Calling Gemini...")
    response = engine.model.generate_content(prompt)
    print("\n--- RAW RESPONSE FROM GEMINI ---")
    print(response.text)
    print("--------------------------------")
except Exception as e:
    print("API Error:", e)
