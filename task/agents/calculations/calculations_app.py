import os

import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.calculations.calculations_agent import CalculationsAgent
from task.agents.calculations.tools.simple_calculator_tool import SimpleCalculatorTool
from task.agents.calculations.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool
from task.tools.base_tool import BaseTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

_PYINTERPRETER_MCP_URL = os.getenv('PYINTERPRETER_MCP_URL', "http://localhost:8050/mcp")


class CalculationsApplication(ChatCompletion):

    def __init__(self):
        self.tools: list[BaseTool] = []

    async def _create_tools(self) -> list[BaseTool]:
        print(f"PYINTERPRETER_MCP_URL {_PYINTERPRETER_MCP_URL}")
        return [
            ContentManagementAgentTool(DIAL_ENDPOINT),
            WebSearchAgentTool(DIAL_ENDPOINT),
            SimpleCalculatorTool(),
            await PythonCodeInterpreterTool.create(
                mcp_url=_PYINTERPRETER_MCP_URL,
                tool_name="execute_code",
                dial_endpoint=DIAL_ENDPOINT,
            ),
        ]

    async def chat_completion(self, request: Request, response: Response) -> None:
        if not self.tools:
            self.tools = await self._create_tools()

        with response.create_single_choice() as choice:
            await CalculationsAgent(
                endpoint=DIAL_ENDPOINT,
                tools=self.tools,
            ).handle_request(
                choice=choice,
                deployment_name=DEPLOYMENT_NAME,
                request=request,
                response=response,
            )


app: DIALApp = DIALApp()
agent_app = CalculationsApplication()
app.add_chat_completion(deployment_name="calculations-agent", impl=agent_app)

if __name__ == "__main__":
    uvicorn.run(app, port=5001, host="0.0.0.0", log_level="info")
