from customer_service import (
    get_customer_by_email,
    get_customer_by_orders,
    get_customer_by_tickets
)

print("Customer Service Test Started")


email = input("Enter customer email: ")


customer = get_customer_by_email(email)


if customer:

    print("\nCustomer found!")
    print(customer)
    
    customer_id = customer[0]
    
    orders = get_customer_by_orders(customer_id)
    print("\nOrders")
    
    for order in orders:
        print(order)
        
    
    tickets = get_customer_by_tickets(customer_id)
    print("\nTickets")
    
    for ticket in tickets:
        print(ticket)    
    
    
else:

    print("\nCustomer not found.")