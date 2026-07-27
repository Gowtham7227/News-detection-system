from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.history import PredictionHistory
from app.schemas.prediction import HistoryItem

router = APIRouter()


@router.get("/history", response_model=List[HistoryItem], summary="Fetch historical classification records")
def get_prediction_history(
    skip: int = Query(0, ge=0, description="Offset index for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Page limit size for history retrieval"),
    db: Session = Depends(get_db)
):
    """
    Queries prediction history database logs, sorted in reverse-chronological order.
    Supports basic limit/offset pagination.
    """
    history = db.query(PredictionHistory)\
        .order_by(PredictionHistory.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    return history
