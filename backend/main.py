"""
Personal Vault - Hybrid Medical Compliance Microservice
Architecture: "ONE BRAIN, TWO VOICES"

This FastAPI application exposes the same core logic through two interfaces:
1. REST API (Voice 1): For React Frontend (Humans)
2. MCP Server (Voice 2): For AI Agents (Claude Desktop/Cursor)

The design demonstrates "Agentic Architecture" and "Product Engineering" principles.
"""

import os
import base64
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import httpx
from supabase import create_client, Client

# Import our data contract
from schemas import (
    ComplianceResult,
    VaccineRecord,
    VaccineStatus,
    VaccineName,
    HealthResponse,
    UploadResult,
    StandardizationResult,
    StandardizationRequest,
    ComplianceStandard,
    LanguageCode,
    TranscriptionResult, 
    TranslationResult,
    AgentComplianceResponse
)

# Import core services
from services import perform_standardization, analyze_image_with_ai, process_ai_result

# Load environment variables
load_dotenv()

# Environment configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required environment variables
if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    print("WARNING: Missing required environment variables. Please set:")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_KEY")
    print("  - OPENAI_API_KEY")

# Initialize FastAPI
app = FastAPI(
    title="Personal Vault API",
    description="Medical Compliance Microservice - Upload Once, Standardize Many Times",
    version="2.1.0",
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for uploaded records
# TODO: Replace with Redis or database in production
uploaded_records = {}

# Helper for Analytics
async def log_analytics_event(session_id: str, event_type: str, data: dict = None):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return
            
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase.table("analytics_events").insert({
            "session_id": session_id,
            "event_type": event_type,
            "event_data": data or {}
        }).execute()
    except Exception as e:
        print(f"Analytics Error: {e}")



# ============================================================================
# VOICE 1: REST API (For Humans via React Frontend)
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return HealthResponse(
        status="running",
        mode="REST + MCP",
        version="2.1.0",
        pipeline="Transcription → Translation → Standardization"
    )


# ============================================================================
# NEW API v2.1: Separated Upload and Standardization
# ============================================================================

@app.post("/upload", response_model=UploadResult)
async def upload_vaccine_record(
    file: UploadFile = File(..., description="Vaccination record image (JPG, PNG, PDF)"),
    session_id: Optional[str] = Form(None, description="Optional session ID for tracking")
):
    """
    Upload and extract vaccine data (generic format, no standard applied).
    """
    """
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )
    
    try:
        # Generate unique record ID
        record_id = str(uuid.uuid4())
        
        # Process with AI
        data = await analyze_image_with_ai(file_bytes, OPENAI_API_KEY)
        
        # Map to our internal schemas using shared helper
        transcription, translation, extracted_vaccines = process_ai_result(data)
        
        # Upload to Supabase Storage
        try:
            # Initialize Supabase client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Create filename
            filename = f"{record_id}.jpg"
            
            # Upload
            bucket_name = "vaccine-records"
            supabase.storage.from_(bucket_name).upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Get Public URL
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{filename}"
            
        except Exception as e:
            print(f"Supabase Upload Failed: {e}")
            image_url = f"https://placeholder.com/failed-upload/{record_id}.jpg"

        # Create result
        result = UploadResult(
            record_id=record_id,
            transcription=transcription,
            translation=translation,
            extracted_vaccines=extracted_vaccines,
            image_url=image_url,
            session_id=session_id,
            uploaded_at=datetime.utcnow().isoformat()
        )
        
        # Cache the uploaded record
        uploaded_records[record_id] = result
        
        # Log Analytics
        await log_analytics_event(session_id, "UPLOAD_COMPLETE", {"record_id": record_id})
        
        return result
        
    except Exception as e:
        print(f"Error in upload_vaccine_record: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.get("/records/{session_id}", response_model=List[UploadResult])
async def get_session_records(session_id: str):
    """
    Retrieve all uploaded records for a specific session.
    """
    session_records = [
        record for record in uploaded_records.values() 
        if record.session_id == session_id
    ]
    return session_records


@app.post("/standardize/{standard}", response_model=StandardizationResult)
async def standardize_record(
    standard: str,
    request: StandardizationRequest
):
    """
    Standardize an uploaded record against a specific compliance standard.
    """
    # Validate standard
    valid_standards = ["cornell_tech", "us_cdc", "uk_nhs", "canada_health"]
    if standard not in valid_standards:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid standard. Supported: {', '.join(valid_standards)}"
        )
    
    # Fetch uploaded record from cache
    if request.record_id not in uploaded_records:
        raise HTTPException(
            status_code=404,
            detail="Record not found. Please upload first."
        )
        
    uploaded_record = uploaded_records[request.record_id]
    
    # Perform standardization using the shared helper
    result = perform_standardization(standard, uploaded_record.extracted_vaccines)
    
    # Save to Database
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        db_record = {
            "record_id": request.record_id,
            "session_id": uploaded_record.session_id,
            "standard": standard,
            "transcription": uploaded_record.transcription.model_dump(mode='json'),
            "translation": uploaded_record.translation.model_dump(mode='json'),
            "standardization": result.model_dump(mode='json'),
            "image_url": uploaded_record.image_url,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        # Insert into DB
        supabase.table("compliance_results").insert(db_record).execute()
        
    except Exception as e:
        print(f"Warning: Failed to save to database: {e}")
    
    # Log Analytics
    await log_analytics_event(uploaded_record.session_id, "STANDARDIZATION_RUN", {
        "record_id": request.record_id,
        "standard": standard,
        "is_compliant": result.is_compliant
    })
    
    return result


@app.post("/report/{standard}", response_model=StandardizationResult)
async def generate_session_report(
    standard: str,
    session_id: str = Body(..., embed=True)
):
    """
    Generate an aggregate compliance report for a full session (Unified View).
    """
    # Validate standard
    valid_standards = ["cornell_tech", "us_cdc", "uk_nhs", "canada_health"]
    if standard not in valid_standards:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid standard. Supported: {', '.join(valid_standards)}"
        )

    # Get all records for session
    session_records = [r for r in uploaded_records.values() if r.session_id == session_id]
    
    if not session_records:
        return StandardizationResult(
            standard=ComplianceStandard(standard) if standard in [s.value for s in ComplianceStandard] else ComplianceStandard.US_CDC,
            is_compliant=False,
            records=[],
            missing_vaccines=[],
            compliance_notes="No records found for this session."
        )

    # Aggregate all vaccines
    all_vaccines = []
    for r in session_records:
        all_vaccines.extend(r.extracted_vaccines)
        
    # Standardize aggregated list
    result = perform_standardization(standard, all_vaccines)
    
    return result


# ============================================================================
# VOICE 2: MCP Server (For AI Agents via Claude Desktop/Cursor)
# ============================================================================

@app.post("/verify_vaccine_record", response_model=AgentComplianceResponse)
async def verify_vaccine_record(
    image_url: str, 
    session_id: Optional[str] = None,
    standard: str = "us_cdc"
) -> AgentComplianceResponse:
    """
    MCP Tool (HTTP Adapter): Verify a vaccination record from an image URL.
    Returns an agent-optimized, flat response.
    """
    Returns an agent-optimized, flat response.
    """
    
    try:
        # Download image from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            file_bytes = response.content
            
        # Process with AI
        data = await analyze_image_with_ai(file_bytes, OPENAI_API_KEY)
        
        # Map to schemas
        transcription, translation, extracted_vaccines = process_ai_result(data)
        
        # Stage 3: Standardization
        standardization = perform_standardization(standard, extracted_vaccines)
        
        # Construct Agent-Optimized Result
        found_vax_names = [v.vaccine_name.value for v in standardization.records]
        missing_vax_names = [v.value for v in standardization.missing_vaccines]
        
        evidence = {
            "vaccines": [
                {
                    "name": v.vaccine_name.value,
                    "date": v.date,
                    "provider": v.provider
                } for v in standardization.records
            ],
            "original_text_snippet": transcription.raw_text[:200] + "..." if len(transcription.raw_text) > 200 else transcription.raw_text
        }
        
        return AgentComplianceResponse(
            is_compliant=standardization.is_compliant,
            missing_vaccines=missing_vax_names,
            extracted_vaccines=found_vax_names,
            compliance_summary=standardization.compliance_notes or "Analysis complete.",
            evidence=evidence,
            overall_confidence=transcription.confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vaccine record verification failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 Personal Vault - Medical Compliance Microservice v2.1")
    print("=" * 80)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
