import httpx
import os
import sys

# Add parent directory to path to import schemas if needed, but we'll just use raw dicts for simplicity
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE_PATH = "test_record.jpg"

def test_pipeline():
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"Error: {TEST_IMAGE_PATH} not found.")
        return

    print(f"Testing pipeline with {TEST_IMAGE_PATH}...")

    # 1. Upload
    print("\n--- Step 1: Uploading Image ---")
    try:
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"file": ("test_record.jpg", f, "image/jpeg")}
            response = httpx.post(f"{BASE_URL}/upload", files=files)
            
        if response.status_code != 200:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return
            
        upload_result = response.json()
        print("Upload Successful!")
        print(f"Record ID: {upload_result.get('record_id')}")
        print(f"Image URL: {upload_result.get('image_url')}")
        print(f"Extracted Vaccines: {len(upload_result.get('extracted_vaccines', []))}")
        
        record_id = upload_result.get('record_id')
        
    except Exception as e:
        print(f"Upload exception: {e}")
        return

    # 2. Standardize
    print("\n--- Step 2: Standardizing (US CDC) ---")
    try:
        payload = {"record_id": record_id}
        response = httpx.post(f"{BASE_URL}/standardize/us_cdc", json=payload)
        
        if response.status_code != 200:
            print(f"Standardization failed: {response.status_code} - {response.text}")
            return
            
        std_result = response.json()
        print("Standardization Successful!")
        print(f"Is Compliant: {std_result.get('is_compliant')}")
        print(f"Missing Vaccines: {std_result.get('missing_vaccines')}")
        print(f"Records: {len(std_result.get('records', []))}")
        
    except Exception as e:
        print(f"Standardization exception: {e}")
        return

if __name__ == "__main__":
    test_pipeline()
