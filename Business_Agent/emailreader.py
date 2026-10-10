import os
import imaplib
import email

from dotenv import load_dotenv
from email.header import decode_header


load_dotenv()


def read_emails():
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_address or not email_password :
        print("The email and the password is not correct or they are missing ")
        return 
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    
    try:
        mail.login(email_address, email_password)
        
        mail.select("INBOX")
        
        status, messages = mail.search(None, "UNSEEN")
        
        if status !="OK":
            print("Could not search box")
            
        email_ids = messages[0].split()
        
        if not email_ids:
            print("No unread email found ")
            return
        
        for email_id in email_ids:
            status , data = mail.fetch(email_id,"(RFC822)")
            
            if status != "OK":
                print("Could not fetch email:",email_id)
                continue
            raw_email = data[0][1]
            
            message = email.message_from_bytes(raw_email)
            
            sender = email.utils.parseaddr(
                message.get("From","")
            )[1]
            
            subject_parts = decode_header(
                message.get("subject","")
            )
            
            
            subject = ""
            
            for part , encoding in subject_parts :
                if isinstance(part,bytes):
                    subject += part.decode(
                        encoding or "utf-8",
                        errors = "replace"
                    )
                else:
                    subject += part 
                    
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        if part.get_content_disposition() == "attachemt":
                            continue
                        
                        payload = part.get_payload(decode=True)
                        
                        if payload:
                            body = payload.decode(
                                part.get_content_charset() or "utf-8",
                                errors = "replace "
                            )
                            break
            else:
                if message.get_content_type() == "text/plain":
                    payload = message.get_payload(decode=True)
                    
                    if payload:
                        body = payload.decode(
                            message.get_content_charset() or "utf-8",
                            errors="replace"
                        )
            
            print("\nNew Email Found!")
            print("From:", sender)
            print("Subject:", subject)
            print("Message:")
            print(body)

    finally:
        try:
            mail.logout()
        except (imaplib.IMAP4.error, OSError):
            pass    
                            