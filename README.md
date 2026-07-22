# private-doc-agent

Private Doc Agent is a local-first API for reading, searching, indexing, and querying private documents. Document processing, vector storage, embeddings, and language-model inference run locally through FastAPI, ChromaDB, and Ollama.

## Current version

`v0.3.0`

## Implemented capabilities

- FastAPI backend with interactive OpenAPI documentation.
- Discovery and reading of local `.txt` and `.md` documents.
- Case-insensitive keyword search.
- Document summarization with a local Ollama model.
- Configurable text chunking with overlap.
- Local document and query embeddings through Ollama.
- Persistent local vector storage with ChromaDB.
- Indexing of one document or all supported documents.
- Semantic retrieval of relevant document chunks.
- Retrieval-augmented generation (RAG) with traceable sources.
- Grounded answers based only on retrieved document evidence.
- Centralized console and rotating-file logging.
- Separate local logging of complete LLM prompts and responses for debugging.
- Automated tests for chunking, embeddings, vector storage, indexing, retrieval, RAG, API endpoints, and logging.

Agents, MCP integrations, a frontend, and support for document formats other than `.txt` and `.md` are not implemented in this version.

## Architecture

```text
Client / Swagger
       |
       v
    FastAPI
       |
       +--------------------+---------------------+
       |                    |                     |
       v                    v                     v
Document operations   Indexing pipeline      RAG query pipeline
list / read / search  load -> chunk           question embedding
summarize             -> embeddings           -> ChromaDB search
                      -> ChromaDB              -> RAG prompt
                                               -> local LLM
                                               -> answer + sources
```

Keyword search is literal and does not use embeddings. Semantic retrieval and RAG require documents to be indexed first.

## Project structure

```text
private-doc-agent/
  app/
    main.py
    config.py
    logging_config.py
    prompts/
      summarize_prompt.txt
      rag_prompt.txt
    services/
      document_loader.py
      simple_search.py
      document_chunker.py
      embedding_service.py
      vector_store.py
      indexing_service.py
      retrieval_service.py
      llm_client.py
      summarizer.py
      rag_service.py
  data/
    input/
    chroma/
  logs/
    app.log
    llm_io.log
  tests/
  .env.example
  .gitignore
  README.md
  requirements.txt
```

The `data/chroma/` and `logs/` directories are generated locally and must not be committed.

## Requirements

- Python 3.11 or later.
- Ollama installed and running locally.
- A local text-generation model, such as `qwen3.5:4b`.
- A local embedding model, such as `nomic-embed-text-v2-moe:latest`.
- Dependencies listed in `requirements.txt`.

## Local deployment

### 1. Clone the repository

```powershell
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the environment

Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Default configuration:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text-v2-moe:latest
EMBEDDING_BATCH_SIZE=32
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHROMA_COLLECTION_NAME=private_documents
```

`CHUNK_OVERLAP` must be smaller than `CHUNK_SIZE`. The `.env` file contains local configuration and must not be committed.

### 5. Start and validate Ollama

