import os
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Setup paths and embeddings
INDEX_PATH = "./faiss_index"
UPLOAD_FOLDER = './teacher_pdfs'
embeddings = OpenAIEmbeddings()

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check if the vector index already exists
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
    vector_store = FAISS.from_texts(text_chunks, embeddings)
    vector_store.save_local(INDEX_PATH)

# Function to create a conversational retrieval chain
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

# Function to process question and get an answer
def process_question(question, uuploaded_pdfs = ["teacher_pdfs/chapter4.pdf", "teacher_pdfs/chapter5.pdf"] ):
    # Extract text from PDFs and create a vector store if necessary
    if check_existing_index(INDEX_PATH):
        # Load existing vector store
        vector_store = FAISS.load_local(INDEX_PATH, embeddings=embeddings, allow_dangerous_deserialization=True)
    else:
        # Process the uploaded PDFs
        raw_text = get_pdf_text(uploaded_pdfs)
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)
        vector_store = FAISS.load_local(INDEX_PATH, embeddings=embeddings, allow_dangerous_deserialization=True)

    # Create the conversational retrieval chain
    chain = get_conversational_chain(vector_store)

    # Initialize chat history
    chat_history = []

    # Run the chain to get the answer
    response = chain.run(question=question, context=vector_store, chat_history=chat_history)

    return response

# Example usage of the process_question function
if __name__ == "__main__":
    # Example question and PDF files
    uploaded_pdfs = ["teacher_pdfs/chapter4.pdf", "teacher_pdfs/chapter5.pdf"]  # Replace with actual PDF file paths
    question = "What is the main topic of the document?"

    # Get the answer to the question
    answer = process_question(question, uploaded_pdfs)
    print(answer)
