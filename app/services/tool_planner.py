"""
Local tool planner for the Private Doc Agent.

This module asks the configured local Ollama model to select one registered
tool for a user request. It validates the model output but deliberately does
not execute the proposed tool. Keeping planning and execution separate makes
the agent flow easier to test, audit, and control.

Privacy and safety strategy:
- The planner exposes only public tool metadata to the model.
- Model output must be one strict JSON object.
- Tool names and arguments must match the allowlisted registry contract.
- Logs contain operational metadata only, never the request or argument values.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.llm_client import LLMClientError, generate_text
from app.services.tool_registry import ToolRegistry, tool_registry


logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "tool_planner_prompt.txt"


class ToolPlannerError(Exception):
    """Base exception for controlled tool-planning failures."""


class InvalidToolPlanError(ToolPlannerError):
    """Raised when the local model returns an invalid or unsafe plan."""


@dataclass(frozen=True)
class ToolPlan:
    """Validated proposal for one future tool execution."""

    tool: str
    arguments: dict[str, Any]

    def to_dict(self) -> dict:
        """Returns a serializable representation of the plan."""
        return {"tool": self.tool, "arguments": self.arguments}


def _load_prompt_template() -> str:
    """Loads the planner prompt maintained outside the Python module."""
    try:
        template = PROMPT_PATH.read_text(encoding="utf-8")
    except OSError as error:
        raise ToolPlannerError(
            f"Unable to load the tool planner prompt: {error}"
        ) from error

    if not template.strip():
        raise ToolPlannerError("The tool planner prompt cannot be empty.")
    return template


def build_tool_planner_prompt(
    user_request: str,
    registry: ToolRegistry = tool_registry,
) -> str:
    """Builds a prompt containing the request and public tool contracts."""
    if not isinstance(user_request, str) or not user_request.strip():
        raise ValueError("User request cannot be empty.")
    if not isinstance(registry, ToolRegistry):
        raise TypeError("registry must be a ToolRegistry.")

    tools_json = json.dumps(
        registry.list_tools(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    return _load_prompt_template().format(
        tools_json=tools_json,
        user_request=user_request.strip(),
    )


def _parse_model_response(response: str) -> dict:
    """Parses one strict JSON object without accepting surrounding text."""
    if not isinstance(response, str) or not response.strip():
        raise InvalidToolPlanError("The local LLM returned an empty tool plan.")

    try:
        plan = json.loads(response)
    except json.JSONDecodeError as error:
        raise InvalidToolPlanError(
            "The local LLM returned invalid JSON for the tool plan."
        ) from error

    if not isinstance(plan, dict):
        raise InvalidToolPlanError("The tool plan must be a JSON object.")

    expected_keys = {"tool", "arguments"}
    actual_keys = set(plan)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        unexpected = sorted(actual_keys - expected_keys)
        details = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected keys: {', '.join(unexpected)}")
        raise InvalidToolPlanError(
            f"The tool plan has an invalid structure ({'; '.join(details)})."
        )

    if not isinstance(plan["tool"], str) or not plan["tool"].strip():
        raise InvalidToolPlanError("The tool plan must include a valid tool name.")
    if not isinstance(plan["arguments"], dict):
        raise InvalidToolPlanError("Tool plan arguments must be a JSON object.")

    return plan


def _argument_type_is_valid(value: Any, declared_type: str) -> bool:
    """Checks the JSON value against a registry type name."""
    expected_types = {
        "str": str,
        "int": int,
        "float": (int, float),
        "bool": bool,
        "dict": dict,
        "list": list,
    }
    expected = expected_types.get(declared_type)
    if expected is None:
        raise InvalidToolPlanError(
            f"Unsupported registered argument type: {declared_type}"
        )

    if declared_type in {"int", "float"} and isinstance(value, bool):
        return False
    return isinstance(value, expected)


def _validate_plan(plan: dict, registry: ToolRegistry) -> ToolPlan:
    """Validates a parsed plan against public registry metadata."""
    tools = {tool["name"]: tool for tool in registry.list_tools()}
    tool_name = plan["tool"].strip()
    tool = tools.get(tool_name)
    if tool is None:
        raise InvalidToolPlanError(f"Unknown planned tool: {tool_name}")

    supplied_arguments = plan["arguments"]
    argument_definitions = {
        argument["name"]: argument for argument in tool["arguments"]
    }

    unexpected = sorted(set(supplied_arguments) - set(argument_definitions))
    if unexpected:
        raise InvalidToolPlanError(
            f"Unexpected arguments for '{tool_name}': {', '.join(unexpected)}"
        )

    missing = sorted(
        name
        for name, definition in argument_definitions.items()
        if definition["required"] and name not in supplied_arguments
    )
    if missing:
        raise InvalidToolPlanError(
            f"Missing required arguments for '{tool_name}': {', '.join(missing)}"
        )

    for name, value in supplied_arguments.items():
        declared_type = argument_definitions[name]["type"]
        if not _argument_type_is_valid(value, declared_type):
            raise InvalidToolPlanError(
                f"Argument '{name}' for '{tool_name}' must be {declared_type}."
            )

    return ToolPlan(tool=tool_name, arguments=dict(supplied_arguments))


def plan_tool(
    user_request: str,
    registry: ToolRegistry = tool_registry,
) -> ToolPlan:
    """Requests and validates one tool plan from the configured local LLM."""
    prompt = build_tool_planner_prompt(user_request, registry)
    logger.info(
        "Requesting local tool plan. available_tools=%s request_length=%s",
        len(registry.list_tools()),
        len(user_request.strip()),
    )

    try:
        response = generate_text(prompt)
    except LLMClientError as error:
        logger.error("Local tool planning failed because the LLM is unavailable.")
        raise ToolPlannerError(f"Unable to generate a tool plan: {error}") from error

    plan = _validate_plan(_parse_model_response(response), registry)
    logger.info(
        "Local tool plan validated. tool=%s argument_names=%s",
        plan.tool,
        sorted(plan.arguments),
    )
    return plan
