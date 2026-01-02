from fastapi.testclient import TestClient
from api.main import app
import os

client = TestClient(app)

def test_api_endpoints():
    print("=== Testing API Endpoints ===")
    
    # 1. Test Root
    response = client.get("/")
    assert response.status_code == 200
    print("[PASS] Root Endpoint")

    # 2. Test Law Explanation (Module A)
    # Mocking or assuming Module A works. 
    # If Vector DB is empty for Module A, it might return empty sources but should not crash.
    print("\n[Testing] /api/v1/explain")
    payload = {"query": "How to get citizenship?"}
    try:
        response = client.post("/api/v1/explain", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Law Explanation: {data.get('summary', 'No summary')[:50]}...")
        else:
            print(f"[FAIL] Law Explanation: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Law Explanation: {e}")

    # 3. Test Letter Generation (Module C)
    print("\n[Testing] /api/v1/generate-letter")
    payload = {
        "description": "I need a citizenship certificate for my son",
        "additional_data": {"Date": "2081-01-01", "District": "Kathmandu"}
    }
    
    # Check for API Key
    if not os.getenv("MISTRAL_API_KEY"):
        print("[WARN] MISTRAL_API_KEY not set. Skipping generation test to avoid failure.")
    else:
        try:
            response = client.post("/api/v1/generate-letter", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"[PASS] Letter Generation: {data.get('template_used')}")
                else:
                    print(f"[FAIL] Letter Generation: {data.get('error')}")
            else:
                print(f"[FAIL] Letter Generation: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERROR] Letter Generation: {e}")

    # 4. Test Analyze Requirements (Module C)
    print("\n[Testing] /api/v1/analyze-requirements")
    payload = {"description": "I need a citizenship certificate"}
    try:
        response = client.post("/api/v1/analyze-requirements", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"[PASS] Analysis: Missing {data.get('missing_fields')}")
            else:
                print(f"[FAIL] Analysis: {data.get('error')}")
        else:
            print(f"[FAIL] Analysis: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Analysis: {e}")

if __name__ == "__main__":
    test_api_endpoints()
