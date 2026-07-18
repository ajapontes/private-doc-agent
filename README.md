# private-doc-agent

Private Doc Agent is a local-first API for reading, searching, and summarizing private documents. It runs the application and language model locally so document processing does not depend on an external LLM service.

## Current version

`v0.2.2`

## Implemented capabilities

- FastAPI backend.
- Application health check.
- Discovery of local `.txt` and `.md` documents.
- Retrieval of document content.
- Case-insensitive keyword search across documents.
- Local document summarization through Ollama.
- Configurable Ollama URL and model.
- Reusable prompt template for document summarization.
- Centralized console and rotating-file logging.
- Separate logging of LLM prompts and responses for local debugging.
- Request separators to make individual API executions easier to trace.

The current summarization flow sends the complete document to the configured local model. The project does not currently implement chunking, embeddings, a vector database, RAG, agents, MCP, or a frontend.

## Architecture

```text
Client
  -> FastAPI endpoint
  -> document loader
  -> summarization service
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local model
```

Document listing, reading, and keyword search are deterministic operations and do not call the language model.

## Project structure

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
    llm_io.log
  tests/
  .env.example
  .gitignore
  README.md
  requirements.txt
```

The files under `logs/` are generated locally and must not be committed.

## Requirements

- Python 3.11 or later.
- Ollama installed and running locally.
- A local Ollama model, such as `qwen3.5:4b`.
- Project dependencies listed in `requirements.txt`.

## Local deployment

### 1. Clone the repository

```bash
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Create a `.env` file in the project root using `.env.example` as the reference:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
```

Use the name of a model installed in your local Ollama instance. The `.env` file contains local configuration and must not be committed.

### 5. Start and validate Ollama

Confirm that Ollama is available:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434
```

Expected response:

```text
Ollama is running
```

List the installed models:

```powershell
ollama list
```

If the configured model is not installed, download it before starting the API:

```powershell
ollama pull qwen3.5:4b
```

### 6. Add documents

Copy the `.txt` or `.md` files to be processed into:

```text
data/input/
```

### 7. Start the API

From the project root, run:

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://localhost:8000
```

Interactive OpenAPI documentation:

```text
http://localhost:8000/docs
```

## API endpoints

### Health check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.2"
}
```

### List documents

```http
GET /documents
```

Returns the supported documents found in `data/input/`.

### Read a document

```http
GET /documents/{filename}
```

Examples:

```http
GET /documents/demo.txt
GET /documents/demo.md
```

### Search documents

```http
POST /search
```

Request body:

```json
{
  "query": "RAG"
}
```

Example response:

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

### Summarize a document

```http
POST /summarize
```

Request body:

```json
{
  "filename": "demo.md"
}
```

Example response:

```json
{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.2"
}
```

The generated summary varies according to the selected model and document content.

## Logging

The application writes logs to the console while running with Uvicorn and uses rotating files to prevent unlimited log growth.

### General application log

```text
logs/app.log
```

This log records operational metadata such as:

- API request flow.
- Document listing and reading events.
- Keyword searches and match counts.
- Ollama calls and model name.
- Document and prompt lengths.
- Summarization flow.
- Errors.

It is designed to avoid storing full document content, complete prompts, and generated summaries.

View recent entries:

```powershell
Get-Content .\logs\app.log -Tail 80
```

Watch the log in real time:

```powershell
Get-Content .\logs\app.log -Wait
```

### LLM input/output log

```text
logs/llm_io.log
```

This local debugging log records the complete prompt sent to Ollama and the complete model response, together with the timestamp, model name, prompt length, and response length.

Because prompts can contain private document text, this file may contain sensitive information. It must remain local and must never be committed to the repository.

View recent entries:

```powershell
Get-Content .\logs\llm_io.log -Tail 120
```

Watch the log in real time:

```powershell
Get-Content .\logs\llm_io.log -Wait
```

The repository ignore rules should include:

```gitignore
logs/
*.log
```

## Direct service tests

Test the local LLM client:

```powershell
python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
```

Test document summarization:

```powershell
python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
```

## Implemented version history

### v0.1.0 — Local document handling and search

- FastAPI application structure.
- Health endpoint.
- Local `.txt` and `.md` document discovery.
- Document content retrieval.
- Case-insensitive keyword search.

### v0.2.0 — Local LLM document summarization

- Ollama integration.
- Environment-based model configuration.
- Local LLM client.
- Reusable summarization prompt.
- Document summarization service.
- `POST /summarize` endpoint.

### v0.2.1 — Centralized application logging

- Console logging.
- Rotating general log file.
- Request-level visual separators.
- Logging across endpoints and internal services.
- Privacy-aware operational logging.

### v0.2.2 — LLM input/output logging

- Dedicated local log for complete prompts and model responses.
- LLM interaction metadata for debugging and traceability.
- Separation between privacy-aware operational logs and sensitive LLM interaction logs.

## Current limitations

- Only `.txt` and `.md` documents are supported.
- Summarization sends the complete document to the local model.
- Large documents may exceed the model context window.
- There is no chunking, embedding generation, vector database, RAG, agent, MCP server, or frontend.

## Privacy considerations

- Documents and inference remain in the local environment when Ollama is configured locally.
- `.env`, `logs/app.log`, and `logs/llm_io.log` must not be committed.
- `logs/llm_io.log` can contain complete private document text.
- Access to the machine, project directory, and log files must be restricted according to the sensitivity of the processed documents.
Biblioteca
/
Proyectos de IA
/
README.md


