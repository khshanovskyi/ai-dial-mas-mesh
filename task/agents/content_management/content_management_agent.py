from task.agents.base_agent import BaseAgent
from task.agents.content_management._prompts import SYSTEM_PROMPT
from task.tools.base_tool import BaseTool


class ContentManagementAgent(BaseAgent):

    def __init__(self, endpoint: str, tools: list[BaseTool]):
        super().__init__(
            endpoint=endpoint,
            system_prompt=SYSTEM_PROMPT,
            tools=tools,
        )
