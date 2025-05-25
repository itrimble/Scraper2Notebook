import streamlit as st
from streamlit_chat import message # Assuming this is still the chat component
from converse import Converse
from tinydb import TinyDB
import time
import ollama
import logging

# --- Page Configuration (Dark Theme & Layout) ---
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="RooCode Data Query",
    theme="dark" # Explicitly set Streamlit's dark theme
)

# --- Custom CSS Injection ---
st.markdown("""
<style>
    /* Base Dark Theme Adjustments (if needed beyond Streamlit's default) */
    body {
        color: #FAFAFA; /* Ensure text is light on dark backgrounds */
    }
    .main {
        background-color: #0E1117; /* Dark background for the main content area */
    }
    .stApp { /* Target the root Streamlit app container */
        background-color: #0E1117;
    }

    /* Sidebar Styling */
    .st-emotion-cache-10oheav { /* Specific selector for sidebar background, may change with Streamlit versions */
        background-color: #1E232E !important; /* Darker sidebar */
    }
    .st-emotion-cache-10oheav .stButton > button { /* Sidebar buttons */
        background-color: #4A5568; /* A medium dark shade for buttons */
        color: #FAFAFA;
        border-radius: 5px;
        border: 1px solid #2D3748; /* Subtle border */
        margin-bottom: 10px; /* Spacing between buttons */
        width: 100%; /* Make buttons fill sidebar width */
    }
    .st-emotion-cache-10oheav .stButton > button:hover {
        background-color: #2D3748;
        color: #E2E8F0;
    }
    .st-emotion-cache-10oheav .stSelectbox > div > div { /* Sidebar selectbox */
        background-color: #2D3748; /* Background for selectbox */
        color: #FAFAFA;
        border-radius: 5px;
    }
     .st-emotion-cache-10oheav label { /* Sidebar labels */
        color: #A0AEC0 !important; /* Lighter grey for labels */
    }


    /* Chat Message Styling */
    /* Note: streamlit_chat might render HTML that needs specific targeting.
       These are common patterns. If they don't work, browser dev tools would be needed to find actual classes.
       The `message` function from `streamlit_chat` generates divs with classes like `stChatMessage` or similar,
       and often uses inline styles for user/avatar distinction. We'll try to override.
    */
    .stChatMessage {
        background-color: #1E232E; /* Default dark bubble color */
        color: #FAFAFA;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid #2D3748;
        width: fit-content;
        max-width: 70%; /* Max width for bubbles */
    }

    /* User messages (assuming is_user=True adds some specific attribute or class, or uses inline style) */
    /* We'll try to target based on the structure streamlit_chat usually creates.
       It often puts user messages on the right. The `message` function's `is_user` flag
       results in different styling, often inline.
       A common pattern is that user messages are aligned to the right.
       If `streamlit_chat` uses specific classes like `user-message` or `ai-message`, those would be better.
       Let's assume `is_user=True` results in a container that can be selected.
       The library itself adds styling. We'll try to make it more distinct.
    */
    div[data-testid="stChatMessageContent"] > div[style*="text-align: right;"] > div { /* User messages (right-aligned by streamlit-chat) */
        background-color: #2b313e !important; /* Darker blue/grey for user */
        border-radius: 10px !important;
        padding: 12px !important;
        margin-left: auto; /* Align to right */
        margin-right: 0;
    }

    div[data-testid="stChatMessageContent"] > div[style*="text-align: left;"] > div { /* AI messages (left-aligned by streamlit-chat) */
        background-color: #222831 !important; /* Slightly different dark shade for AI */
        border-radius: 10px !important;
        padding: 12px !important;
        margin-left: 0;
        margin-right: auto; /* Align to left */
    }


    /* Main Text Input Area */
    .stTextInput > div > div > input {
        background-color: #1A202C; /* Dark input background */
        color: #FAFAFA;
        border: 1px solid #4A5568; /* Subtle border */
        border-radius: 5px;
        padding: 10px;
    }
    .stTextInput > label {
        color: #A0AEC0 !important; /* Lighter grey for input label */
    }

    /* Response Time Styling */
    .stText[data-testid="stText"] { /* Attempt to target the response time text */
        font-size: 0.85em;
        color: #A0AEC0; /* Lighter grey, less prominent */
        text-align: right; /* Align to the right if desired */
        margin-top: -10px; /* Adjust spacing */
    }

    /* Title styling */
    .stTitle {
        color: #E2E8F0; /* Light color for title */
    }

</style>
""", unsafe_allow_html=True)


