from Business_Agent.ai.llm import ask_llm
from Business_Agent.services.emailservice import send_email


print("LLM + Email Test Started")


email = input("Enter customer email: ")

question = input("Enter your question: ")


answer = ask_llm(question, email)


print("\nAI Response:")
print(answer)


send_email(
    email,
    "Customer Support Response",
    answer
)