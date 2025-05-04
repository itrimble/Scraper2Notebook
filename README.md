# Scraper2Notebook

A customizable Retrieval-Augmented Generation (RAG) implementation using Ollama for a private local instance Large Language Model (LLM) agent with a convenient web interface.

## Features

- Configure the agent (chatbot) with a script, or dive into the Modelfile yourself
- Configure the models used for your chatbot with a script
- Easily scrape your collection of PDFs and ingest with handy scripts
- Simple interface to run and interact with the chatbot agent using Streamlit
- Long term memory, compressing and making searchable with day-bound timestamps
- Web search when the chatbot cannot come up with a good answer (disabled by default)

## Getting Started

See the SETUP_GUIDE.md file for detailed setup instructions.


## Troubleshooting

### Common Issues

1. **Missing dependencies**
   - Make sure to run `pip install -r requirements.txt` to install all required packages
   - If you see errors about langchain packages, try installing them individually:
     ```
     pip install langchain langchain-ollama langchain-community langchain-core langchain-chroma langchain-huggingface
     ```

2. **Ollama model issues**
   - Ensure Ollama is running with `ollama serve`
   - If you can't find models, check available models with `ollama list`
   - Pull models manually if needed: `ollama pull llama3:8b` or `ollama pull mistral`

3. **ChromaDB errors**
   - If you see errors about ChromaDB, ensure you have the correct directory structure
   - The paths should be `./chroma_db_pdfs` for PDF storage
   - If you need to reset, delete the ChromaDB directories and start fresh

4. **Reddit API configuration**
   - See the `reddit.config.example.json` file for instructions on getting Reddit API credentials
   - Make sure to update the config.json file with your actual credentials

5. **Memory issues**
   - LLMs can be memory-intensive; if you encounter OOM errors, try a smaller model
   - Reduce batch size or chunk size in the ingestion scripts

For more detailed help, check the GitHub issues section or open a new issue with details about your problem.
