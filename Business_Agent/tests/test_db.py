import sqlite3


conn = sqlite3.connect("customer.db")

cursor = conn.cursor()


print("\nCUSTOMERS")

cursor.execute("""
    SELECT *
    FROM customers
""")

for row in cursor.fetchall():
    print(row)


print("\nORDERS")

cursor.execute("""
    SELECT *
    FROM orders
""")

for row in cursor.fetchall():
    print(row)


print("\nORDER ITEMS")

cursor.execute("""
    SELECT *
    FROM order_items
""")

for row in cursor.fetchall():
    print(row)


print("\nPRODUCTS")

cursor.execute("""
    SELECT *
    FROM products
""")

for row in cursor.fetchall():
    print(row)


print("\nSUPPORT TICKETS")

cursor.execute("""
    SELECT *
    FROM support_tickets
""")

for row in cursor.fetchall():
    print(row)


conn.close()