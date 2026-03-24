from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class CalculationsAgentTool(BaseAgentTool):

    @property
    def deployment_name(self) -> str:
        return "calculations-agent"

    @property
    def name(self) -> str:
        return "calculations_agent"

    @property
    def description(self) -> str:
        return (
            "Delegate a task to the Calculations Agent. "
            "Use this tool for: mathematical computations, data analysis, chart/graph generation, "
            "Python code execution, statistical calculations, and any numeric processing. "
            "The agent has access to a Python Code Interpreter and a simple calculator."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The task or question to send to the Calculations Agent."
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate the previous conversation history with this agent. "
                                   "Set to true for follow-up tasks that depend on prior interactions."
                }
            },
            "required": ["prompt"]
        }
