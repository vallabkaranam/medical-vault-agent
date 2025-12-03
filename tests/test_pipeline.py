import httpx
import os
import sys
import json
import time

def test_full_pipeline():
    base_url = "http://localhost:8000"
    image_path = "test_record.jpg"
    
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        sys.exit(1)
        
    print("=== Testing Full Pipeline ===")
    
    # Step 1: Upload
    print(f"\n1. Uploading {image_path}...")
    files = {'file': ('test_record.jpg', open(image_path, 'rb'), 'image/jpeg')}
    
    try:
        upload_response = httpx.post(f"{base_url}/upload", files=files, timeout=60.0)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(upload_response.text)
            return
            
        upload_data = upload_response.json()
        record_id = upload_data.get("record_id")
        print(f"✅ Upload successful. Record ID: {record_id}")
        print(f"   Extracted {len(upload_data.get('extracted_vaccines', []))} vaccines.")
        
        if "placeholder.com" in upload_data.get("image_url", ""):
            print("   ⚠️  Note: Supabase upload failed (using placeholder), but flow continues.")
        
        # Step 2: Standardize (US CDC)
        print(f"\n2. Standardizing against US CDC...")
        std_request = {"record_id": record_id}
        
        cdc_response = httpx.post(
            f"{base_url}/standardize/us_cdc", 
            json=std_request, 
            timeout=30.0
        )
        
        if cdc_response.status_code != 200:
            print(f"❌ Standardization failed: {cdc_response.status_code}")
            print(cdc_response.text)
            return
            
        cdc_data = cdc_response.json()
        print(f"✅ US CDC Standardization successful.")
        print(f"   Compliant: {cdc_data.get('is_compliant')}")
        print(f"   Missing: {cdc_data.get('missing_vaccines')}")
        
        # Step 3: Standardize (Cornell Tech)
        print(f"\n3. Standardizing against Cornell Tech...")
        
        cornell_response = httpx.post(
            f"{base_url}/standardize/cornell_tech", 
            json=std_request, 
            timeout=30.0
        )
        
        if cornell_response.status_code != 200:
            print(f"❌ Standardization failed: {cornell_response.status_code}")
            print(cornell_response.text)
            return
            
        cornell_data = cornell_response.json()
        print(f"✅ Cornell Tech Standardization successful.")
        print(f"   Compliant: {cornell_data.get('is_compliant')}")
        print(f"   Missing: {cornell_data.get('missing_vaccines')}")
        
        print("\n=== Pipeline Verification Complete ===")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_full_pipeline()
