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
*   **Note:** After this initial setup, the `subreddit` and `post_limit` values within `reddit.config.json` can also be viewed and modified directly from the application's UI sidebar. Manual data scraping and ingestion can also be triggered from the UI.

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
        *   A "Select model:" dropdown.
        *   "Refresh Models" button.
        *   "Clear Chat" button.
        *   Text indicating the "Using model: `model_name`".
        *   Display of "Current Reddit Scrape Settings" (Subreddit, Post Limit).
        *   Input fields for "Modify Reddit Scrape Settings" (New Subreddit, New Post Limit) and a "Save Reddit Settings" button.
        *   "Manual Data Operations" section with "Scrape Reddit Data Now" and "Ingest Data to DB Now" buttons, along with their status displays and output expanders.
        *   "System Status" section showing "Vector DB Status".
        *   A "Built by RooCode" attribution.
    5.  **Chat Area:** The main chat area is initially empty. If the user had a previous session and the application state was somehow preserved by Streamlit (though the application is designed to clear chat history on model change), those messages might appear, but typically it will be blank for a new session or after a model change.
*   **Outcome:** The RooCode Data Query application is running, visible in the browser, and ready for user interaction with all controls visible.

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

## 8. Flow 7: Modifying Reddit Scrape Settings via UI

*   **Objective:** To change the target subreddit and/or post limit for Reddit data scraping directly from the application UI.
*   **Steps:**
    1.  **Locate Controls:** User navigates to the "Modify Reddit Scrape Settings" section in the sidebar.
    2.  **Enter New Subreddit (Optional):** User types the desired subreddit name into the "New Subreddit:" text input field.
    3.  **Enter New Post Limit (Optional):** User adjusts the value in the "New Post Limit:" number input field.
    4.  **Save Settings:** User clicks the "Save Reddit Settings" button.
    5.  **Feedback:**
        *   If successful, a "Reddit settings saved successfully!" message appears in the sidebar. The "Current Reddit Scrape Settings" display updates to show the new values, and the input fields are pre-filled with these new values.
        *   If there's an error (e.g., `reddit.config.json` not found, not writable, or malformed), an error message is displayed in the sidebar.
*   **Outcome:** The `reddit.config.json` file on the server is updated with the new subreddit and post limit. Subsequent manual or automated Reddit scraping will use these new parameters.

## 9. Flow 8: Triggering Reddit Data Scraping via UI

*   **Objective:** To manually initiate the process of scraping data from Reddit using the current settings in `reddit.config.json`.
*   **Steps:**
    1.  **Locate Button:** User navigates to the "Manual Data Operations" section in the sidebar and finds the "Scrape Reddit Data Now" button.
    2.  **Click Button:** User clicks the "Scrape Reddit Data Now" button.
    3.  **Spinner Indicator:** A spinner appears in the sidebar with the message "Scraping Reddit data... Please wait."
    4.  **Status Update:** Upon completion (or failure), the "Last Scrape Attempt:" text below the button updates with a timestamp and the status (e.g., "Success" or "Failed (Code: X)").
    5.  **View Details (Optional):** User can click on the "Last Scraping Details (Output from scrape_reddit.py)" expander to view the standard output and standard error from the `scrape_reddit.py` script execution, as well as its exit code.
*   **Outcome:** The `scrape_reddit.py` script is executed on the server. If successful, the Reddit data file (e.g., `reddit_data.txt`) is updated. The user is informed of the outcome via the UI.

## 10. Flow 9: Triggering Data Ingestion via UI

*   **Objective:** To manually initiate the process of ingesting data from the source files (e.g., `reddit_data.txt`, `github_data.txt`) into the ChromaDB vector store.
*   **Steps:**
    1.  **Locate Button:** User navigates to the "Manual Data Operations" section in the sidebar and finds the "Ingest Data to DB Now" button.
    2.  **Click Button:** User clicks the "Ingest Data to DB Now" button.
    3.  **Spinner Indicator:** A spinner appears in the sidebar with the message "Ingesting data into vector store... Please wait."
    4.  **Feedback & Status Update:**
        *   A direct success ("Data ingestion completed successfully!") or error ("Data ingestion failed.") message is displayed in the sidebar.
        *   The "Last Ingest Attempt:" text below the button updates with a timestamp and the status (e.g., "Success" or "Failed (Code: X)").
    5.  **View Details (Optional):** User can click on the "Last Ingestion Details (Output from ingest.py)" expander to view the standard output and standard error from the `ingest.py` script execution, as well as its exit code.
*   **Outcome:** The `ingest.py` script is executed on the server. If successful, the ChromaDB vector store (`./chroma_db`) is updated with the latest data. The user is informed of the outcome via the UI. The "Vector DB Status" display may also update to reflect changes (e.g., from "Not Found" to "Loaded and Populated").
