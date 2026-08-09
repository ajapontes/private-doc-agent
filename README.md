# private-doc-agent

Private Doc Agent is a local-first API for reading, searching, indexing, and querying private documents. Document processing, vector storage, embeddings, and language-model inference run locally through FastAPI, ChromaDB, and Ollama.

## Current version

`v0.7.0`

Documentation is also available in [Spanish](README_ES.md).

## Implemented capabilities

- FastAPI backend with interactive OpenAPI documentation.
- Discovery, text extraction, and reading of local `.txt`, `.md`, `.pdf`, and `.docx` documents.
- Case-insensitive keyword search.
- Document summarization with a local Ollama model.
- Configurable text chunking with overlap.
- Local document and query embeddings through Ollama.
- Persistent local vector storage with ChromaDB.
- Indexing of one document or all supported documents.
- Resilient bulk indexing that quarantines invalid documents in `data/invalid/` and continues processing valid files.
- Semantic retrieval of relevant document chunks.
- Retrieval-augmented generation (RAG) with traceable sources.
- Grounded answers based on retrieved document evidence.
- Single-step local agent execution through an allowlisted tool registry.
- Configurable vector distance metric (`cosine`, `l2`, or `ip`).
- Configurable retrieval result count and optional minimum relevance score.
- Safe vector collection reset with explicit confirmation.
- Controlled behavior when the available documents do not provide sufficient context.
- Centralized console and rotating-file logging.
- Separate local logging of complete LLM prompts and responses for debugging.
- Optional structured agent trace showing stages, components, tool decisions, and execution metadata without request or document content.
- Automated tests for document loading, chunking, embeddings, vector storage, indexing, retrieval, RAG, agent execution, API endpoints, configuration, reset operations, and logging.

Multi-step agent orchestration, MCP integrations, a frontend, and formats other than `.txt`, `.md`, `.pdf`, and `.docx` are not implemented in this version.

## Architecture

```text
Client / Swagger
       |
       v
    FastAPI
       |
       +----------------+----------------+----------------+
       |                |                |                |
       v                v                v                v
Document operations  Indexing/RAG    Local agent    Administration
list/read/search     chunk/embed     plan request   confirm reset
summarize            ChromaDB        select tool    recreate collection
                     retrieve/ask    execute once   configured metric
```

### Main components

- **FastAPI:** exposes the application endpoints and interactive API documentation.
- **Document loader:** discovers supported files and extracts their text through a unified interface.
- **Document chunker:** divides extracted text into overlapping fragments.
- **Embedding service:** creates document and query embeddings through Ollama.
- **ChromaDB vector store:** persists embeddings and metadata locally using the configured distance metric.
- **Indexing service:** coordinates loading, chunking, embedding generation, and storage.
- **Retrieval service:** finds the chunks most closely related to a question.
- **RAG service:** builds a grounded prompt, invokes the local model, and returns the answer with its sources.
- **Tool registry and planner:** expose allowlisted local tools and select one tool for a request.
- **Agent service:** validates the plan, executes one allowed tool, and returns a traceable result.
- **Administrative reset:** safely recreates only the configured ChromaDB collection after explicit confirmation.
- **Logging:** separates operational metadata from complete, potentially sensitive LLM interactions.

## Supported document formats

| Format | Extension | Processing |
|---|---|---|
| Plain text | `.txt` | Read directly as text. |
| Markdown | `.md` | Read directly as text. |
| PDF | `.pdf` | Extract text from the document's embedded text layer. |
| Microsoft Word | `.docx` | Extract text from document paragraphs. |

Place local documents in:

```text
data/input/
```

New files in this directory are ignored by Git to prevent private documents from being added accidentally. The versioned `demo.txt`, `demo.md`, and `demo.pdf` files remain available for development and testing.

## Requirements

- Python 3.11 or later.
- Ollama installed and running locally.
- A local generation model configured through `OLLAMA_MODEL`.
- A local embedding model configured through the application settings.

The default Ollama URL is:

```text
http://localhost:11434
```

## Installation

Clone the repository:

```powershell
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
```

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a local environment file based on the example included in the repository, if available:

```powershell
Copy-Item .env.example .env
```

Review the values in `.env` and confirm that the required Ollama models are installed:

```powershell
ollama list
```

### Vector search configuration

The following values can be configured in `.env`:

| Variable | Default | Purpose |
|---|---:|---|
| `VECTOR_DISTANCE_METRIC` | `cosine` | ChromaDB distance metric: `cosine`, `l2`, or `ip`. |
| `VECTOR_SEARCH_TOP_K` | `5` | Default maximum number of chunks returned by `/retrieve` and supplied to `/ask`. |
| `VECTOR_MIN_RELEVANCE_SCORE` | empty | Optional normalized relevance threshold from `0` to `1`. |
| `DETAILED_TRACE_ENABLED` | `false` | Include a content-safe structured execution trace in successful `/agent` responses. |

