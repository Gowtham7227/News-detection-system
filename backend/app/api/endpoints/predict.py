import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.history import PredictionHistory
from app.schemas.prediction import PredictRequest, PredictResponse
from app.services.parser import DocumentParser
from app.core.config import settings

# Lazy import model predictor to allow server to boot even if no model trained yet
try:
    from model.predict import FakeNewsPredictor
    PREDICTOR_LOADED = True
except ImportError:
    PREDICTOR_LOADED = False

router = APIRouter()
logger = logging.getLogger("fakenews.predict")


def get_predictor():
    """
    Dependency resolver for FakeNewsPredictor.
    Ensures model artifacts are present before running predictions.
    """
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model is not initialized or trained yet."
        )
    try:
        return FakeNewsPredictor()
    except Exception as e:
        logger.error(f"Failed to load predictor artifacts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading classification model: {str(e)}"
        )


@router.post("/predict", response_model=PredictResponse, summary="Predict truth score on raw text article")
def predict_text(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    predictor: FakeNewsPredictor = Depends(get_predictor)
):
    """
    Analyzes news article plain-text body, determines authenticity classification (Real/Fake),
    and records the transaction inside prediction history database.
    """
    try:
        # Run classification model
        result = predictor.predict(payload.text)
        
        if result.get("status") != "Success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("status", "Prediction failed")
            )
            
        snippet = payload.text[:150] + ("..." if len(payload.text) > 150 else "")
        
        # Save to database history
        history_item = PredictionHistory(
            text_snippet=snippet,
            predicted_label=result["label"],
            confidence=result["confidence"]
        )
        db.add(history_item)
        db.commit()
        db.refresh(history_item)
        
        return PredictResponse(
            text_snippet=snippet,
            label=result["label"],
            label_id=result["label_id"],
            confidence=result["confidence"],
            timestamp=datetime.datetime.utcnow(),
            status="Success"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/upload", response_model=PredictResponse, summary="Analyze uploaded document file")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    predictor: FakeNewsPredictor = Depends(get_predictor)
):
    """
    Uploads a file (txt, pdf, docx), parses text content, classifies authenticity,
    and logs prediction transaction inside history database.
    """
    # 1. Validate File Format/Extension
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {ext}. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
        
    # 2. Read file bytes and validate size
    try:
        content_bytes = await file.read()
        file_size_mb = len(content_bytes) / (1024 * 1024)
        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum upload size limits of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
            
        # 3. Parse text based on document type
        text_content = DocumentParser.extract_text(file.filename, content_bytes)
        
        # 4. Check parsed length
        if len(text_content.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Extracted document text content is too short (min 10 characters)."
            )
            
        # 5. Run Predictor
        result = predictor.predict(text_content)
        
        if result.get("status") != "Success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("status", "Prediction failed")
            )
            
        snippet = text_content[:150] + ("..." if len(text_content) > 150 else "")
        
        # 6. Save history logs including original filename
        history_item = PredictionHistory(
            text_snippet=snippet,
            file_name=file.filename,
            predicted_label=result["label"],
            confidence=result["confidence"]
        )
        db.add(history_item)
        db.commit()
        db.refresh(history_item)
        
        return PredictResponse(
            text_snippet=snippet,
            label=result["label"],
            label_id=result["label_id"],
            confidence=result["confidence"],
            timestamp=datetime.datetime.utcnow(),
            status="Success"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing uploaded file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
