


import os
import imaplib
import email

from dotenv import load_dotenv


load_dotenv()


def read_emails():

    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    mail.login(
        email_address,
        email_password
    )

    mail.select("inbox")

    status, messages = mail.search(
        None,
        "UNSEEN"
    )

    email_ids = messages[0].split()

    for email_id in email_ids:

        status, data = mail.fetch(
            email_id,
            "(RFC822)"
        )

        raw_email = data[0][1]

        message = email.message_from_bytes(
            raw_email
        )

        sender = message["From"]
        subject = message["Subject"]

        print("\nNew Email Found!")
        print("From:", sender)
        print("Subject:", subject)

        if message.is_multipart():

            for part in message.walk():

                if part.get_content_type() == "text/plain":

                    body = part.get_payload(
                        decode=True
                    ).decode(
                        errors="ignore"
                    )

                    print("Message:")
                    print(body)

                    break

        else:

            body = message.get_payload(
                decode=True
            ).decode(
                errors="ignore"
            )

            print("Message:")
            print(body)

    mail.close()
    mail.logout()