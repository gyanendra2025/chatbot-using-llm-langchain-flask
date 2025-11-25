from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

def load_pdf_files(data):
    return DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader).load()

def filter_to_minimal_docs(docs):
    return [Document(page_content=doc.page_content, metadata={"source": doc.metadata.get("source")}) for doc in docs]

def text_split(minimal_docs):
    return RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    ).split_documents(minimal_docs)

def download_hugging_face_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
