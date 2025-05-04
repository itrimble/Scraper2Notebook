# Detailed Setup Guide for Scraper2Notebook

This guide provides step-by-step instructions to set up and use the Scraper2Notebook project.

## Prerequisites

1. **Python 3.8+**
   - Check with `python3 --version`
   - Install from https://www.python.org/downloads/ if needed

2. **Ollama**
   - Install from https://ollama.com/download
   - Verify installation with `ollama --version`

3. **Required models**
   - Pull the models with: `ollama pull llama3:8b` and `ollama pull mistral`
   - For a full list of available models: `ollama list`

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/itrimble/Scraper2Notebook.git
   cd Scraper2Notebook
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   python setup.py
   ```
   This will create a `config.json` file with your settings.

5. **Start Ollama service**
   ```bash
   ollama serve
   ```
   Keep this running in a separate terminal.

## Setting Up Data Sources

### PDF Ingestion

1. **Scrape PDF file paths**
   ```bash
   ./scrape-pdf-list.sh /path/to/your/pdfs
   ```
   This creates a list of PDF files in `pdf-files.txt`.

2. **Ingest PDFs into the database**
   ```bash
   python ingest-pdf.py
   ```
   This may take a while depending on the number and size of PDFs.

### Reddit Data (Optional)

1. **Get Reddit API credentials**
   - Go to https://www.reddit.com/prefs/apps
   - Create a new application (type: script)
   - Note your client_id and client_secret

2. **Configure Reddit API access**
   - Copy `reddit.config.example.json` to `config.json`
   - Replace the placeholders with your actual credentials

3. **Run the Reddit scraper**
   ```bash
   python scrape_reddit.py
   ```

### GitHub Data (Optional)

1. **Configure GitHub repositories to scrape**
   - Edit `scrape_github.py` to include the repositories you want to scrape
   - By default, public repositories don't need authentication

2. **Run the GitHub scraper**
   ```bash
   python scrape_github.py
   ```

## Running the Application

1. **Start the web interface**
   ```bash
   ./run.sh
   ```
   Or if you want to clear previous conversation memory:
   ```bash
   ./cleanRun.sh
   ```

2. **Access the interface**
   - Open your browser to http://localhost:8501
   - Choose a model from the dropdown
   - Start asking questions!

## Advanced Configuration

- **Customizing the agent**: Edit `config.json` manually or run `python setup.py` again
- **Changing models**: Use the dropdown in the web interface or edit `config.json`
- **Enabling web search**: Edit `converse.py` and set `WEB_SEARCH_ENABLED = True`

## Maintenance

- **Clearing memory**: Run `./cleanRun.sh` to remove dynamic memory
- **Complete reset**: Run `./reset.sh` to remove all configuration and memory

## Need Help?

Check the Troubleshooting section in the README.md or open an issue on GitHub.
