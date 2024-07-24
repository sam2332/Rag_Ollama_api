import logging
import os
from typing import List

from langchain_ollama import ChatOllama
from typing_extensions import TypedDict

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Setup logging
logging.basicConfig(level=logging.INFO)

# Build prompt
llm = ChatOllama(
    model=os.getenv("tool_model"),
    temperature=0.3,
    num_ctx=4096,
)

base_dir = os.getenv("vector_document_dir")
os.makedirs(base_dir, exist_ok=True)

# List all files in the directory that are PDFs
files = []
# recursive on base_dir
for root, dirs, file in os.walk(base_dir):
    for f in file:
        if f.lower().endswith(".pdf"):
            files.append(os.path.join(root, f))
logging.info(f"Processing files: {files}")

# List to store all documents (each page of each PDF as a separate document)
docs = []

# Process each PDF file
for file_path in files:
    try:
        loader = PyPDFLoader(file_path)
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
logging.info(f"Total documents processed: {len(docs)}")

logging.info(f"Type: {type(docs[0])}")

embeddings = OllamaEmbeddings()
vectordb = Chroma.from_documents(docs, embeddings)


def register_routes(app):
    @app.get("/langchain/query_vector", tags=["langchain"])
    def query_langchain_vector(question: str):
        app.logger.info(f"Received query: {question}")
        template = """Use the following pieces of context to answer the question 
        at the end. If you don't know the answer, just say that you don't know, 
        don't try to make up an answer. Use three sentences maximum. 
        Keep the answer as concise as possible. Always say "thanks for asking!" 
        at the end of the answer. 
        {context}
        Question: {question}
        Helpful Answer:"""
        QA_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question"], template=template
        )

        try:
            from langchain.chains import RetrievalQA

            qa_chain = RetrievalQA.from_chain_type(
                llm,
                retriever=vectordb.as_retriever(),
                return_source_documents=True,
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
            )

            result = qa_chain.invoke({"query": question})
            app.logger.info(f"Result: {result}")
            return result["result"]
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return {"error": "Failed to process your query due to an internal error."}
