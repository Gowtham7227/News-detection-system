from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """
    Pydantic schema validation for incoming prediction request text.
    """
    text: str = Field(
        ..., 
        min_length=10, 
        max_length=50000, 
        description="The news article text to analyze for authenticity."
    )


class PredictResponse(BaseModel):
    """
    Pydantic schema structure for prediction outputs.
    """
    text_snippet: str = Field(..., description="Truncated snippet of the analyzed text.")
    label: str = Field(..., description="Predicted class label (Real News or Fake News).")
    label_id: int = Field(..., description="Numerical representation: 0 for Fake, 1 for Real.")
    confidence: float = Field(..., description="Prediction confidence percentage (0.0 to 1.0).")
    timestamp: datetime = Field(..., description="Prediction run timestamp.")
    status: str = Field(..., description="Response status message.")


class HistoryItem(BaseModel):
    """
    Pydantic schema representing an entry in prediction history.
    """
    id: int
    text_snippet: str
    file_name: Optional[str] = None
    predicted_label: str
    confidence: float
    timestamp: datetime

    class Config:
        from_attributes = True


class ModelMetrics(BaseModel):
    """
    Pydantic schema for active model performance metrics.
    """
    accuracy: float
    precision: float
    recall: float
    f1_score: float


class ModelInfoResponse(BaseModel):
    """
    Pydantic schema returning information about active models.
    """
    model_name: str
    vectorizer_type: str
    max_features: int
    vocabulary_size: int
    last_trained: str
    status: str
