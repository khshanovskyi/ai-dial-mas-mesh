from task.agents.base_agent import BaseAgent
from task.agents.calculations._prompts import SYSTEM_PROMPT
from task.tools.base_tool import BaseTool


class CalculationsAgent(BaseAgent):

    def __init__(self, endpoint: str, tools: list[BaseTool]):
        super().__init__(
            endpoint=endpoint,
            system_prompt=SYSTEM_PROMPT,
            tools=tools,
        )
