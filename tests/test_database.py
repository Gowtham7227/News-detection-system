from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.history import PredictionHistory

def test_database_model_logs():
    engine = create_engine("sqlite:///:memory:")
    SessionClass = sessionmaker(bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = SessionClass()
    
    log = PredictionHistory(
        text_snippet="Relief package passed...",
        predicted_label="Real News",
        confidence=0.941
    )
    db.add(log)
    db.commit()
    
    retrieved = db.query(PredictionHistory).first()
    assert retrieved is not None
    assert retrieved.predicted_label == "Real News"
    assert retrieved.confidence == 0.941
    
    db.close()
