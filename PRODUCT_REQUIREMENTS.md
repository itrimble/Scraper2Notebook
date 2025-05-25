# Product Requirements Document: RooCode Data Query

## 1. Introduction

The RooCode Data Query application is a chat-based interface designed to allow users to query and interact with a specialized knowledge base. This knowledge base is derived from data sources relevant to the "RooCode" community/topic, primarily Reddit discussions and GitHub repository information.

The primary purpose of the application is to provide an intuitive way for users to ask natural language questions and receive answers synthesized by a Large Language Model (LLM), augmented by relevant information retrieved from these data sources.

The application is built using Python, with Streamlit for the web interface, Ollama for LLM integration, and ChromaDB as the vector store for the knowledge base.

## 2. Goals/Objectives

*   **Enable Knowledge Access:** Allow users to easily ask questions and retrieve relevant answers from the curated RooCode knowledge base.
*   **Intuitive User Experience:** Provide a professional, intuitive, and responsive user interface that makes querying and information retrieval straightforward.
*   **Maintainable Knowledge Base:** Allow for periodic updates of the knowledge base, particularly the Reddit data, to ensure information remains current.
*   **Flexible LLM Support:** Support different LLMs via Ollama, allowing users to choose models based on their needs or preferences.

## 3. Target Audience

*   **Cybersecurity Students and Analysts:** Individuals studying or working in cybersecurity who might find the "RooCode" related data relevant for research, learning, or analysis (assuming "RooCode" pertains to a topic within this domain, as per related project context).
*   **Developers and Community Members:** Developers, contributors, or users interested in the "RooCode" project, community, or specific technologies discussed within its data sources.

## 4. Core Features

### 4.1 Data Ingestion

*   **Reddit Scraper (`scrape_reddit.py`):**
    *   Fetches posts (titles and selftext) and top-level comments from a user-configured subreddit.
    *   Configuration (subreddit name, post limit, API credentials) is managed via `reddit.config.json`.
    *   Requires valid user-provided Reddit API credentials (`client_id`, `client_secret`, `user_agent`).
    *   Outputs scraped data into a structured text file (default: `reddit_data.txt`).
