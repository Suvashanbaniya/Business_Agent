from flask import Flask , request ,jsonify ,render_template
from flask_cors import CORS
from llm import ask_llm

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Business AI Assistant  is running successfully "

@app.route("/chat",methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message","")
    
    if not user_message.strip():
        return jsonify({"response":"Please enter a message"})
    
    print("\nCustomer:",user_message)
    
    reply = ask_llm(user_message)
    
    reply = ask_llm(user_message)
    
    print("AI:",reply)
    
    return jsonify({
        "response":reply,
        "status":"success",
        "model":"llama3",
    
    })   
    
if __name__ == "__main__":
        app.run(debug=True) 
    