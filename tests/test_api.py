from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Testing for the Health Check
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Zorvyn API Vault" in response.json()["status"]

# 2. Testing the Security Perimeter (Unauthorized Access)
def test_unauthorized_records_access():
    # Trying to get records without a token
    response = client.get("/api/v1/records/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# 3. Test Invalid Login (Timing Attack Mitigation Check)
def test_invalid_login():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "fakeuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials"