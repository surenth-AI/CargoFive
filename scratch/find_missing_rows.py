import pandas as pd

expected_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_processed.xlsx"
actual_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\processed_54060_FCL_Cotransa_contract (7).xlsx"

df_exp = pd.read_excel(expected_path, sheet_name="FCL Freight & Surcharges")
df_act = pd.read_excel(actual_path, sheet_name="Fletes y Recargos ")

df_exp_clean = df_exp.dropna(subset=['DESTINATION PORT', '20DRY', '40DRY'], how='all')
df_act_clean = df_act.dropna(subset=['DESTINATION PORT', '20DRY', '40DRY'], how='all')

print(f"Cleaned Expected rows: {len(df_exp_clean)}")
print(f"Cleaned Actual rows: {len(df_act_clean)}")

# Let's count occurrences of DESTINATION PORT in Expected vs DESTINATION LOCATION/PORT in Actual
exp_dests = df_exp_clean['DESTINATION PORT'].dropna().value_counts()
act_dests = df_act_clean['DESTINATION LOCATION'].dropna().value_counts()

print("\nTop 15 destinations in Expected:")
print(exp_dests.head(15))

print("\nTop 15 destinations in Actual:")
print(act_dests.head(15))
