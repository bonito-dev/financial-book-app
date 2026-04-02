import pandas as pd

file = "My Financial Book.xlsx"

xls = pd.ExcelFile(file)

print("Sheets:", xls.sheet_names)

for sheet in xls.sheet_names:
    df = pd.read_excel(file, sheet_name=sheet)
    print(f"\n--- {sheet} ---")
    print(df.head())