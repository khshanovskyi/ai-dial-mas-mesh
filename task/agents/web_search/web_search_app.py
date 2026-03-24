import os

import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.web_search.web_search_agent import WebSearchAgent
from task.tools.base_tool import BaseTool
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.mcp.mcp_client import MCPClient
from task.tools.mcp.mcp_tool import MCPTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

_DDG_MCP_URL = os.getenv('DDG_MCP_URL', "http://localhost:8051/mcp")


class WebSearchApplication(ChatCompletion):

    def __init__(self):
        self.tools: list[BaseTool] = []

    async def _get_mcp_tools(self, url: str) -> list[BaseTool]:
        try:
            mcp_client = await MCPClient.create(url)
            return [MCPTool(client=mcp_client, mcp_tool_model=m) for m in await mcp_client.get_tools()]
        except Exception as e:
            print(f"Warning: Could not load MCP tools: {e}")
            raise e

    async def _create_tools(self) -> list[BaseTool]:
        print(f"DDG_MCP_URL {_DDG_MCP_URL}")
        tools: list[BaseTool] = [
            CalculationsAgentTool(DIAL_ENDPOINT),
            ContentManagementAgentTool(DIAL_ENDPOINT),
        ]
        tools.extend(await self._get_mcp_tools(_DDG_MCP_URL))
        return tools

    async def chat_completion(self, request: Request, response: Response) -> None:
        if not self.tools:
            self.tools = await self._create_tools()

        with response.create_single_choice() as choice:
            await WebSearchAgent(
                endpoint=DIAL_ENDPOINT,
                tools=self.tools,
            ).handle_request(
                choice=choice,
                deployment_name=DEPLOYMENT_NAME,
                request=request,
                response=response,
            )


app: DIALApp = DIALApp()
agent_app = WebSearchApplication()
app.add_chat_completion(deployment_name="web-search-agent", impl=agent_app)

if __name__ == "__main__":
    uvicorn.run(app, port=5003, host="0.0.0.0", log_level="info")
