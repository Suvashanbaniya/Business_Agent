
# -------- Test Customer Order Filtering --------

# Import the knowledge base and filtering function from llm.py.
from Business_Agent.ai.llm import knowledge_base, filter_metadata


# Get all order records from the knowledge base.
orders = knowledge_base["orders"]

# Display the customer ID stored in each order.
print("All orders:")
for order in orders:
    print(
        "Order ID:", order.get("id"),
        "| Customer ID:", order.get("customer_id")
    )

print("-------------------------")

# Filter orders belonging to customer ID 1.
customer_orders = filter_metadata(
    orders,
    {"customer_id": 1}
)

# Display the filtered results.
print("Orders for customer ID 1:")

if customer_orders:
    for order in customer_orders:
        print(order["text"])
else:
    print("No orders found for customer ID 1.")
