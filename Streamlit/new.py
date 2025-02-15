import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from PyPDF2 import PdfReader

import streamlit as st


# PostgreSQL database connection
def connect_db():
    conn = psycopg2.connect(
        host="localhost", 
        database="eduquery", 
        user="postgres", 
        password="Sa@251004"
    )
    return conn

# Function to create the questions table if it doesn't exist
def create_table():
    """Create the questions table if it does not exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            dissimilar BOOLEAN NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

# Function to insert a new question with dissimilar status into the database
def insert_question(question, dissimilar):
    """Insert a new student question into the database with dissimilar status."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (question, dissimilar) VALUES (%s, %s) RETURNING id;", (question, dissimilar))
    question_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return question_id

# Function to retrieve all questions and their dissimilar status
def get_questions(dissimilar):
    """Retrieve questions from the database with custom timestamp formatting."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # SQL query to get questions based on dissimilar status
    cursor.execute("SELECT question, submitted_at FROM questions WHERE dissimilar = %s ORDER BY submitted_at DESC;", (dissimilar,))
    rows = cursor.fetchall()
    
    formatted_questions = []
    
    for row in rows:
        question = row[0]
        submitted_at = row[1]
        
        # Format the timestamp as 'hh:mm AM/PM, Month Day, Year'
        formatted_timestamp = submitted_at.strftime('%I:%M %p, %b %d, %Y')
        
        formatted_questions.append((question, formatted_timestamp))
    
    conn.close()
    return formatted_questions

def clear_all_entries():
    """Delete all entries from the questions table."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # SQL query to delete all rows from the questions table
    cursor.execute("DELETE FROM questions;")
    conn.commit()  # Commit the transaction
    conn.close()


def calculate_similarities(questions_csv, embeddings_csv, questions_mongo, embeddings_mongo):
    similarities = cosine_similarity(embeddings_csv, embeddings_mongo)
    dissimilarities = 1 - similarities
    results = []

    for i, question_csv in enumerate(questions_csv):
        for j, question_mongo in enumerate(questions_mongo):
            dissimilarity = round(dissimilarities[i, j], 2)  # Round to 2 decimal places
            rag_answer = "True" if 0.0 <= dissimilarity <= 0.35 else "False"
            results.append({
                "question_from_csv": question_csv,
                "question_from_mongo": question_mongo,
                "dissimilarity": dissimilarity,  # Rounded value
                "rag_answer": rag_answer
            })

    results_df = pd.DataFrame(results)
    grouped_and_sorted = (
        results_df.groupby("question_from_csv", group_keys=False)
        .apply(lambda group: group.sort_values(by="dissimilarity", ascending=True).head(3))
    )
    return grouped_and_sorted.to_dict(orient="records")

load_dotenv()
embeddings = OpenAIEmbeddings()
# Directory for storing PDFs and FAISS index
UPLOAD_FOLDER = './teacher_pdfs'
INDEX_PATH = "./faiss_index"

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dummy database for users
users = {
    "student": {"username": "st1", "password": "pass"},
    "teacher": {"username": "te1", "password": "pass"}
}

# Function to check login credentials
def check_login(username, password, role):
    return users.get(role) and users[role]["username"] == username and users[role]["password"] == password

# Function to check if a vector index already exists
def check_existing_index(index_path):
    return os.path.exists(index_path)

# Function to get text from uploaded PDF files
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to split the text into chunks for vector store
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks

# Function to create and save a vector store from text chunks
def get_vector_store(text_chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(text_chunks, embeddings)
    vector_store.save_local(INDEX_PATH)

# Function to create a conversational retrieval chain for answering questions
def get_conversational_chain(vectorstore):
    prompt_template = """
    System: You are a highly knowledgeable tutor, specializing in explaining the content of specific documents provided by the user. Your task is to help the user understand and learn from the documents they have uploaded, strictly using only the information provided therein. Here are your guidelines:

    - Use only information from the user's uploaded PDF documents to answer questions.
    - If the question relates to information not covered in the PDFs, politely inform the user that "This question will be answered by your teacher".
    - Cite specific sections or pages from the PDFs when relevant to provide detailed and precise answers.
    - Encourage the user to explore related concepts within the PDFs to enhance understanding.
    - Maintain a professional tone and focus on educational support.

    Chat History:
    {chat_history}

    Context from Documents:
    {context}

    User's Question:
    {question}

    Your Response:
    """

    prompt = PromptTemplate(
        input_variables=["chat_history", "context", "question"],
        template=prompt_template
    )

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)
    retriever = vectorstore.as_retriever()

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={'prompt': prompt}
    )
    return chain

