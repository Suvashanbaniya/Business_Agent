
import json
import requests

llm_url = "http://localhost:11434/api/generate"

VALID_INTENTS = [
    "order_status",
    "product_inquiry",
    "refund_request",
    "complaint",
    "general_question",
    "positive_reply",
    "negative_reply",
    "ticket_status",
    "other"
]


def detect_intent(user_input):

    prompt = f"""
You are an intent classification system for a business
customer support agent.

Classify the customer's message into exactly one category:
- order_status: asking about an order, delivery, or shipping
- ticket_status: asking about an existing support ticket,
  previous complaint, ticket progress, or resolution
- product_inquiry: asking about product price, stock, or warranty
- refund_request: requesting a refund or return
- complaint: reporting a new problem or expressing dissatisfaction
- general_question: asking a general business question
- Questions about previously created tickets must be classified as ticket_status.
- Reporting a new product problem must be classified as complaint.
- Do not classify ticket-status questions as general_question.


Rules:
- Classify the customer's main intent.
- Do not answer the customer.
- Do not invent facts.
- Refund requests and complaints require human review.
- Negative replies require human review.
- If uncertain, use other and require human review.
- Return a JSON object with these keys:
  intent, confidence, needs_human

Customer message:
{user_input}

Example:
{{"intent": "order_status", "confidence": 0.95,
"needs_human": false}}
"""

    try:
        response = requests.post(
            llm_url,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.0,
                "format": "json"
            },
            timeout=60
        )

        response.raise_for_status()

        result_text = response.json().get("response", "").strip()

        # Extract the JSON object if the model adds extra text.
        start = result_text.find("{")
        end = result_text.rfind("}")

        if start == -1 or end == -1 or end < start:
            raise ValueError("No valid JSON object found")

        result = json.loads(result_text[start:end + 1])

        intent = result.get("intent", "other")

        try:
            confidence = float(result.get("confidence", 0.0))
        except (ValueError, TypeError):
            confidence = 0.0

        needs_human = result.get("needs_human", True)

        # Reject unexpected intent names.
        if intent not in VALID_INTENTS:
            intent = "other"
            confidence = 0.0
            needs_human = True

        # Validate the confidence score.
        if not 0.0 <= confidence <= 1.0:
            confidence = 0.0
            needs_human = True

        if not isinstance(needs_human, bool):
            needs_human = True

        # Sensitive or negative messages require review.
        if intent in [
            "refund_request",
            "complaint",
            "negative_reply"
        ]:
            needs_human = True

        # Low-confidence classifications require review.
        if confidence < 0.70:
            needs_human = True

        return {
            "intent": intent,
            "confidence": confidence,
            "needs_human": needs_human
        }

    except (
        requests.RequestException,
        ValueError,
        TypeError,
        AttributeError
    ) as error:

        print("Intent detection error:", error)

        return {
            "intent": "other",
            "confidence": 0.0,
            "needs_human": True
        }
