# Changelog

All notable changes to Private Doc Agent are documented in this file.

The Spanish version is available in [CHANGELOG_ES.md](CHANGELOG_ES.md).

## [0.10.0] - 2026-08-17

### Added

- Optional `X-API-Key` authentication configured through `API_KEY`.
- Optional full operational endpoint protection through `API_KEY_PROTECT_ALL`.
- Automated unit and HTTP integration coverage for authentication behavior.

### Changed

- Administrative endpoints require the configured API key while preserving open local mode when no key is configured.
- Application version updated to `0.10.0`.
- English and Spanish security documentation synchronized.

### Security

- API keys are compared in constant time.
- Missing credentials return HTTP `401`; invalid credentials return HTTP `403`.
- Authentication rejection logs exclude configured and supplied secrets.
- Health and API documentation endpoints remain public when full protection is enabled.

## [0.9.0] - 2026-08-16

### Added

- Spanish changelog in `CHANGELOG_ES.md`, covering the complete project history.
- Cross-language links between the English and Spanish changelogs.

### Changed

- English and Spanish repository documentation synchronized for release `0.9.0`.
- Application version updated to `0.9.0`.

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
