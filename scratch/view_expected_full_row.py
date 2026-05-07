import pandas as pd

expected_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_processed.xlsx"
df_exp = pd.read_excel(expected_path, sheet_name="FCL Freight & Surcharges")
df_exp_clean = df_exp.dropna(how='all')

row_with_data = df_exp_clean[df_exp_clean['DESTINATION PORT'].notna()].iloc[0]
for col, val in row_with_data.items():
    if pd.notna(val):
        print(f"{col}: {val}")
