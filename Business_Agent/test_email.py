from emailservice import send_email


# Ask for the customer's email address
customer_email = input("Enter customer email: ")


# Ask for the customer's message
customer_message = input("Enter customer message: ")


# Create a subject using the customer's message
subject = "Customer Support Response"


# Create the response
response = f"""
Hello,

Thank you for contacting our customer support team.

We received your message:

"{customer_message}"

Our team is currently reviewing your request.

We will get back to you with more information shortly.

Regards,
Customer Support Team
"""


# Send the email
send_email(
    customer_email,
    subject,
    response
)