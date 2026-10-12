import requests, json
from sklearn.metrics.pairwise import cosine_similarity
import uuid
import sqlite3

from customer_service import (
    get_customer_by_email,
    get_customer_by_orders,
    get_customer_by_tickets
)

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
            "date":join_date,
            "phone":phone,
            "text":chunk
        })
        
    return customer_chunks    


#this is the product  part 
def get_product_data():
    """ Retrieve all product information from the database.

    This function is responsible only for the products table.
    It provides product details such as:
    - Product ID
    - Product Name
    - Category
    - Price
    - Stock Quantity
    - Warranty"""
    
    #for squl query 
    cursor.execute("""SELECT
                   product_id,product_name,category,price,
                   stock_quantity,warranty_months
                   FROM products""")
                   
    rows = cursor.fetchall() 
    product_chunks = []     
    
    
    for product_id, product_name, category,price, stock_quantity , warranty_months in rows:
            
            #create  one chunk per product  
            
            chunk = (
                f"Product_id : {product_id}\n"
                f"Product_name: {product_name }\n"
                f"Category: {category}\n"
                f"Price: {price}\n"
                f"Stock: {stock_quantity}\n"
                f"Warranty:{warranty_months}"
            )
            
            product_chunks.append({
                "id":product_id,
                "table":"products",
                "type":"product",
                "warranty":warranty_months,
                "stock":stock_quantity,
                "price":price,
                "text":chunk
            })
            
    return  product_chunks      




#this is for get order 

def get_order_data():
    """ 
    This function only provide the information about the orders 
    and give the information ask related to products 
    It provies information about 
    order_id
    customer_id
    order_date
    status
    total_amount
    """
    
    #for SQL query 
    cursor.execute("""
                   SELECT order_id,
                   customer_id,
                   order_date,
                   status,
                   total_amount
                   FROM orders """)

    rows = cursor.fetchall()
    
    #this code will store customer data in chunks 
    order_chunks = []
    
    #loop through every customer 
    for order_id, customer_id, order_date, status , total_amount in rows:
        
        #create  one chunk per customer 
        
        chunk = (
            f"Order ID :{order_id}\n"
            f"Customer ID : {customer_id}\n"
            f"Order Date: {order_date}\n"
            f"Status: {status}\n"
            f"Total Amount: {total_amount}\n"
            
        )
        
        order_chunks.append({
            "id":order_id,
            "customer_id":customer_id,
            "table":"orders",
            "type":"order",
            "date":order_date,
            "status":status,
            "amount":total_amount,
            "text":chunk
        })
        
    return order_chunks    



#this is for order_items table 

def get_order_items_data():
    """ 
    This function only provide the information about the orders_items
    and give the information ask related to order_items
    It provies information about 
    item_id
    order_id
    product_id
    quantity
    """
    
    #for SQL query 
    cursor.execute("""
                   SELECT 
                   item_id,
                   order_id,
                  product_id,
                  quantity
                   FROM order_items """)

    rows = cursor.fetchall()
    
    #this code will store customer data in chunks 
    order_items_chunks = []
    
    #loop through every customer 
    for  item_id,order_id, product_id,quantity in rows:
        
        #create  one chunk per customer 
        
        chunk = (
            f"Order ID :{order_id}\n"
            f"Item ID : {item_id}\n"
            f"Product Id: {product_id}\n"
            f"Quantity: {quantity}"
           
            
        )
        
        order_items_chunks.append({
            "order_id":order_id,
            "id":item_id,
            "product_id":product_id,
            "table":"order_items",
            "type":"order_item",
            "quantity":quantity,
            "text":chunk
        })
        
    return order_items_chunks    







