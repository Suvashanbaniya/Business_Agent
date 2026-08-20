from customer_service import get_customer_by_email


print("Customer Service Test Started")


email = input("Enter customer email: ")


customer = get_customer_by_email(email)


if customer:

    print("\nCustomer found!")

    print(customer)

else:

    print("\nCustomer not found.")