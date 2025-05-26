import sys
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os # For checking file existence

def main_ingestion_logic():
    print("Starting data ingestion process...")
    documents = []
    source_files = ["reddit_data.txt", "github_data.txt"]
    
    # Check for existence of reddit_data.txt, github_data.txt is optional
    if not os.path.exists("reddit_data.txt"):
        print(f"Error: Required data file 'reddit_data.txt' not found.")
        # No need to sys.exit(1) here, will be caught by the FileNotFoundError in the loop or handled by main try-except
        raise FileNotFoundError("reddit_data.txt not found, which is required for ingestion.")

    print(f"Loading documents from: {', '.join(source_files)}")
    for file_path in source_files:
        if os.path.exists(file_path): # Only load if file exists
            print(f"Loading {file_path}...")
            try:
                loader = TextLoader(file_path, encoding='utf-8') # Added encoding
                documents.extend(loader.load())
                print(f"Successfully loaded {file_path}.")
            except Exception as e: # Catch errors during loading of a specific file
                print(f"Error loading or processing file {file_path}: {e}")
                # Depending on policy, you might want to raise e to stop all ingestion
                # or just skip this file. For now, we'll let it be caught by the main handler if critical.
                # If reddit_data.txt fails, it's critical. If github_data.txt fails, maybe less so.
                if file_path == "reddit_data.txt":
                    raise # Re-raise if critical file fails
                else:
                    print(f"Skipping optional file {file_path} due to error.")
        else:
            if file_path == "reddit_data.txt": 
                # This case should have been caught above, but as a safeguard:
                print(f"Critical Error: {file_path} was not found during loading phase.")
                raise FileNotFoundError(f"{file_path} not found during loading phase.")
            else:
                print(f"Optional file {file_path} not found, skipping.")

    if not documents:
        print("No documents were loaded. Nothing to ingest. This might be due to missing source files or errors during loading.")
        # Consider this a failure if reddit_data.txt was expected and nothing loaded.
        # If reddit_data.txt was found and loaded but was empty, docs might be empty.
        # If only github_data.txt was optional and missing, this could be acceptable.
        # For now, if no documents at all, it's an issue.
        raise ValueError("No documents loaded for ingestion. Check source files and logs.")

    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print(f"Successfully split documents into {len(docs)} chunks.")

    print("Creating embeddings using 'sentence-transformers/all-MiniLM-L6-v2'...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Embeddings model loaded.")

    print("Storing document chunks and embeddings in ChromaDB (persist_directory='./chroma_db')...")
    # This operation can take some time.
    Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
    print("Successfully stored documents in ChromaDB.")

if __name__ == "__main__":
    try:
        main_ingestion_logic()
        print("ingest.py executed successfully.")
        sys.exit(0)
    except FileNotFoundError as e:
        # Specific handling for FileNotFoundError if main_ingestion_logic raises it for critical files
        print(f"Error: A required file was not found. Details: {e}")
        sys.exit(1)
    except ValueError as e:
        # Handling for ValueError, e.g. "No documents loaded"
        print(f"Error: A value error occurred during ingestion. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred in ingest.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)