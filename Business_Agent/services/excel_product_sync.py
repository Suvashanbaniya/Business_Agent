import sqlite3
from pathlib import Path
from openpyxl import load_workbook


# -------- Locate project and Excel files

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "customer.db"

EXCEL_PATH = Path(
    r"C:\Users\ACER\OneDrive\Business_Agent_Data\Business_Data.xlsx"
)


def read_excel_product():

    """
    Read one product from the vertical Excel layout.
    """

    workbook = load_workbook(EXCEL_PATH, data_only=True)

    try:
        sheet = workbook.active

        product = {}

        for row in sheet.iter_rows(min_row=2, values_only=True):

            field_name = row[0]
            field_value = row[1]

            if field_name is not None:
                product[str(field_name).strip()] = field_value

        return product

    finally:
        workbook.close()


def sync_excel_product():

    """
    Insert or update a product using its product_id.
    """

    product = read_excel_product()

    required_fields = [
        "product_id",
        "product_name",
        "price"
    ]

    # Check whether important fields are available
    for field in required_fields:

        if product.get(field) is None:
            raise ValueError(f"Missing required field: {field}")

    with sqlite3.connect(DATABASE_PATH) as connection:

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

        print("Product synchronized successfully!")


if __name__ == "__main__":
    sync_excel_product()