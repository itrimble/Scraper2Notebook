from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load documents
documents = []
for file in ["reddit_data.txt", "github_data.txt"]:
    loader = TextLoader(file)
    documents.extend(loader.load())

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# Create embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Store in Chroma
Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")