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
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from dotenv import load_dotenv

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
)

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

# Initialize MCP Server (Voice 2)
# FastApiMCP requires the FastAPI app instance as the first parameter
mcp = FastApiMCP(app)

# In-memory cache for uploaded records
# TODO: Replace with Redis or database in production
uploaded_records = {}


# ============================================================================
# CORE LOGIC: 3-Stage Pipeline
# ============================================================================

async def _process_image(
    file_bytes: bytes, 
    session_id: Optional[str] = None,
    standard: str = "us_cdc"
) -> ComplianceResult:
    """
    Core 3-stage pipeline: Transcription → Translation → Standardization
    
    STAGE 1: TRANSCRIPTION
      - OCR/Vision AI extracts raw text
      - Detects language
      - Returns structured data
    
    STAGE 2: TRANSLATION
      - Translates to English if needed
      - Preserves original text for lineage
    
    STAGE 3: STANDARDIZATION
      - Maps to selected compliance standard (US CDC or Cornell Tech)
      - Validates against required vaccines
      - Returns compliance status
    
    Args:
        file_bytes: Raw image bytes
        session_id: Optional session identifier
        standard: Compliance standard ("us_cdc" or "cornell_tech")
        
    Returns:
        ComplianceResult with all 3 stages
        
    Raises:
        HTTPException: If processing fails
    """
    
    try:
        # Encode image for AI
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        
        # ====================================================================
        # STAGE 1: TRANSCRIPTION
        # ====================================================================
        # TODO: Implement OpenAI Vision API for transcription
        """
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        transcription_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": '''You are a medical document OCR system. Extract ALL text 
                    from the vaccination record image. Detect the language and return the 
                    raw text with any structured data you can identify (dates, names, etc.).
                    Return in JSON format with: raw_text, detected_language, confidence, structured_data'''
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this vaccination record."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        
        transcription_data = json.loads(transcription_response.choices[0].message.content)
        """
        
        # MOCK: Stage 1 - Transcription
        from schemas import TranscriptionResult, LanguageCode
        transcription = TranscriptionResult(
            raw_text="MMR Vaccine - 05/15/2023, Lot: ABC123, Provider: University Health Center",
            detected_language=LanguageCode.ENGLISH,
            confidence=0.95,
            structured_data={
                "dates": ["2023-05-15"],
                "vaccines": ["MMR"],
                "lot_numbers": ["ABC123"]
            }
        )
        
        # ====================================================================
        # STAGE 2: TRANSLATION
        # ====================================================================
        # TODO: Implement translation if needed
        """
        if transcription.detected_language != LanguageCode.ENGLISH:
            translation_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f'''Translate the following medical text from 
                        {transcription.detected_language} to English. Preserve all 
                        medical terms, dates, and numbers exactly.'''
                    },
                    {
                        "role": "user",
                        "content": transcription.raw_text
                    }
                ],
                response_format={"type": "json_object"}
            )
            translation_data = json.loads(translation_response.choices[0].message.content)
        else:
            # No translation needed
            translation_data = {
                "translated_text": transcription.raw_text,
                "translation_confidence": 1.0
            }
        """
        
        # MOCK: Stage 2 - Translation
        from schemas import TranslationResult
        translation = TranslationResult(
            original_text=transcription.raw_text,
            translated_text=transcription.raw_text,  # Same since English
            source_language=transcription.detected_language,
            target_language=LanguageCode.ENGLISH,
            translation_confidence=1.0
        )
        
        # ====================================================================
        # STAGE 3: STANDARDIZATION
        # ====================================================================
        # TODO: Implement standardization with AI
        """
        # Define required vaccines based on standard
        required_vaccines_map = {
            "us_cdc": ["MMR", "Tetanus", "Hepatitis B", "Varicella"],
            "cornell_tech": ["MMR", "Tetanus", "Hepatitis B", "Varicella", "Meningococcal", "TB Test"]
        }
        
        standardization_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f'''You are a medical compliance validator. Extract vaccine 
                    records from the text and map them to standardized vaccine names. 
                    Validate against {standard} requirements: {required_vaccines_map[standard]}.
                    Return JSON with: records (list), missing_vaccines (list), is_compliant (bool)'''
                },
                {
                    "role": "user",
                    "content": translation.translated_text
                }
            ],
            response_format={"type": "json_object"}
        )
        
        standardization_data = json.loads(standardization_response.choices[0].message.content)
        """
        
        # MOCK: Stage 3 - Standardization
        from schemas import StandardizationResult, VaccineRecord, VaccineStatus, VaccineName, ComplianceStandard
        
        # Define required vaccines per standard
        required_vaccines = {
            "us_cdc": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B},
            "cornell_tech": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B, 
                           VaccineName.MENINGOCOCCAL, VaccineName.TB_TEST}
        }
        
        # Mock extracted records
        vaccine_records = [
            VaccineRecord(
                vaccine_name=VaccineName.MMR,
                date="2023-05-15",
                status=VaccineStatus.COMPLIANT,
                original_text="MMR Vaccine - 05/15/2023",
                translated_text="MMR Vaccine - 05/15/2023",
                lot_number="ABC123",
                provider="University Health Center"
            )
        ]
        
        # Calculate compliance
        extracted_vaccines = {record.vaccine_name for record in vaccine_records}
        missing = list(required_vaccines.get(standard, set()) - extracted_vaccines)
        is_compliant = len(missing) == 0
        
        standardization = StandardizationResult(
            standard=ComplianceStandard(standard),
            is_compliant=is_compliant,
            records=vaccine_records,
            missing_vaccines=missing,
            compliance_notes=f"Validated against {standard.upper()} requirements"
        )
        
        # ====================================================================
        # UPLOAD TO STORAGE (only if all stages succeeded)
        # ====================================================================
        # TODO: Implement Supabase upload
        """
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id or 'anonymous'}_{timestamp}.jpg"
        
        supabase.storage.from_("vaccine-records").upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        
        image_url = supabase.storage.from_("vaccine-records").get_public_url(filename)
        """
        
        image_url = f"https://supabase.example.com/storage/{session_id or 'test'}.jpg"
        
        # ====================================================================
        # SAVE TO DATABASE
        # ====================================================================
        # TODO: Save complete pipeline result to database
        """
        db_record = {
            "session_id": session_id,
            "standard": standard,
            "transcription": transcription.dict(),
            "translation": translation.dict(),
            "standardization": standardization.dict(),
            "image_url": image_url,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("compliance_results").insert(db_record).execute()
        """
        
        # ====================================================================
        # RETURN COMPLETE RESULT
        # ====================================================================
        overall_confidence = (
            transcription.confidence + 
            translation.translation_confidence
        ) / 2.0
        
        result = ComplianceResult(
            transcription=transcription,
            translation=translation,
            standardization=standardization,
            overall_confidence=overall_confidence,
            image_url=image_url,
            session_id=session_id,
            processed_at=datetime.utcnow().isoformat()
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline processing failed: {str(e)}"
        )


