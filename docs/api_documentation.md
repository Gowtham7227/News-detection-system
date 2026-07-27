# Backend API Specification (V1)

This document contains descriptions, sample payloads, and status codes for the endpoints in the VeritasAI backend.

---

## 1. Base URL
Local API Endpoint prefix:
```text
http://127.0.0.1:8000/api/v1
```

Interactive OpenAPI docs:
```text
http://127.0.0.1:8000/docs
```

---

## 2. API Endpoints

### 2.1 Health Check
*   **Method**: `GET`
*   **Path**: `/health`
*   **Summary**: Verifies API configuration states, database availability, and model readiness.
*   **Response Codes**:
    *   `200 OK`: Database connected, model is trained.
    *   `503 Service Unavailable`: Database is offline, or model weights are missing.
*   **Sample Response**:
    ```json
    {
      "status": "healthy",
      "environment": "development",
      "database_connected": true,
      "model_trained": true,
      "api_version": "1.0.0"
    }
    ```

---

### 2.2 Text Prediction
*   **Method**: `POST`
*   **Path**: `/api/v1/predict`
*   **Summary**: Classifies the authenticity of raw text bodies.
*   **Request Schema (`PredictRequest`)**:
    ```json
    {
      "text": "Paste news article paragraphs here (min 10 characters)..."
    }
    ```
*   **Response Codes**:
    *   `200 OK`: Successful classification.
    *   `422 Unprocessable Entity`: Input validation failure (e.g. text too short).
    *   `503 Service Unavailable`: Active model is not trained yet.
*   **Sample Response**:
    ```json
    {
      "text_snippet": "Congress passed the economic relief bill yesterday with bipartisan support. The new...",
      "label": "Real News",
      "label_id": 1,
      "confidence": 0.9654,
      "timestamp": "2026-07-27T12:35:48.123456Z",
      "status": "Success"
    }
    ```

---

### 2.3 Document Upload & Prediction
*   **Method**: `POST`
*   **Path**: `/api/v1/upload`
*   **Summary**: Uploads a file (PDF, DOCX, TXT) and processes predictions.
*   **Request Headers**: `Content-Type: multipart/form-data`
*   **Request Schema**:
    *   `file`: Binary file stream.
*   **Response Codes**:
    *   `200 OK`: File parsed and classified successfully.
    *   `400 Bad Request`: File type not allowed (only txt, pdf, docx allowed).
    *   `413 Payload Too Large`: Upload exceeds maximum size (5MB).
    *   `422 Unprocessable Entity`: Extracted text is empty or too short.
*   **Sample Response**:
    ```json
    {
      "text_snippet": "SHOCKING: Secret documents prove the government is using weather control satellites...",
      "label": "Fake News",
      "label_id": 0,
      "confidence": 0.9981,
      "timestamp": "2026-07-27T12:37:51.987654Z",
      "status": "Success"
    }
    ```

---

### 2.4 Model Retraining
*   **Method**: `POST`
*   **Path**: `/api/v1/retrain`
*   **Summary**: Triggers background retraining pipelines asynchronously.
*   **Response Codes**:
    *   `202 Accepted`: Retraining triggered.
*   **Sample Response**:
    ```json
    {
      "status": "Accepted",
      "message": "Model retraining pipeline launched successfully in background."
    }
    ```

---

### 2.5 Active Model Performance Metrics
*   **Method**: `GET`
*   **Path**: `/api/v1/metrics`
*   **Summary**: Retrieves performance statistics (Accuracy, Precision, Recall, F1) and the confusion matrix.
*   **Response Codes**:
    *   `200 OK`: Metrics loaded.
    *   `404 Not Found`: Metrics file missing.
*   **Sample Response**:
    ```json
    {
      "accuracy": 0.925,
      "precision": 0.941,
      "recall": 0.912,
      "f1_score": 0.926,
      "confusion_matrix": {
        "tn": 46,
        "fp": 4,
        "fn": 5,
        "tp": 45
      }
    }
    ```

---

### 2.6 Active Model Info
*   **Method**: `GET`
*   **Path**: `/api/v1/model-info`
*   **Summary**: Retrieves details about the loaded model.
*   **Response Codes**:
    *   `200 OK`: Information loaded.
*   **Sample Response**:
    ```json
    {
      "model_name": "LinearSVC",
      "vectorizer_type": "TfidfVectorizer",
      "max_features": 5000,
      "vocabulary_size": 5000,
      "last_trained": "2026-07-27 18:07:36",
      "status": "Active"
    }
    ```

---

### 2.7 Prediction History Logs
*   **Method**: `GET`
*   **Path**: `/api/v1/history`
*   **Summary**: Retrieves paginated prediction history logs.
*   **Query Parameters**:
    *   `skip`: Number of records to skip (default `0`).
    *   `limit`: Page size limit (default `10`, max `100`).
*   **Response Codes**:
    *   `200 OK`: History loaded.
*   **Sample Response**:
    ```json
    [
      {
        "id": 1,
        "text_snippet": "Congress passed the economic relief bill yesterday with bipartisan support...",
        "file_name": null,
        "predicted_label": "Real News",
        "confidence": 0.9654,
        "timestamp": "2026-07-27T12:35:48.123456Z"
      }
    ]
    ```
