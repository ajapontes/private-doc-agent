# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and answer questions over private documents.

The project starts with simple document loading and keyword search over `.txt` and `.md` files. Later, it will evolve into a local LLM-powered RAG assistant with tools, MCP and multi-agent validation.

## Current Version

v0.1.0

## Features

- FastAPI backend
- Health check endpoint
- Local document listing
- Support for `.txt` and `.md` files
- Simple keyword search across documents

## Project Structure

```text
private-doc-agent/
  app/
    main.py
    config.py
    services/
      document_loader.py
      simple_search.py
  data/
    input/
    processed/
  docs/
  tests/
  README.md
  requirements.txt