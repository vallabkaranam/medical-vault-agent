# Personal Vault - Medical Compliance Microservice

A hybrid "One Brain, Two Voices" application that allows users to upload medical records, extract data using AI, and verify compliance against various standards (Cornell Tech, US CDC, etc.).

## Architecture

- **Frontend**: React + Vite + Tailwind CSS (Voice 1: For Humans)
- **Backend**: FastAPI + OpenAI Vision + Supabase (Voice 2: MCP Server for AI Agents)
- **Storage**: Supabase (PostgreSQL + Storage)

## Project Structure

```
medical-vault/
├── backend/                # Python FastAPI Backend
│   ├── main.py            # Application entry point & API routes
│   ├── services.py        # Core logic (AI extraction, standardization)
│   ├── schemas.py         # Pydantic models & Enums
│   ├── requirements.txt   # Python dependencies
│   └── tests/             # Tests
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # UI Components (VaultGrid, UnifiedView, etc.)
│   │   ├── api.js         # API Client
│   │   └── App.jsx        # Main Application Logic
│   └── ...
└── ...
```

## Setup & Running

### Prerequisites
- Python 3.9+
- Node.js 16+
- Supabase Account
- OpenAI API Key

### Backend

1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv ../venv
   source ../venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up `.env` file in `backend/` (copy from `.env.example`).
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Features

- **Upload**: Securely upload vaccine cards (Image/PDF).
- **AI Extraction**: Automatically extracts vaccine dates, names, and providers.
- **Standardization**: Verifies compliance against Cornell Tech, US CDC, and other standards.
- **Unified View**: Aggregates records into a single, standardized history.
- **Reports**: Generates official compliance reports.
