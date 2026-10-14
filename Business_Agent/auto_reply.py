
import os

from dotenv import load_dotenv


from services.emailreader import read_emails
from ai.intent_detector import detect_intent
from ai.llm import ask_llm
from services.emailservice import send_email



load_dotenv()


def process_emails():

    # Read unread emails from the support inbox.
    emails = read_emails()

    if not emails:
        print("No emails to process.")
        return

    support_email = os.getenv("EMAIL_ADDRESS", "").strip().lower()

    for message in emails:

        sender = message["sender"]
        subject = message["subject"]
        body = message["body"]

        # Skip messages without a sender or message body.
        if not sender or not body.strip():
            print("Skipping email with missing sender or body.")
            continue

        # Prevent the system from replying to itself.
        if sender.strip().lower() == support_email:
            print("Skipping email sent by the support account.")
            continue

        print("\n------------------------------")
        print("Processing email from:", sender)
        print("Subject:", subject)

        # Step 1: Identify the customer's intent.
        intent_result = detect_intent(body)

        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        needs_human = intent_result["needs_human"]

        print("Detected intent:", intent)
        print("Confidence:", confidence)
        print("Needs human review:", needs_human)

        # Step 2: Handle positive feedback without an AI reply.
        if intent == "positive_reply":
            print("Positive feedback recorded in the console.")
            print("No automatic reply sent.")
            continue

        # Step 3: Hold sensitive or uncertain emails for review.
        if needs_human or intent in [
            "refund_request",
            "complaint",
            "negative_reply",
            "other"
        ]:
            print("Email requires human review.")
            print("No automatic reply sent.")
            print("Customer:", sender)
            print("Subject:", subject)
            print("Message:", body)
            continue

        # Step 4: Answer normal customer questions using your RAG system.
        if intent in [
            "order_status",
            "product_inquiry",
            "general_question"
        ]:

            answer = ask_llm(body, sender)

            # Do not email an error message returned by the LLM.
            if answer.startswith("LLM Error:"):
                print("Could not generate a reply:", answer)
                continue

            print("\nAI ANSWER BEFORE SENDING:")
            print(answer)

            # Step 5: Send the generated response.
            reply_subject = (
                "Re: " + subject
                if subject.strip()
                else "Customer Support Response"
            )

            send_email(
                sender,
                reply_subject,
                answer
            )

            print("Reply sent to:", sender)


if __name__ == "__main__":
    process_emails()
