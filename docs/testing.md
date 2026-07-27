# Testing & Quality Assurance Guide

This document outlines the testing methodologies, configurations, and verification scripts for the Fake News Detection System.

---

## 1. Testing Framework

We use **Pytest** for testing both the FastAPI endpoints and the machine learning modules.

### Prerequisites
Make sure dev dependencies are installed:
```bash
pip install pytest pytest-cov httpx
```

---

## 2. Running the Test Suite

Execute the test suite from the project root:

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=backend/app --cov=model tests/
```

---

## 3. Writing Unit & Integration Tests

### 3.1 Unit Testing the Preprocessor (`tests/test_preprocessing.py`)
Verify that the `TextPreprocessor` correctly cleans and tokenizes raw strings.
Create `tests/test_preprocessing.py`:
```python
from model.preprocessing import TextPreprocessor

def test_clean_text():
    preprocessor = TextPreprocessor()
    raw_text = "<html><body>Verify: Http://Google.Com?q=Test! 123.</body></html>"
    cleaned = preprocessor.clean_text(raw_text)
    
    assert "verify" in cleaned
    assert "google" not in cleaned
    assert "123" not in cleaned
    assert "<html" not in cleaned

def test_tokenize_and_lemmatize():
    preprocessor = TextPreprocessor()
    raw_text = "The scientists are searching for new discoveries."
    processed = preprocessor.tokenize_and_lemmatize(raw_text)
    
    # "scientists" should be lemmatized to "scientist" or "scientific"
    # "searching" should be lemmatized to "searching" or "search"
    # Stopwords like "the", "are", "for" should be removed
    assert "scientist" in processed or "scientific" in processed
    assert "search" in processed
    assert "are" not in processed
```

### 3.2 Testing Database Logging (`tests/test_database.py`)
Verify that the database session creates table columns and commits transactions.
Create `tests/test_database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.history import PredictionHistory

def test_database_model_logs():
    # Use in-memory SQLite database for unit test safety
    engine = create_engine("sqlite:///:memory:")
    SessionClass = sessionmaker(bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = SessionClass()
    
    # Write mock history log
    log = PredictionHistory(
        text_snippet="Relief package passed...",
        predicted_label="Real News",
        confidence=0.941
    )
    db.add(log)
    db.commit()
    
    # Query database
    retrieved = db.query(PredictionHistory).first()
    assert retrieved is not None
    assert retrieved.predicted_label == "Real News"
    assert retrieved.confidence == 0.941
    
    db.close()
```

### 3.3 Integration Testing API Endpoints (`tests/test_endpoints.py`)
Use `httpx.Client` to verify endpoints respond with appropriate payload schemas and status codes.
Create `tests/test_endpoints.py`:
```python
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
```
