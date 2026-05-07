import pandas as pd

actual_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\processed_54060_FCL_Cotransa_contract (7).xlsx"
df_act = pd.read_excel(actual_path, sheet_name="Arbitraries")
df_act_clean = df_act.dropna(how='all')
print(f"Actual Arbitraries cleaned rows: {len(df_act_clean)}")
if len(df_act_clean) > 0:
    print(df_act_clean.head(10).to_string())
