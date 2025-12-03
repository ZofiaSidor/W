from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from hash_chain import Amendment, HashChain, LLMSummaryGenerator

app = FastAPI(
    title="Legal Act Change Tracker API",
    description="Track legal amendments",
    version="1.0.0"
)

llm_generator = LLMSummaryGenerator()
current_chain: Optional[HashChain] = None

# ...existing models...

class AmendmentRequest(BaseModel):
    content: str
    change_type: str
    author: str
    summary: Optional[str] = None

@app.get("/")
def root():
    """API root"""
    return {
        "api_name": "Legal Act Change Tracker",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}

@app.get("/amendments")
def list_amendments(skip: int = 0, limit: int = 10):
    """List amendments"""
    if not current_chain:
        return {"error": "No chain loaded"}
    
    history = current_chain.get_history()
    return {"amendments": history[skip:skip + limit], "total": len(history)}

@app.post("/ingest")
def ingest_xml(filepath: str):
    """Ingest XML"""
    return {"success": True, "message": f"Would ingest {filepath}"}

@app.get("/verify")
def verify():
    """Verify chain"""
    if not current_chain:
        return {"valid": False, "error": "No chain"}
    
    is_valid = current_chain.verify_integrity()
    return {"valid": is_valid, "amendments": len(current_chain.chain)}


if __name__ == "__main__":
    print("\n" + "="*70)
    print("API MODULE - DEBUG TEST")
    print("="*70)
    
    # Create test client
    client = TestClient(app)
    
    # TEST 1: Root endpoint
    print("\n✓ TEST 1: Root Endpoint")
    try:
        response = client.get("/")
        print(f"  ✓ Status: {response.status_code}")
        data = response.json()
        assert data["api_name"] == "Legal Act Change Tracker"
        print(f"  ✓ API name: {data['api_name']}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 2: Health check
    print("\n✓ TEST 2: Health Check")
    try:
        response = client.get("/health")
        print(f"  ✓ Status: {response.status_code}")
        data = response.json()
        assert data["status"] == "healthy"
        print(f"  ✓ Health status: {data['status']}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 3: List amendments (empty)
    print("\n✓ TEST 3: List Amendments (Empty)")
    try:
        response = client.get("/amendments")
        print(f"  ✓ Status: {response.status_code}")
        data = response.json()
        assert "error" in data
        print(f"  ✓ Expected error: {data['error']}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 4: Ingest endpoint
    print("\n✓ TEST 4: Ingest Endpoint")
    try:
        response = client.post("/ingest?filepath=test.xml")
        print(f"  ✓ Status: {response.status_code}")
        data = response.json()
        assert data["success"] == True
        print(f"  ✓ Response: {data['message']}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    # TEST 5: Verify endpoint
    print("\n✓ TEST 5: Verify Endpoint")
    try:
        response = client.get("/verify")
        print(f"  ✓ Status: {response.status_code}")
        data = response.json()
        print(f"  ✓ Verification result: {data}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        exit(1)
    
    print("\n" + "="*70)
    print("✓ ALL API TESTS PASSED!")
    print("="*70 + "\n")
