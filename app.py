import pandas as pd
import openpyxl

excel_path = 'REPORTE P1 Y P3 AGOSTO 2026.xlsx'
wb = openpyxl.load_workbook(excel_path, data_only=True)
print("Sheet names:", wb.sheetnames)

sheet = wb['DASHBOARD']
# Read rows to inspect non-empty data blocks
df = pd.DataFrame(sheet.values)
print("DF Shape:", df.shape)

# Let's inspect columns and sample non-null areas
for col_idx in range(df.shape[1]):
    col_vals = df.iloc[:, col_idx].dropna().tolist()
    if col_vals:
        print(f"Col {col_idx} (Letter {openpyxl.utils.get_column_letter(col_idx+1)}): {col_vals[:5]}")