# ============================================================================
# VOICE 1: REST API (For Humans via React Frontend)
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service is running.
    
    Returns:
        HealthResponse with service status, mode, and pipeline info
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
    
    STAGES 1 & 2 ONLY:
    1. TRANSCRIPTION: OCR/Vision AI extracts text and detects language
    2. TRANSLATION: Translates to English if needed
    
    Returns generic extracted data that can be standardized later.
    
    Args:
        file: Uploaded image file
        session_id: Optional session identifier
        
    Returns:
        UploadResult with record_id and generic extracted data
    """
    from schemas import UploadResult, TranscriptionResult, TranslationResult, LanguageCode
    import uuid
    import json
    from openai import OpenAI
    
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
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
        data = await _analyze_image_with_ai(file_bytes)
        
        # Map to our internal schemas
        
        # Stage 1: Transcription
        transcription = TranscriptionResult(
            raw_text=data.get("raw_text", ""),
            detected_language=LanguageCode(data.get("detected_language", "en")) if data.get("detected_language") in [l.value for l in LanguageCode] else LanguageCode.UNKNOWN,
            confidence=data.get("confidence", 0.0),
            structured_data=data.get("structured_data", {})
        )
        
        # Stage 2: Translation
        trans_data = data.get("translation", {})
        translation = TranslationResult(
            original_text=trans_data.get("original_text", transcription.raw_text),
            translated_text=trans_data.get("translated_text", transcription.raw_text),
            source_language=transcription.detected_language,
            target_language=LanguageCode.ENGLISH,
            translation_confidence=trans_data.get("confidence", 1.0)
        )
        
        # Extracted Vaccines
        extracted_vaccines = data.get("extracted_vaccines", [])
        
        # TODO: Upload to Supabase Storage (Mocked for now)
        image_url = f"https://supabase.example.com/storage/{record_id}.jpg"
        
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
        
        return result
        
    except Exception as e:
        print(f"Error in upload_vaccine_record: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.post("/standardize/{standard}", response_model=StandardizationResult)
async def standardize_record(
    standard: str,
    request: StandardizationRequest
):
    """
    Standardize an uploaded record against a specific compliance standard.
    
    STAGE 3 ONLY: Apply institution/country-specific requirements.
    
    Supported standards:
    - cornell_tech: Cornell Tech requirements
    - us_cdc: US CDC general guidelines
    - uk_nhs: UK NHS requirements (future)
    - canada_health: Canada Health requirements (future)
    
    Args:
        standard: Compliance standard identifier
        request: Contains record_id to standardize
        
    Returns:
        StandardizationResult with compliance status for that standard
    """
    from schemas import StandardizationResult, VaccineRecord, VaccineStatus, VaccineName, ComplianceStandard
    
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
            detail=f"Record {request.record_id} not found. Please upload first."
        )
    
    uploaded_record = uploaded_records[request.record_id]
    
    # Define required vaccines per standard
    required_vaccines_map = {
        "us_cdc": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B},
        "cornell_tech": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B, 
                       VaccineName.MENINGOCOCCAL, VaccineName.TB_TEST},
        "uk_nhs": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.MENINGOCOCCAL},
        "canada_health": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B, VaccineName.VARICELLA}
    }
    
    # Convert extracted vaccines to VaccineRecord objects
    vaccine_records = []
    # Convert extracted vaccines to VaccineRecord objects
    vaccine_records = []
    
    # Helper map for common variations if AI misses exact Enum match
    name_mapping = {
        "MMR II": VaccineName.MMR,
        "Measles Mumps Rubella": VaccineName.MMR,
        "Td": VaccineName.TETANUS, # Often Td is acceptable for Tetanus booster
        "DTap": VaccineName.TDAP,
        "Varicella Zoster": VaccineName.VARICELLA,
        "Chicken Pox": VaccineName.VARICELLA,
        "Meningitis": VaccineName.MENINGOCOCCAL,
        "PPD": VaccineName.TB_TEST,
        "Mantoux": VaccineName.TB_TEST
    }

    for vax in uploaded_record.extracted_vaccines:
        v_name_str = vax["vaccine_name"]
        
        # Try direct Enum match
        try:
            v_name_enum = VaccineName(v_name_str)
        except ValueError:
            # Try mapping
            v_name_enum = name_mapping.get(v_name_str)
            
            # If still not found, try case-insensitive match against Enum values
            if not v_name_enum:
                for member in VaccineName:
                    if member.value.lower() == v_name_str.lower():
                        v_name_enum = member
                        break
            
            # If still not found, skip or mark as Other
            if not v_name_enum:
                # We could log this or add to a "unknown" list
                # For now, we skip as per original logic, or maybe map to OTHER
                # Let's map to OTHER to preserve the record
                v_name_enum = VaccineName.OTHER

        vaccine_records.append(
            VaccineRecord(
                vaccine_name=v_name_enum,
                date=vax["date"],
                status=VaccineStatus.COMPLIANT,  # TODO: Check expiration, etc.
                original_text=vax["original_text"],
                translated_text=vax.get("original_text"), # This might be missing in extracted_vaccines if not passed
                lot_number=vax.get("lot_number"),
                provider=vax.get("provider")
            )
        )
    
    # Calculate compliance
    extracted_vaccine_names = {record.vaccine_name for record in vaccine_records}
    required_vaccines = required_vaccines_map.get(standard, set())
    missing_vaccines = list(required_vaccines - extracted_vaccine_names)
    is_compliant = len(missing_vaccines) == 0
    
    # Create standardization result
    result = StandardizationResult(
        standard=ComplianceStandard(standard),
        is_compliant=is_compliant,
        records=vaccine_records,
        missing_vaccines=missing_vaccines,
        compliance_notes=f"Validated against {standard.upper()} requirements. " +
                        (f"Missing: {', '.join([v.value for v in missing_vaccines])}" if missing_vaccines else "All required vaccines present.")
    )
    
    return result


# ============================================================================
# VOICE 2: MCP Server (For AI Agents via Claude Desktop/Cursor)
# ============================================================================

# Note: fastapi-mcp automatically converts FastAPI endpoints to MCP tools
# We just need to create a regular FastAPI endpoint and it will be exposed via MCP

async def _analyze_image_with_ai(file_bytes: bytes) -> dict:
    """
    Shared helper to send image to OpenAI Vision API and extract data.
    Returns the raw JSON response from the AI.
    """
    from openai import OpenAI
    import base64
    import json
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Encode image
    base64_image = base64.b64encode(file_bytes).decode('utf-8')
    
    system_prompt = """You are a medical document OCR and extraction expert. 
    Your task is to analyze a vaccination record image and extract structured data.
    
    Perform the following steps:
    1. TRANSCRIPTION: Extract all visible text.
    2. LANGUAGE DETECTION: Detect the primary language.
    3. TRANSLATION: If not English, provide an English translation of the key medical text.
    4. EXTRACTION: Extract vaccine records into a structured list.
    
    For each vaccine record, try to normalize the 'vaccine_name' to one of these standard values if possible:
    MMR, Measles, Mumps, Rubella, Tetanus, Diphtheria, Pertussis, Tdap, Hepatitis A, Hepatitis B, 
    Varicella, Meningococcal, COVID-19, Influenza, HPV, Polio, TB Test.
    If it doesn't match, use the raw name.
    
    Return ONLY a JSON object with this structure:
    {
        "raw_text": "full extracted text...",
        "detected_language": "en" (or "es", "fr", etc.),
        "confidence": 0.95,
        "translation": {
            "original_text": "...",
            "translated_text": "...",
            "confidence": 1.0
        },
        "structured_data": {
            "dates": ["YYYY-MM-DD", ...],
            "vaccines": ["Name1", "Name2"],
            "lot_numbers": ["..."]
        },
        "extracted_vaccines": [
            {
                "vaccine_name": "Standardized Or Raw Name",
                "date": "YYYY-MM-DD",
                "original_text": "Line from doc",
                "lot_number": "...",
                "provider": "..."
            }
        ]
    }
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this vaccination record."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    return json.loads(response.choices[0].message.content)


