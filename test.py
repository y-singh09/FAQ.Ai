from langchain.document_loaders import PyPdfLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import huggingfaceEmbeddings
from langchain.chains import RetrievalQA


# streamlit ui
import streamlit as st

# watsonX interface
from langchain_ibm import WatsonxLLM

#setup the credentials
creds = {
    "api_key": "ZyI97fL0tvNju2Pe2v4iWnE0xo3n3CKDC2V1pYgxA5On",
    "api_url": "https://eu-de.ml.cloud.ibm.com"
}

#create the llm using the langchain
llm = WatsonxLLM(
    model="meta-llama/Llama-2-70b-chat",
    params={
        "decoding_method": "sample",
        "max_new_tokens": 200,
        "temperature": 0.5
    },
    project_id="51a6613d-b886-4c96-a641-c161049bfaae"
)

# load the pdf file
@st.cache_resource
def load_pdf():
    #update the pdf name here
    pdf_name = "what is gen ai.pdf" 
    loaders = [PyPdfLoader(pdf_name)]

    #create the index/ vector database / chromadb
    index = VectorstoreIndexCreator(
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
        embedding=huggingfaceEmbeddings(model_name="all-MiniLM-L12-v2")
    ).from_loaders(loaders)

# return the vector database
    return index

# loader er on up
index = load_pdf()

# create the q&a chain
qa_chain = RetrievalQA.from_chain_type( 
    llm=llm,
    chain_type="stuff",
    retriever=index.vectorstore.as_retriever(), 
    input_key="question",
)

#setup the app title
st.title("ask watsonX")

#setup the session state to store the old messages
if "messages" not in st.session_state:
    st.session_state.messages = []

#display the chat messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

#Build the prompt input
prompt = st.text_input("enter the question you want to ask watsonX")

#if the user hit the enter key
if prompt:
    # display the prompt
    st.chat_message("user").markdown(prompt)

    # store the prompt in the session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # send the prompt to llm
    response = qa_chain.run(prompt)

    # show the llm response
    st.chat_message("assistant").markdown(response)

    # store the llm response in the session state
    st.session_state.messages.append({"role": "assistant", "content": response})