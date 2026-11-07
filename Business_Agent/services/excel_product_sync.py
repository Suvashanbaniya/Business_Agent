import sqlite3
from pathlib import Path
from openpyxl import load_workbook


# -------- Locate project and Excel files

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "customer.db"

EXCEL_PATH = Path(
    r"C:\Users\ACER\OneDrive\Business_Agent_Data\Business_Data.xlsx"
)

def read_excel_products():
    """
    Read multiple products from the Excel Products worksheet.
    """

    workbook = load_workbook(EXCEL_PATH, data_only=True)

    try:
        sheet = workbook["products"]

        # Read column headings from the first row
        headers = [
            str(cell).strip()
            for cell in next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
        ]

        products = []

        # Read every product row after the headings
        for row in sheet.iter_rows(min_row=2, values_only=True):

            if not any(value is not None for value in row):
                continue

            product = dict(zip(headers, row))
            products.append(product)

        return products

    finally:
        workbook.close()
    
        
def sync_excel_product():

    """
    Insert or update multiple products from Excel.
    """

    products = read_excel_products()

    if not products:
        print("No products found in Excel.")
        return

    with sqlite3.connect(DATABASE_PATH) as connection:

        for product in products:

            required_fields = [
                "product_id",
                "product_name",
                "price"
            ]

            # Validate required product information
            for field in required_fields:
                if product.get(field) is None:
                    raise ValueError(
                        f"Missing required field: {field}"
                    )

            connection.execute("""
                INSERT INTO products (
                    product_id,
                    product_name,
                    category,
                    price,
                    stock_quantity,
                    warranty_months,
                    description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(product_id) DO UPDATE SET
                    product_name = excluded.product_name,
                    category = excluded.category,
                    price = excluded.price,
                    stock_quantity = excluded.stock_quantity,
                    warranty_months = excluded.warranty_months,
                    description = excluded.description
            """, (
                int(product["product_id"]),
                str(product["product_name"]),
                product.get("category"),
                float(product["price"]),
                int(product.get("stock_quantity") or 0),
                int(product.get("warranty_months") or 0),
                product.get("description")
            ))

    print(f"Successfully synchronized {len(products)} products!")


if __name__ == "__main__":
    sync_excel_product()