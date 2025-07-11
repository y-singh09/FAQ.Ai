from langchain.document_loaders import PyPdfLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import HuggingFaceEmbeddings   # corrected class name
from langchain.chains import RetrievalQA

import streamlit as st

from langchain_ibm import WatsonxLLM

# Setup credentials for IBM watsonX
creds = {
    "api_key": "ZyI97fL0tvNju2Pe2v4iWnE0xo3n3CKDC2V1pYgxA5On",
    "api_url": "https://eu-de.ml.cloud.ibm.com"
}

# Create the LLM using langchain
llm = WatsonxLLM(
    model="meta-llama/Llama-2-70b-chat",
    params={
        "decoding_method": "sample",
        "max_new_tokens": 200,
        "temperature": 0.5
    },
    project_id="51a6613d-b886-4c96-a641-c161049bfaae"
)

# Load and index the PDF
@st.cache_resource
def load_pdf():
    pdf_name = "what is gen ai.pdf"  # Ensure this file exists!
    loaders = [PyPdfLoader(pdf_name)]

    # Create the index/vector database
    index = VectorstoreIndexCreator(
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
        embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")   # corrected class name
    ).from_loaders(loaders)

    return index

index = load_pdf()

# Create the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=index.vectorstore.as_retriever(),
    input_key="question",
)

# Streamlit UI setup
st.title("Ask watsonX")

# Store chat messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# Prompt input
prompt = st.text_input("Enter the question you want to ask watsonX")

# On user prompt
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Run the QA chain
    try:
        response = qa_chain.run(prompt)
    except Exception as e:
        response = f"Error: {e}"

    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