@app.post("/verify_vaccine_record", response_model=ComplianceResult)
async def verify_vaccine_record(
    image_url: str, 
    session_id: Optional[str] = None,
    standard: str = "us_cdc"
) -> ComplianceResult:
    """
    MCP Tool: Verify a vaccination record from an image URL.
    
    This endpoint is automatically exposed as an MCP tool by fastapi-mcp.
    AI agents (like Claude Desktop) can call this to analyze vaccine records
    by providing an image URL.
    
    Uses the same 3-stage pipeline: Transcription → Translation → Standardization
    
    Args:
        image_url: URL to the vaccination record image
        session_id: Optional session identifier for tracking
        standard: Compliance standard ("us_cdc" or "cornell_tech")
        
    Returns:
        ComplianceResult with all 3 pipeline stages
    """
    import httpx
    from schemas import (
        TranscriptionResult, TranslationResult, StandardizationResult,
        VaccineRecord, VaccineStatus, VaccineName, LanguageCode, ComplianceStandard
    )
    
    try:
        # Download image from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            file_bytes = response.content
            
        # Process with AI
        data = await _analyze_image_with_ai(file_bytes)
        
        # Map to schemas (Reuse logic - ideally this should be shared but duplicating for speed)
        
        # Stage 1: Transcription
        transcription = TranscriptionResult(
            raw_text=data.get("raw_text", ""),
            detected_language=LanguageCode(data.get("detected_language", "en")) if data.get("detected_language") in [l.value for l in LanguageCode] else LanguageCode.UNKNOWN,
            confidence=data.get("confidence", 0.0),
            structured_data=data.get("structured_data", {})
        )
        
        # Stage 2: Translation
        trans_data = data.get("translation", {})
        translation = TranslationResult(
            original_text=trans_data.get("original_text", transcription.raw_text),
            translated_text=trans_data.get("translated_text", transcription.raw_text),
            source_language=transcription.detected_language,
            target_language=LanguageCode.ENGLISH,
            translation_confidence=trans_data.get("confidence", 1.0)
        )
        
        # Stage 3: Standardization
        # Convert extracted vaccines to VaccineRecord objects
        vaccine_records = []
        name_mapping = {
            "MMR II": VaccineName.MMR,
            "Measles Mumps Rubella": VaccineName.MMR,
            "Td": VaccineName.TETANUS,
            "DTap": VaccineName.TDAP,
            "Varicella Zoster": VaccineName.VARICELLA,
            "Chicken Pox": VaccineName.VARICELLA,
            "Meningitis": VaccineName.MENINGOCOCCAL,
            "PPD": VaccineName.TB_TEST,
            "Mantoux": VaccineName.TB_TEST
        }

        for vax in data.get("extracted_vaccines", []):
            v_name_str = vax["vaccine_name"]
            try:
                v_name_enum = VaccineName(v_name_str)
            except ValueError:
                v_name_enum = name_mapping.get(v_name_str)
                if not v_name_enum:
                    for member in VaccineName:
                        if member.value.lower() == v_name_str.lower():
                            v_name_enum = member
                            break
                if not v_name_enum:
                    v_name_enum = VaccineName.OTHER

            vaccine_records.append(
                VaccineRecord(
                    vaccine_name=v_name_enum,
                    date=vax["date"],
                    status=VaccineStatus.COMPLIANT,
                    original_text=vax["original_text"],
                    translated_text=vax.get("original_text"),
                    lot_number=vax.get("lot_number"),
                    provider=vax.get("provider")
                )
            )
            
        # Check compliance
        required_vaccines_map = {
            "us_cdc": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B},
            "cornell_tech": {VaccineName.MMR, VaccineName.TETANUS, VaccineName.HEPATITIS_B, 
                           VaccineName.MENINGOCOCCAL, VaccineName.TB_TEST}
        }
        
        extracted_names = {r.vaccine_name for r in vaccine_records}
        required = required_vaccines_map.get(standard, set())
        missing = list(required - extracted_names)
        is_compliant = len(missing) == 0
        
        standardization = StandardizationResult(
            standard=ComplianceStandard(standard) if standard in [s.value for s in ComplianceStandard] else ComplianceStandard.US_CDC,
            is_compliant=is_compliant,
            records=vaccine_records,
            missing_vaccines=missing,
            compliance_notes=f"Validated against {standard}"
        )
        
        result = ComplianceResult(
            transcription=transcription,
            translation=translation,
            standardization=standardization,
            overall_confidence=transcription.confidence,
            image_url=image_url,
            session_id=session_id,
            processed_at=datetime.utcnow().isoformat()
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vaccine record verification failed: {str(e)}"
        )


# ============================================================================
# MCP Server Integration
# ============================================================================

# Mount MCP server to FastAPI app
# This allows AI agents to discover and use our tools via the MCP protocol
mcp.mount()


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 Personal Vault - Medical Compliance Microservice v2.1")
    print("=" * 80)
    print("Architecture: ONE BRAIN, TWO VOICES")
    print("Pipeline: Upload (Generic) → Standardize (Specific)")
    print("")
    print("🆕 NEW v2.1 Endpoints:")
    print("  → POST http://localhost:8000/upload (Generic Extraction)")
    print("  → POST http://localhost:8000/standardize/cornell_tech")
    print("  → POST http://localhost:8000/standardize/us_cdc")
    print("")
    print("Voice 1 (REST API):")
    print("  → http://localhost:8000/docs")
    print("  → http://localhost:8000/health")
    print("")
    print("Voice 2 (MCP Server):")
    print("  → http://localhost:8000/mcp")
    print("  → Tool: verify_vaccine_record")
    print("")
    print("=" * 80)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
