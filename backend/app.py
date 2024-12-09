from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS  # Import CORS
from pymongo import MongoClient
import random
from langchain_openai import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity  # For cosine similarity calculation
from utils import process_question
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['tutor']
COLLECTION_NAME = "openai_embedding"

# Function to embed the user question
def embed_question(question):
    return embeddings.embed_query(question)

# Function to fetch questions and embeddings from MongoDB
def fetch_from_mongodb():
    collection = db[COLLECTION_NAME]
    documents = list(collection.find({}, {"_id": 0, "question": 1, "embedding": 1}))
    
    questions = [doc["question"] for doc in documents]
    stored_embeddings = [doc["embedding"] for doc in documents]
    return questions, np.array(stored_embeddings)

# Fetch the questions and embeddings from MongoDB
mongo_question, mongo_embed = fetch_from_mongodb()

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/tutor"
mongo = PyMongo(app)

# Get the collection (users collection in MongoDB)
users_collection = mongo.db.users
rag_answering_collection = mongo.db.rag_answering  # Collection for high similarity
teacher_answering_collection = mongo.db.teacher_answering  # Collection for low similarity

# Message Handling Route
message_history = []
# Login Route

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # Check if both username and password exist in MongoDB
    user = users_collection.find_one({"username": username, "password": password})
    if not user:
        return jsonify({"message": "Invalid username or password"}), 400

    # Successfully authenticated, return user data
    return jsonify({
        "message": "Login successful",
        "user": {
            "name": user['name'],
            "username": user['username'],
            "role": user['role'],
            "class_name": user.get('class_name', None)
        }
    }), 200

@app.route("/api/send-message", methods=["POST"])
def send_message():
    user_message = request.json.get("message")
    
    if not user_message:
        return jsonify({"error": "Message is required!"}), 400
    
    # Log the received user message
    print(f"Received question: {user_message}")
    
    # Embed the user's question
    user_embedding = embed_question(user_message)
    
    # Calculate cosine similarity between the user message embedding and stored embeddings
    similarities = cosine_similarity([user_embedding], mongo_embed)
    
    # Find the index of the most similar question
    most_similar_index = np.argmax(similarities)
    
    # Retrieve the most similar question
    most_similar_question = mongo_question[most_similar_index]
    
    # Get the cosine similarity score
    similarity_score = similarities[0][most_similar_index]
    
    # Log the bot response (based on most similar question)
    print(f"Most similar question: {most_similar_question}")
    print(f"Cosine similarity score: {similarity_score}")
    
    # Classify based on similarity score
    if similarity_score > 0.2:
        answer=process_question(user_message)
        # Store in rag_answering collection for high similarity
        rag_answering_collection.insert_one({
            "user_message": user_message,
            "most_similar_question": most_similar_question,
            "similarity_score": similarity_score
        })
        bot_response = f" {answer} (Similarity: {similarity_score})"
    else:
        # Store in teacher_answering collection for low similarity
        teacher_answering_collection.insert_one({
            "user_message": user_message,
            "most_similar_question": most_similar_question,
            "similarity_score": similarity_score
        })
        bot_response = f"Teacher Bot: The most similar question was: {most_similar_question} (Similarity: {similarity_score})"

    # Add the user and bot messages to the history
    message_history.append({"type": "user", "content": user_message})
    message_history.append({"type": "bot", "content": bot_response})

    # Limit the history size (optional)
    if len(message_history) > 50:
        message_history.pop(0)  # Keep the history to 50 messages for performance

    return jsonify({
        "bot_response": bot_response,
        "similarity_score": similarity_score
    })

# Route to get message history
@app.route("/api/get-history", methods=["GET"])
def get_history():
    return jsonify({"messages": message_history})

if __name__ == "__main__":
    app.run(debug=True)