Changing `VECTOR_DISTANCE_METRIC` requires recreating the collection and reindexing the documents. Use the confirmed administrative reset endpoint described below; the application never removes the complete ChromaDB directory.

## Run the API

Start the development server:

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Return application health and version. |
| `GET` | `/documents` | List supported local documents. |
| `GET` | `/documents/{filename}` | Read a supported document. |
| `POST` | `/documents/index` | Index all supported documents. |
| `POST` | `/documents/{filename}/index` | Index one document. |
| `POST` | `/search` | Perform literal keyword search. |
| `POST` | `/retrieve` | Retrieve semantically related chunks. |
| `POST` | `/summarize` | Summarize one complete document. |
| `POST` | `/ask` | Generate a grounded RAG answer with source metadata. |
| `POST` | `/agent` | Plan and execute one allowlisted local tool. |
| `POST` | `/admin/vector-store/reset` | Recreate the configured vector collection after explicit confirmation. |

### Health check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.6.0"
}
```

### List documents

```http
GET /documents
```

Returns the supported documents currently available in `data/input/`.

### Read a document

```http
GET /documents/demo.md
```

The document loader extracts and returns text using the appropriate reader for its format.

### Index all documents

```http
POST /documents/index
```

The response reports indexed and invalid document counts, quarantined files, chunks, and embedding information. An unreadable or empty document is moved to `data/invalid/`; remaining valid documents continue processing. Infrastructure failures such as an unavailable Ollama or ChromaDB service still stop the operation so valid documents are not misclassified.

### Index one document

```http
POST /documents/demo.md/index
```

Use this endpoint to rebuild the vector index for a single supported file.

### Keyword search

```http
POST /search
```

Performs a case-insensitive literal search over the available supported documents.

### Semantic retrieval

```http
POST /retrieve
```

Semantic retrieval embeds the query and returns the most relevant indexed chunks with document metadata, original distance, and normalized relevance score. Results use the configured metric, result count, and optional relevance threshold.

Documents must be indexed before they can be retrieved semantically.

### Document summarization

```http
POST /summarize
```

Summarization loads the selected document and sends its extracted text to the configured local Ollama model.

### Grounded question answering

```http
POST /ask
```

The RAG workflow:

1. Embeds the question.
2. Retrieves the most relevant indexed chunks.
3. Builds a prompt containing only the retrieved evidence.
4. Generates an answer with the local Ollama model.
5. Returns the answer and traceable source metadata.

Example response:

```json
{
  "question": "What is the main objective of the project?",
  "answer": "The project objective is described in the indexed documents.",
  "sources": [
    {
      "filename": "demo.pdf",
      "chunk_id": 0,
      "distance": 0.473012,
      "relevance_score": 0.526988
    }
  ]
}
```

If retrieval does not provide usable context, the API returns the controlled response:

```text
No sufficient information was found in the available documents.
```

### Local agent

```http
POST /agent
```

The local agent uses a dedicated planner prompt to select one allowlisted tool, validates its arguments, executes it once, and returns the result with tool-use metadata. It does not run an autonomous multi-step loop.

Set `DETAILED_TRACE_ENABLED=true` to include a `trace` array in successful responses. The trace identifies the request-validation, planning, decision, execution, and result stages together with the responsible function or component. It records only safe metadata such as lengths, tool names, argument names, and result types; it does not include the user request, document content, prompts, or tool results.

### Reset the vector collection

```http
POST /admin/vector-store/reset
Content-Type: application/json

