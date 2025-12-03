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
    
    This tool performs a 3-stage analysis:
    1. Transcription (OCR)
    2. Translation (if needed)
    3. Standardization (checking against requirements)
    
    Args:
        image_url: Public URL of the image to analyze (must be accessible)
        standard: Compliance standard to check against. Options: "us_cdc", "cornell_tech", "uk_nhs", "canada_health". Default: "us_cdc".
        
    Returns:
        A JSON string containing the full compliance result, including extracted vaccines and missing requirements.
    """
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not set in environment."

    try:
        # 1. Download image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
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
        
        # Return as JSON string for the agent to parse
        return result.model_dump_json(indent=2)
        
    except httpx.HTTPStatusError as e:
        return f"Error downloading image: {e}"
    except Exception as e:
        return f"Error processing record: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
