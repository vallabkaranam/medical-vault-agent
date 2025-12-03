"""
Data Contract for Personal Vault Medical Compliance Microservice.

This module defines the Pydantic models and enums that serve as the data contract
for the 3-stage pipeline: Transcription → Translation → Standardization.
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS: Standardized Values
# ============================================================================

class LanguageCode(str, Enum):
    """ISO 639-1 language codes for international support."""
    ENGLISH = "en"
    SPANISH = "es"
    CHINESE = "zh"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    ARABIC = "ar"
    HINDI = "hi"
    UNKNOWN = "unknown"


class ComplianceStandard(str, Enum):
    """
    Supported compliance standards for vaccine requirements.
    Each standard has different required vaccines and rules.
    """
    US_CDC = "us_cdc"  # General US CDC guidelines
    CORNELL_TECH = "cornell_tech"  # Cornell Tech specific requirements (POC)
    UK_NHS = "uk_nhs"  # UK NHS requirements
    CANADA_HEALTH = "canada_health"  # Canada Health requirements


class VaccineName(str, Enum):
    """
    Standardized vaccine names to prevent AI hallucinations.
    The AI must map extracted text to one of these enum values.
    """
    MMR = "MMR"
    MEASLES = "Measles"
    MUMPS = "Mumps"
    RUBELLA = "Rubella"
    TETANUS = "Tetanus"
    DIPHTHERIA = "Diphtheria"
    PERTUSSIS = "Pertussis"
    TDAP = "Tdap"
    HEPATITIS_A = "Hepatitis A"
    HEPATITIS_B = "Hepatitis B"
    VARICELLA = "Varicella"
    MENINGOCOCCAL = "Meningococcal"
    COVID_19 = "COVID-19"
    INFLUENZA = "Influenza"
    HPV = "HPV"
    POLIO = "Polio"
    TB_TEST = "TB Test"
    OTHER = "Other"


class VaccineStatus(str, Enum):
    """Compliance status for each vaccine record."""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    REVIEW_NEEDED = "Review Needed"
    EXPIRED = "Expired"


# ============================================================================
# STAGE 1: TRANSCRIPTION
# ============================================================================

class TranscriptionResult(BaseModel):
    """
    Result from Stage 1: OCR/Vision AI transcription.
    Raw text extraction with language detection.
    """
    raw_text: str = Field(
        ...,
        description="Raw text extracted from the image"
    )
    detected_language: LanguageCode = Field(
        ...,
        description="Detected language of the document"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="OCR confidence score"
    )
    structured_data: Optional[Dict] = Field(
        None,
        description="Any structured data extracted (dates, names, etc.)"
    )


# ============================================================================
# STAGE 2: TRANSLATION
# ============================================================================

class TranslationResult(BaseModel):
    """
    Result from Stage 2: Translation to English (if needed).
    """
    original_text: str = Field(
        ...,
        description="Original text before translation"
    )
    translated_text: str = Field(
        ...,
        description="Text translated to English (same as original if already English)"
    )
    source_language: LanguageCode = Field(
        ...,
        description="Source language detected"
    )
    target_language: LanguageCode = Field(
        default=LanguageCode.ENGLISH,
        description="Target language (always English)"
    )
    translation_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Translation quality confidence"
    )


# ============================================================================
# STAGE 3: STANDARDIZATION
# ============================================================================

class VaccineRecord(BaseModel):
    """
    Standardized vaccine record after Stage 3.
    Mapped to compliance standard requirements.
    """
    vaccine_name: VaccineName = Field(
        ...,
        description="Standardized vaccine name"
    )
    date: str = Field(
        ...,
        description="Vaccination date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    status: VaccineStatus = Field(
        ...,
        description="Compliance status against selected standard"
    )
    original_text: str = Field(
        ...,
        description="Original text from document (for data lineage)"
    )
    translated_text: Optional[str] = Field(
        None,
        description="Translated text if translation was performed"
    )
    lot_number: Optional[str] = Field(
        None,
        description="Vaccine lot number if available"
    )
    provider: Optional[str] = Field(
        None,
        description="Healthcare provider or clinic name"
    )
    expiration_date: Optional[str] = Field(
        None,
        description="Expiration date if applicable (for TB tests, etc.)"
    )


class StandardizationResult(BaseModel):
    """
    Result from Stage 3: Standardization against compliance standard.
    """
    standard: ComplianceStandard = Field(
        ...,
        description="Compliance standard used for validation"
    )
    is_compliant: bool = Field(
        ...,
        description="Overall compliance status"
    )
    records: List[VaccineRecord] = Field(
        default_factory=list,
        description="Standardized vaccine records"
    )
    missing_vaccines: List[VaccineName] = Field(
        default_factory=list,
        description="Required vaccines missing for this standard"
    )
    compliance_notes: Optional[str] = Field(
        None,
        description="Additional notes about compliance status"
    )


# ============================================================================
# COMPLETE PIPELINE RESULT
# ============================================================================

class UploadResult(BaseModel):
    """
    Result from upload endpoint (Transcription + Translation only).
    Generic extracted data before any standardization is applied.
    """
    record_id: str = Field(
        ...,
        description="Unique identifier for this uploaded record"
    )
    transcription: TranscriptionResult = Field(
        ...,
        description="Stage 1: Transcription result"
    )
    translation: TranslationResult = Field(
        ...,
        description="Stage 2: Translation result"
    )
    extracted_vaccines: List[Dict] = Field(
        default_factory=list,
        description="Generic vaccine data extracted (no standard applied)"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to uploaded image in storage"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for tracking"
    )
    uploaded_at: str = Field(
        ...,
        description="ISO 8601 timestamp of upload"
    )


class StandardizationRequest(BaseModel):
    """
    Request to standardize an uploaded record against a specific standard.
    """
    record_id: str = Field(
        ...,
        description="ID of the uploaded record to standardize"
    )


class ComplianceResult(BaseModel):
    """
    Complete result from the 3-stage pipeline.
    Combines Transcription → Translation → Standardization.
    """
    # Pipeline stages
    transcription: TranscriptionResult = Field(
        ...,
        description="Stage 1: Transcription result"
    )
    translation: TranslationResult = Field(
        ...,
        description="Stage 2: Translation result"
    )
    standardization: StandardizationResult = Field(
        ...,
        description="Stage 3: Standardization result"
    )
    
    # Overall metadata
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall pipeline confidence score"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to uploaded image in storage"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for tracking"
    )
    processed_at: str = Field(
        ...,
        description="ISO 8601 timestamp of processing"
    )


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint."""
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for tracking"
    )
    standard: ComplianceStandard = Field(
        default=ComplianceStandard.US_CDC,
        description="Compliance standard to validate against"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    mode: str = Field(..., description="Operating mode")
    version: str = Field(default="2.0.0", description="API version")
    pipeline: str = Field(
        default="Transcription → Translation → Standardization",
        description="Pipeline architecture"
    )


# ============================================================================
# AGENT-OPTIMIZED MODELS (Voice 2)
# ============================================================================

class AgentError(BaseModel):
    """
    Standardized error format for AI agents.
    Allows agents to reason about failures (e.g., retry on DOWNLOAD_ERROR).
    """
    code: str = Field(..., description="Machine-readable error code (e.g., IMAGE_NOT_FOUND)")
    message: str = Field(..., description="Human-readable error message")
    suggestion: Optional[str] = Field(None, description="Suggestion for the agent on how to proceed")


class AgentComplianceResponse(BaseModel):
    """
    Token-efficient, flat response optimized for LLM agents.
    Surfaces the most critical decision-making data to the top level.
    """
    is_compliant: bool = Field(..., description="Is the record compliant with the standard?")
    missing_vaccines: List[str] = Field(..., description="List of missing vaccine names")
    extracted_vaccines: List[str] = Field(..., description="List of vaccines found in the record")
    compliance_summary: str = Field(..., description="Natural language summary of the compliance status")
    
    # Detailed evidence (nested but optional/secondary)
    evidence: Optional[Dict] = Field(
        None, 
        description="Detailed evidence including dates and providers if needed for deep verification"
    )
    
    overall_confidence: float = Field(..., description="Confidence score of the analysis")

