import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage, HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv


load_dotenv()
embeddings = OpenAIEmbeddings()
# Directory for storing PDFs and FAISS index
UPLOAD_FOLDER = 'teacher_pdfs'
INDEX_PATH = "faiss_index"

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
    - If the question relates to information not covered in the PDFs, politely inform the user that the required information is not available in the uploaded documents.
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
        combine_docs_chain_kwargs={'prompt': prompt},
        verbose=True
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
    if uploaded_files_list:
        st.write("Uploaded PDF Files:")
        for file in uploaded_files_list:
            st.write(file)
    
    # Button to delete all uploaded PDFs
    if st.button("Delete All PDFs"):
        for file in uploaded_files_list:
            os.remove(os.path.join(UPLOAD_FOLDER, file))
        st.success("All PDFs have been deleted successfully!")

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

        if user_question:
            st.session_state.chat_history.append(HumanMessage(content=user_question))
            with st.chat_message("Human"):
                st.markdown(user_question)

            # Get the AI's response based on the uploaded PDFs
            response = chain.run(question=user_question,context=vector_store, chat_history=st.session_state.chat_history)
            st.session_state.chat_history.append(AIMessage(content=response))

            with st.chat_message("AI"):
                st.info(response)
    else:
        st.warning("No documents have been uploaded by the teacher yet.")

# Main function to control the flow
def main():
    handle_login()

    # Show appropriate dashboard based on role
    if st.session_state.logged_in:
        if st.session_state.role == "teacher":
            teacher_dashboard()
        elif st.session_state.role == "student":
            student_dashboard()

if __name__ == "__main__":
    main()
