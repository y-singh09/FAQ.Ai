from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
import streamlit as st
from langchain_ibm import WatsonxLLM
import os

# Setup the credentials
creds = {
    "api_key": "txvo6Pf_tn6TRh6j6SPpwohUbqxd0yLGVte8BBA4oRTM",
    "api_url": "https://eu-de.ml.cloud.ibm.com"
}

# Create the LLM using WatsonxLLM
llm = WatsonxLLM(
    model="ibm/granite-13b-chat-v2",
    params={
        "decoding_method": "sample",
        "max_new_tokens": 200,
        "temperature": 0.5
    },
    project_id="4e4cb703-076b-4b88-ad56-1759197c7d43",
    url=creds["api_url"],
    apikey=creds["api_key"]
)

# Streamlit app title
st.title("Ask Watsonx")

# Hardcoded PDF file path
pdf_path = "/workspaces/FAQ.Ai/AnswersNewComer.pdf"

# Load the PDF and create index
@st.cache_resource
def load_pdf(path):
    loaders = [PyPDFLoader(path)]
    index = VectorstoreIndexCreator(
        vectorstore_cls=Chroma,
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
        embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")
    ).from_loaders(loaders)
    return index

# Initialize index if path is valid
index = None
if os.path.exists(pdf_path):
    index = load_pdf(pdf_path)
else:
    st.error("The specified file path does not exist.")

# Setup the session state to store old messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the chat messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# Build the prompt input
prompt = st.text_input("Enter the question you want to ask Watsonx")

# If the user submits a prompt
if prompt and index:
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=index.vectorstore.as_retriever(),
        input_key="question"
    )
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = qa_chain.run(prompt)
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
elif prompt and not index:
    st.warning("PDF file could not be loaded. Please check the file path.")
