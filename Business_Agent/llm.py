import requests , json 
from sklearn.metrics.pairwise import cosine_similarity
import uuid 
import sqlite3
llm_url = "http://localhost:11434/api/generate"
embeded_url = "http://localhost:11434/api/embeddings"


conn = sqlite3.connect("customer.db",check_same_thread=False)
cursor = conn.cursor ()

messages = []


temperature = 0.3

def business_info():
    
    #customer information 
    cursor.execute("SELECT full_name , email , phone FROM customers ")
    rows = cursor.fetchall()
    text = ""
    for full_name , email , phone in rows :
       text += f"{full_name} ({email}): {phone}\n"
       
    #this is for products
    cursor.execute("""
                   SELECT product_name, price , stock_quantity, warranty_months FROM products """) 
    
    for name , price , stock , warranty in cursor.fetchall():
        text +=(
            f"Product : {name},"
            f"price:${price},"
            f"stock: {stock},"
            f"warranty: {warranty} months \n"
        )
    
      
    return text     



#customer data function 
def get_customer_data():
    """ 
    Reterive all customer information from the database.
    This function is made only for the customer data 
    and it only responsible for the customer table.
    """
    #for SQL query 
    cursor.execute("""
                   SELECT customer_id,full_name,email,
                   phone, join_date FROM customers """)

    rows = cursor.fetchall()
    
    #this code will store customer data in chunks 
    customer_chunks = []
    
    #loop through every customer 
    for customer_id, full_name, email, phone , join_date in rows:
        
        #create  one chunk per customer 
        
        chunk = (
            f"Customer ID : {customer_id}\n"
            f"Name : {full_name }\n"
            f"Email : {email}\n"
            f"Phone: {phone}\n"
            f"Join Date : {join_date}"
        )
        
        customer_chunks.append({
            "id":customer_id,
            "table":"customers",
            "type":"customer",
            "text":chunk
        })
        
    return customer_chunks    



def get_embedding(text):
    try:
        response = requests.post(embeded_url, json={
            'model': 'nomic-embed-text',
            'prompt': text
        })

        data = response.json()

        if "embedding" not in data:
            return [0.0] * 768

        return data.get("embedding", [0.0] * 768)

    except Exception as e:
        print("Embedding error:", e)
        return [0.0] * 768
    
# This part prepare the chunks 

chunk_size = 10 
info = business_info()
lines = info.splitlines()

chunks = []

for i in range (0,len(lines), chunk_size):
    chunk = "\n".join(lines[i:i + chunk_size])
    
    if chunk.strip():
        chunks.append(chunk)
      
      
        
chunk_embeddings = []




for chunk in chunks :
    emb = get_embedding(chunk)
    chunk_embeddings.append(emb)        
    
def ask_llm(user_input):

    query_embedding = get_embedding(user_input)

    similarities = []

    for i in range(len(chunk_embeddings)):
        score = cosine_similarity(
            [query_embedding],
            [chunk_embeddings[i]]
        )[0][0]

        similarities.append((score, chunks[i]))

    similarities.sort(reverse=True)

    top_chunks = similarities[:3]

    context = "\n".join([item[1] for item in top_chunks])

    messages.append({
        "role": "user",
        "content": user_input
    })

    history_text = ""

    for msg in messages:
        history_text += f"{msg['role']} : {msg['content']}\n"

    prompt = f"""
You are a Business Assistant AI.

Answer only from the business data below.

If the answer is not available in the business data, say:
"I don't know."

Business Data:
{context}

Conversation History:
{history_text}

User Question:
{user_input}

Answer naturally.
"""

    try:

        response = requests.post(
            llm_url,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
        )

        data = response.json()

        answer = data.get(
            "response",
            "No response from model"
        )

        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:

        return f"LLM Error: {str(e)}"