# private-doc-agent

Private Doc Agent is a local-first API for reading, searching, and summarizing private documents. It runs the application and language model locally so document processing does not depend on an external LLM service.

## Current version

`v0.2.2`

## Implemented capabilities

- FastAPI backend.
- Application health check.
- Discovery of local `.txt` and `.md` documents.
- Retrieval of document content.
- Case-insensitive keyword search across documents.
- Local document summarization through Ollama.
- Configurable Ollama URL and model.
- Reusable prompt template for document summarization.
- Centralized console and rotating-file logging.
- Separate logging of LLM prompts and responses for local debugging.
- Request separators to make individual API executions easier to trace.

The current summarization flow sends the complete document to the configured local model. The project does not currently implement chunking, embeddings, a vector database, RAG, agents, MCP, or a frontend.

## Architecture

```text
Client
  -> FastAPI endpoint
  -> document loader
  -> summarization service
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local model
```

Document listing, reading, and keyword search are deterministic operations and do not call the language model.

## Project structure

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
    llm_io.log
  tests/
  .env.example
  .gitignore
  README.md
  requirements.txt
```

The files under `logs/` are generated locally and must not be committed.

## Requirements

- Python 3.11 or later.
- Ollama installed and running locally.
- A local Ollama model, such as `qwen3.5:4b`.
- Project dependencies listed in `requirements.txt`.

## Local deployment

### 1. Clone the repository

```bash
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Create a `.env` file in the project root using `.env.example` as the reference:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
```

Use the name of a model installed in your local Ollama instance. The `.env` file contains local configuration and must not be committed.

### 5. Start and validate Ollama

Confirm that Ollama is available:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434
```

Expected response:

```text
Ollama is running
```

List the installed models:

```powershell
ollama list
```

If the configured model is not installed, download it before starting the API:

```powershell
ollama pull qwen3.5:4b
```

### 6. Add documents

Copy the `.txt` or `.md` files to be processed into:

```text
data/input/
```

### 7. Start the API

From the project root, run:

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://localhost:8000
```

Interactive OpenAPI documentation:

```text
http://localhost:8000/docs
```

## API endpoints

### Health check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.2"
}
```

### List documents

```http
GET /documents
```

Returns the supported documents found in `data/input/`.

### Read a document

```http
GET /documents/{filename}
```

Examples:

```http
GET /documents/demo.txt
GET /documents/demo.md
```

### Search documents

```http
POST /search
```

Request body:

```json
{
  "query": "RAG"
}
```

Example response:

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

### Summarize a document

```http
POST /summarize
```

Request body:

```json
{
  "filename": "demo.md"
}
```

Example response:

```json
{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.2"
}
```

The generated summary varies according to the selected model and document content.

## Logging

The application writes logs to the console while running with Uvicorn and uses rotating files to prevent unlimited log growth.

### General application log

```text
logs/app.log
```

This log records operational metadata such as:

- API request flow.
- Document listing and reading events.
- Keyword searches and match counts.
- Ollama calls and model name.
- Document and prompt lengths.
- Summarization flow.
- Errors.

It is designed to avoid storing full document content, complete prompts, and generated summaries.

View recent entries:

```powershell
Get-Content .\logs\app.log -Tail 80
```

Watch the log in real time:

```powershell
Get-Content .\logs\app.log -Wait
```

### LLM input/output log

```text
logs/llm_io.log
```

This local debugging log records the complete prompt sent to Ollama and the complete model response, together with the timestamp, model name, prompt length, and response length.

Because prompts can contain private document text, this file may contain sensitive information. It must remain local and must never be committed to the repository.

View recent entries:

```powershell
Get-Content .\logs\llm_io.log -Tail 120
```

Watch the log in real time:

```powershell
Get-Content .\logs\llm_io.log -Wait
```

The repository ignore rules should include:

```gitignore
logs/
*.log
```

## Direct service tests

Test the local LLM client:

```powershell
python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
```

Test document summarization:

```powershell
python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
```

## Implemented version history

### v0.1.0 — Local document handling and search

- FastAPI application structure.
- Health endpoint.
- Local `.txt` and `.md` document discovery.
- Document content retrieval.
- Case-insensitive keyword search.

### v0.2.0 — Local LLM document summarization

- Ollama integration.
- Environment-based model configuration.
- Local LLM client.
- Reusable summarization prompt.
- Document summarization service.
- `POST /summarize` endpoint.

### v0.2.1 — Centralized application logging

- Console logging.
- Rotating general log file.
- Request-level visual separators.
- Logging across endpoints and internal services.
- Privacy-aware operational logging.

### v0.2.2 — LLM input/output logging

- Dedicated local log for complete prompts and model responses.
- LLM interaction metadata for debugging and traceability.
- Separation between privacy-aware operational logs and sensitive LLM interaction logs.

## Current limitations

- Only `.txt` and `.md` documents are supported.
- Summarization sends the complete document to the local model.
- Large documents may exceed the model context window.
- There is no chunking, embedding generation, vector database, RAG, agent, MCP server, or frontend.

## Privacy considerations

- Documents and inference remain in the local environment when Ollama is configured locally.
- `.env`, `logs/app.log`, and `logs/llm_io.log` must not be committed.
- `logs/llm_io.log` can contain complete private document text.
- Access to the machine, project directory, and log files must be restricted according to the sensitivity of the processed documents.