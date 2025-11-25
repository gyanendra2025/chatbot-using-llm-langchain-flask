from dotenv import load_dotenv
import os
from src.helpers import load_pdf_files, filter_to_minimal_docs, text_split, download_hugging_face_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

if __name__ == '__main__':
    load_dotenv()
    if not (key := os.environ.get('PINECONE_API_KEY')): raise EnvironmentError("Missing PINECONE_API_KEY")
    
    pc = Pinecone(api_key=key)
    index_name = "medical-chatbot"
    
    if not pc.has_index(index_name):
        pc.create_index(index_name, dimension=384, metric="cosine", spec=ServerlessSpec("aws", "us-east-1"))
        
    PineconeVectorStore.from_documents(
        documents=text_split(filter_to_minimal_docs(load_pdf_files('data/'))),
        index_name=index_name,
        embedding=download_hugging_face_embeddings()
    )
    print("Vector store created.")
