"""
Comprehensive Test Suite for Medical Vault Backend
Tests all endpoints, error handling, and edge cases.
"""

import httpx
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE_PATH = "test_record.jpg"

def test_health_check():
    """Test 1: Health check endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data["status"] == "running", "Service should be running"
    assert "version" in data, "Version should be present"
    
    print("✅ Health check passed")
    print(f"   Status: {data['status']}")
    print(f"   Version: {data['version']}")
    print(f"   Mode: {data['mode']}")


def test_upload_endpoint():
    """Test 2: Upload endpoint with real file"""
    print("\n" + "="*80)
    print("TEST 2: Upload Endpoint")
    print("="*80)
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"⚠️  Skipping: {TEST_IMAGE_PATH} not found")
        return None
    
    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"file": ("test_record.jpg", f, "image/jpeg")}
        data = {"session_id": "test_session_001"}
        response = httpx.post(f"{BASE_URL}/upload", files=files, data=data, timeout=30.0)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    result = response.json()
    assert "record_id" in result, "record_id should be present"
    assert "transcription" in result, "transcription should be present"
    assert "translation" in result, "translation should be present"
    assert "extracted_vaccines" in result, "extracted_vaccines should be present"
    
    print("✅ Upload passed")
    print(f"   Record ID: {result['record_id']}")
    print(f"   Extracted Vaccines: {len(result['extracted_vaccines'])}")
    print(f"   Confidence: {result['transcription']['confidence']}")
    
    return result["record_id"]


def test_standardize_endpoint(record_id):
    """Test 3: Standardization endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Standardization Endpoint")
    print("="*80)
    
    if not record_id:
        print("⚠️  Skipping: No record_id from upload")
        return
    
    payload = {"record_id": record_id}
    response = httpx.post(f"{BASE_URL}/standardize/us_cdc", json=payload, timeout=10.0)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    result = response.json()
    assert "is_compliant" in result, "is_compliant should be present"
    assert "records" in result, "records should be present"
    assert "missing_vaccines" in result, "missing_vaccines should be present"
    
    print("✅ Standardization passed")
    print(f"   Standard: {result['standard']}")
    print(f"   Is Compliant: {result['is_compliant']}")
    print(f"   Missing Vaccines: {result['missing_vaccines']}")
    print(f"   Found Records: {len(result['records'])}")


def test_get_session_records():
    """Test 4: Get session records endpoint"""
    print("\n" + "="*80)
    print("TEST 4: Get Session Records")
    print("="*80)
    
    response = httpx.get(f"{BASE_URL}/records/test_session_001", timeout=10.0)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    records = response.json()
    assert isinstance(records, list), "Should return a list"
    
    print("✅ Get session records passed")
    print(f"   Records found: {len(records)}")


def test_invalid_file_type():
    """Test 5: Error handling - invalid file type"""
    print("\n" + "="*80)
    print("TEST 5: Error Handling - Invalid File Type")
    print("="*80)
    
    # Create a fake text file
    files = {"file": ("test.txt", b"This is not an image", "text/plain")}
    response = httpx.post(f"{BASE_URL}/upload", files=files, timeout=10.0)
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    print("✅ Invalid file type correctly rejected")


def test_missing_record():
    """Test 6: Error handling - missing record"""
    print("\n" + "="*80)
    print("TEST 6: Error Handling - Missing Record")
    print("="*80)
    
    payload = {"record_id": "00000000-0000-0000-0000-000000000000"}
    response = httpx.post(f"{BASE_URL}/standardize/us_cdc", json=payload, timeout=10.0)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    print("✅ Missing record correctly handled")


def test_invalid_standard():
    """Test 7: Error handling - invalid standard"""
    print("\n" + "="*80)
    print("TEST 7: Error Handling - Invalid Standard")
    print("="*80)
    
    payload = {"record_id": "dummy"}
    response = httpx.post(f"{BASE_URL}/standardize/invalid_standard", json=payload, timeout=10.0)
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    print("✅ Invalid standard correctly rejected")


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "🧪 " * 20)
    print("COMPREHENSIVE BACKEND TEST SUITE")
    print("🧪 " * 20)
    
    try:
        # Correctness Tests
        test_health_check()
        record_id = test_upload_endpoint()
        test_standardize_endpoint(record_id)
        test_get_session_records()
        
        # Error Handling Tests
        test_invalid_file_type()
        test_missing_record()
        test_invalid_standard()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
