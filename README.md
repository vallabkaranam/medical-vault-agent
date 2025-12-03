# Personal Vault 🏥

**Medical Compliance Microservice** - A dual-interface backend demonstrating "Agentic Architecture" and "Product Engineering" principles.

## 🎯 Architecture: "ONE BRAIN, TWO VOICES"

This FastAPI application exposes the same core logic through two interfaces:

1. **REST API (Voice 1)**: For React Frontend (Humans)
2. **MCP Server (Voice 2)**: For AI Agents (Claude Desktop/Cursor)

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **Agent Protocol**: fastapi-mcp (Model Context Protocol)
- **Data Validation**: Pydantic (Strict schemas to prevent AI hallucinations)
- **AI Engine**: OpenAI GPT-4o
- **Database/Storage**: Supabase (Postgres + Storage Bucket)
- **Auth**: Public Kiosk mode (Session IDs, no login required for MVP)

## 📁 Project Structure

```
medical-vault/
├── main.py              # Hybrid FastAPI + MCP server
├── schemas.py           # Pydantic data contracts
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `OPENAI_API_KEY`: Your OpenAI API key

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### Voice 1: REST API (For Humans)

#### Health Check
```bash
GET http://localhost:8000/health
```

#### Analyze Vaccine Record
```bash
POST http://localhost:8000/analyze
Content-Type: multipart/form-data

file: <image file>
session_id: <optional session ID>
```

**Interactive Documentation**: http://localhost:8000/docs

### Voice 2: MCP Server (For AI Agents)

#### MCP Endpoint
```
http://localhost:8000/mcp
```

#### Available Tools
- `verify_vaccine_record(image_url, session_id)`: Analyze vaccine record from URL

## 📊 Data Contract

### VaccineName Enum
Standardized vaccine names to prevent AI hallucinations:
- MMR
- Tetanus
- Hepatitis B
- Varicella
- Meningococcal
- COVID-19
- Influenza
- HPV
- Polio
- DTaP
- Other

### VaccineStatus Enum
- Compliant
- Non-Compliant
- Review Needed

### ComplianceResult Model
```python
{
    "is_compliant": bool,
    "confidence_score": float,  # 0.0 to 1.0
    "records": [VaccineRecord],
    "missing_vaccines": [VaccineName],
    "image_url": str,
    "session_id": str,
    "extracted_at": str  # ISO 8601 timestamp
}
```

## 🔄 Processing Flow

1. **Receive Image** → Upload via REST or URL via MCP
2. **AI Extraction** → Send to OpenAI GPT-4o for structured extraction
3. **Validation** → IF valid and readable
4. **Storage Upload** → Upload image to Supabase Storage
5. **Database Insert** → Save JSON to Supabase Postgres
6. **Return Result** → Structured ComplianceResult

**Rationale**: We only store images that are successfully processed to avoid paying for unreadable/garbage files.

## 🧪 Testing

### Test REST API with curl

```bash
# Health check
curl http://localhost:8000/health

# Analyze vaccine record
curl -X POST http://localhost:8000/analyze \
  -F "file=@/path/to/vaccine-record.jpg" \
  -F "session_id=test-session-123"
```

### Test with Python

```python
import requests

# Upload vaccine record
with open("vaccine-record.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f},
        data={"session_id": "test-123"}
    )
    
print(response.json())
```

## 🎓 Resume-Grade Features

This codebase demonstrates:

✅ **Agentic Architecture**: Dual-interface design (REST + MCP)  
✅ **Product Engineering**: Complete, runnable MVP with clear value proposition  
✅ **Schema Safety**: Enums prevent AI hallucinations  
✅ **Data Lineage**: `original_text` field for trust and verification  
✅ **Separation of Concerns**: Clean architecture with schemas, core logic, and interfaces  
✅ **Error Handling**: Comprehensive validation and error responses  
✅ **Documentation**: Inline comments, docstrings, and this README  
✅ **CORS Configuration**: Ready for frontend integration  
✅ **Environment Management**: Secure credential handling  

## 🔧 Implementation Status

### ✅ Complete
- FastAPI server setup
- MCP server integration
- Pydantic schemas with strict validation
- REST API endpoints
- MCP tool definition
- CORS configuration
- Health check endpoint
- Project structure

### 🚧 TODO (Marked in code)
- OpenAI GPT-4o Vision API integration
- Supabase Storage upload
- Supabase Database insert
- Image download for MCP tool
- Actual compliance rules logic

## 📝 Next Steps

1. **Implement OpenAI Integration**: Uncomment and configure the GPT-4o Vision API calls in `_process_image()`
2. **Setup Supabase**: Create storage bucket and database table
3. **Define Compliance Rules**: Implement actual compliance logic based on requirements
4. **Build React Frontend**: Create the human-facing interface
5. **Deploy**: Deploy to production (Railway, Render, or Fly.io)

## 🤝 Contributing

This is a portfolio/resume project demonstrating modern backend architecture patterns.

## 📄 License

MIT License - Feel free to use this as a reference for your own projects.

---

**Built with ❤️ to demonstrate Agentic Architecture and Product Engineering skills**
