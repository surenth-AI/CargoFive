import pandas as pd

expected_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_processed.xlsx"
actual_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\processed_54060_FCL_Cotransa_contract (7).xlsx"

df_exp = pd.read_excel(expected_path, sheet_name="FCL Freight & Surcharges")
df_act = pd.read_excel(actual_path, sheet_name="Fletes y Recargos ")

exp_charges = set(df_exp['CHARGE'].dropna().unique())
act_charges = set(df_act['CHARGE'].dropna().unique())

print(f"Expected unique charges count: {len(exp_charges)}")
print("Expected charges:", sorted(list(exp_charges)))

print(f"\nActual unique charges count: {len(act_charges)}")
print("Actual charges:", sorted(list(act_charges)))

print("\nCharges expected but missing in actual:")
print(sorted(list(exp_charges - act_charges)))

print("\nCharges in actual but missing in expected:")
print(sorted(list(act_charges - exp_charges)))
