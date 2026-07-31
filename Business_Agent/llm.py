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

knowledge_base = build_knowledge_base()
print(knowledge_base.keys())


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