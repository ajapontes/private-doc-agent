"""
HTTP API tests for single-step local agent execution.

These tests replace the agent service with controlled results or failures.
They verify response serialization, HTTP error mapping, request forwarding,
schema validation, and logging privacy without calling Ollama or local tools.
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.agent_service import (
    AgentExecutionError,
    AgentPlanningError,
    AgentResult,
)
from app.services.tool_planner import ToolPlan


class AgentApiTests(unittest.TestCase):
    """Validates the public endpoint for the single-step local agent."""

    @staticmethod
    def _agent_result():
        """Returns a representative serializable agent result."""
        return AgentResult(
            plan=ToolPlan(
                tool="list_documents",
                arguments={},
            ),
            result={
                "documents": ["demo.txt"],
                "count": 1,
            },
        )

    @patch("app.main.run_agent")
    def test_agent_endpoint_returns_plan_tool_and_result(self, mock_run_agent):
        """POST /agent returns the complete auditable agent response."""
        mock_run_agent.return_value = self._agent_result()

        with TestClient(app) as client:
            response = client.post(
                "/agent",
                json={"request": "List the available documents."},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["plan"]["tool"], "list_documents")
        self.assertEqual(response.json()["tools_used"], ["list_documents"])
        self.assertEqual(response.json()["result"]["count"], 1)

    @patch("app.main.run_agent")
    def test_agent_endpoint_forwards_user_request(self, mock_run_agent):
        """The endpoint forwards the natural-language request unchanged."""
        mock_run_agent.return_value = self._agent_result()
        user_request = "List the available documents."

        with TestClient(app) as client:
            client.post("/agent", json={"request": user_request})

        mock_run_agent.assert_called_once_with(user_request)

    @patch("app.main.run_agent")
    def test_empty_agent_request_returns_400(self, mock_run_agent):
        """An empty request rejected by the service maps to HTTP 400."""
        mock_run_agent.side_effect = ValueError("User request cannot be empty.")

        with TestClient(app) as client:
            response = client.post("/agent", json={"request": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "User request cannot be empty.",
        )

    def test_missing_agent_request_returns_422(self):
        """FastAPI rejects a payload without the required request field."""
        with TestClient(app) as client:
            response = client.post("/agent", json={})

        self.assertEqual(response.status_code, 422)

    @patch("app.main.run_agent")
    def test_agent_planning_failure_returns_422(self, mock_run_agent):
        """Controlled planning failures map to HTTP 422."""
        mock_run_agent.side_effect = AgentPlanningError(
            "Unable to plan local agent action."
        )

        with TestClient(app) as client:
            response = client.post(
                "/agent",
                json={"request": "List the available documents."},
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"],
            "Unable to plan local agent action.",
        )

    @patch("app.main.run_agent")
    def test_agent_execution_failure_returns_500(self, mock_run_agent):
        """Controlled tool execution failures map to HTTP 500."""
        mock_run_agent.side_effect = AgentExecutionError(
            "Unable to execute planned tool."
        )

        with TestClient(app) as client:
            response = client.post(
                "/agent",
                json={"request": "List the available documents."},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["detail"],
            "Unable to execute planned tool.",
        )

    @patch("app.main.run_agent")
    def test_agent_logs_do_not_expose_request_or_result(self, mock_run_agent):
        """Operational logs contain metrics but no private request or result."""
        private_request = "CONFIDENTIAL agent request"
        private_result = "CONFIDENTIAL tool result"
        mock_run_agent.return_value = AgentResult(
            plan=ToolPlan(tool="read_document", arguments={"filename": "private.txt"}),
            result={"content": private_result},
        )

        with self.assertLogs("app.main", level="INFO") as captured_logs:
            with TestClient(app) as client:
                response = client.post(
                    "/agent",
                    json={"request": private_request},
                )

        log_output = "\n".join(captured_logs.output)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"request_length={len(private_request)}", log_output)
        self.assertIn("tools_used=1", log_output)
        self.assertNotIn(private_request, log_output)
        self.assertNotIn(private_result, log_output)


if __name__ == "__main__":
    unittest.main()
