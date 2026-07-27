from fastapi import APIRouter
from app.api.endpoints import predict, model, history

api_router = APIRouter()

api_router.include_router(predict.router, tags=["Predictions"])
api_router.include_router(model.router, tags=["Model Operations"])
api_router.include_router(history.router, tags=["Prediction History"])
