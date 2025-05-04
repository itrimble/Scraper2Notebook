import streamlit as st
from streamlit_chat import message
from converse import Converse
from tinydb import TinyDB
import time
import ollama
import logging

# Set up logging
logging.basicConfig(filename='query_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Cache retrieval results for faster repeated queries
@st.cache_data
def cached_similarity_search(query):
    conversation = Converse()
    docs = conversation.retriever.invoke(query)
    return docs

# Cache the model list to avoid repeated calls to ollama.list()
@st.cache_data
def get_available_models():
    try:
        ollama_response = ollama.list()
        print("Debug: Ollama list response:", ollama_response)
        # Access the 'model' attribute instead of 'name'
        available_models = [model.model for model in ollama_response.get('models', [])]
        # Filter out embedding models (e.g., mxbai-embed-large)
        model_options = [model for model in available_models if not model.startswith('mxbai-embed')]
        if not model_options:
            raise ValueError("No valid models found in Ollama response")
    except Exception as e:
        # Only print the error the first time
        if "error_printed" not in st.session_state:
            print(f"Error fetching models from Ollama: {e}")
            st.session_state["error_printed"] = True
        model_options = ["llama3:8b", "llama3:8b-q4_0", "qwen2.5:1.5b"]  # Fallback list
    return model_options

db = TinyDB('db.json')
agent_table = db.table('agent')

# Ensure agent_table has at least one entry
if not agent_table.all():
    print("Debug: Inserting default entry.")
    agent_table.insert({
        "model": "llama3:8b",
        "system_message": "You are a helpful assistant with access to a knowledge base of scraped data from r/RooCode and related GitHub repositories.",
        "user_name": "User",
        "agent_name": "RooCode Assistant"
    })

# Fetch available models
model_options = get_available_models()

# Add a refresh button for the model list
if st.button("Refresh Models"):
    st.cache_data.clear()  # Clear all cached data, including get_available_models
    st.rerun()

# Model selection dropdown
st.title("RooCode Data Query")
selected_model = st.selectbox("Select model:", model_options, index=0)
st.write(f"Using model: {selected_model}")

# Update agent_table with the selected model
agent_table.truncate()
agent_table.insert({
    "model": selected_model,
    "system_message": "You are a helpful assistant with access to a knowledge base of scraped data from r/RooCode and related GitHub repositories.",
    "user_name": "User",
    "agent_name": "RooCode Assistant"
})

agent_table_rows = agent_table.all()
if not agent_table_rows:
    st.error("Failed to initialize the agent table. Please check the database setup.")
    st.stop()

agent_table_row = agent_table_rows[0]
user_name = agent_table_row["user_name"]
agent_name = agent_table_row["agent_name"]

if "messages" not in st.session_state:
    st.session_state["messages"] = []
query = st.text_input("Ask about RooCode or the GitHub repos:")
if query:
    with st.spinner("Generating response..."):
        start_time = time.time()
        try:
            conversation = Converse()
            docs = cached_similarity_search(query)
            context = docs[0].page_content[:1000] if docs else "No relevant context found."
            response = conversation.chat(f"Context: {context}\nQuestion: {query}", agent_table_row)
        except Exception as e:
            response = f"Error processing query: {str(e)}"
        end_time = time.time()
        # Log the query and response
        logging.info(f"Query: {query} | Response: {response} | Time: {end_time - start_time:.2f}s")
        st.session_state.messages.append({"message": query, "is_user": True})
        st.session_state.messages.append({"message": response, "is_user": False})
        st.write(f"Response time: {end_time - start_time:.2f} seconds")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.rerun()

for i, msg in enumerate(st.session_state.messages):
    message(msg["message"], is_user=msg["is_user"], key=str(i))