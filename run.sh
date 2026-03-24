#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Starting MAS Mesh ==="

if [ -z "${DIAL_API_KEY}" ]; then
  echo "ERROR: DIAL_API_KEY is not set. Export your upstream AI-proxy key before running:"
  echo "  export DIAL_API_KEY=your-key-here"
  exit 1
fi

# Render core/config.json from template using the upstream key
envsubst '${DIAL_API_KEY}' < core/config.template.json > core/config.json

echo "Starting Docker services..."
docker compose up -d

echo "Waiting for Docker services to be ready..."
sleep 8

source .venv/bin/activate

export DIAL_ENDPOINT="${DIAL_ENDPOINT:-http://localhost:8080}"
export DEPLOYMENT_NAME="${DEPLOYMENT_NAME:-gpt-4o}"
# Bypass DIAL Core/adapter-dial for backbone LLM calls (avoids gzip parsing bug in core 0.42.x)
export LLM_ENDPOINT="${LLM_ENDPOINT:-https://ai-proxy.lab.epam.com/}"
export LLM_API_KEY="${LLM_API_KEY:-${DIAL_API_KEY}}"
# DIAL_API_KEY is the local DIAL Core key — must match core/config.json "keys" section
export DIAL_API_KEY="dial_api_key"
export PYINTERPRETER_MCP_URL="${PYINTERPRETER_MCP_URL:-http://localhost:8050/mcp}"
export DDG_MCP_URL="${DDG_MCP_URL:-http://localhost:8051/mcp}"

echo "Starting Calculations Agent on port 5001..."
python -m task.agents.calculations.calculations_app &
CALC_PID=$!

echo "Starting Content Management Agent on port 5002..."
python -m task.agents.content_management.content_management_app &
CM_PID=$!

echo "Starting Web Search Agent on port 5003..."
python -m task.agents.web_search.web_search_app &
WS_PID=$!

echo ""
echo "=== All agents started ==="
echo "  Calculations Agent:      http://localhost:5001"
echo "  Content Management Agent: http://localhost:5002"
echo "  Web Search Agent:        http://localhost:5003"
echo "  DIAL Core:               http://localhost:8080"
echo "  Chat UI:                 http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all agents."

trap "echo 'Stopping agents...'; kill $CALC_PID $CM_PID $WS_PID 2>/dev/null; exit 0" INT TERM

wait $CALC_PID $CM_PID $WS_PID
