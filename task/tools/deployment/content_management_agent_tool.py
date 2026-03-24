from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class ContentManagementAgentTool(BaseAgentTool):

    @property
    def deployment_name(self) -> str:
        return "content-management-agent"

    @property
    def name(self) -> str:
        return "content_management_agent"

    @property
    def description(self) -> str:
        return (
            "Delegate a task to the Content Management Agent. "
            "Use this tool for: extracting text from uploaded files (PDF, TXT, CSV, HTML), "
            "answering questions about document content, semantic search within documents (RAG), "
            "and any file-based information retrieval tasks."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The task or question to send to the Content Management Agent."
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate the previous conversation history with this agent. "
                                   "Set to true for follow-up tasks that depend on prior interactions."
                }
            },
            "required": ["prompt"]
        }
