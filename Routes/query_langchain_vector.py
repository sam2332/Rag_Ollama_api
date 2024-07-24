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

files = [str(os.path.join(base_dir, f)) for f in os.listdir(base_dir)]
logging.info(f"Processing files: {files}")

try:
    loader = UnstructuredFileLoader(files)
    documents = loader.load()
except Exception as e:
    logging.error(f"Error loading documents: {e}")
    raise

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(documents)

embeddings = OllamaEmbeddings()
vectordb = Chroma.from_documents(docs, embeddings)


def register_routes(app):
    @app.get("/langchain/query_vector", tags=["langchain"])
    def query_langchain_vector(question: str):
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

            result = qa_chain({"query": question})
            return result["result"]
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return {"error": "Failed to process your query due to an internal error."}
