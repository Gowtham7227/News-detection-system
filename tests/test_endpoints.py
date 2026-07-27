import os
import sys

# Ensure backend directory is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code in [200, 503]
    json_data = response.json()
    assert "status" in json_data
    assert "environment" in json_data

def test_prediction_validation():
    # Payload is too short (min_length=10)
    response = client.post(
        "/api/v1/predict",
        json={"text": "Short"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()
