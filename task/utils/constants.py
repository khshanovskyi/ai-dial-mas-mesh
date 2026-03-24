import os

DIAL_ENDPOINT = os.getenv('DIAL_ENDPOINT', "http://localhost:8080")
DEPLOYMENT_NAME = os.getenv('DEPLOYMENT_NAME', 'gpt-4o')
DIAL_API_KEY = os.getenv('DIAL_API_KEY', 'dial_api_key')

# Direct LLM endpoint — bypasses DIAL Core/adapter-dial (avoids gzip parsing bug in core 0.42.x)
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', DIAL_ENDPOINT)
LLM_API_KEY = os.getenv('LLM_API_KEY', DIAL_API_KEY)

TOOL_CALL_HISTORY_KEY = "tool_call_history"
CUSTOM_CONTENT = "custom_content"