#this is the function of ticket-data 
def get_ticket_data():
    """ Retrieve all ticket information from the database.

    This function is responsible only for the tickets table.
    It provides product details such as:
    - ticket ID
    - customer id
    - issue tittle
    - issue description
    - status
    - created at """
    
    #for squl query 
    cursor.execute("""SELECT
                   ticket_id,
                   customer_id,
                   issue_title,
                   issue_description,
                   status,
                   created_at
                   FROM support_tickets""")
                   
    rows = cursor.fetchall() 
    tickets_chunks = []     
    
    
    for ticket_id, customer_id,issue_title,issue_description, status, created_at in rows:
            
            #create  one chunk per product  
            
            chunk = (
                f"Ticket Id : {ticket_id}\n"
                f"Customer ID: {customer_id }\n"
                f"Issue Description: {issue_description}\n"
                f"Issue Title: {issue_title}\n"
                f"Status: {status}\n"
                f"Created at:{created_at}"
            )
            
            tickets_chunks.append({
                "id":ticket_id,
                "table":"support_tickets",
                "type":"ticket",
                "issue_description":issue_description,
                "issue_title":issue_title,
                "created_at":created_at,
                "text":chunk
            })
            
    return  tickets_chunks      



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
    
    
def  build_knowledge_base():
    """
    This is the complete knowledge base of the system.
    
    This function collects data from every business table
    and stores it in a structured dictionary
    
    returns :
        dict :Complete Knowledge base
    
    """
    
    
    knowledge_base ={
        "customers":get_customer_data(),
        "products":get_product_data(),
        "orders":get_order_data(),
        "order_items":get_order_items_data(),
        "tickets":get_ticket_data()
        
    }
    
    return knowledge_base



# Building  embeddings  
def build_embeddings(knowledge_base):
    for category , items  in knowledge_base.items():
        for item in items:
            item["embedding"] = get_embedding(item["text"])
    return knowledge_base

knowledge_base = build_knowledge_base()
knowledge_base = build_embeddings(knowledge_base)

print("\nEmbedding Test")
print("----------------")

for category, items in knowledge_base.items():

    print(f"\n{category}: {len(items)} items")

    if len(items) > 0:

        print("First item:")
        print(items[0]["text"])

        print("Embedding length:")
        print(len(items[0]["embedding"]))

print(knowledge_base.keys())


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
 
 
 
def get_customer_context(email):
    customer = get_customer_by_email(email)
    
    if not customer:
        return None
    
    customer_id = customer[0]
    
    orders = get_customer_by_orders(customer_id)
    tickets = get_customer_by_tickets(customer_id)
    
    context = {
        "customer":customer,
        "orders":orders,
        "tickets":tickets
    }
    
    return context 


def route_question(question):
    
    question = question.lower()
    
    
    if any(word in question for word in [
        "product","price", "cost","warranty","stock","available","smartphone"
    ]):
        return "products"
    
    elif any(word in question for word in[
        "my email","my phone","my name",
        "customer details","join date"
    ]):
        
        return "customers"
    
    elif any(word in question for word in [
        "quantity","item in my order", "how many items"
    ]):
        return "order_items"
    
    elif any (word in question for word in [
        "order","delivery", "delivered","shipping", "tracking"
    ]):
       return "orders"
    
    else :
        return "all"


#-- creating filetering the metadata 

def filter_metadata(items,metadata_filters=None):
    if not metadata_filters:
        return items 
    
    filtered_items = []
    
    
    for item in items :
        matches = True 
        
        for key , excepted_value in metadata_filters.items():
            
            actual_value = item.get(key)
            
            if(
                actual_value is None 
                or str(actual_value).lower()
                != str(excepted_value).lower()
            ):
                matches = False
                break 
            
        if matches:
            filtered_items.append(item)
    return filtered_items



# -------- Retrieve Relevant Chunks --------

def retrieve_relevant_chunks(
    user_input,
    category="all",
    top_k=3,
    metadata_filters=None
):
    # Convert the question into an embedding.
    query_embedding = get_embedding(user_input)

    similarities = []

    # Go through each knowledge-base category.
    for current_category, items in knowledge_base.items():

        # Skip categories not selected by the router.
        if category != "all" and current_category != category:
            continue

        # Apply metadata filters before similarity search.
        filtered_items = filter_metadata(
            items,
            metadata_filters
        )

        # Compare the question with filtered records.
        for item in filtered_items:
            embedding = item.get("embedding")

            # Skip records without embeddings.
            if not embedding:
                continue

            score = cosine_similarity(
                [query_embedding],
                [embedding]
            )[0][0]

            similarities.append((score, item))

    # Rank records by similarity, highest first.
    similarities.sort(
        key=lambda result: result[0],
        reverse=True
    )

    # Select the best matches.
    top_results = similarities[:top_k]

    # Combine the matching records into context.
    context = "\n\n".join(
        item["text"] for score, item in top_results
    )

    return context
   
   
 #-- rewritting the follow up question 
 
 
