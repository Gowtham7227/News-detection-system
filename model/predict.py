import os
import joblib
import numpy as np
from model.preprocessing import TextPreprocessor


class FakeNewsPredictor:
    """
    Inference interface for loading models and classifying news texts.
    Maps raw text inputs to fake/real label predictions and confidence percentages.
    """

    def __init__(self, artifacts_dir: str = "model/artifacts"):
        self.artifacts_dir = artifacts_dir
        self.vectorizer_path = os.path.join(self.artifacts_dir, "tfidf_vectorizer.pkl")
        self.model_path = os.path.join(self.artifacts_dir, "best_model.pkl")
        
        self.preprocessor = TextPreprocessor()
        self.vectorizer = None
        self.model = None
        
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """
        Loads the pre-trained vectorizer and best classification model.
        """
        if not os.path.exists(self.model_path) or not os.path.exists(self.vectorizer_path):
            raise FileNotFoundError(
                "Model or Vectorizer artifacts missing. Please train a model first using train.py."
            )
        
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.model = joblib.load(self.model_path)
        print("FakeNewsPredictor successfully initialized and artifacts loaded.")

    def predict(self, text: str) -> dict:
        """
        Preprocesses raw input text, extracts features, performs inference,
        and estimates prediction confidence.
        """
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            return {
                "text": text,
                "label": "Unknown",
                "label_id": -1,
                "confidence": 0.0,
                "status": "Empty text provided"
            }

        # 1. Preprocess
        cleaned_text = self.preprocessor.tokenize_and_lemmatize(text)
        
        # 2. Extract Features
        features = self.vectorizer.transform([cleaned_text])
        
        # 3. Model Prediction
        prediction_id = int(self.model.predict(features)[0])
        label = "Real News" if prediction_id == 1 else "Fake News"
        
        # 4. Calculate Confidence (handling models without predict_proba e.g. LinearSVC)
        confidence = 0.5
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(features)[0]
            confidence = float(probabilities[prediction_id])
        elif hasattr(self.model, "decision_function"):
            decision_score = self.model.decision_function(features)[0]
            # Map decision score to probability using Sigmoid (Platt scaling approximation)
            prob_real = 1 / (1 + np.exp(-decision_score))
            confidence = float(prob_real if prediction_id == 1 else (1 - prob_real))
            
        return {
            "text": text,
            "label": label,
            "label_id": prediction_id,
            "confidence": round(confidence, 4),
            "status": "Success"
        }


if __name__ == "__main__":
    # Smoke test runs if artifacts exist
    try:
        predictor = FakeNewsPredictor()
        
        real_sample = "The research team published their finding showing solar panels increased efficiency by 15%."
        fake_sample = "CONFIRMED: The government has banned all home solar panels to prevent off-grid power access!"
        
        print("\nTesting Real Sample:")
        print(predictor.predict(real_sample))
        
        print("\nTesting Fake Sample:")
        print(predictor.predict(fake_sample))
    except Exception as e:
        print(f"Skipping quick prediction test: {e}")
        print("Please train your model using train.py first to run predictions.")
