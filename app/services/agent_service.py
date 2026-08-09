"""
Single-step local agent orchestration for the Private Doc Agent.

This module connects the tool planner with the allowlisted tool registry. A
user request produces exactly one validated plan and one controlled execution.
The service deliberately avoids loops and additional model calls so the first
agent flow remains predictable, auditable, and easy to test.

Privacy and safety strategy:
- Only a ToolPlan validated by the planner reaches the registry.
- Only the allowlisted registry executes the selected tool.
- Logs contain tool and argument names, never request or result content.
- Planning and execution failures are exposed as separate controlled errors.
"""

import logging
from dataclasses import dataclass
from typing import Any

from app.config import DETAILED_TRACE_ENABLED
from app.services.tool_planner import ToolPlan, ToolPlannerError, plan_tool
from app.services.tool_registry import (
    ToolRegistry,
    ToolRegistryError,
    tool_registry,
)


logger = logging.getLogger(__name__)


class AgentServiceError(Exception):
    """Base exception for controlled local-agent failures."""


class AgentPlanningError(AgentServiceError):
    """Raised when the local model cannot produce a valid tool plan."""


class AgentExecutionError(AgentServiceError):
    """Raised when the selected local tool cannot be executed."""


@dataclass(frozen=True)
class AgentResult:
    """Serializable result of one planned and executed local tool."""

    plan: ToolPlan
    result: Any
    trace: tuple[dict, ...] = ()

    def to_dict(self) -> dict:
        """Returns the public response contract for the future API endpoint."""
        response = {
            "plan": self.plan.to_dict(),
            "tools_used": [self.plan.tool],
            "result": self.result,
        }
        if self.trace:
            response["trace"] = list(self.trace)
        return response


def _trace_event(stage: str, component: str, action: str, **details: Any) -> dict:
    """Builds one content-safe structured diagnostic event."""
    return {
        "stage": stage,
        "component": component,
        "action": action,
        "details": details,
    }


def run_agent(
    user_request: str,
    registry: ToolRegistry = tool_registry,
    detailed_trace: bool = DETAILED_TRACE_ENABLED,
) -> AgentResult:
    """Plans and executes exactly one allowlisted tool for a user request."""
    if not isinstance(user_request, str) or not user_request.strip():
        raise ValueError("User request cannot be empty.")
    if not isinstance(registry, ToolRegistry):
        raise TypeError("registry must be a ToolRegistry.")

    trace = []
    if detailed_trace:
        trace.append(
            _trace_event(
                "request",
                "agent_service.run_agent",
                "validate_request",
                request_length=len(user_request.strip()),
            )
        )

    logger.info(
        "Starting local agent execution. request_length=%s available_tools=%s",
        len(user_request.strip()),
        len(registry.list_tools()),
    )

    try:
        if detailed_trace:
            trace.append(
                _trace_event(
                    "planning",
                    "tool_planner.plan_tool",
                    "select_allowlisted_tool",
                    available_tools=len(registry.list_tools()),
                )
            )
        plan = plan_tool(user_request.strip(), registry)
    except ToolPlannerError as error:
        logger.warning("Local agent planning failed. error_type=%s", type(error).__name__)
        raise AgentPlanningError(f"Unable to plan local agent action: {error}") from error

    logger.info(
        "Executing planned local tool. tool=%s argument_names=%s",
        plan.tool,
        sorted(plan.arguments),
    )
    if detailed_trace:
        trace.append(
            _trace_event(
                "decision",
                "tool_planner.plan_tool",
                "tool_plan_validated",
                tool=plan.tool,
                argument_names=sorted(plan.arguments),
            )
        )

    try:
        if detailed_trace:
            trace.append(
                _trace_event(
                    "execution",
                    "tool_registry.ToolRegistry.execute",
                    "execute_tool",
                    tool=plan.tool,
                )
            )
        result = registry.execute(plan.tool, plan.arguments)
    except ToolRegistryError as error:
        logger.warning(
            "Local agent tool execution failed. tool=%s error_type=%s",
            plan.tool,
            type(error).__name__,
        )
        raise AgentExecutionError(
            f"Unable to execute planned tool '{plan.tool}': {error}"
        ) from error

    if detailed_trace:
        trace.append(
            _trace_event(
                "result",
                "agent_service.run_agent",
                "execution_completed",
                tool=plan.tool,
                result_type=type(result).__name__,
            )
        )
        logger.debug("Detailed agent trace generated. events=%s", len(trace))

    logger.info("Local agent execution completed. tool=%s", plan.tool)
    return AgentResult(plan=plan, result=result, trace=tuple(trace))
