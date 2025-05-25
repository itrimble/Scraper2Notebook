# Frontend Documentation: RooCode Data Query

## 1. Overview

The frontend of the RooCode Data Query application is an interactive web interface built entirely using Streamlit, a Python library for creating web applications with simple Python scripts. Its primary purpose is to provide users with an intuitive and easy-to-use platform for querying the specialized "RooCode" knowledge base. This is achieved through a familiar chat-like experience, where users can ask natural language questions and receive AI-generated answers.

A key characteristic of the frontend is its "professional and polished" dark theme dashboard aesthetic. This design choice aims to provide a visually comfortable and focused environment for users interacting with the application, especially during extended sessions.

## 2. UI Structure and Components (defined in `app.py`)

The entire user interface is defined within the `app.py` script using Streamlit components. The layout is organized into a main page area and a sidebar.

### Main Page Area

*   **Title:** Displays the application's title, "RooCode Data Query," using `st.title("RooCode Data Query")`.
*   **Query Input:** A text input field, created with `st.text_input("Ask about RooCode or the GitHub repos:")`, allows users to type their questions.
*   **Chat History:** The conversation between the user and the AI is displayed in this area. The `streamlit_chat.message` function is used to render individual messages. User messages and AI messages are visually differentiated for clarity (e.g., different background colors and alignment).
*   **Response Time:** After an AI response is generated, the time taken for the generation is displayed using `st.text(f"Response time: {end_time - start_time:.2f} seconds")`. This text is styled via custom CSS to be less prominent.
*   **Spinner:** While the backend is processing a query and generating a response, a visual spinner is shown using `with st.spinner("Generating response..."):` to indicate that the application is working.

### Sidebar (`st.sidebar`)

The sidebar, created using `with st.sidebar:`, houses various controls and information:

*   **Model Selection:** A dropdown menu, implemented with `st.selectbox("Select model:", model_options, ...)` allows users to choose which Ollama Large Language Model (LLM) they want to use for generating answers.
*   **Refresh Models Button:** A button created with `st.button("Refresh Models")`. Clicking this button triggers an update of the available LLM list from the Ollama service.
*   **Clear Chat Button:** A button implemented with `st.button("Clear Chat")`. This allows users to erase the current conversation history from the display.
*   **Current Model Display:** Text indicating the currently active LLM, shown using `st.write(f"Using model: \`{selected_model}\`")`.
*   **Attribution:** A small text element `st.markdown("Built by RooCode")` attributing the application.

## 3. Styling and Theme

The application's visual appearance is carefully curated to align with the desired dark theme dashboard aesthetic.

*   **Base Theme:** Streamlit's built-in dark theme is activated as the foundation using `st.set_page_config(layout="wide", ..., theme="dark")`. The `layout="wide"` setting ensures the application utilizes the available screen width effectively.
*   **Custom CSS:** Extensive custom CSS rules are injected directly into the application using `st.markdown("""<style>...</style>""", unsafe_allow_html=True)`. This approach allows for fine-grained control over the appearance of various components:
    *   **Consistent Dark Theme:** Ensures that the dark theme is applied uniformly across the body, main content area, sidebar, chat messages, input fields, and buttons. Specific hex color codes are used for backgrounds, text, and borders (e.g., `#0E1117` for the main background, `#1E232E` for the sidebar).
    *   **Styled Chat Bubbles:** Chat messages (`.stChatMessage` and more specific selectors like `div[data-testid="stChatMessageContent"] > div[style*="text-align: right;"] > div` for user messages) are styled with distinct background colors (e.g., `#2b313e` for user, `#222831` for AI), rounded corners (`border-radius: 10px`), and appropriate padding (`padding: 12px`) to clearly differentiate between user queries and AI responses and to enhance the dashboard look.
    *   **Improved Input Fields and Buttons:** The main text input (`.stTextInput`) and buttons in the sidebar (`.st-emotion-cache-10oheav .stButton > button`) are styled for better visual integration with the dark theme, including custom background colors, text colors, borders, and hover effects.
    *   **Overall Visual Polish:** The custom CSS also contributes to general visual polish by ensuring font consistency (Streamlit's default sans-serif font is generally maintained), appropriate spacing between elements, and by styling elements like the title (`.stTitle`) and response time text for better hierarchy and readability.

## 4. Key User Interactions and Backend Coupling

The frontend components are tightly coupled with backend logic defined in `app.py` and other modules like `converse.py`.

*   **Submitting a Query:**
    1.  The user types their question into the `st.text_input` field and presses Enter.
    2.  `app.py` captures this query string.
    3.  It then calls the `cached_similarity_search` function (which internally uses `Converse().retriever.invoke(query)`) to fetch relevant context from the ChromaDB knowledge base.
    4.  The original query and the retrieved context are passed to `Converse().chat(...)` method, which communicates with the selected Ollama LLM to get an answer.
    5.  The AI's response is received by `app.py`.
    6.  Both the user's query and the AI's response are appended to the `st.session_state.messages` list.
    7.  Streamlit automatically re-renders the page, updating the chat history display with the new messages.
*   **Selecting an LLM Model:**
    1.  The user selects a model from the `st.selectbox` in the sidebar.
    2.  The `selected_model` variable in `app.py` is updated.
    3.  This selection is persisted in `db.json` (TinyDB) and is used to instantiate the `OllamaLLM` in `converse.py` for subsequent queries.
    4.  Crucially, changing the selected model automatically clears `st.session_state.messages` (the chat history) to prevent context mismatches from different models.
*   **Refreshing Models:**
    1.  The user clicks the "Refresh Models" button in the sidebar.
    2.  `app.py` executes `st.cache_data.clear()` to clear all of Streamlit's cached functions, including `get_available_models()`.
    3.  `st.rerun()` is then called, forcing the application to re-execute its script from the top. This re-calls `get_available_models()`, which fetches an updated list of LLMs from the Ollama service.
*   **Clearing Chat:**
    1.  The user clicks the "Clear Chat" button in the sidebar.
    2.  `app.py` clears the `st.session_state.messages` list (e.g., `st.session_state["messages"] = []`).
    3.  `st.rerun()` is called to refresh the UI, which now displays an empty chat history area.

## 5. File Structure (Frontend Perspective)

From a frontend development standpoint, the structure is exceptionally streamlined:

*   **`app.py`:** This single Python script is the heart of the frontend. It contains all the Streamlit code necessary to:
    *   Define the layout and structure of the web page (main area, sidebar).
    *   Instantiate and configure all UI components (text inputs, buttons, dropdowns, chat messages).
    *   Inject all custom CSS for styling and theming.
    *   Handle all user interaction logic and coordinate with backend services.
*   **No External Frontend Files:** There are no separate HTML, CSS, or JavaScript files that need to be managed or linked. All aspects of the frontend's appearance and behavior are encapsulated within `app.py` through Python code and embedded CSS strings. This simplifies development and deployment for this type of application.
