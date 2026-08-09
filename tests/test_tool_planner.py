"""Unit tests for local tool planning with Ollama."""

import json
import unittest
from unittest.mock import patch

from app.services.llm_client import LLMClientError
from app.services.tool_planner import (
    InvalidToolPlanError,
    ToolPlannerError,
    build_tool_planner_prompt,
    plan_tool,
)


class ToolPlannerTests(unittest.TestCase):
    """Validates prompt construction, strict JSON, and registry contracts."""

    def test_prompt_contains_request_and_public_tool_metadata(self):
        """The prompt describes allowlisted tools without exposing handlers."""
        prompt = build_tool_planner_prompt("List my documents")

        self.assertIn("List my documents", prompt)
        self.assertIn('"name": "list_documents"', prompt)
        self.assertIn('"name": "answer_with_rag"', prompt)
        self.assertNotIn("handler", prompt)
        self.assertIn("Return only one valid JSON object", prompt)

    def test_empty_request_is_rejected_before_calling_llm(self):
        """Blank requests never reach the local model."""
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            plan_tool("   ")

    @patch("app.services.tool_planner.generate_text")
    def test_valid_plan_is_returned_without_executing_tool(self, mock_generate):
        """A valid model proposal becomes a serializable ToolPlan."""
        mock_generate.return_value = json.dumps(
            {
                "tool": "read_document",
                "arguments": {"filename": "guide.pdf"},
            }
        )

        plan = plan_tool("Read guide.pdf")

        self.assertEqual(plan.tool, "read_document")
        self.assertEqual(plan.arguments, {"filename": "guide.pdf"})
        self.assertEqual(
            plan.to_dict(),
            {
                "tool": "read_document",
                "arguments": {"filename": "guide.pdf"},
            },
        )
        mock_generate.assert_called_once()

    @patch("app.services.tool_planner.generate_text")
    def test_tool_without_arguments_is_valid(self, mock_generate):
        """A no-argument tool must still provide an empty arguments object."""
        mock_generate.return_value = (
            '{"tool": "list_documents", "arguments": {}}'
        )

        plan = plan_tool("What documents are available?")

        self.assertEqual(plan.tool, "list_documents")
        self.assertEqual(plan.arguments, {})

    @patch("app.services.tool_planner.generate_text")
    def test_missing_arguments_key_is_normalized_for_no_argument_tool(
        self,
        mock_generate,
    ):
        """A missing arguments key becomes empty for a no-argument tool."""
        mock_generate.return_value = '{"tool": "list_documents"}'

        plan = plan_tool("What documents are available?")

        self.assertEqual(plan.tool, "list_documents")
        self.assertEqual(plan.arguments, {})

    @patch("app.services.tool_planner.generate_text")
    def test_missing_arguments_key_does_not_bypass_required_arguments(
        self,
        mock_generate,
    ):
        """Normalization does not bypass required tool arguments."""
        mock_generate.return_value = '{"tool": "read_document"}'

        with self.assertRaisesRegex(InvalidToolPlanError, "filename"):
            plan_tool("Read a document")

    @patch("app.services.tool_planner.generate_text")
    def test_invalid_json_is_rejected(self, mock_generate):
        """Markdown or explanatory text is not silently extracted."""
        mock_generate.return_value = (
            '```json\n{"tool": "list_documents", "arguments": {}}\n```'
        )

        with self.assertRaisesRegex(InvalidToolPlanError, "invalid JSON"):
            plan_tool("List documents")

    @patch("app.services.tool_planner.generate_text")
    def test_non_object_json_is_rejected(self, mock_generate):
        """The top-level response must be an object."""
        mock_generate.return_value = '["list_documents"]'

        with self.assertRaisesRegex(InvalidToolPlanError, "JSON object"):
            plan_tool("List documents")

    @patch("app.services.tool_planner.generate_text")
    def test_extra_top_level_key_is_rejected(self, mock_generate):
        """The model cannot add execution or control fields."""
        mock_generate.return_value = json.dumps(
            {
                "tool": "list_documents",
                "arguments": {},
                "execute": True,
            }
        )

        with self.assertRaisesRegex(InvalidToolPlanError, "unexpected keys"):
            plan_tool("List and execute")

    @patch("app.services.tool_planner.generate_text")
    def test_unknown_tool_is_rejected(self, mock_generate):
        """A model-proposed tool must exist in the registry."""
        mock_generate.return_value = (
            '{"tool": "delete_documents", "arguments": {}}'
        )

        with self.assertRaisesRegex(InvalidToolPlanError, "Unknown planned tool"):
            plan_tool("Delete everything")

    @patch("app.services.tool_planner.generate_text")
    def test_missing_required_argument_is_rejected(self, mock_generate):
        """Required registry arguments remain mandatory in model plans."""
        mock_generate.return_value = (
            '{"tool": "read_document", "arguments": {}}'
        )

        with self.assertRaisesRegex(InvalidToolPlanError, "filename"):
            plan_tool("Read a document")

    @patch("app.services.tool_planner.generate_text")
    def test_unexpected_argument_is_rejected(self, mock_generate):
        """The model cannot invent arguments for a registered tool."""
        mock_generate.return_value = json.dumps(
            {
                "tool": "list_documents",
                "arguments": {"directory": "../private"},
            }
        )

        with self.assertRaisesRegex(InvalidToolPlanError, "Unexpected arguments"):
            plan_tool("List another directory")

    @patch("app.services.tool_planner.generate_text")
    def test_invalid_argument_type_is_rejected(self, mock_generate):
        """Registry types are enforced before any future execution."""
        for invalid_top_k in ("3", 1.5, True):
            with self.subTest(top_k=invalid_top_k):
                mock_generate.return_value = json.dumps(
                    {
                        "tool": "retrieve_context",
                        "arguments": {
                            "question": "What is documented?",
                            "top_k": invalid_top_k,
                        },
                    }
                )

                with self.assertRaisesRegex(InvalidToolPlanError, "must be int"):
                    plan_tool("Retrieve context")

    @patch("app.services.tool_planner.generate_text")
    def test_llm_failure_is_wrapped(self, mock_generate):
        """Ollama failures become planner-layer errors."""
        mock_generate.side_effect = LLMClientError("Ollama unavailable")

        with self.assertRaisesRegex(ToolPlannerError, "Ollama unavailable"):
            plan_tool("List documents")


if __name__ == "__main__":
    unittest.main()
