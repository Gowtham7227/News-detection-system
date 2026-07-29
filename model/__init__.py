# model/__init__.py
# Sub-modules are imported lazily to prevent startup crashes when
# optional dependencies (NLTK data, sklearn, joblib artifacts) are missing.

__all__ = [
    "TextPreprocessor",
    "DatasetLoader",
    "FeatureExtractor",
    "ModelTrainer",
    "ModelEvaluator",
    "FakeNewsPredictor"
]
