"""Unit tests for the local tool registry."""

import unittest
from unittest.mock import patch

from app.services.tool_registry import (
    ToolArgument,
    ToolArgumentError,
    ToolDefinition,
    ToolExecutionError,
    ToolNotFoundError,
    ToolRegistry,
    tool_registry,
)


class ToolRegistryTests(unittest.TestCase):
    """Validates tool metadata, argument contracts, execution, and failures."""

    def test_default_registry_exposes_six_tools_without_handlers(self):
        """Public metadata lists the allowlisted tools and serializable arguments."""
        tools = tool_registry.list_tools()

        self.assertEqual(
            {tool["name"] for tool in tools},
            {
                "list_documents",
                "read_document",
                "search_documents",
                "summarize_document",
                "retrieve_context",
                "answer_with_rag",
            },
        )
        self.assertNotIn("handler", tools[0])

        retrieve_tool = next(
            tool for tool in tools if tool["name"] == "retrieve_context"
        )
        top_k = next(
            argument
            for argument in retrieve_tool["arguments"]
            if argument["name"] == "top_k"
        )
        self.assertEqual(top_k["type"], "int")
        self.assertFalse(top_k["required"])
        self.assertEqual(top_k["default"], 3)

    def test_custom_tool_is_registered_and_executed(self):
        """A declared handler receives validated arguments."""
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="repeat",
                description="Repeat text.",
                arguments=(ToolArgument("text", str, "Text to repeat."),),
                handler=lambda text: {"text": text},
            )
        )

        self.assertEqual(
            registry.execute("repeat", {"text": "private"}),
            {"text": "private"},
        )

    def test_duplicate_tool_name_is_rejected(self):
        """Registration cannot silently replace an existing handler."""
        tool = ToolDefinition("same", "Description.", (), lambda: None)
        registry = ToolRegistry((tool,))

        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(tool)

    def test_unknown_tool_is_rejected(self):
        """Only explicitly registered tool names can be executed."""
        with self.assertRaisesRegex(ToolNotFoundError, "Unknown tool"):
            tool_registry.execute("delete_everything")

    def test_missing_required_argument_is_rejected(self):
        """Required arguments are checked before invoking a handler."""
        with self.assertRaisesRegex(ToolArgumentError, "filename"):
            tool_registry.execute("read_document", {})

    def test_unexpected_argument_is_rejected(self):
        """Undeclared arguments cannot reach the underlying function."""
        with self.assertRaisesRegex(ToolArgumentError, "Unexpected arguments"):
            tool_registry.execute(
                "list_documents",
                {"directory": "outside-input"},
            )

    def test_invalid_argument_type_is_rejected(self):
        """Declared basic types are enforced, including bool versus int."""
        for invalid_top_k in ("3", 1.5, True):
            with self.subTest(top_k=invalid_top_k):
                with self.assertRaisesRegex(ToolArgumentError, "must be int"):
                    tool_registry.execute(
                        "retrieve_context",
                        {"question": "What is documented?", "top_k": invalid_top_k},
                    )

    @patch("app.services.tool_registry.list_documents")
    def test_list_documents_returns_counted_result(self, mock_list_documents):
        """The list wrapper returns the same API-oriented result shape."""
        mock_list_documents.return_value = [{"filename": "demo.txt"}]

        result = tool_registry.execute("list_documents")

        self.assertEqual(
            result,
            {"documents": [{"filename": "demo.txt"}], "count": 1},
        )

    @patch("app.services.tool_registry.retrieve_relevant_chunks")
    def test_optional_top_k_uses_declared_default(self, mock_retrieve):
        """Optional arguments are supplied with their registered default."""
        mock_retrieve.return_value = {
            "question": "What is documented?",
            "matches": [],
        }

        result = tool_registry.execute(
            "retrieve_context",
            {"question": "What is documented?"},
        )

        self.assertEqual(result["matches"], [])
        mock_retrieve.assert_called_once_with(
            question="What is documented?",
            top_k=3,
        )

    def test_input_failure_becomes_argument_error(self):
        """Expected validation failures remain distinct from internal failures."""
        registry = ToolRegistry(
            (
                ToolDefinition(
                    "validate",
                    "Validate input.",
                    (),
                    lambda: (_ for _ in ()).throw(ValueError("Invalid value.")),
                ),
            )
        )

        with self.assertRaisesRegex(ToolArgumentError, "Invalid value"):
            registry.execute("validate")

    def test_internal_failure_becomes_execution_error(self):
        """Unexpected handler failures are wrapped consistently."""
        registry = ToolRegistry(
            (
                ToolDefinition(
                    "fail",
                    "Fail internally.",
                    (),
                    lambda: (_ for _ in ()).throw(RuntimeError("Unavailable")),
                ),
            )
        )

        with self.assertRaisesRegex(ToolExecutionError, "Unavailable"):
            registry.execute("fail")


if __name__ == "__main__":
    unittest.main()
