import openpyxl

contract_path = r"c:\Users\AxeGlobal Ai\Desktop\test ground\SAMPLE SHEET\54060_FCL_Cotransa_contract.xlsx"
wb = openpyxl.load_workbook(contract_path, read_only=True)
print("Contract sheet names:", wb.sheetnames)
