from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain_groq import ChatGroq  # ✅ New import
 
import streamlit as st
import os
 
# Set your Groq API key
# os.environ["GROQ_API_KEY"] = ""
 
# Create the LLM using Groq
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # or another supported model
    temperature=0.5,
    max_tokens=200
)
 
# Load the PDF file
@st.cache_resource
def load_pdf():
    pdf_name = "AnswersNewComer.pdf"
    loaders = [PyPDFLoader(pdf_name)]
 
    index = VectorstoreIndexCreator(
        vectorstore_cls=Chroma,
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
        embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")
    ).from_loaders(loaders)
 
    return index
 
index = load_pdf()
 
# Create the Q&A chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=index.vectorstore.as_retriever(),
    input_key="question",
)
 
# Streamlit UI
st.title("Ask Groq LLM")
 
if "messages" not in st.session_state:
    st.session_state.messages = []
 
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])
 
prompt = st.text_input("Enter your question for Groq")
 
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
 
    response = qa_chain.run(prompt)
 
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})