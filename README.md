# RooCode Data Query Application

## Overview

The RooCode Data Query Application is a Python-based tool designed to provide a chat-based interface for querying a specialized knowledge base. It utilizes Streamlit for its professional, dark-themed user interface, allowing users to interact intuitively with data. The knowledge base is built from information scraped from Reddit (specifically the "RooCode" community or user-configured subreddits) and potentially other text sources like GitHub repository data. This application leverages local Large Language Models (LLMs) served via Ollama and employs ChromaDB as a vector store to enable Retrieval Augmented Generation (RAG), delivering informed and contextually relevant answers.

## Features

*   **Chat-Based Querying:** Interact with your data using natural language questions.
*   **Configurable Reddit Data Scraping:** Tailor data collection from specific subreddits with adjustable post limits.
*   **Vector Store Ingestion:** A robust pipeline processes text data and populates a ChromaDB vector store for efficient semantic search.
*   **Local LLM Integration:** Seamlessly connects with local LLMs hosted by Ollama.
*   **LLM Selection:** Dynamically choose from available Ollama models directly within the UI.
*   **Polished UI:** A dark-themed, professional interface built with Streamlit, featuring a sidebar for controls and clear chat display.
*   **Chat Management:** Easily clear chat history for a fresh start.
*   **Performance Metrics:** Displays response time for each AI-generated answer.

## Tech Stack

*   **Core:** Python 3.7+
*   **Web UI:** Streamlit
*   **LLM Integration:** Ollama, `ollama` Python library
*   **RAG & Orchestration:** Langchain
*   **Vector Database:** ChromaDB (via `langchain_chroma`)
*   **Embeddings:** HuggingFace Sentence Transformers (via `langchain_huggingface`, e.g., `sentence-transformers/all-MiniLM-L6-v2`)
*   **Reddit Scraping:** PRAW (Python Reddit API Wrapper)
*   **Configuration Database:** TinyDB (for storing agent/model settings)

## Prerequisites

*   **Python:** Version 3.7 or higher.
*   **Ollama:** The Ollama service must be installed, running, and accessible.
    *   Ensure desired models (e.g., Llama3, Qwen2.5) are downloaded:
        ```bash
        ollama pull llama3:8b
        ollama pull qwen2.5:1.5b 
        # Add any other models you wish to use
        ```
*   **Git:** Required for cloning the repository.

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your_repository_url> 
    # Example: git clone https://github.com/yourusername/roocode-data-query.git
    cd <repository_directory> 
    # Example: cd roocode-data-query
    ```

2.  **Install Dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure Reddit API Access:**
    *   Copy the example Reddit configuration file:
        ```bash
        cp reddit.config.example.json reddit.config.json
        ```
    *   Edit `reddit.config.json` with your own Reddit API `client_id`, `client_secret`, and `user_agent`.
        *   To obtain these credentials, visit [Reddit's app preferences page](https://www.reddit.com/prefs/apps), create a new application (select "script" type). Your `client_id` is under the personal use script section, and `client_secret` is also provided there. The `user_agent` can be a descriptive string (e.g., "RooCodeQueryApp/0.1 by YourUsername").
    *   Optionally, customize `subreddit` (e.g., "learnpython", "LocalLLaMA"), `post_limit`, and `output_file` within `reddit.config.json`. It is recommended to keep `output_file` as `"reddit_data.txt"` as this is the default expected by `ingest.py`.

4.  **Prepare GitHub Data (Optional):**
    *   If you have relevant GitHub data (e.g., code snippets, documentation excerpts, issue discussions), save this information as plain text in a file named `github_data.txt` in the root directory of the project.
    *   The `ingest.py` script will automatically look for this file and process its content if it exists.

## Running the Application

Make sure your Ollama service is running before starting the application.

1.  **Step 1: Scrape Reddit Data:**
    *   Ensure `reddit.config.json` is correctly configured.
    *   Run the Reddit scraper script from the project's root directory:
        ```bash
        python scrape_reddit.py
        ```
    *   This will create or update the `reddit_data.txt` file (or the filename specified in your config) with the fetched data.

2.  **Step 2: Ingest Data into Vector Store:**
    *   Run the ingestion script from the project's root directory:
        ```bash
        python ingest.py
        ```
    *   This script processes the text from `reddit_data.txt` (and `github_data.txt` if it exists) and populates or updates the local ChromaDB vector store located in the `./chroma_db` directory.

3.  **Step 3: Launch the Streamlit Application:**
    *   Run the Streamlit app from the project's root directory:
        ```bash
        streamlit run app.py
        ```
    *   Streamlit will typically provide a local URL (e.g., `http://localhost:8501`). Open this URL in your web browser to interact with the RooCode Data Query application.

## Project Documentation

This project includes comprehensive documentation to help you understand its architecture, setup, and usage:

*   [**Product Requirements Document (PRODUCT_REQUIREMENTS.md):**](PRODUCT_REQUIREMENTS.md) Detailed overview of the application's goals, features, and target audience.
*   [**Backend Documentation (BACKEND_DOCUMENTATION.md):**](BACKEND_DOCUMENTATION.md) In-depth information about the backend components, data flow, and key libraries.
*   [**Frontend Documentation (FRONTEND_DOCUMENTATION.md):**](FRONTEND_DOCUMENTATION.md) Description of the UI structure, styling, and user interaction logic.
*   [**User Flow Documentation (USER_FLOW_DOCUMENTATION.md):**](USER_FLOW_DOCUMENTATION.md) Step-by-step guide through typical user journeys within the application.

## Troubleshooting

*   **Ollama Connection Issues:**
    *   Ensure the Ollama service is running and accessible on your system.
    *   Verify that the models you intend to use (e.g., `llama3:8b`) have been pulled using `ollama pull <model_name>`.
    *   Check if the model names in the Streamlit UI match those available in Ollama. Use the "Refresh Models" button in the UI.
*   **`reddit.config.json` Errors:**
    *   Ensure the file `reddit.config.json` exists in the root directory.
    *   Double-check that your Reddit API `client_id`, `client_secret`, and `user_agent` are correct and that the JSON structure is valid.
*   **Python Dependencies & `pip install` Issues:**
    *   Make sure you are using a compatible Python version (3.7+).
    *   If `pip install -r requirements.txt` fails, check your internet connection. Try upgrading pip (`pip install --upgrade pip`).
    *   Ensure you have activated your virtual environment if you are using one.
*   **"No relevant context found" or Unsatisfactory Answers:**
    *   This may indicate that the scraped data or `github_data.txt` does not contain information relevant to your query. Consider expanding your data sources or refining your scraping parameters in `reddit.config.json`.
    *   Ensure the `ingest.py` script ran successfully after updating data sources.
    *   Experiment with different LLMs available through Ollama, as some may perform better on certain types of queries.

## License

Refer to the `LICENSE` file for licensing information regarding this project.
*(If a LICENSE file is not present, you might consider adding one, e.g., MIT License).*
