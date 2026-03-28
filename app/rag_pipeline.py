import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)

def ingest_pdfs(uploaded_files):
    """Take a list of Streamlit uploaded files, return a FAISS vectorstore"""
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)

    for uf in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uf.read())
            tmp_path = tmp.name
        try:
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            chunks = splitter.split_documents(pages)
            all_docs.extend(chunks)
        finally:
            os.unlink(tmp_path)

    if not all_docs:
        return None

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(all_docs, embeddings)
    return vectorstore

def retrieve_context(vectorstore, query, k=4):
    """Return top-k relevant chunks as a single string"""
    if vectorstore is None:
        return ""
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([d.page_content for d in docs])
