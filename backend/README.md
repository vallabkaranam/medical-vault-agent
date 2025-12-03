# Personal Vault - Backend Microservice

This microservice implements the "One Brain, Two Voices" architecture for medical record compliance.

## Architecture

- **Voice 1 (REST API)**: Served via `main.py` (FastAPI). Designed for the React Frontend (Humans).
- **Voice 2 (MCP Server)**: Served via `mcp_server.py` (FastMCP). Designed for AI Agents (Claude, Cursor).

Both voices share the same "Brain" (Core Logic) in `services.py` and Data Contract in `schemas.py`.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and set your keys:
   ```bash
   cp .env.example .env
   ```
   Required: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`.

## Running Voice 1 (REST API)

For the Frontend application:
```bash
uvicorn main:app --reload --port 8000
```
- Swagger Docs: http://localhost:8000/docs

## Running Voice 2 (MCP Server)

For AI Agents (Claude Desktop, Cursor):
```bash
python mcp_server.py
```
- This runs the MCP server over stdio. Configure your agent to point to this script.

## Testing

Run the agent voice verification:
```bash
export MOCK_AI=true
python tests/test_agent_voice.py
```
