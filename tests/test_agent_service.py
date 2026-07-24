"""Unit tests for single-step local agent orchestration."""

import unittest
from unittest.mock import Mock, patch

from app.services.agent_service import (
    AgentExecutionError,
    AgentPlanningError,
    AgentResult,
    run_agent,
)
from app.services.tool_planner import InvalidToolPlanError, ToolPlan
from app.services.tool_registry import (
    ToolArgumentError,
    ToolDefinition,
    ToolRegistry,
)


class AgentServiceTests(unittest.TestCase):
    """Validates controlled planning, execution, errors, and output."""

    def setUp(self):
        """Creates an isolated registry without document or Ollama calls."""
        self.handler = Mock(return_value={"documents": ["guide.pdf"], "count": 1})
        self.registry = ToolRegistry(
            (
                ToolDefinition(
                    name="list_documents",
                    description="List documents.",
                    arguments=(),
                    handler=self.handler,
                ),
            )
        )

    @patch("app.services.agent_service.plan_tool")
    def test_valid_plan_executes_exactly_one_tool(self, mock_plan):
        """A valid plan reaches the registry once and returns its result."""
        mock_plan.return_value = ToolPlan(tool="list_documents", arguments={})

        response = run_agent("What documents are available?", self.registry)

        self.assertIsInstance(response, AgentResult)
        self.assertEqual(response.plan.tool, "list_documents")
        self.assertEqual(response.result["count"], 1)
        mock_plan.assert_called_once_with(
            "What documents are available?",
            self.registry,
        )
        self.handler.assert_called_once_with()

    @patch("app.services.agent_service.plan_tool")
    def test_result_has_serializable_api_contract(self, mock_plan):
        """The service exposes plan, tools used, and tool result."""
        mock_plan.return_value = ToolPlan(tool="list_documents", arguments={})

        response = run_agent("List documents", self.registry).to_dict()

        self.assertEqual(
            response,
            {
                "plan": {
                    "tool": "list_documents",
                    "arguments": {},
                },
                "tools_used": ["list_documents"],
                "result": {
                    "documents": ["guide.pdf"],
                    "count": 1,
                },
            },
        )

    @patch("app.services.agent_service.plan_tool")
    def test_request_is_trimmed_before_planning(self, mock_plan):
        """Surrounding whitespace is removed before calling the planner."""
        mock_plan.return_value = ToolPlan(tool="list_documents", arguments={})

        run_agent("  List documents  ", self.registry)

        mock_plan.assert_called_once_with("List documents", self.registry)

    @patch("app.services.agent_service.plan_tool")
    def test_empty_request_is_rejected_before_planning(self, mock_plan):
        """Blank requests cannot reach the planner or registry."""
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            run_agent("   ", self.registry)

        mock_plan.assert_not_called()
        self.handler.assert_not_called()

    def test_invalid_registry_is_rejected(self):
        """The orchestrator requires the controlled ToolRegistry contract."""
        with self.assertRaisesRegex(TypeError, "must be a ToolRegistry"):
            run_agent("List documents", registry={})

    @patch("app.services.agent_service.plan_tool")
    def test_planner_failure_is_wrapped_without_execution(self, mock_plan):
        """Invalid model output becomes an agent planning error."""
        mock_plan.side_effect = InvalidToolPlanError("Unknown planned tool")

        with self.assertRaisesRegex(AgentPlanningError, "Unknown planned tool"):
            run_agent("Delete everything", self.registry)

        self.handler.assert_not_called()

    @patch("app.services.agent_service.plan_tool")
    def test_registry_failure_is_wrapped_as_execution_error(self, mock_plan):
        """A plan that fails registry validation has a distinct error type."""
        mock_plan.return_value = ToolPlan(
            tool="list_documents",
            arguments={"directory": "../private"},
        )

        with self.assertRaisesRegex(
            AgentExecutionError,
            "Unable to execute planned tool",
        ):
            run_agent("List another directory", self.registry)

        self.handler.assert_not_called()

    @patch("app.services.agent_service.plan_tool")
    def test_execution_error_keeps_original_cause(self, mock_plan):
        """Controlled errors retain the registry exception for diagnostics."""
        mock_plan.return_value = ToolPlan(
            tool="list_documents",
            arguments={"unexpected": True},
        )

        with self.assertRaises(AgentExecutionError) as context:
            run_agent("List documents", self.registry)

        self.assertIsInstance(context.exception.__cause__, ToolArgumentError)

    @patch("app.services.agent_service.plan_tool")
    def test_agent_does_not_request_a_second_plan(self, mock_plan):
        """The initial agent version is deliberately limited to one step."""
        mock_plan.return_value = ToolPlan(tool="list_documents", arguments={})

        run_agent("List documents", self.registry)

        self.assertEqual(mock_plan.call_count, 1)
        self.assertEqual(self.handler.call_count, 1)


if __name__ == "__main__":
    unittest.main()
