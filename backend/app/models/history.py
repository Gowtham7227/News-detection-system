import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core.database import Base


class PredictionHistory(Base):
    """
    SQLAlchemy model for tracking predictions history in SQLite.
    Stores metadata, predicted labels, confidence levels, and input texts.
    """
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    text_snippet = Column(Text, nullable=False)
    file_name = Column(String, nullable=True)
    predicted_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
