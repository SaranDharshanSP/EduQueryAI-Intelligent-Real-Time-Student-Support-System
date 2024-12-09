from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from pymongo import MongoClient
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings
from utils import process_question  # Assuming this is a custom utility function

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['tutor']
COLLECTION_NAME = "openai_embedding"
rag_collection = db['rag_answering']
teacher_answering_collection = db['teacher_answering']

# Function to embed the user question using OpenAI embeddings
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
CORS(app)  # Enable CORS to allow requests from other domains

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/tutor"
mongo = PyMongo(app)

# Get the collections
users_collection = mongo.db.users

# Message History (to store chat messages)
message_history = []

# ------------------------- Routes -------------------------

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

# API to handle sending messages and processing them
@app.route("/api/send-message", methods=["POST"])
def send_message():
    user_message = request.json.get("message")
    
    if not user_message:
        return jsonify({"error": "Message is required!"}), 400
    
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
    
    # If the question is similar, use RAG for answering
    if similarity_score > 0.8:
        answer = process_question(user_message)  # Assuming a function that generates an answer
        
        # Store the answer in the RAG collection for future reference
        rag_collection.insert_one({
            "user_message": user_message,
            "most_similar_question": most_similar_question,
            "similarity_score": similarity_score,
            "answer": answer
        })
        
        bot_response = f"{answer} (Similarity: {similarity_score})"
    else:
        # If the question is not similar, store it in the teacher_answering collection
        teacher_answering_collection.insert_one({
            "user_message": user_message,
            "similarity_score": similarity_score,
            "status": "pending"  # Mark it as pending teacher's review
        })
        
        bot_response = f"Teacher Bot: Your question has been submitted for review by the teacher. We'll get back to you shortly."

    # Add the user and bot messages to the history (if applicable)
    message_history.append({"type": "user", "content": user_message})
    message_history.append({"type": "bot", "content": bot_response})

    # Limit the history size (optional)
    if len(message_history) > 50:
        message_history.pop(0)  # Keep the history to 50 messages for performance

    return jsonify({
        "bot_response": bot_response,
        "similarity_score": similarity_score
    })

# Route for the teacher to provide an answer to a pending question
@app.route('/api/teacher-answering/<question_id>', methods=['PUT'])
def teacher_answer(question_id):
    # Get the teacher's answer from the request body
    teacher_answer = request.json.get('teacher_answer')
    if not teacher_answer:
        return jsonify({"error": "Teacher's answer is required"}), 400
    
    # Update the teacher's answer and set the status to 'answered'
    result = teacher_answering_collection.update_one(
        {"_id": question_id, "status": "pending"},
        {"$set": {"teacher_answer": teacher_answer, "status": "answered"}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Question not found or already answered"}), 404

    # Send the teacher's answer to the student's chat
    bot_response = f"Teacher Bot: {teacher_answer}"

    # Add the teacher's answer to the chat history
    message_history.append({"type": "bot", "content": bot_response})

    return jsonify({"message": "Answer updated and sent to student", "bot_response": bot_response}), 200

# Route to get the teacher answering history
@app.route('/api/teacher-answering', methods=['GET'])
def get_teacher_answering():
    data = list(teacher_answering_collection.find({"status": "pending"}, {"_id": 0}))  # Fetch only pending questions
    return jsonify(data)

# Registration Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get("name")
    username = data.get("username")
    password = data.get("password")
    is_student = data.get("isStudent")
    class_name = data.get("className") if is_student else None

    # Check if username already exists
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400

    # Create user data to insert
    user_data = {
        "name": name,
        "username": username,
        "password": password,  # Store password in plain text (not recommended for production)
        "role": "student" if is_student else "teacher",
        "class_name": class_name if is_student else None
    }

    # Insert user data into MongoDB
    users_collection.insert_one(user_data)

    return jsonify({"message": "Registration successful"}), 201

# Route to get message history
@app.route("/api/get-history", methods=["GET"])
def get_history():
    return jsonify({"messages": message_history})

# ------------------------- Main -------------------------
if __name__ == "__main__":
    app.run(debug=True)
