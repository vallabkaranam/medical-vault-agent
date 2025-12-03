"""
Medical Vault MCP Server (Voice 2)
This server exposes the core medical record analysis logic to AI agents (Claude, Cursor, etc.)
via the Model Context Protocol (MCP).
"""

import os
import httpx
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import core services and schemas
# Note: We assume this is run from the backend directory
from services import analyze_image_with_ai, perform_standardization, process_ai_result
from schemas import ComplianceResult, LanguageCode, TranscriptionResult, TranslationResult

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize MCP Server
mcp = FastMCP("Medical Vault")

@mcp.tool()
async def verify_vaccine_record(image_url: str, standard: str = "us_cdc") -> str:
    """
    Verify a vaccination record from an image URL against a compliance standard.
    
    Use this tool when you need to check if a medical document meets specific health requirements.
    It performs OCR, translation, and standardization in one step.
    
    Args:
        image_url: The public, accessible URL of the image file (JPG/PNG/PDF).
        standard: The compliance standard to validate against. 
                  Supported values: "us_cdc", "cornell_tech", "uk_nhs", "canada_health".
                  Default: "us_cdc".
        
    Returns:
        A JSON string containing the structured compliance result.
        On error, returns a JSON object with an "error" key and "code".
    """
    if not OPENAI_API_KEY:
        return '{"error": {"code": "CONFIG_ERROR", "message": "OPENAI_API_KEY not set"}}'

    try:
        # 1. Download image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code == 404:
                return '{"error": {"code": "IMAGE_NOT_FOUND", "message": "The image URL could not be reached."}}'
            response.raise_for_status()
            file_bytes = response.content
            
        # 2. Process with AI (Brain)
        data = await analyze_image_with_ai(file_bytes, OPENAI_API_KEY)
        
        # 3. Map to schemas
        transcription, translation, extracted_vaccines = process_ai_result(data)
        
        # 4. Standardize
        standardization = perform_standardization(standard, extracted_vaccines)
        
        # 5. Construct Result
        result = ComplianceResult(
            transcription=transcription,
            translation=translation,
            standardization=standardization,
            overall_confidence=transcription.confidence,
            image_url=image_url,
            session_id="mcp-agent-session",
            processed_at=transcription.structured_data.get("processed_at", "") # Fallback or new date
        )
        
        # Return as JSON string for the agent to parse (Token-Efficient)
        # We use exclude_none=True to keep the payload smaller
        return result.model_dump_json(indent=2, exclude_none=True)
        
    except httpx.HTTPStatusError as e:
        return f'{{"error": {{"code": "DOWNLOAD_ERROR", "message": "{str(e)}"}} }}'
    except Exception as e:
        return f'{{"error": {{"code": "PROCESSING_ERROR", "message": "{str(e)}"}} }}'

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
