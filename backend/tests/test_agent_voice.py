import asyncio
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import verify_vaccine_record

async def test_agent_voice():
    print("🧪 Testing Voice 2 (MCP Server) Implementation...")
    
    # Mock the httpx.AsyncClient to avoid real network calls
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_bytes"
    mock_response.raise_for_status = MagicMock()

    # Mock context manager for httpx.AsyncClient
    mock_client = MagicMock()
    # Make get return a coroutine
    async def async_get(*args, **kwargs):
        return mock_response
    mock_client.get = MagicMock(side_effect=async_get)
    
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch('httpx.AsyncClient', return_value=mock_client):
        # Run the tool
        print("\n--- Calling verify_vaccine_record (Mocked) ---")
        result_json = await verify_vaccine_record("http://example.com/vax.jpg", "us_cdc")
        
        # Parse result
        try:
            result = json.loads(result_json)
            print("✅ Result is valid JSON")
            
            if "error" in result:
                print(f"❌ Error returned: {result['error']}")
            else:
                print("✅ Success Response:")
                print(json.dumps(result, indent=2))
                
                # Verify structure
                assert "is_compliant" in result
                assert "compliance_summary" in result
                assert "evidence" in result
                print("✅ Schema validation passed (AgentComplianceResponse)")
                
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON: {result_json}")

if __name__ == "__main__":
    # Ensure MOCK_AI is set
    os.environ["MOCK_AI"] = "true"
    os.environ["OPENAI_API_KEY"] = "sk-mock-key" # Dummy key to pass check
    
    asyncio.run(test_agent_voice())
