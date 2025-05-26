# User Flow Documentation: RooCode Data Query

## 1. Introduction

This document outlines the typical paths and interactions users will have with the RooCode Data Query application. It covers the journey from initial setup and data preparation to the primary interaction loops of querying data and managing application settings.

## 2. Flow 1: First-Time Setup & Data Preparation

*   **Objective:** To prepare the necessary configurations and data for the application to use.
*   **Steps:**
    1.  **Obtain Reddit API Credentials:** User navigates to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and creates a new application (selecting "script" type) to get a `client_id` (under personal use script) and `client_secret`. The `user_agent` can be a descriptive string like "RooCodeScraper/0.1 by YourUsername".
    2.  **Create Configuration File:** User creates a new file named `reddit.config.json` in the root directory of the application, typically by copying the provided `reddit.config.example.json` template.
    3.  **Populate Configuration:** User opens `reddit.config.json` and fills in their specific Reddit API `client_id`, `client_secret`, and `user_agent`. They also specify the target `subreddit` to scrape, the `post_limit` (number of posts to fetch), and the desired `output_file` name for the scraped data (e.g., `reddit_data.txt`).
    4.  **Prepare GitHub Data (Optional):** If GitHub data is to be included, the user prepares or updates a plain text file named `github_data.txt` in the root directory with the relevant textual content.
    5.  **Run Reddit Scraper:** User opens a command line interface, navigates to the application's root directory, and executes the command:
        ```bash
        python scrape_reddit.py
        ```
        The script will output status messages (e.g., indicating successful connection, number of posts fetched, or errors if `reddit.config.json` is missing/malformed). Upon successful completion, the specified `output_file` (e.g., `reddit_data.txt`) will be created or updated with the scraped data.
    6.  **Run Data Ingestion:** After the data sources are ready, the user runs the ingestion script from the command line in the application's root directory:
        ```bash
        python ingest.py
        ```
        This script processes the text data from `reddit_data.txt` (and `github_data.txt` if present), splits it into chunks, generates vector embeddings for these chunks, and populates or updates the ChromaDB vector store located in the `./chroma_db` directory. The console may display status messages about the number of documents processed or loaded.
*   **Outcome:** The `reddit.config.json` file is correctly configured with API credentials and scraping parameters. The `./chroma_db` directory is created and populated with the embedded knowledge base, making the application ready for querying.

## 3. Flow 2: Application Launch & Initial View

*   **Objective:** To start the application and see the main interface.
*   **Steps:**
    1.  **Launch Command:** User opens a command line interface, navigates to the application's root directory, and executes the command:
        ```bash
        streamlit run app.py
        ```
    2.  **Browser Opens:** The application automatically opens in the user's default web browser, typically at an address like `http://localhost:8501`.
    3.  **Main Interface:** The user is presented with the main chat interface. The title "RooCode Data Query" is prominently displayed at the top of the main content area.
    4.  **Sidebar Contents:** The sidebar on the left (expanded by default) displays:
        *   A "Select model:" dropdown showing the currently selected Ollama LLM (or a default if none was previously selected).
        *   A "Refresh Models" button.
        *   A "Clear Chat" button.
        *   Text indicating the "Using model: `model_name`".
        *   A "Built by RooCode" attribution.
    5.  **Chat Area:** The main chat area is initially empty. If the user had a previous session and the application state was somehow preserved by Streamlit (though the application is designed to clear chat history on model change), those messages might appear, but typically it will be blank for a new session or after a model change.
*   **Outcome:** The RooCode Data Query application is running, visible in the browser, and ready for user interaction.

## 4. Flow 3: Querying Data (Main Interaction Loop)

*   **Objective:** To ask questions and receive answers from the AI based on the knowledge base.
*   **Steps:**
    1.  **Enter Query:** User types their question into the text input field labeled "Ask about RooCode or the GitHub repos:" located at the bottom of the main chat area.
    2.  **Submit Query:** User presses the `Enter` key or clicks outside the input field to submit the query.
    3.  **Spinner Indicator:** A "Generating response..." spinner animation appears, indicating that the application is processing the query and generating a response.
    4.  **User Message Displayed:** The user's typed query immediately appears in the chat history section, typically styled as a user message (e.g., aligned to the right, specific background color).
    5.  **AI Response Displayed:** After the backend processing (context retrieval and LLM generation) is complete, the AI's response appears as a new message in the chat history, styled as an AI message (e.g., aligned to the left, different background color).
    6.  **Response Time:** A small text note (e.g., "Response time: X.XX seconds") appears, usually below the AI's response or in a consistent location, indicating how long the generation took.
    7.  **Continue Interaction:** The user can now type another question into the input field to continue the conversation, ask follow-up questions, or query about different topics.
*   **Outcome:** The user receives answers to their questions, and a conversation history is built up in the chat interface, allowing them to review previous interactions.

## 5. Flow 4: Changing the LLM Model

*   **Objective:** To switch to a different Ollama LLM for generating responses, potentially to leverage different model capabilities or performance characteristics.
*   **Steps:**
    1.  **Access Dropdown:** User locates the "Select model:" dropdown menu in the sidebar.
    2.  **Select New Model:** User clicks on the dropdown to expand it and then clicks on a different model name from the displayed list of available Ollama models.
    3.  **Sidebar Update:** The text below the dropdown, "Using model: ...", updates to reflect the newly selected model name.
    4.  **Chat History Cleared:** The chat history displayed in the main area is automatically cleared. This is to ensure that subsequent interactions are relevant to the context and capabilities of the newly chosen model.
*   **Outcome:** Future queries submitted by the user will be processed by the newly selected LLM. The chat interface is reset, providing a clean slate for the new model's context.

## 6. Flow 5: Refreshing the Model List

*   **Objective:** To update the list of available LLMs in the dropdown, in case new models have been added to or removed from the local Ollama service since the application was started.
*   **Steps:**
    1.  **Click Refresh Button:** User clicks the "Refresh Models" button located in the sidebar.
    2.  **Fetch Updated List:** The application attempts to communicate with the Ollama service to re-fetch the list of currently available models.
    3.  **Dropdown Update:** The "Select model:" dropdown in the sidebar is repopulated. If new models were pulled into Ollama, they will now appear in the list. If models were removed from Ollama, they will no longer be listed.
*   **Outcome:** The model selection dropdown accurately reflects the current set of models available through the connected Ollama instance, allowing the user to select from the most up-to-date list.

## 7. Flow 6: Clearing Chat History

*   **Objective:** To remove the current conversation (all user queries and AI responses) from the user interface, providing a clean chat area without changing the selected LLM.
*   **Steps:**
    1.  **Click Clear Chat Button:** User clicks the "Clear Chat" button located in the sidebar.
    2.  **Chat Area Reset:** All messages currently displayed in the chat history area (both user-submitted queries and AI-generated responses) are immediately removed.
*   **Outcome:** The chat interface is reset to an empty state, ready for a new conversation. The underlying LLM selection and other application settings remain unchanged.
