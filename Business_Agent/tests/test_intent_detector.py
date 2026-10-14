from Business_Agent.ai.intent_detector import detect_intent

while True:
    question = input("Enter a customer message ( or exit):")
    
    if question.lower() =="exit":
        break
    result = detect_intent(question)
    
    print("\nIntent:", result["intent"])
    print("Confidence:", result["confidence"])
    print("Needs human review:", result["needs_human"])