*   **GitHub Data Handling:**
    *   The ingestion process (`ingest.py`) utilizes a `github_data.txt` file.
    *   Currently, the mechanism for creating or updating `github_data.txt` is outside the defined scope of the automated tools (i.e., it's assumed to be manually prepared or obtained).
*   **Vector Store Population (`ingest.py`):**
    *   Processes text data from specified source files (`reddit_data.txt`, `github_data.txt`).
    *   Splits text into manageable chunks.
    *   Generates embeddings for these chunks using a sentence transformer model.
    *   Stores the text chunks and their corresponding embeddings in a ChromaDB vector store, persisted locally (default: `./chroma_db`).

### 4.2 Chat Interface (`app.py`)

*   **Web Application:** Built using Streamlit, providing an interactive web-based UI.
*   **Natural Language Queries:** Users can type questions in natural language into a text input field.
*   **Chat History Display:** Displays a chronological history of user queries and AI-generated responses.
*   **RAG-Powered Responses:**
    *   Retrieves relevant context (document snippets) from the ChromaDB vector store based on the user's query.
    *   Uses a selected Ollama LLM to generate a response, considering both the user's query and the retrieved context.

### 4.3 LLM Model Selection

*   **Dynamic Model Choice:** Users can select from a list of available LLMs hosted by their local Ollama instance.
*   **Model List Fetching:** The application dynamically fetches the list of available models from Ollama on startup.
    *   Includes a fallback list of common models if the Ollama API call fails.
*   **Refresh Models:** A "Refresh Models" button in the sidebar allows users to update the list of available models without restarting the application.
*   **Chat Reset on Model Change:** Changing the selected LLM automatically clears the current chat history to ensure contextual relevance.

### 4.4 User Interface (UI)

*   **Dark Theme:** Employs a dark theme for a professional appearance and improved visual comfort, especially in low-light environments.
*   **Sidebar Controls:**
    *   Model selection dropdown.
    *   "Refresh Models" button.
    *   "Clear Chat" button.
    *   Displays the currently active model.
*   **Main Chat Area:** Dedicated space for displaying the chat history and the query input field.
*   **Styled Chat Messages:** User and AI messages are styled distinctly (e.g., different background colors, alignment) for better readability and to clearly differentiate speakers.
*   **Response Time Display:** Shows the time taken for the LLM to generate a response after a query is submitted.

### 4.5 Configuration

*   **Reddit Scraping (`reddit.config.json`):**
    *   Manages Reddit API credentials (`client_id`, `client_secret`, `user_agent`).
    *   Defines scraping parameters like `subreddit`, `post_limit`, and `output_file`.
    *   An example file (`reddit.config.example.json`) is provided as a template.
*   **Application Behavior (`db.json` - TinyDB):**
    *   Stores the currently selected Ollama model and system message/persona for the AI agent.
    *   This allows persistence of some application settings between sessions (though model selection is dynamic on load).

## 5. User Interaction Flow (High-Level)

### 5.1 Setup & Data Update (First time or Periodic)

1.  **Configure Reddit:** User copies `reddit.config.example.json` to `reddit.config.json` and fills in their Reddit API credentials and desired subreddit/parameters.
2.  **Scrape Reddit:** User runs the `scrape_reddit.py` script from the command line (e.g., `python scrape_reddit.py`). This generates/updates `reddit_data.txt`.
3.  **Prepare GitHub Data (Manual):** User prepares or updates `github_data.txt` with relevant GitHub information.
4.  **Ingest Data:** User runs the `ingest.py` script (e.g., `python ingest.py`). This processes `reddit_data.txt` and `github_data.txt`, generates embeddings, and populates/updates the ChromaDB vector store in `./chroma_db`.

### 5.2 Application Usage

1.  **Launch Application:** User runs `streamlit run app.py` from the command line. The application opens in a web browser.
2.  **Select LLM (Optional):**
    *   The application defaults to a pre-configured or the first available LLM.
    *   User can use the sidebar dropdown to select a different Ollama model.
    *   User can click "Refresh Models" to update the list if new models were added to Ollama while the app was running.
3.  **Submit Query:** User types a question into the chat input field at the bottom of the main area and presses Enter.
4.  **Context Retrieval:** The application performs a similarity search in ChromaDB using the query to find relevant text chunks.
5.  **LLM Processing:** The query and the retrieved context are sent to the selected Ollama LLM.
6.  **Display Response:** The LLM's response is displayed in the chat interface as a new message from the "RooCode Assistant". The response time is also shown.
7.  **Interact Further:**
    *   User can continue asking questions.
    *   User can click "Clear Chat" in the sidebar to erase the current conversation history.

## 6. Design & UI/UX

*   **Overall Feel:** Professional, polished, and data-centric, akin to a specialized dashboard or querying tool.
*   **Theme:** Consistent dark theme with high contrast for text elements, ensuring readability and reducing eye strain.
*   **Layout:**
    *   **Sidebar:** Cleanly separates operational controls (model selection, refresh, clear chat) from the primary interaction area.
    *   **Main Area:** Focuses on the chat conversation flow and query input.
*   **Inspiration:** The UI styling aims for a look and feel inspired by modern data analysis and monitoring tools (e.g., Splunk, Datadog), emphasizing clarity and efficiency.
*   **Chat Bubbles:** Styled to be distinct for user vs. AI, with rounded corners and appropriate padding.

## 7. Technical Stack (High-Level)

*   **Backend Logic:** Python 3.x
*   **Web UI Framework:** Streamlit
*   **LLM Hosting & Serving:** Ollama
*   **LLM Interaction Library:** `ollama` Python library, Langchain components
*   **Vector Database:** ChromaDB (local persistence)
*   **Embedding Model:** Sentence Transformers (via Langchain/HuggingFace Embeddings)
*   **Reddit API Wrapper:** PRAW (Python Reddit API Wrapper)
*   **Data Storage (Configuration):** TinyDB (for `db.json`)
*   **Data Parsing/Handling:** Standard Python libraries (e.g., `json`)

## 8. Future Considerations

*(This section outlines potential ideas for future development and is not part of the current committed scope.)*

*   **Automated Data Refresh:**
    *   Implement scheduled execution (e.g., cron jobs or a built-in scheduler) for `scrape_reddit.py` and `ingest.py` to keep the knowledge base up-to-date automatically.
*   **Enhanced GitHub Ingestion:**
    *   Develop a dedicated GitHub scraper to fetch data from specific repositories (issues, PRs, READMEs, code comments) based on user configuration.
*   **User Authentication:**
    *   Add an optional user authentication layer to restrict access or personalize experiences.
*   **Multi-Source Management:**
    *   Allow users to configure and manage multiple distinct knowledge bases or data source collections within the application.
*   **Advanced Search & Filtering:**
    *   Provide options to filter search results by data source (Reddit, GitHub), date ranges, or other metadata before sending to the LLM.
*   **Feedback Mechanism:**
    *   Allow users to provide feedback on the quality of responses, which could be used for improving prompts or fine-tuning models.
*   **Streaming Responses:**
    *   Implement streaming for LLM responses to display text as it's generated, improving perceived responsiveness.
*   **Export Chat History:**
    *   Allow users to export their current chat conversation.
