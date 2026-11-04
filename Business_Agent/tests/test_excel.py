from openpyxl import load_workbook

# Location of our shared Excel workbook
EXCEL_PATH = (
    r"C:\Users\ACER\OneDrive\Business_Agent_Data\Business_Data.xlsx"
)

# Open the Excel workbook
workbook = load_workbook(EXCEL_PATH, data_only=True)

# Select the active worksheet
sheet = workbook.active

# Read product information from Column A and Column B
product = {}

for row in sheet.iter_rows(min_row=1, values_only=True):

    field_name = row[0]
    field_value = row[1]

    if field_name is not None:
        product[str(field_name).strip()] = field_value

# Display the retrieved product
print("Product information:")

for key, value in product.items():
    print(f"{key}: {value}")

workbook.close()