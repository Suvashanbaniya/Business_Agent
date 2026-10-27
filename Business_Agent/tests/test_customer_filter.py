#-------- Test Customer Order Filtering

from Business_Agent.ai.llm import knowledge_base, filter_metadata


def test_customer_order_filtering():
    # Get all order records from the knowledge base.
    orders = knowledge_base["orders"]

    # Filter orders belonging to customer ID 1.
    customer_orders = filter_metadata(
        orders,
        {"customer_id": 1}
    )

    # Check that customer 1 has at least one order.
    assert len(customer_orders) > 0, (
        "No orders found for customer ID 1."
    )

    # Check that every returned order belongs to customer 1.
    assert all(
        order["customer_id"] == 1
        for order in customer_orders
    ), "An order belonging to another customer was returned."
    
    
    
    
    
#-------- Test Customer Order-Item Filtering
def test_customer_order_item_filtering():
    order_items = knowledge_base["order_items"]

    customer_items = filter_metadata(
        order_items,
        {"customer_id": 1}
    )

    # Verify customer 1 has order items.
    assert len(customer_items) > 0, (
        "No order items found for customer ID 1."
    )

    # Verify every item belongs to customer 1.
    assert all(
        item["customer_id"] == 1
        for item in customer_items
    ), "An order item belonging to another customer was returned."


#-------- Test Customer Ticket Filtering
def test_customer_ticket_filtering():
    tickets = knowledge_base["tickets"]

    customer_tickets = filter_metadata(
        tickets,
        {"customer_id": 1}
    )

    # Verify customer 1 has tickets.
    assert len(customer_tickets) > 0, (
        "No tickets found for customer ID 1."
    )

    # Verify every ticket belongs to customer 1.
    assert all(
        ticket["customer_id"] == 1
        for ticket in customer_tickets
    ), "A ticket belonging to another customer was returned."