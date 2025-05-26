import streamlit as st
from streamlit_chat import message # Assuming this is still the chat component
from converse import Converse
from tinydb import TinyDB
import time
import ollama
import logging
import json # Added
import os   # Added
import subprocess # Added
import datetime   # Added
import sys        # Added

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

# --- Reddit Configuration Loading ---
REDDIT_CONFIG_FILE = "reddit.config.json"
DEFAULT_REDDIT_CONFIG = {"subreddit": "default_subreddit_value", "post_limit": 25}

def load_reddit_config():
    """Loads Reddit scraping configuration from reddit.config.json."""
    if not os.path.exists(REDDIT_CONFIG_FILE):
        st.warning(f"Warning: '{REDDIT_CONFIG_FILE}' not found. Using default Reddit scrape settings.")
        return DEFAULT_REDDIT_CONFIG.copy()
    try:
        with open(REDDIT_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        scrape_config = config.get("scrape_config", {})
        subreddit = scrape_config.get("subreddit")
        post_limit = scrape_config.get("post_limit")

        if not subreddit or not isinstance(subreddit, str):
            st.warning(f"Warning: 'subreddit' missing or invalid in '{REDDIT_CONFIG_FILE}'. Using default.")
            subreddit = DEFAULT_REDDIT_CONFIG["subreddit"]
        
        if not isinstance(post_limit, int) or post_limit <= 0:
            st.warning(f"Warning: 'post_limit' missing or invalid in '{REDDIT_CONFIG_FILE}'. Using default.")
            post_limit = DEFAULT_REDDIT_CONFIG["post_limit"]
            
        loaded_config = {"subreddit": subreddit, "post_limit": post_limit}
        print(f"Debug: Loaded Reddit config: {loaded_config}") # For debugging
        return loaded_config

    except json.JSONDecodeError:
        st.warning(f"Warning: Could not decode JSON from '{REDDIT_CONFIG_FILE}'. Using default Reddit scrape settings.")
        return DEFAULT_REDDIT_CONFIG.copy()
    except Exception as e:
        st.warning(f"Warning: An unexpected error occurred while loading '{REDDIT_CONFIG_FILE}': {e}. Using defaults.")
        return DEFAULT_REDDIT_CONFIG.copy()

def update_reddit_config(new_subreddit, new_post_limit):
    """Updates reddit.config.json with new subreddit and post_limit."""
    try:
        # Read existing config or create a default structure if file doesn't exist or is empty
        if not os.path.exists(REDDIT_CONFIG_FILE):
            # If file doesn't exist, start with a structure that includes 'reddit' and 'scrape_config'
            # This assumes that other parts of reddit.config.json (like API keys) should be preserved if they exist,
            # or would be manually added later if the file is created from scratch here.
            # For robustness, let's assume if the file is missing, we create it with just the scrape_config.
            # A more complete solution might involve prompting user for API keys or having a more complex default.
            # However, scrape_reddit.py expects 'reddit' (API keys) and 'scrape_config'.
            # For this specific update function, we'll focus on updating/creating 'scrape_config'.
            # If the file is missing, it's safer to error out as critical API keys would be missing.
            st.sidebar.error(f"Error: '{REDDIT_CONFIG_FILE}' not found. Cannot save settings.")
            st.sidebar.caption(f"Please ensure the file exists, perhaps by copying from '.example.json' and configuring API keys first.")
            return False
            
        with open(REDDIT_CONFIG_FILE, 'r') as f:
            # Handle empty file by providing a default structure
            content = f.read()
            if not content.strip(): # File is empty or whitespace
                loaded_config_data = {"reddit": {}, "scrape_config": {}} # Basic structure
                st.warning(f"Warning: '{REDDIT_CONFIG_FILE}' was empty. Initializing with basic structure.")
            else:
                loaded_config_data = json.loads(content) # Use json.loads on pre-read content

    except json.JSONDecodeError:
        st.sidebar.error(f"Error: Could not decode JSON from '{REDDIT_CONFIG_FILE}'. Please check its syntax.")
        return False
    except Exception as e: # Catch other read-related errors
        st.sidebar.error(f"Error reading '{REDDIT_CONFIG_FILE}': {e}")
        return False

    # Ensure 'scrape_config' key exists and is a dictionary
    if "scrape_config" not in loaded_config_data or not isinstance(loaded_config_data.get("scrape_config"), dict):
        loaded_config_data["scrape_config"] = {}
        st.info("Info: 'scrape_config' section was missing/invalid; initialized in config.")
    
    # Ensure 'reddit' key exists (for API keys, though not modified here, it's expected by scrape_reddit.py)
    if "reddit" not in loaded_config_data or not isinstance(loaded_config_data.get("reddit"), dict):
        loaded_config_data["reddit"] = {} # Initialize if missing, API keys would need manual entry
        st.warning("Warning: 'reddit' (API keys) section was missing; initialized. API keys need to be configured manually.")


    # Update values
    loaded_config_data["scrape_config"]["subreddit"] = new_subreddit
    loaded_config_data["scrape_config"]["post_limit"] = new_post_limit

    try:
        with open(REDDIT_CONFIG_FILE, "w") as f:
            json.dump(loaded_config_data, f, indent=4)
        return True
    except IOError:
        st.sidebar.error(f"Error: Could not write to '{REDDIT_CONFIG_FILE}'. Check permissions.")
        return False
    except Exception as e: # Catch other write-related errors
        st.sidebar.error(f"Error writing to '{REDDIT_CONFIG_FILE}': {e}")
        return False

# Initialize Reddit config in session state if not already present
if "reddit_config" not in st.session_state:
    st.session_state.reddit_config = load_reddit_config()

# Initialize scrape status in session state if not already present
if "last_scrape_status" not in st.session_state:
    st.session_state.last_scrape_status = "Not run yet."
if "last_ingest_status" not in st.session_state:
    st.session_state.last_ingest_status = "Not run yet."

# --- Vector DB Status Check ---
CHROMA_DB_PATH = "./chroma_db"

def get_vector_db_status():
    """Checks the status of the ChromaDB vector store directory."""
    if os.path.exists(CHROMA_DB_PATH) and os.path.isdir(CHROMA_DB_PATH):
        if len(os.listdir(CHROMA_DB_PATH)) > 0:
            # A more robust check might involve trying to connect
            # or checking for specific ChromaDB files (e.g., *.parquet, *.duckdb)
            # For now, non-empty is a good basic indicator.
            return "Loaded and Populated (basic check)"
        else:
            return "Directory Exists but Appears Empty"
    else:
        return "Not Found or Not Initialized"

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
    
    st.sidebar.divider() # Visual separator

    # Display Current Reddit Scrape Settings
    st.sidebar.subheader("Current Reddit Scrape Settings")
    st.sidebar.text(f"Subreddit: {st.session_state.reddit_config.get('subreddit', 'N/A')}")
    st.sidebar.text(f"Post Limit: {st.session_state.reddit_config.get('post_limit', 'N/A')}")
    # Add a note if defaults are being used.
    if st.session_state.reddit_config["subreddit"] == DEFAULT_REDDIT_CONFIG["subreddit"] or \
       st.session_state.reddit_config["post_limit"] == DEFAULT_REDDIT_CONFIG["post_limit"]:
        st.sidebar.caption("Using default values (config file issue or defaults).")

    st.sidebar.divider()

    # --- Controls to Modify Reddit Scrape Settings ---
    st.sidebar.subheader("Modify Reddit Scrape Settings")

    # Get current values from session state to pre-fill inputs
    current_subreddit = st.session_state.reddit_config.get("subreddit", DEFAULT_REDDIT_CONFIG["subreddit"])
    current_post_limit = st.session_state.reddit_config.get("post_limit", DEFAULT_REDDIT_CONFIG["post_limit"])

    st.sidebar.text_input(
        label="New Subreddit:",
        value=current_subreddit, # Pre-fill with current/default
        key="new_subreddit_input" # Key to access this input's state
    )

    st.sidebar.number_input(
        label="New Post Limit:",
        value=current_post_limit, # Pre-fill with current/default
        min_value=1,
        step=5,
        key="new_post_limit_input" # Key to access this input's state
    )

    if st.session_state.get("save_reddit_settings_button_clicked"): # Use .get for buttons when state is managed
        new_sub = st.session_state.new_subreddit_input
        new_limit = st.session_state.new_post_limit_input

        # Basic validation for inputs before attempting to save
        if not new_sub or not isinstance(new_sub, str) or not new_sub.strip():
            st.sidebar.warning("Subreddit cannot be empty.")
        elif not isinstance(new_limit, int) or new_limit <= 0:
            st.sidebar.warning("Post limit must be a positive number.")
        else:
            success = update_reddit_config(new_sub, new_limit)
            if success:
                st.sidebar.success("Reddit settings saved successfully!")
                # Update session state to reflect the saved settings immediately
                st.session_state.reddit_config["subreddit"] = new_sub
                st.session_state.reddit_config["post_limit"] = new_limit
                # No need to clear individual input keys if we rerun
                st.rerun() # Rerun to update the displayed "Current settings" and pre-fill inputs
            # If not success, update_reddit_config would have shown an error
        # Reset button state after processing
        st.session_state.save_reddit_settings_button_clicked = False


    st.sidebar.divider() # Added for visual separation of sections

    # --- Manual Data Operations ---
    st.sidebar.subheader("Manual Data Operations")

    if st.sidebar.button("Scrape Reddit Data Now", key="scrape_reddit_button_clicked"):
        with st.sidebar.spinner("Scraping Reddit data... Please wait."):
            cmd = [sys.executable, "scrape_reddit.py"]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if process.returncode == 0:
                st.session_state.last_scrape_status = f"{timestamp} - Success"
                # No need for st.sidebar.success here as rerun will update the status display.
                # User can check expander for details.
            else:
                st.session_state.last_scrape_status = f"{timestamp} - Failed (Code: {process.returncode})"
                # No need for st.sidebar.error here.
            
            # Store output for display in expander, regardless of success
            st.session_state.last_scrape_stdout = process.stdout
            st.session_state.last_scrape_stderr = process.stderr
            st.session_state.last_scrape_returncode = process.returncode
        
        # Reset button state
        st.session_state.scrape_reddit_button_clicked = False
        st.rerun() # Force rerun to update status display and expander content

    st.sidebar.markdown(f"**Last Scrape Attempt:**<br>{st.session_state.last_scrape_status}", unsafe_allow_html=True)
    
    # Expander for scrape details - always visible if details exist
    if "last_scrape_returncode" in st.session_state:
        with st.sidebar.expander("Last Scraping Details (Output from scrape_reddit.py)", expanded=False):
            st.text(f"Exit Code: {st.session_state.last_scrape_returncode}")
            st.subheader("Stdout:")
            st.text_area("scrape_stdout", st.session_state.get("last_scrape_stdout", ""), height=150, disabled=True, key="scrape_stdout_area_display") # Changed key
            st.subheader("Stderr:")
            st.text_area("scrape_stderr", st.session_state.get("last_scrape_stderr", ""), height=150, disabled=True, key="scrape_stderr_area_display") # Changed key

    # --- Ingest Data Button ---
    if st.sidebar.button("Ingest Data to DB Now", key="ingest_data_button_clicked"):
        with st.sidebar.spinner("Ingesting data into vector store... Please wait."):
            cmd = [sys.executable, "ingest.py"]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if process.returncode == 0:
                st.session_state.last_ingest_status = f"{timestamp} - Success"
                st.sidebar.success("Data ingestion completed successfully!") # Direct feedback
            else:
                st.session_state.last_ingest_status = f"{timestamp} - Failed (Code: {process.returncode})"
                st.sidebar.error("Data ingestion failed.") # Direct feedback
            
            # Store output for display in expander
            st.session_state.last_ingest_stdout = process.stdout
            st.session_state.last_ingest_stderr = process.stderr
            st.session_state.last_ingest_returncode = process.returncode
        
        # Reset button state
        st.session_state.ingest_data_button_clicked = False
        st.rerun()

    st.sidebar.markdown(f"**Last Ingest Attempt:**<br>{st.session_state.last_ingest_status}", unsafe_allow_html=True)

    if "last_ingest_returncode" in st.session_state:
        with st.sidebar.expander("Last Ingestion Details (Output from ingest.py)", expanded=False):
            st.text(f"Exit Code: {st.session_state.last_ingest_returncode}")
            st.subheader("Stdout:")
            st.text_area("ingest_stdout_display", st.session_state.get("last_ingest_stdout", ""), height=150, disabled=True, key="ingest_stdout_area_display") # Unique key
            st.subheader("Stderr:")
            st.text_area("ingest_stderr_display", st.session_state.get("last_ingest_stderr", ""), height=150, disabled=True, key="ingest_stderr_area_display") # Unique key
    
    st.sidebar.divider()

    # --- System Status Section ---
    st.sidebar.subheader("System Status")
    db_status = get_vector_db_status()
    st.sidebar.markdown(f"**Vector DB Status:**<br>{db_status}", unsafe_allow_html=True)
    
    st.sidebar.divider()


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