{
  "confirm": true
}
```

The endpoint counts the stored chunks, deletes only the configured collection, and recreates it with the current distance metric. A missing or false confirmation is rejected with HTTP `400`. After a successful reset, index the documents again before using semantic retrieval or RAG.

## Local data and persistence

### Input documents

```text
data/input/
```

This directory contains documents available to the application. Private input files remain local and are excluded by the repository ignore rules.

### Vector database

```text
data/chroma/
```

ChromaDB persists document chunks, embeddings, and related metadata locally. This directory is not committed to Git.

### Invalid documents

```text
data/invalid/
```

Bulk indexing moves unreadable, damaged, encrypted, or empty documents to this local quarantine directory. Existing files are preserved by adding a numeric suffix to name collisions. The directory is excluded from Git.

### Logs

Operational application logs are written to the console and to rotating local log files. These logs record request flow, execution metadata, document operations, indexing, retrieval configuration, agent execution, vector reset events, and local LLM calls without storing complete document contents in the operational log.

Complete LLM prompts and responses are written separately to:

```text
logs/llm_io.log
```

This debugging log may include private document fragments supplied as RAG context. It must remain local and is excluded from Git.

To inspect the log in PowerShell:

```powershell
Get-Content .\logs\llm_io.log -Tail 120
Get-Content .\logs\llm_io.log -Wait
```

The Ollama client also records response metadata useful for local diagnostics, including generated response length, thinking length, completion reason, and token evaluation counts. Prompt and response contents remain confined to the separate LLM interaction log.

For supported Ollama models, thinking output is disabled in generation requests so the returned content is handled as the final answer. Missing and empty model responses produce controlled application errors instead of being accepted silently.

## Tests

Run the complete automated suite:

```powershell
python -m unittest discover -s tests -v
```

The `v0.7.0` implementation contains 146 automated tests, including resilient-ingestion, quarantine, and detailed-trace coverage.

The suite covers:

- Supported document discovery and loading.
- PDF and DOCX text extraction.
- Text chunking and overlap validation.
- Ollama embedding requests.
- ChromaDB storage and retrieval.
- Vector metric selection and distance-to-relevance conversion.
- Configurable result limits and minimum relevance filtering.
- Confirmed vector collection reset through the service and API.
- Single-document and bulk indexing.
- Semantic retrieval.
- RAG prompt construction and grounded answers.
- Source metadata and no-context behavior.
- Missing and empty Ollama responses.
- API endpoints.
- Tool registration, planning, local agent execution, and error handling.
- Environment configuration validation.
- Operational and LLM interaction logging.

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

### v0.4.0 - PDF and DOCX document ingestion

- Local text extraction from PDF and DOCX documents.
- Unified document loading for `.txt`, `.md`, `.pdf`, and `.docx` files.
- PDF and DOCX integration with the existing indexing and RAG pipelines.
- Protection of private input documents through repository ignore rules.
- Versioned demo documents preserved for development and testing.
- Disabled thinking output for supported Ollama models.
- Controlled handling of missing or empty Ollama responses.
- Additional LLM response metadata for local diagnostics.
- Expanded automated test suite with 76 tests.

### v0.5.0 - Local tool agent

- Allowlisted local tool registry.
- Dedicated tool-planning prompt and structured plan validation.
- Single-step agent service with controlled execution and traceable tool metadata.
- `POST /agent` endpoint and expanded error handling.
- Expanded automated test suite with 115 tests.

### v0.6.0 - Configurable vector search and safe reset

- Environment-based ChromaDB collection and vector search settings.
- Configurable `cosine`, `l2`, and `ip` distance metrics.
- Normalized relevance scores while preserving original ChromaDB distances.
- Configurable default `top_k` for retrieval and RAG.
- Optional minimum relevance score filtering.
- Safe collection reset requiring explicit confirmation.
- Administrative `POST /admin/vector-store/reset` endpoint.
- Privacy-aware operational logs for metric selection, retrieval, and reset events.
- Expanded automated test suite with 141 tests.

### v0.7.0 - Resilient ingestion and detailed diagnostics

- Invalid documents are moved to `data/invalid/` during bulk indexing.
- Valid documents continue indexing after a document-level failure.
- Infrastructure failures remain blocking and do not quarantine valid files.
- Optional structured trace for local-agent request, planning, decision, execution, and result stages.
- English and Spanish repository documentation maintained together.
- Privacy-aware logs and automated coverage for the new workflows.

## Current limitations

- Only `.txt`, `.md`, `.pdf`, and `.docx` documents are supported.
- Scanned PDFs without an embedded text layer require OCR, which is not implemented.
- Summarization sends the complete extracted document text to the model.
- Indexing must be triggered manually after adding or modifying documents.
- Reranking is not implemented; ranking relies on the configured ChromaDB distance metric.
- RAG source references identify files and chunks but do not expose PDF page numbers.
- ChromaDB is intended for local, single-application use in this version.
- The administrative reset endpoint does not yet have authentication or authorization and must not be exposed to untrusted networks.
- There is no frontend, multi-step agent orchestration, or MCP server.

## Privacy considerations

- Document processing, embeddings, vector storage, and model inference run locally.
- Private files placed in `data/input/` are ignored by Git unless explicitly versioned.
- Generated indexes, environment files, and logs are excluded from the repository.
- Operational logs avoid recording complete document contents.
- The dedicated LLM interaction log can contain prompts, answers, and retrieved private fragments; keep it on the local machine.
- Before sharing diagnostic information, review logs and API responses for document names or sensitive content.

## Repository

[github.com/ajapontes/private-doc-agent](https://github.com/ajapontes/private-doc-agent)
