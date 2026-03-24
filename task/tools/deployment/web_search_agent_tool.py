from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class WebSearchAgentTool(BaseAgentTool):

    @property
    def deployment_name(self) -> str:
        return "web-search-agent"

    @property
    def name(self) -> str:
        return "web_search_agent"

    @property
    def description(self) -> str:
        return (
            "Delegate a task to the Web Search Agent. "
            "Use this tool for: searching the internet, finding current information, "
            "verifying facts, researching topics, retrieving news or recent events, "
            "and any tasks requiring up-to-date web data."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The search query or research task to send to the Web Search Agent."
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate the previous conversation history with this agent. "
                                   "Set to true for follow-up tasks that depend on prior interactions."
                }
            },
            "required": ["prompt"]
        }
