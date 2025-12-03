"""
Medical Vault MCP Server (Voice 2)
This server exposes the core medical record analysis logic to AI agents (Claude, Cursor, etc.)
via the Model Context Protocol (MCP).

Best Practices Implemented:
1. Semantic, Typed APIs (Pydantic Models)
2. Machine-Readable Errors (AgentError)
3. Token-Aware, Flat Responses (AgentComplianceResponse)
4. Action-Oriented Naming (verify_vaccine_record)
"""

import os
import httpx
import json
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import core services and schemas
from services import analyze_image_with_ai, perform_standardization, process_ai_result
from schemas import (
    ComplianceResult, 
    AgentComplianceResponse, 
    AgentError,
    LanguageCode
)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize MCP Server
mcp = FastMCP("Medical Vault")

def _create_error(code: str, message: str, suggestion: str = None) -> str:
    """Helper to create a standardized machine-readable error response."""
    return json.dumps({
        "error": AgentError(
            code=code, 
            message=message, 
            suggestion=suggestion
        ).model_dump()
    })

@mcp.tool()
async def verify_vaccine_record(image_url: str, standard: str = "us_cdc") -> str:
    """
    Verify a vaccination record from an image URL against a compliance standard.
    
    This tool performs a complete analysis pipeline:
    1. OCR & Transcription (reads the text)
    2. Translation (if not in English)
    3. Standardization (maps to vaccine codes)
    4. Compliance Check (verifies against rules)

    Args:
        image_url: The public, accessible URL of the image file (JPG/PNG/PDF).
        standard: The compliance standard to validate against. 
                  Supported: "us_cdc", "cornell_tech", "uk_nhs", "canada_health".
                  Default: "us_cdc".
        
    Returns:
        A JSON string containing the 'AgentComplianceResponse'.
        
    Example Response:
    {
      "is_compliant": false,
      "missing_vaccines": ["Hepatitis B"],
      "extracted_vaccines": ["MMR", "Tetanus"],
      "compliance_summary": "Non-Compliant. Missing Hepatitis B.",
      "overall_confidence": 0.98
    }
    """
    if not OPENAI_API_KEY:
        return _create_error(
            "CONFIG_ERROR", 
            "OPENAI_API_KEY not set on server.",
            "Please contact the system administrator to configure the backend."
        )

    try:
        # 1. Download image
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(image_url)
                if response.status_code == 404:
                    return _create_error(
                        "IMAGE_NOT_FOUND", 
                        f"The image at {image_url} could not be found (404).",
                        "Check the URL and try again."
                    )
                response.raise_for_status()
                file_bytes = response.content
            except httpx.RequestError as e:
                return _create_error(
                    "DOWNLOAD_ERROR", 
                    f"Failed to download image: {str(e)}",
                    "Ensure the URL is publicly accessible and valid."
                )
            
        # 2. Process with AI (Brain)
        # Note: analyze_image_with_ai handles the OpenAI call
        data = await analyze_image_with_ai(file_bytes, OPENAI_API_KEY)
        
        # 3. Map to schemas
        transcription, translation, extracted_vaccines = process_ai_result(data)
        
        # 4. Standardize
        standardization = perform_standardization(standard, extracted_vaccines)
        
        # 5. Construct Agent-Optimized Result (Flat & Token-Efficient)
        
        # Create simple lists for the agent
        found_vax_names = [v.vaccine_name.value for v in standardization.records]
        missing_vax_names = [v.value for v in standardization.missing_vaccines]
        
        # Create evidence dict (lighter than full objects)
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
        
        response_model = AgentComplianceResponse(
            is_compliant=standardization.is_compliant,
            missing_vaccines=missing_vax_names,
            extracted_vaccines=found_vax_names,
            compliance_summary=standardization.compliance_notes or "Analysis complete.",
            evidence=evidence,
            overall_confidence=transcription.confidence
        )
        
        # Return as JSON string
        return response_model.model_dump_json(indent=2)
        
    except Exception as e:
        return _create_error(
            "PROCESSING_ERROR", 
            f"An unexpected error occurred: {str(e)}",
            "This may be a temporary system issue. Please try again."
        )

if __name__ == "__main__":
    # Run the MCP server
    print("🚀 Starting Medical Vault MCP Server (Voice 2)...")
    mcp.run()
