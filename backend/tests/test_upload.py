import httpx
import os
import sys
import json

def test_upload_flow():
    url = "http://localhost:8000/upload"
    image_path = "test_record.jpg"
    
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found. Run create_image.py first.")
        sys.exit(1)
        
    print(f"Testing upload to {url} with {image_path}...")
    
    files = {'file': ('test_record.jpg', open(image_path, 'rb'), 'image/jpeg')}
    
    try:
        response = httpx.post(url, files=files, timeout=30.0)
        
        if response.status_code == 200:
            print("✅ Success! Response:")
            print(json.dumps(response.json(), indent=2))
            
            # Basic assertions
            data = response.json()
            assert "record_id" in data
            assert "transcription" in data
            assert "extracted_vaccines" in data
            
            # Check if our mocked/AI extracted data is there
            vaccines = data.get("extracted_vaccines", [])
            print(f"\nFound {len(vaccines)} vaccines.")
            
        else:
            print(f"❌ Failed with status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_upload_flow()
