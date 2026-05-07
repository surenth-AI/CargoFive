import pandas as pd

expected_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_processed.xlsx"
df_exp = pd.read_excel(expected_path, sheet_name="FCL Freight & Surcharges")
df_exp_clean = df_exp.dropna(how='all')

# Print first 20 rows of the cleaned Expected DataFrame, showing only specific key columns
cols = ['ORIGIN LOCATION', 'ORIGIN PORT', 'DESTINATION PORT', 'DESTINATION LOCATION', 'CHARGE TYPE', 'CHARGE', '20DRY', '40DRY']
print(df_exp_clean[cols].head(20).to_string())
