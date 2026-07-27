import os
import json
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from model.preprocessing import TextPreprocessor
from model.dataset_loader import DatasetLoader
from model.feature_extraction import FeatureExtractor


class ModelTrainer:
    """
    Coordinates loading data, preprocessing, TF-IDF vectorization,
    training candidate models, comparing them, and saving the best candidate.
    """

    def __init__(self, artifacts_dir: str = "model/artifacts", reports_dir: str = "reports"):
        self.artifacts_dir = artifacts_dir
        self.reports_dir = reports_dir
        self.preprocessor = TextPreprocessor()
        self.loader = DatasetLoader()
        
        # Models configuration dictionary
        self.models = {
            "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
            "Naive Bayes": MultinomialNB(alpha=1.0),
            "Linear SVM": LinearSVC(C=1.0, dual=False, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
        }
        
        os.makedirs(self.artifacts_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def run_training_pipeline(self) -> str:
        """
        Executes the full pipeline:
        1. Load dataset (generate synthetic if none)
        2. Preprocess texts
        3. Feature extraction (TF-IDF Vectorization)
        4. Model training & comparison
        5. Save best model and vectorizer
        """
        print("--- Starting Fake News Detection Model Training Pipeline ---")
        
        # 1. Load data
        df = self.loader.load_dataset()
        X_train_raw, X_test_raw, y_train, y_test = self.loader.prepare_splits(df)
        
        # 2. Preprocess text
        print("Preprocessing training corpus...")
        X_train_cleaned = self.preprocessor.preprocess_series(X_train_raw)
        print("Preprocessing testing corpus...")
        X_test_cleaned = self.preprocessor.preprocess_series(X_test_raw)
        
        # 3. Extract features
        print("Fitting TF-IDF Vectorizer...")
        extractor = FeatureExtractor(max_features=5000)
        X_train_vec = extractor.fit_transform(X_train_cleaned)
        X_test_vec = extractor.transform(X_test_cleaned)
        
        # Save vectorizer immediately
        vectorizer_path = os.path.join(self.artifacts_dir, "tfidf_vectorizer.pkl")
        extractor.save_vectorizer(vectorizer_path)
        
        # 4. Train and evaluate models
        comparison_results = {}
        best_f1 = -1.0
        best_model_name = ""
        best_model_obj = None

        print("\nTraining and evaluating models...")
        for name, clf in self.models.items():
            print(f"Training {name}...")
            clf.fit(X_train_vec, y_train)
            
            # Predict
            preds = clf.predict(X_test_vec)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, preds)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_test, preds, average="binary"
            )
            
            print(f"[{name}] Acc: {accuracy:.4f} | Prec: {precision:.4f} | Rec: {recall:.4f} | F1: {f1:.4f}")
            
            comparison_results[name] = {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1)
            }
            
            # Choose best model based on F1 Score
            if f1 > best_f1:
                best_f1 = f1
                best_model_name = name
                best_model_obj = clf

        print(f"\n--- Best Model Identified: {best_model_name} (F1 Score: {best_f1:.4f}) ---")
        
        # 5. Save the best model
        best_model_filename = "best_model.pkl"
        model_save_path = os.path.join(self.artifacts_dir, best_model_filename)
        joblib.dump(best_model_obj, model_save_path)
        print(f"Best model saved to {model_save_path}")
        
        # Save comparison report JSON
        report_path = os.path.join(self.reports_dir, "model_comparison.json")
        with open(report_path, "w") as f:
            json.dump({
                "best_model": best_model_name,
                "metrics": comparison_results
            }, f, indent=4)
        print(f"Comparison report saved to {report_path}")
        
        # Save test splits for evaluation module
        test_data_path = os.path.join(self.artifacts_dir, "test_split.pkl")
        joblib.dump((X_test_cleaned, y_test), test_data_path)
        
        return best_model_name


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run_training_pipeline()
