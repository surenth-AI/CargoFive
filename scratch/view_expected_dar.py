import pandas as pd

expected_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_processed.xlsx"
df_exp = pd.read_excel(expected_path, sheet_name="FCL Freight & Surcharges")
df_exp_clean = df_exp.dropna(subset=['DESTINATION PORT'])

dar_rows = df_exp_clean[df_exp_clean['DESTINATION PORT'].str.contains('DAR ES SALAAM', case=False, na=False)]
print(f"Total rows for Dar Es Salaam in Expected: {len(dar_rows)}")
cols = ['ORIGIN PORT', 'DESTINATION PORT', 'CHARGE TYPE', 'CHARGE', 'RATE BASIS', 'CURRENCY', '20DRY', '40DRY', 'COMMODITY', 'SERVICE NAME']
print(dar_rows[cols].to_string())
