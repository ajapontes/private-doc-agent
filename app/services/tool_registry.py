"""
Local tool registry for the Private Doc Agent.

This module exposes the application's existing document capabilities through
a small, controlled registry. Future agent components can inspect the
available tool descriptions and execute only explicitly registered functions.

Security and validation strategy:
- Only allowlisted tools can be executed.
- Arguments are validated by name, presence, and basic type before execution.
- Operational logs contain tool names and argument names, never document
  content or generated answers.
"""

import logging
from dataclasses import dataclass
from typing import Any, Callable

from app.services.document_loader import list_documents, read_document
from app.services.rag_service import answer_question
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document


logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    """Base exception for controlled tool-registry failures."""


class ToolNotFoundError(ToolRegistryError):
    """Raised when a requested tool is not registered."""


class ToolArgumentError(ToolRegistryError):
    """Raised when tool arguments are missing, unexpected, or invalid."""


class ToolExecutionError(ToolRegistryError):
    """Raised when a registered tool fails during execution."""


@dataclass(frozen=True)
class ToolArgument:
    """Describes one validated argument accepted by a local tool."""

    name: str
    argument_type: type
    description: str
    required: bool = True
    default: Any = None


@dataclass(frozen=True)
class ToolDefinition:
    """Defines the metadata and callable associated with a local tool."""

    name: str
    description: str
    arguments: tuple[ToolArgument, ...]
    handler: Callable[..., Any]

    def public_description(self) -> dict:
        """Returns serializable metadata without exposing the Python callable."""
        return {
            "name": self.name,
            "description": self.description,
            "arguments": [
                {
                    "name": argument.name,
                    "type": argument.argument_type.__name__,
                    "description": argument.description,
                    "required": argument.required,
                    **(
                        {"default": argument.default}
                        if not argument.required
                        else {}
                    ),
                }
                for argument in self.arguments
            ],
        }


def _list_documents_tool() -> dict:
    documents = list_documents()
    return {"documents": documents, "count": len(documents)}


def _read_document_tool(filename: str) -> dict:
    return {"filename": filename, "content": read_document(filename)}


def _search_documents_tool(query: str) -> dict:
    matches = search_keyword(query)
    return {"query": query, "matches": matches, "count": len(matches)}


def _summarize_document_tool(filename: str) -> dict:
    return {"filename": filename, "summary": summarize_document(filename)}


def _retrieve_context_tool(question: str, top_k: int = 3) -> dict:
    return retrieve_relevant_chunks(question=question, top_k=top_k)


def _answer_with_rag_tool(question: str, top_k: int = 3) -> dict:
    return answer_question(question=question, top_k=top_k)


class ToolRegistry:
    """Stores, describes, validates, and executes allowlisted local tools."""

    def __init__(self, tools: tuple[ToolDefinition, ...] = ()) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: ToolDefinition) -> None:
        """Registers one tool while preventing accidental name replacement."""
        if not isinstance(tool, ToolDefinition):
            raise TypeError("tool must be a ToolDefinition.")
        if not tool.name.strip():
            raise ValueError("Tool name cannot be empty.")
        if tool.name in self._tools:
            raise ValueError(f"Tool is already registered: {tool.name}")
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict]:
        """Returns public metadata for every registered tool."""
        return [
            tool.public_description()
            for tool in sorted(self._tools.values(), key=lambda item: item.name)
        ]

    def execute(self, name: str, arguments: dict | None = None) -> Any:
        """Validates and executes one registered tool."""
        if not isinstance(name, str) or not name.strip():
            raise ToolNotFoundError("Tool name cannot be empty.")

        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Unknown tool: {name}")

        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            raise ToolArgumentError("Tool arguments must be a dictionary.")

        validated_arguments = self._validate_arguments(tool, arguments)
        logger.info(
            "Executing local tool. tool=%s argument_names=%s",
            name,
            sorted(validated_arguments),
        )

        try:
            result = tool.handler(**validated_arguments)
        except (FileNotFoundError, ValueError, TypeError) as error:
            logger.warning("Local tool rejected input. tool=%s error=%s", name, error)
            raise ToolArgumentError(str(error)) from error
        except Exception as error:
            logger.error("Local tool execution failed. tool=%s error=%s", name, error)
            raise ToolExecutionError(f"Tool '{name}' failed: {error}") from error

        logger.info("Local tool execution completed. tool=%s", name)
        return result

    @staticmethod
    def _validate_arguments(
        tool: ToolDefinition,
        supplied_arguments: dict,
    ) -> dict:
        """Applies the declared argument contract for one tool."""
        definitions = {argument.name: argument for argument in tool.arguments}
        unexpected = sorted(set(supplied_arguments) - set(definitions))
        if unexpected:
            raise ToolArgumentError(
                f"Unexpected arguments for '{tool.name}': {', '.join(unexpected)}"
            )

        validated = {}
        for argument in tool.arguments:
            if argument.name not in supplied_arguments:
                if argument.required:
                    raise ToolArgumentError(
                        f"Missing required argument for '{tool.name}': "
                        f"{argument.name}"
                    )
                validated[argument.name] = argument.default
                continue

            value = supplied_arguments[argument.name]
            expected_type = argument.argument_type
            is_valid = isinstance(value, expected_type)
            if expected_type is int and isinstance(value, bool):
                is_valid = False
            if not is_valid:
                raise ToolArgumentError(
                    f"Argument '{argument.name}' for '{tool.name}' must be "
                    f"{expected_type.__name__}."
                )
            validated[argument.name] = value

        return validated


DEFAULT_TOOLS = (
    ToolDefinition(
        name="list_documents",
        description="List supported documents available in the local input folder.",
        arguments=(),
        handler=_list_documents_tool,
    ),
    ToolDefinition(
        name="read_document",
        description="Read the extracted text of one supported local document.",
        arguments=(
            ToolArgument("filename", str, "Name of the document to read."),
        ),
        handler=_read_document_tool,
    ),
    ToolDefinition(
        name="search_documents",
        description="Search a keyword or phrase across local documents.",
        arguments=(
            ToolArgument("query", str, "Keyword or phrase to search for."),
        ),
        handler=_search_documents_tool,
    ),
    ToolDefinition(
        name="summarize_document",
        description="Summarize one local document with the configured local LLM.",
        arguments=(
            ToolArgument("filename", str, "Name of the document to summarize."),
        ),
        handler=_summarize_document_tool,
    ),
    ToolDefinition(
        name="retrieve_context",
        description="Retrieve document chunks semantically related to a question.",
        arguments=(
            ToolArgument("question", str, "Question used for semantic retrieval."),
            ToolArgument(
                "top_k",
                int,
                "Maximum number of relevant chunks.",
                required=False,
                default=3,
            ),
        ),
        handler=_retrieve_context_tool,
    ),
    ToolDefinition(
        name="answer_with_rag",
        description="Answer a question using evidence from indexed documents.",
        arguments=(
            ToolArgument("question", str, "Question to answer from documents."),
            ToolArgument(
                "top_k",
                int,
                "Maximum number of evidence chunks.",
                required=False,
                default=3,
            ),
        ),
        handler=_answer_with_rag_tool,
    ),
)


tool_registry = ToolRegistry(DEFAULT_TOOLS)
