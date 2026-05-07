import pandas as pd

expected_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_processed.xlsx"
actual_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\processed_54060_FCL_Cotransa_contract (7).xlsx"

df_exp = pd.read_excel(expected_path, sheet_name="FCL Freight & Surcharges")
df_act = pd.read_excel(actual_path, sheet_name="Fletes y Recargos ")

print("=== EXPECTED UNIQUE CHARGES ===")
print(df_exp['CHARGE'].dropna().unique())

print("\n=== ACTUAL UNIQUE CHARGES ===")
print(df_act['CHARGE'].dropna().unique())