# Set up logging
logging.basicConfig(filename='query_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Cache retrieval results for faster repeated queries
@st.cache_data
def cached_similarity_search(query):
    conversation = Converse()
    docs = conversation.retriever.invoke(query)
    return docs

# Cache the model list to avoid repeated calls to ollama.list()
@st.cache_data(show_spinner=False) # Hide spinner for this cache
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

# --- Database Initialization ---
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

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Controls")
    # Fetch available models
    model_options = get_available_models()

    # Add a refresh button for the model list
    if st.button("Refresh Models"):
        st.cache_data.clear()  # Clear all cached data, including get_available_models
        st.rerun()

    # Model selection dropdown
    selected_model = st.selectbox("Select model:", model_options, index=model_options.index(agent_table.all()[0]['model']) if agent_table.all() and agent_table.all()[0]['model'] in model_options else 0)
    st.write(f"Using model: `{selected_model}`") # Using markdown for slight emphasis

    # Add a clear chat button
    if st.button("Clear Chat"):
        st.session_state["messages"] = []
        st.rerun()

    st.markdown("---") # Separator
    st.markdown("Built by RooCode")


# --- Main Page Layout ---
st.title("RooCode Data Query")

# Update agent_table with the selected model if it has changed
current_db_model = agent_table.all()[0]['model'] if agent_table.all() else None
if selected_model != current_db_model:
    agent_table.truncate() # Clear existing entries
    agent_table.insert({
        "model": selected_model,
        "system_message": "You are a helpful assistant with access to a knowledge base of scraped data from r/RooCode and related GitHub repositories.",
        "user_name": "User", # These could also be made configurable if needed
        "agent_name": "RooCode Assistant"
    })
    # Clear chat history if model changes, as context might not be relevant
    st.session_state["messages"] = []


agent_table_rows = agent_table.all()
if not agent_table_rows:
    st.error("Failed to initialize the agent table. Please check the database setup.")
    st.stop()

agent_table_row = agent_table_rows[0]
# user_name = agent_table_row["user_name"] # Not explicitly used in chat message display by streamlit_chat
# agent_name = agent_table_row["agent_name"] # Not explicitly used

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages from history
# The streamlit_chat library handles the display. We've styled .stChatMessage above.
# The key is important for Streamlit to correctly track elements.
for i, msg_data in enumerate(st.session_state.messages):
    message(msg_data["message"], is_user=msg_data["is_user"], key=f"msg_{i}")


# Chat input
query = st.text_input("Ask about RooCode or the GitHub repos:", key="chat_input")

if query:
    st.session_state.messages.append({"message": query, "is_user": True})
    # Display the user's message immediately
    message(query, is_user=True, key=f"msg_{len(st.session_state.messages)}_user")

    with st.spinner("Generating response..."):
        start_time = time.time()
        try:
            conversation = Converse()
            # Use the selected model for the conversation
            current_agent_config = agent_table.all()[0] # Get the latest config
            
            docs = cached_similarity_search(query) # RAG retrieval
            context = ""
            if docs: # Check if docs is not None and not empty
                # Concatenate content from multiple relevant documents if available
                context_parts = [doc.page_content for doc in docs[:2]] # Use top 2 docs for context
                context = "\n---\n".join(context_parts)
                context = context[:3000] # Limit context size
            else:
                context = "No relevant context found."

            response = conversation.chat(f"Context: {context}\nQuestion: {query}", current_agent_config)
        except Exception as e:
            response = f"Error processing query: {str(e)}"
            logging.error(f"Error processing query '{query}': {e}")
        end_time = time.time()

        # Log the query and response
        logging.info(f"Query: {query} | Response: {response} | Time: {end_time - start_time:.2f}s | Model: {selected_model}")
        
        st.session_state.messages.append({"message": response, "is_user": False})
        # Display AI's message
        message(response, is_user=False, key=f"msg_{len(st.session_state.messages)}_ai")
        
        # Display response time (styled via CSS)
        st.text(f"Response time: {end_time - start_time:.2f} seconds")
        
        # Rerun to clear the input box and update message display smoothly
        st.rerun()