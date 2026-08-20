import os
import smtplib

from dotenv import load_dotenv
from email.message import EmailMessage


load_dotenv()


def send_email(customer_email, subject, body):

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    message = EmailMessage()

    message["From"] = sender_email
    message["To"] = customer_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            sender_email,
            sender_password
        )

        server.send_message(message)

    print("Email sent successfully!")