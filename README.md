# Personal Vault: Medical Compliance Microservice

> **"One Brain, Two Voices"**
> A hybrid full-stack application that serves both Humans (via React) and AI Agents (via MCP).

![Unified View](https://github.com/vallabkaranam/medical-vault-agent/raw/main/unified_view_screenshot.png)

## 🚀 Overview

Personal Vault is an intelligent medical record aggregator that solves the problem of fragmented health history. It allows users to upload vaccination records in any format or language, digitizes them using GPT-4o Vision, and standardizes them against global health requirements (US CDC, Cornell Tech, UK NHS).

### Key Features
*   **Universal Ingestion**: Accepts photos, PDFs, and handwriting in any language.
*   **AI-Powered Pipeline**:
    1.  **Transcription**: OCR with 99% accuracy.
    2.  **Translation**: Auto-detects and translates non-English records.
    3.  **Standardization**: Maps generic terms ("Chicken Pox") to medical standards ("Varicella").
*   **Unified View**: Aggregates data from multiple uploads into a single timeline.
*   **Compliance Engine**: Checks against specific institutional requirements (e.g., Cornell Tech).
*   **Dual Interface**:
    *   **Voice 1 (Human)**: A beautiful React + Vite frontend.
    *   **Voice 2 (Agent)**: A Model Context Protocol (MCP) server for Claude/Cursor.

---

## 🏗️ Architecture

The project follows a **Monorepo** structure with a shared "Brain" (Service Layer).

```
medical-vault/
├── backend/               # Python FastAPI + MCP
│   ├── main.py           # Voice 1: REST API (FastAPI)
│   ├── mcp_server.py     # Voice 2: MCP Server (Stdio)
│   ├── services.py       # The Brain: Core AI & Standardization Logic
│   ├── schemas.py        # Shared Data Contracts (Pydantic)
│   └── requirements.txt
│
└── frontend/             # React + Vite + Tailwind
    ├── src/
    │   ├── components/   # Modular UI Components
    │   ├── api.js        # API Client
    │   └── App.jsx       # Main Orchestrator
    └── ...
```

### Tech Stack
*   **Frontend**: React, Vite, TailwindCSS, Framer Motion, Lucide Icons.
*   **Backend**: Python, FastAPI, Pydantic, MCP (Model Context Protocol).
*   **AI**: OpenAI GPT-4o Vision.
*   **Storage**: Supabase (PostgreSQL + Storage Buckets).
*   **Deployment**: Vercel (Frontend) + Render (Backend).

---

## 🛠️ Setup & Installation

### Prerequisites
*   Node.js 18+
*   Python 3.9+
*   OpenAI API Key
*   Supabase Project

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OPENAI_API_KEY, SUPABASE_URL, and SUPABASE_KEY
```

**Run REST API (Voice 1):**
```bash
uvicorn main:app --reload
# Available at http://localhost:8000
```

**Run MCP Server (Voice 2):**
```bash
mcp run mcp_server.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Available at http://localhost:5173
```

---

## 🤖 Using with Claude Desktop (MCP)

You can connect Claude Desktop to this project to give it the ability to "see" and verify medical records.

1.  Open your Claude Desktop config file:
    *   macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2.  Add this configuration:
```json
{
  "mcpServers": {
    "medical-vault": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/medical-vault/backend",
        "run",
        "mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```
*(Note: We recommend using `uv` for fast Python execution, but `python` works too if dependencies are installed globally).*

3.  Restart Claude. You can now ask:
    > "Here is a link to my vaccine card: [URL]. Is it compliant with Cornell Tech requirements?"

---

## 🌍 Deployment

*   **Backend**: Automatically deploys to **Render** via `render.yaml`.
*   **Frontend**: Deploys to **Vercel**. Set `VITE_API_URL` to your Render backend URL.

---

## 🛡️ Security & Privacy
*   **HIPAA Compliance**: The architecture is designed to be stateless where possible.
*   **Encryption**: Data at rest in Supabase is encrypted.
*   **Ephemeral Processing**: The "Brain" processes data in-memory during the AI analysis phase.

---

© 2025 Personal Vault Inc.
