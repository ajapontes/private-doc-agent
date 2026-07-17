# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and interact with private documents.

The project is being built incrementally, starting from deterministic document loading and keyword search, and evolving toward a private AI-powered document agent with local LLM support, RAG, tools, MCP, and multi-agent validation.

## Current Version

v0.2.1

## What it does now

Private Doc Agent currently provides a FastAPI backend that can read local `.txt` and `.md` documents, list available files, retrieve document content, search keywords across documents, and summarize documents using a locally running LLM through Ollama.

The current version includes the first AI-powered capability: local document summarization.

The document content is processed locally and sent to a local model served by Ollama. This keeps the project aligned with a local-first and privacy-oriented architecture.

This version also adds centralized application logging to improve traceability and debugging across the API and internal services.

## Current Features

- FastAPI backend.
- Health check endpoint.
- Local document listing.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Simple keyword search across supported documents.
- Local LLM integration through Ollama.
- Configurable model using environment variables.
- Prompt template for document summarization.
- Document summarization endpoint.
- Centralized application logging.
- Console and rotating file logging.
- Request-level log separator for better traceability.
- Privacy-aware logs that avoid storing document content, full prompts or generated responses.

## AI Layer Introduced

In version `v0.2.0`, the project introduced a local LLM-based generation layer.

Current AI flow:

```text
Local document
  -> document loader
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local generative model
  -> generated summary
```

At this stage, this is not RAG yet. The application sends the full document content to the local LLM as context.

RAG will be introduced in a future version using chunking, embeddings, vector storage, and context retrieval.

## Project Structure

```text
private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    logging_config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  logs/
    app.log
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
```

Note: `logs/app.log` is generated locally and should not be committed to GitHub.

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- requests
- Ollama installed and running locally

## Setup

Clone the repository:

```bash
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root based on `.env.example`.

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
```

The `.env` file should not be committed to GitHub.

The `.env.example` file should be committed to document the required configuration.

## Ollama Setup

Make sure Ollama is running locally.

Validate Ollama:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434
```

Expected response:

```text
Ollama is running
```

List installed models:

```powershell
ollama list
```

Example model used in this project:

```text
qwen3.5:4b
```

If needed, update `.env` with the model available in your local environment.

## Run the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://localhost:8000/docs
```

## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

Logs are written to:

```text
logs/app.log
```

The application also writes logs to the console while running with Uvicorn.

### Logging capabilities

- Logs API request flow.
- Logs document listing and document reading events.
- Logs keyword search execution.
- Logs local LLM calls through Ollama.
- Logs document summarization flow.
- Adds a visual separator between API executions.
- Uses rotating log files to avoid unlimited log growth.

### Privacy-aware logging

The application intentionally avoids logging sensitive content.

The logs may include:

```text
- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
```

The logs should not include:

```text
- full document content
- full prompt content
- full generated summary
- private document data
```

### View logs

To view the latest log entries:

```powershell
Get-Content .\logs\app.log -Tail 80
```

To watch logs in real time:

```powershell
Get-Content .\logs\app.log -Wait
```

## API Endpoints

### Health Check

```http
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.1"
}
```

### List Documents

```http
GET /documents
```

Returns all supported documents from `data/input`.

### Read Document

```http
GET /documents/{filename}
```

Examples:

```http
GET /documents/demo.txt
GET /documents/demo.md
```

### Search Documents

```http
POST /search
```

Request body:

```json
{
  "query": "RAG"
}
```

Expected response structure:

```json
{
  "query": "RAG",
  "matches": [
    {
      "filename": "demo.md",
      "line_number": 10,
      "line": "- Build a RAG pipeline"
    }
  ],
  "count": 1
}
```

### Summarize Document

```http
POST /summarize
```

Request body:

```json
{
  "filename": "demo.md"
}
```

Expected response structure:

```json
{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.1"
}
```

## Testing the LLM Client

You can test the local LLM client directly from PowerShell:

```powershell
python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
```

Expected result:

```text
An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
```

The exact response may vary depending on the model.

## Testing Document Summarization

You can test summarization directly from Python:

```powershell
python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
```

## Version History

### v0.1.0 - Basic Local Document Search

Initial version focused on deterministic document handling without AI.

Features introduced:

- FastAPI application structure.
- Health check endpoint.
- Local document discovery.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Case-insensitive keyword search across local documents.

AI status:

```text
No AI capabilities yet.
This version establishes the document ingestion and search foundation.
```

### v0.2.0 - Local LLM Document Summarization

This version introduced the first AI-powered capability.

Features introduced:

- Local LLM integration through Ollama.
- Configurable Ollama base URL and model through `.env`.
- Local LLM client service.
- Prompt template for summarization.
- Document summarization service.
- `POST /summarize` endpoint.
- Improved separation between document loading, search, LLM communication, and summarization logic.

AI status:

```text
Local document content
  -> controlled prompt
  -> local LLM
  -> generated summary
```

This version is still not RAG. The full document is passed as context to the local model.

### v0.2.1 - Application Logging

This version adds centralized application logging and traceability across the project.

Features introduced:

- Centralized logging configuration.
- Console logging.
- Rotating file logging under `logs/app.log`.
- Request-level visual separator.
- Logging across API endpoints and services.
- Traceability for document loading, keyword search, local LLM calls and summarization.
- Privacy-aware logging that avoids storing full document content, prompts or generated summaries.

AI status:

```text
No new AI capability introduced.
This version improves observability and debugging for the local LLM summarization flow.
```

## Roadmap

### v0.3.0 - Basic RAG

Planned capabilities:

- Split documents into chunks.
- Generate local embeddings.
- Store vectors in ChromaDB.
- Retrieve relevant chunks based on a user question.
- Answer questions using retrieved context.
- Return sources used to generate the answer.

### v0.4.0 - Tool-Based Agent

Planned capabilities:

- Add document tools such as search, summarize, and ask.
- Create a simple agent router.
- Allow the system to decide which tool to use based on user intent.

### v0.5.0 - Auditor Agent

Planned capabilities:

- Add a second validation layer.
- Review answers for unsupported claims.
- Check whether the response is grounded in document evidence.
- Add confidence levels.

### v0.6.0 - MCP Server

Planned capabilities:

- Expose document tools through MCP.
- Allow external clients or agents to call document-related tools using a standard protocol.

## Design Principles

- Local-first execution.
- Privacy-oriented architecture.
- Incremental learning by layers.
- Clear separation of responsibilities.
- Documented code.
- No external LLM dependency for private document processing.
- Build deterministic capabilities before adding agentic behavior.

## Current Limitations

- Only `.txt` and `.md` files are supported.
- Summarization sends the full document content to the local model.
- Large documents may exceed the model context window.
- No chunking yet.
- No embeddings yet.
- No vector database yet.
- No RAG yet.
- No agent or MCP support yet.
- No frontend yet.

## Suggested Commit for v0.2.1

```bash
git add .
git commit -m "feat: add local LLM summarization with logging"
git push origin feature/local-llm-summarization
```

After merging into `main`, the suggested tag is:

```bash
git tag v0.2.1
git push origin v0.2.1
```