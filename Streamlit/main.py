import os
import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths and settings
PDF_FOLDER = './pdfs'
index_path = "faiss_index"  # Path for saving FAISS index

# Load OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Sample usernames and passwords for student and teacher
sample_users = {
    "student": {"username": "student123", "password": "studentpass"},
    "teacher": {"username": "teacher123", "password": "teacherpass"},
}

# Streamlit page configuration
st.set_page_config(page_title="EduQueryAI - Real-Time Student Support", page_icon='📚')

# Check if the session state for user role is already set, if not, default to None
if 'role' not in st.session_state:
    st.session_state['role'] = None

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Login page for student/teacher
def login_page():
    if not st.session_state['logged_in']:  # Only show login page if not logged in
        st.header("Login to EduQueryAI")
        role = st.radio("Choose your role", ["Student", "Teacher"])
        username = st.text_input("Enter your Username")
        password = st.text_input("Enter your Password", type="password")
        
        if st.button("Login"):
            if username and password:
                if validate_credentials(role, username, password):
                    st.session_state['role'] = role.lower()
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username  # Save username to session state
                    st.experimental_rerun()  # Rerun the script to show the dashboard
                else:
                    st.error("Invalid username or password.")
            else:
                st.error("Please enter both username and password.")
    else:
        if st.session_state['role'] == 'student':
            student_dashboard()
        elif st.session_state['role'] == 'teacher':
            teacher_dashboard()

# Validate credentials
def validate_credentials(role, username, password):
    if role.lower() == "student":
        return sample_users["student"]["username"] == username and sample_users["student"]["password"] == password
    elif role.lower() == "teacher":
        return sample_users["teacher"]["username"] == username and sample_users["teacher"]["password"] == password
    return False

# Teacher dashboard
def teacher_dashboard():
    st.sidebar.title("Teacher Dashboard")
    st.sidebar.button("Logout", on_click=logout)
    
    st.header("Teacher Dashboard")
    st.write("Coming Soon! Teacher's page under construction.")
    
    # Future features like query management, uploading course material, etc.
    # Placeholder content for Teacher role

# Student dashboard
def student_dashboard():
    st.sidebar.title("Student Dashboard")
    st.sidebar.button("Logout", on_click=logout)
    
    st.header("Student Dashboard")
    
    # Display chat history from session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            AIMessage(content="Hello there👋, I can help you with your PDFs. Upload any PDF and we can chat.")
        ]
    
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message('AI'):
                st.info(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    # User input section for asking questions
    user_question = st.chat_input("Ask me anything about the course material!")
    if user_question:
        st.session_state.chat_history.append(HumanMessage(content=user_question))

        with st.chat_message("Human"):
            st.markdown(user_question)

        # Get AI response based on user's question
        response, context = user_input(user_question)

        with st.chat_message("AI"):
            st.write(response)

        # Save AI's response in the chat history
        st.session_state.chat_history.append(AIMessage(content=response))

# Function to handle user input and get a response
def user_input(user_question):
    # Load existing knowledge base or create a new one
    if os.path.exists(index_path):
        new_db = FAISS.load_local(index_path, embeddings=embeddings, allow_dangerous_deserialization=True)
    else:
        st.warning("No knowledge base found. Creating one from uploaded PDFs...")
        create_faiss_index()
        new_db = FAISS.load_local(index_path, embeddings=embeddings, allow_dangerous_deserialization=True)

    # Search for relevant documents based on the user's question
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain(new_db)

    context_text = " ".join([doc.page_content for doc in docs])

    # Get AI response based on the question and context
    result = chain.invoke({
        "question": user_question,
        'context': docs,
        "chat_history": '',
    })

    return result['answer'], context_text

# Function to create FAISS index from uploaded PDFs
def create_faiss_index():
    # Handle PDF upload and text extraction
    pdf_docs = st.file_uploader(
        "Upload your PDF File(s) and Click on the Submit & Process Button",
        type="pdf", accept_multiple_files=True
    )
    if st.button("Submit & Process"):
        if pdf_docs:
            with st.spinner("Processing PDFs..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vector_store = FAISS.from_texts(text_chunks, embeddings)
                vector_store.save_local(index_path)
                st.success("Knowledge base created successfully!")
        else:
            st.warning("Please upload at least one PDF file.")

# Function to extract text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(raw_text):
    chunk_size = 200
    chunk_overlap = 100
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_text(raw_text)

# Function to return the Conversational Retrieval Chain
def get_conversational_chain(vectorstore):
    prompt_template = """
    System: You are an expert on networking topics, and your task is to answer the user's questions strictly based on the information provided in the uploaded PDF documents. Here are your guidelines:

    - Use only the information from the user's uploaded PDF documents to determine the answer.
    - If the correct answer is not directly available in the provided information, respond with 'This will be answered by the Teacher.'
    - Keep your response concise and relevant to the user's question.

    Context from Documents:
    {context}

    User: {question}

    Assistant: 
    """
    prompt = PromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(model="gpt-4")  # Specify the LLM model you want to use (can be gpt-3.5 or gpt-4)
    return ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever(), verbose=True)

# Logout function
def logout():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    st.experimental_rerun()  # Rerun the app to show the login page

# Main function to display login page or dashboard
login_page()