def rewrite_follow_up_question(user_input,conversation_history):
    
    if not  conversation_history:
        return user_input
    
    
    recent_messages = conversation_history[-10:]
    history_text = ""
    for message in recent_messages:
        history_text += (
            f"{message['role']}: {message['content']}\n"
        )
    prompt = f"""
     
    You rewrite follow-up questions for a business assistant.

Use the conversation history to understand the latest question.

Rules:
- If the question depends on earlier messages, rewrite it as a
  standalone question with the necessary product or topic named.
- If it is already clear on its own, keep its meaning unchanged.
- Do not answer the question.
- Do not invent product names, customer details, or other facts.
- Return only the rewritten question.

Conversation history:
{history_text}

Latest question:
{user_input}

Standalone question:
"""

    try:
        response = requests.post(
            llm_url,
            json={
                "model":"llama3",
                "prompt":prompt,
                "stream":False,
                "temperature":0.1
            },
            timeout=60
        )
        
        response.raise_for_status()
        
        rewritten_question = response.json().get("response","").strip()
        
        if not rewritten_question:
            return user_input
        
        return rewritten_question
    except Exception as e :
        print("Question rewritting error :",e)
        
        return user_input
     
def ask_llm(user_input, customer_email=None):

    # Get customer-specific information if an email is provided
    customer_context = None

    if customer_email:
        customer_context = get_customer_context(customer_email)

    #== conversation Memory  + reterived
    
    
    standalone_question = rewrite_follow_up_question(
        user_input,
        messages
    )
    
    print("Orginal question:",user_input)
    print("Standalone question:",standalone_question)
    
    category = route_question(standalone_question)
    print("Router selected:",category)
    
    
    context = retrieve_relevant_chunks(
        standalone_question,
        category=category,
        top_k=3
    )
    
    print("Retrived context:\n",context)
    
    messages.append({
        "role":"user",
        "content":user_input,
        
    })
    
    
    recent_messages = messages[-10:]

    # Build conversation history
    history_text = ""

    for msg in messages:
        history_text += f"{msg['role']}: {msg['content']}\n"

    # Build customer-specific information
    customer_data_text = ""

    if customer_context:
        customer_data_text = f"""
Customer:
{customer_context["customer"]}

Orders:
{customer_context["orders"]}

Support Tickets:
{customer_context["tickets"]}

"""
    if not  context.strip() and not customer_data_text.strip():
        answer = "I dont know based on the available business data "
        
        
        messages.append({
            "role":"assistant",
            "content":answer
        })
        
        return answer 
    # Prepare the prompt for Llama 3
    prompt = f"""
You are a Business Assistant AI.

Answer using the available business data.
If the answer is not available, say:
"I don't know."

Do not promise future updates, notifications, refunds, or other actions
unless the system has actually performed or scheduled that action.

Business Data:
{context}

Customer-Specific Data:
{customer_data_text}

Conversation History:
{history_text}

User Question:
{user_input}

Answer naturally.
"""

    # Send the prompt to Ollama
    try:
        response = requests.post(
            llm_url,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "response",
            "No response from model"
        )

        # Save the AI response
        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:
        return f"LLM Error: {str(e)}"
    
    

# -------- Test Metadata Filtering --------

# Get all order records from the knowledge base.
orders = knowledge_base["orders"]

for order in orders:
    print(
        "Order ID :",order.get("id"),
        "|Customer ID :", order.get("customer_id")
    )
    
print("---------------")

#  test filtering for customer ID
customer_orders = filter_metadata(
    orders,
    {"customer_id":1}
)

print("Orders for customer ID 1 :")

for order in customer_orders:
    print(order["text"])

# Keep only orders with Delivered status.
delivered_orders = filter_metadata(
    orders,
    {"status": "Delivered"}
)

print("Delivered orders:")
for order in delivered_orders:
    print(order["text"])

print("-------------------------")

# Keep only orders belonging to customer ID 1.
customer_orders = filter_metadata(
    orders,
    {"customer_id": 1}
)

print("Orders for customer ID 1:")
for order in customer_orders:
    print(order["text"])