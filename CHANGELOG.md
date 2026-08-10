# Changelog

All notable changes to Private Doc Agent are documented in this file.

## [0.8.0] - 2026-08-10

### Added

- Component-level `/health` diagnostics for Ollama and the local vector store.
- Configurable retry handling for transient Ollama connection and server failures.
- Regression coverage for unsupported formats, infrastructure failures, safe reindexing, and exact filename preservation.

### Changed

- Unsupported input formats, including `.xlsx`, are detected during bulk indexing and moved to `data/invalid/` without stopping valid documents.
- Reindexing upserts the new chunks before deleting only obsolete chunks, preserving the previous index when generation or persistence fails.
- Ollama and ChromaDB failures are classified as infrastructure errors and exposed as HTTP `503` responses.
- Physical filenames are preserved exactly; the application does not guess corrections or rename names that appear damaged.
- Application version updated to `0.8.0`.

### Fixed

- Agent plans without an `arguments` property are handled safely.
- Unsupported files are no longer silently ignored by bulk indexing.

## [0.7.0] - 2026-08-08

### Added

- Local `data/invalid/` quarantine for documents that cannot be processed.
- Collision-safe invalid-document movement that preserves existing files.
- Configurable `DETAILED_TRACE_ENABLED` structured diagnostics for the local agent.
- Spanish repository documentation in `README_ES.md`.
- `.env.example` with the supported runtime configuration.
- Automated tests for quarantine, resilient bulk indexing, and trace privacy.

### Changed

- Bulk indexing continues with valid documents after a document-level error.
- Bulk-index responses include invalid-document counts and processing details.
- Application version updated to `0.7.0`.

### Security

- Detailed traces exclude user requests, document contents, prompts, argument values, and tool results.
- Invalid-document storage remains local and excluded from Git.

## [0.6.0]

- Configurable vector distance metrics, retrieval settings, normalized relevance scores, and safe collection reset.

## [0.5.0]

- Allowlisted single-step local tool agent with validated planning and execution.

## [0.4.0]

- PDF and DOCX ingestion integrated with the local RAG pipeline.

## [0.3.0]

- Local embeddings, ChromaDB indexing, semantic retrieval, and grounded RAG.

## [0.2.0]

- Local Ollama summarization and privacy-aware logging improvements.

## [0.1.0]

- FastAPI foundation, document discovery, reading, and keyword search.