# Function to handle login and role selection
def handle_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None

    st.sidebar.header("Login")

    # Select role (Student or Teacher)
    selected_role = st.sidebar.selectbox("Select Role", ["Select Role", "Student", "Teacher"])

    if selected_role != "Select Role" and not st.session_state.logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            if check_login(username, password, selected_role.lower()):
                st.session_state.logged_in = True
                st.session_state.role = selected_role.lower()
                st.success(f"Welcome, {selected_role}!")
            else:
                st.error("Invalid credentials. Please try again.")
    
    # Handle logout
    if st.session_state.logged_in:
        logout_button = st.sidebar.button("Logout")
        if logout_button:
            st.session_state.logged_in = False
            st.session_state.role = None
            st.experimental_rerun()

# Teacher dashboard: Upload PDFs, process and store them
def teacher_dashboard():
    st.subheader("Teacher Dashboard")
    st.write("Welcome to EduQuery AI - Teacher Dashboard")
    st.write("Here, you can upload PDF documents and manage the content.")

    # File upload for teacher
    uploaded_files = st.file_uploader("Upload PDF(s)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        # Save uploaded PDFs to the folder
        for pdf in uploaded_files:
            file_path = os.path.join(UPLOAD_FOLDER, pdf.name)
            with open(file_path, "wb") as f:
                f.write(pdf.getbuffer())
        
        # Process the PDFs and create the vector store
        if st.button("Submit & Process PDFs"):
            raw_text = get_pdf_text(uploaded_files)
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            st.success("PDFs processed successfully! Knowledge base created.")

    # Display uploaded files
    uploaded_files_list = os.listdir(UPLOAD_FOLDER)
    col1, col2 = st.columns([1, 1])  # Create two columns with equal width
    with col1:
        if st.button("Show All PDFs") :
            if uploaded_files_list:
                st.write("Uploaded PDF Files:")
                for file in uploaded_files_list:
                    st.write(file)
    with col2:
    # Button to delete all uploaded PDFs
        if st.button("Delete All PDFs"):
            for file in uploaded_files_list:
                os.remove(os.path.join(UPLOAD_FOLDER, file))
            st.success("All PDFs have been deleted successfully!")

    if st.sidebar.button("Clear All Entries"):
        clear_all_entries()
    col1, col2 = st.columns([1, 1])  # Create two columns with equal width
    with col1:
        if st.button("Answered by the RAG"):
            # Retrieve and display the questions where dissimilar = True
            questions = get_questions(True)
            if questions:
                st.table(questions)
            else:
                st.write("No questions with dissimilar = True.")

    with col2:
        if st.button("Questions to the Teacher"):
            # Retrieve and display the questions where dissimilar = False
            questions = get_questions(False)
            if questions:
                st.table(questions)
            else:
                st.write("No questions with dissimilar = False.")

# Student dashboard: Ask questions based on uploaded PDFs
def student_dashboard():
    st.subheader("Student Dashboard")
    st.write("Welcome to EduQuery AI - Student Dashboard")
    st.write("You can ask questions based on the PDFs uploaded by the teacher.")
    
    # Check if vector store exists
    if check_existing_index(INDEX_PATH):
        # Load the existing index
        vector_store = FAISS.load_local(INDEX_PATH,embeddings=embeddings,allow_dangerous_deserialization=True)
        chain = get_conversational_chain(vector_store)

        # Initialize chat history if not present
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Display chat history
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message('AI'):
                    st.info(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.markdown(message.content)

        # User input for asking questions
        user_question = st.chat_input("Ask a question related to the PDFs")
        question = user_question
        if user_question:
            st.session_state.chat_history.append(HumanMessage(content=user_question))
            with st.chat_message("Human"):
                st.markdown(user_question)
            #calculate_similarities(user_question) 
            # Get the AI's response based on the uploaded PDFs
            response = chain.run(question=user_question,context=vector_store, chat_history=st.session_state.chat_history)
            st.session_state.chat_history.append(AIMessage(content=response))
            if 'your teacher' in response.lower():
                dissimilar_input = False
            else: dissimilar_input = True
            insert_question(question, dissimilar_input)
            print(question,dissimilar_input)

            with st.chat_message("AI"):
                st.info(response)
    else:
        st.warning("No documents have been uploaded by the teacher yet.")

# Main function to control the flow
def main():
    create_table()
    handle_login()

    # Show appropriate dashboard based on role
    if st.session_state.logged_in:
        if st.session_state.role == "teacher":
            teacher_dashboard()
        elif st.session_state.role == "student":
            student_dashboard()

    # Insert the question into the database
if __name__ == "__main__":
    main()
