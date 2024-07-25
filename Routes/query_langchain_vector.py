import logging
import os
from typing import List
from Libs.DB import KV_Store
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma

# Setup logging
logging.basicConfig(level=logging.INFO)


def get_base_folder_hash():
    out = {}
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            out[file] = os.stat(os.path.join(root, file)).st_mtime

    # sha256 hash
    import hashlib

    out_hash = hashlib.sha256(str(out).encode()).hexdigest()
    return out_out


# Build prompt
llm = ChatOllama(
    model=os.getenv("langchain_vector_model"),
    temperature=0.9,
    num_ctx=16000,
)
kvstore = KV_Store()
base_dir = os.getenv("vector_document_dir")
os.makedirs(base_dir, exist_ok=True)

embedding_function = OllamaEmbeddings()
old_base_folder_hash = kvstore.get("base_folder_hash")
base_folder_hash = get_base_folder_hash()
if base_folder_hash is None or old_base_folder_hash != base_folder_hash:
    kvstore.set("base_folder_hash", base_folder_hash)
    if os.path.exists("./chroma_db"):
        os.unlink("./chroma_db")
    logging.info("Files Changed, Creating new Chroma database (this may take a while)")
    # List all files in the directory that are PDFs
    files = []
    allowed_ext = [".pdf", ".txt"]
    # recursive on base_dir
    for root, dirs, file in os.walk(base_dir):
        for f in file:
            if any([f.lower().endswith(ext) for ext in allowed_ext]):
                files.append(os.path.join(root, f))
    logging.info(f"Processing files: {files}")

    # List to store all documents (each page of each PDF as a separate document)
    docs = []
    filename_partial_filter = "xilar"
    # Process each PDF file
    for file_path in files:
        try:
            if filename_partial_filter not in file_path:
                continue
            if file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.lower().endswith(".txt"):
                loader = TextLoader(file_path)
            pages = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=150
            )
            pages = text_splitter.split_documents(pages)
            # Append each page to the docs list
            docs.extend(pages)
            logging.info(f"Added {len(pages)} pages from {file_path}")
        except Exception as e:
            logging.error(f"Failed to process file {file_path}. Error: {str(e)}")

    # Now docs contains all pages from all PDFs as separate documents
    logging.info(f"Total documents to Embed: {len(docs)}")
    logging.info(f"EMBEDDING UNDERWAY, PLEASE WAIT")
    vectordb = Chroma.from_documents(
        documents=docs, embedding=embedding_function, persist_directory="./chroma_db"
    )
    logging.info(
        f"Created Chroma database with {vectordb._collection.count()} documents"
    )
else:
    vectordb = Chroma(
        persist_directory="./chroma_db", embedding_function=embedding_function
    )
    logging.info(f"Loaded {vectordb._collection.count()} existing Chroma database")


def register_routes(app):
    @app.post("/langchain/query_vector", tags=["langchain"])
    def query_langchain_vector(question: str, temperature: float = 0.9):
        app.logger.info(f"Received query: {question}")
        template = """Use the following pieces of context to answer the question 
        at the end. If you don't know the answer, just say that you don't know, 
        don't try to make up an answer. Use three sentences maximum. 
        Keep the answer as concise as possible. 
        
        {context}
        Question: {question}
        Helpful Answer:"""
        QA_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question"], template=template
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vectordb.as_retriever(
                search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        )

        try:
            result = qa_chain.invoke({"query": question})
            app.logger.info(f"Result: {result}")
            return result["result"]
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return {"error": "Failed to process your query due to an internal error."}