Confirm that Ollama is available:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434
ollama list
```

Install the configured models if necessary:

```powershell
ollama pull qwen3.5:4b
ollama pull nomic-embed-text-v2-moe:latest
```

### 6. Add documents

Copy supported `.txt` or `.md` files into:

```text
data/input/
```

### 7. Start the API

```powershell
uvicorn app.main:app --reload
```

API base URL:

```text
http://127.0.0.1:8000
```

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

## Recommended RAG workflow

1. Add documents to `data/input/`.
2. Index one document with `POST /documents/{filename}/index` or all documents with `POST /documents/index`.
3. Inspect semantic matches with `POST /retrieve` when needed.
4. Ask grounded questions with `POST /ask`.

Reindex a document after changing its content. The indexing workflow replaces that document's previously stored chunks only after the new embeddings have been generated successfully.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Return application health and version. |
| `GET` | `/documents` | List supported local documents. |
| `GET` | `/documents/{filename}` | Read a document. |
| `POST` | `/documents/index` | Index all supported documents. |
| `POST` | `/documents/{filename}/index` | Index one document. |
| `POST` | `/search` | Perform literal keyword search. |
| `POST` | `/retrieve` | Retrieve semantically related chunks. |
| `POST` | `/summarize` | Summarize one complete document. |
| `POST` | `/ask` | Generate a RAG answer with source metadata. |

### Health check

```http
GET /health
```

```json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.3.0"
}
```

### Index all documents

```http
POST /documents/index
```

The response reports the number of documents and chunks indexed, plus the embedding model and vector dimension for each document.

### Index one document

```http
POST /documents/demo.md/index
```

Example response:

```json
{
  "filename": "demo.md",
  "chunks_indexed": 2,
  "vector_dimension": 768,
  "embedding_model": "nomic-embed-text-v2-moe:latest"
}
```

### Keyword search

```http
POST /search
```

```json
{
  "query": "RAG"
}
```

### Semantic retrieval

```http
POST /retrieve
```

```json
{
  "question": "What does the private document assistant do?",
  "top_k": 3
}
```

The response contains ranked matches with `filename`, `chunk_id`, content boundaries, chunk content, and cosine similarity.

### Ask a grounded question

```http
POST /ask
```

```json
{
  "question": "¿Qué hace el asistente de documentos privados?",
  "top_k": 2
}
```

Example response structure:

```json
{
  "question": "¿Qué hace el asistente de documentos privados?",
  "answer": "El asistente permite consultar documentos privados localmente...",
  "sources": [
    {
      "filename": "demo.txt",
      "chunk_id": 0,
      "similarity": 0.508248
    }
  ]
}
```

If retrieval returns no evidence, the service does not call the language model and returns an empty `sources` list with a controlled message.

### Summarize a document

```http
POST /summarize
```

```json
{
  "filename": "demo.md"
}
```

Summarization sends the complete document to the configured text-generation model and is separate from the chunk-based RAG flow.

## Logging

The application writes logs to the console and uses rotating local files to prevent unlimited growth.

### Operational log

```text
logs/app.log
```

This log records request flow, filenames, model names, endpoints, counts, dimensions, lengths, and errors. The RAG and embedding flows avoid writing questions, retrieved content, full prompts, responses, and vectors to this log.

View recent entries or follow the log:

```powershell
Get-Content .\logs\app.log -Tail 80
Get-Content .\logs\app.log -Wait
```

### LLM input/output log

```text
logs/llm_io.log
```

This debugging log contains complete prompts and model responses. Because RAG prompts can include private document fragments, this file may contain sensitive information and must remain local.

```powershell
Get-Content .\logs\llm_io.log -Tail 120
Get-Content .\logs\llm_io.log -Wait
```

Repository ignore rules cover `.env`, `logs/`, `*.log`, and `data/chroma/`.

## Tests

Run the complete automated suite:

```powershell
python -m unittest discover -s tests -v
```

The `v0.3.0` implementation contains 62 automated tests.

## Implemented version history

### v0.1.0 - Local document handling and search

- FastAPI application structure and health endpoint.
- Local `.txt` and `.md` discovery and reading.
- Case-insensitive keyword search.

### v0.2.0 - Local LLM summarization

- Ollama integration and environment-based configuration.
- Reusable prompt and document summarization service.
- `POST /summarize` endpoint.

### v0.2.1 - Centralized application logging

- Console and rotating-file logging.
- Request separators and privacy-aware operational metadata.

### v0.2.2 - LLM input/output logging

- Dedicated local log for complete prompts and model responses.
- Separation of operational metadata from sensitive LLM interactions.

### v0.3.0 - Basic local RAG

- Configurable document chunking with overlap.
- Local document and query embeddings through Ollama.
- Persistent ChromaDB vector store.
- Single-document and bulk indexing endpoints.
- Semantic retrieval through `POST /retrieve`.
- Grounded question answering through `POST /ask`.
- Source metadata and controlled no-context behavior.
- Logging support for direct service execution without duplicate handlers.
- Expanded automated test suite covering the RAG pipeline.

## Current limitations

- Only `.txt` and `.md` documents are supported.
- Summarization still sends the complete document to the model.
- Indexing must be triggered manually after adding or modifying documents.
- Retrieval uses a fixed `top_k`; reranking and similarity thresholds are not implemented.
- RAG source references identify files and chunks but do not yet expose page numbers.
- ChromaDB is intended for local, single-application use in this version.
- There is no authentication, authorization, frontend, agent orchestration, or MCP server.

## Privacy considerations

- Documents, embeddings, vector storage, and inference remain local when Ollama uses the configured local URL.
- `.env`, `data/chroma/`, `logs/app.log`, and `logs/llm_io.log` must not be committed.
- `logs/llm_io.log` can contain complete private document content included in prompts.
- Access to the machine, project directory, vector database, and logs must be restricted according to document sensitivity.
