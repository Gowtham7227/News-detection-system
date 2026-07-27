import os
import json
import logging
import joblib
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.schemas.prediction import ModelMetrics, ModelInfoResponse
from app.core.config import settings

# Lazy imports for model operations
try:
    from model.train import ModelTrainer
    from model.evaluate import ModelEvaluator
    TRAINER_AVAILABLE = True
except ImportError:
    TRAINER_AVAILABLE = False

router = APIRouter()
logger = logging.getLogger("fakenews.model")

# Track retraining state in memory
RETRAINING_IN_PROGRESS = False


def execute_retraining_task() -> None:
    """
    Background worker function that triggers dataset load, text cleaning,
    feature extraction, model training, best model picking, and re-evaluation.
    """
    global RETRAINING_IN_PROGRESS
    try:
        logger.info("Background model retraining process initiated...")
        
        # 1. Initialize trainer and run pipeline
        trainer = ModelTrainer()
        best_model_name = trainer.run_training_pipeline()
        logger.info(f"Model retraining completed. Best candidate chosen: {best_model_name}")
        
        # 2. Run evaluator to update metrics reports
        evaluator = ModelEvaluator()
        evaluator.evaluate()
        logger.info("Evaluation metrics refreshed successfully.")
    except Exception as e:
        logger.error(f"Error during background model retraining: {e}", exc_info=True)
    finally:
        RETRAINING_IN_PROGRESS = False


@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED, summary="Trigger model retraining pipeline in background")
def retrain_model(background_tasks: BackgroundTasks):
    """
    Kicks off the machine learning model training pipeline asynchronously.
    Updates classifiers and writes results back to the artifacts registry.
    """
    global RETRAINING_IN_PROGRESS
    
    if not TRAINER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning training dependencies are not available."
        )
        
    if RETRAINING_IN_PROGRESS:
        return {"status": "Processing", "message": "Model retraining is already running in the background."}
        
    RETRAINING_IN_PROGRESS = True
    background_tasks.add_task(execute_retraining_task)
    
    return {"status": "Accepted", "message": "Model retraining pipeline launched successfully in background."}


@router.get("/metrics", response_model=ModelMetrics, summary="Retrieve active model classification metrics")
def get_model_metrics():
    """
    Fetches the evaluation accuracy, precision, recall, and F1 metrics
    generated during the last model training/evaluation iteration.
    """
    metrics_path = "reports/evaluation_metrics.json"
    if not os.path.exists(metrics_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics report not found. The model might not have been evaluated yet."
        )
    try:
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f)
        return ModelMetrics(**metrics_data)
    except Exception as e:
        logger.error(f"Error loading metrics report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse evaluation metrics report."
        )


@router.get("/model-info", response_model=ModelInfoResponse, summary="Get details of active classification model")
def get_model_info():
    """
    Inspects active serialized pipeline models and vectorizers to report details
    such as feature dimensions, classifier type, and modification dates.
    """
    model_path = os.path.join("model/artifacts", "best_model.pkl")
    vectorizer_path = os.path.join("model/artifacts", "tfidf_vectorizer.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        return ModelInfoResponse(
            model_name="Uninitialized",
            vectorizer_type="Uninitialized",
            max_features=0,
            vocabulary_size=0,
            last_trained="Never",
            status="No trained model artifacts found."
        )
        
    try:
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        # Get last modification time
        mtime = os.path.getmtime(model_path)
        from datetime import datetime
        last_trained_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        # Get info on loaded models
        model_name = type(model).__name__
        vec_name = type(vectorizer).__name__
        vocab_size = len(vectorizer.vocabulary_) if hasattr(vectorizer, "vocabulary_") else 0
        max_features = vectorizer.max_features if hasattr(vectorizer, "max_features") else 0
        
        return ModelInfoResponse(
            model_name=model_name,
            vectorizer_type=vec_name,
            max_features=max_features or vocab_size,
            vocabulary_size=vocab_size,
            last_trained=last_trained_date,
            status="Active"
        )
    except Exception as e:
        logger.error(f"Error reading model artifacts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inspecting model configurations: {str(e)}"
        )
