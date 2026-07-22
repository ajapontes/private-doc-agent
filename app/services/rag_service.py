"""
Retrieval-augmented generation service.

This module coordinates semantic retrieval and local text generation. It
builds a source-labelled context from the retrieved document chunks, sends a
grounded prompt to the configured local LLM, and returns the answer together
with traceable source metadata.

Logging strategy:
- Logs result limits, match counts, prompt length, and answer length.
- Does not log questions, document content, prompts, or generated answers.
"""

import logging

from app.config import BASE_DIR
from app.services.llm_client import LLMClientError, generate_text
from app.services.retrieval_service import (
    RetrievalServiceError,
    retrieve_relevant_chunks,
)


logger = logging.getLogger(__name__)

PROMPT_PATH = BASE_DIR / "app" / "prompts" / "rag_prompt.txt"
NO_CONTEXT_ANSWER = (
    "No se encontró información suficiente en los documentos disponibles."
)


class RAGServiceError(Exception):
    """Raised when a grounded answer cannot be generated."""

    pass


def load_rag_prompt_template() -> str:
    """Loads the RAG prompt template from the prompts directory."""
    if not PROMPT_PATH.exists():
        logger.error("RAG prompt template not found. path=%s", PROMPT_PATH)
        raise RAGServiceError(f"RAG prompt template not found: {PROMPT_PATH}")

    template = PROMPT_PATH.read_text(encoding="utf-8")
    logger.info("RAG prompt template loaded. template_length=%s", len(template))
    return template


def build_rag_context(matches: list[dict]) -> str:
    """Formats retrieved chunks as clearly delimited, source-labelled evidence."""
    context_blocks = []

    for source_number, match in enumerate(matches, start=1):
        context_blocks.append(
            "\n".join(
                [
                    f"[Source {source_number}]",
                    f"Filename: {match['filename']}",
                    f"Chunk ID: {match['chunk_id']}",
                    "Content:",
                    match["content"],
                ]
            )
        )

    return "\n\n".join(context_blocks)


def build_rag_prompt(question: str, matches: list[dict]) -> str:
    """Injects the normalized question and retrieved evidence into the template."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not matches:
        raise ValueError("At least one retrieved match is required.")

    template = load_rag_prompt_template()
    context = build_rag_context(matches)
    return template.replace("{question}", question.strip()).replace(
        "{context}", context
    )


def answer_question(question: str, top_k: int = 3) -> dict:
    """
    Answers a question using only semantically retrieved document evidence.

    Empty retrieval results are returned without calling the LLM. Retrieval
    and generation failures are exposed as a single RAG-layer exception.
    """
    try:
        retrieval_result = retrieve_relevant_chunks(question, top_k=top_k)
    except (ValueError, TypeError):
        raise
    except RetrievalServiceError as error:
        logger.error("RAG retrieval failed. top_k=%s error=%s", top_k, error)
        raise RAGServiceError(f"Unable to retrieve RAG context: {error}") from error

    normalized_question = retrieval_result["question"]
    matches = retrieval_result["matches"]

    if not matches:
        logger.info("RAG generation skipped because no context was retrieved.")
        return {
            "question": normalized_question,
            "answer": NO_CONTEXT_ANSWER,
            "sources": [],
        }

    prompt = build_rag_prompt(normalized_question, matches)

    try:
        answer = generate_text(prompt)
    except LLMClientError as error:
        logger.error("RAG generation failed. top_k=%s error=%s", top_k, error)
        raise RAGServiceError(f"Unable to generate grounded answer: {error}") from error

    sources = [
        {
            "filename": match["filename"],
            "chunk_id": match["chunk_id"],
            "similarity": match["similarity"],
        }
        for match in matches
    ]

    logger.info(
        "RAG answer generated. sources=%s prompt_length=%s answer_length=%s",
        len(sources),
        len(prompt),
        len(answer),
    )

    return {
        "question": normalized_question,
        "answer": answer,
        "sources": sources,
    }
