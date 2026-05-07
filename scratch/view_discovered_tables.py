from discovery_engine import discovery_engine
from mapping_engine import mapping_engine

file_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_contract.xlsx"
workbook_data = discovery_engine.process_excel(file_path)

print("\n=== DISCOVERED TABLES RELEVANCE ANALYSIS ===")
for sheet_name, sheet_obj in workbook_data.items():
    print(f"\nSheet: {sheet_name}")
    tables = sheet_obj.get('tables', []) if isinstance(sheet_obj, dict) else sheet_obj
    for table in tables:
        tname = table.get('name')
        trange = table.get('range')
        ttype = table.get('type')
        headers = table.get('headers', [])
        is_rel = mapping_engine._is_relevant_table(table)
        print(f"  - Table: '{tname}' (Range: {trange}, Type: {ttype}) -> Relevant: {is_rel}")
        print(f"    Headers: {headers[:10]}")
