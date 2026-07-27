import os
import json
import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

# Optional import for plotting
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False


class ModelEvaluator:
    """
    Loads saved test datasets, models, and vectorizers, generates prediction metrics,
    creates classification reports, and plots/saves the confusion matrix.
    """

    def __init__(self, artifacts_dir: str = "model/artifacts", reports_dir: str = "reports"):
        self.artifacts_dir = artifacts_dir
        self.reports_dir = reports_dir
        
        self.vectorizer_path = os.path.join(self.artifacts_dir, "tfidf_vectorizer.pkl")
        self.model_path = os.path.join(self.artifacts_dir, "best_model.pkl")
        self.test_data_path = os.path.join(self.artifacts_dir, "test_split.pkl")
        
        os.makedirs(self.reports_dir, exist_ok=True)

    def evaluate(self) -> dict:
        """
        Executes model evaluations on testing dataset and outputs metrics/plots.
        """
        print("--- Initiating Model Evaluation Protocol ---")
        
        # Load artifacts
        if not os.path.exists(self.model_path) or not os.path.exists(self.vectorizer_path):
            raise FileNotFoundError("Model or Vectorizer artifacts missing. Please run train.py first.")
            
        if not os.path.exists(self.test_data_path):
            raise FileNotFoundError("Test data split file missing. Please run train.py first.")
            
        print("Loading evaluation artifacts...")
        vectorizer = joblib.load(self.vectorizer_path)
        model = joblib.load(self.model_path)
        X_test_cleaned, y_test = joblib.load(self.test_data_path)
        
        # Transform features
        print("Extracting test text features...")
        X_test_vec = vectorizer.transform(X_test_cleaned)
        
        # Predict
        print("Predicting test labels...")
        preds = model.predict(X_test_vec)
        
        # Metrics
        accuracy = accuracy_score(y_test, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, preds, average="binary"
        )
        conf_matrix = confusion_matrix(y_test, preds)
        cls_report = classification_report(y_test, preds, target_names=["Fake News", "Real News"])
        
        print("\n--- Classification Performance Report ---")
        print(cls_report)
        
        print("\n--- Confusion Matrix (Text representation) ---")
        print(f"True Negative (Fake): {conf_matrix[0][0]} | False Positive (Fake predicted as Real): {conf_matrix[0][1]}")
        print(f"False Negative (Real predicted as Fake): {conf_matrix[1][0]} | True Positive (Real): {conf_matrix[1][1]}")
        
        # Save JSON Report
        evaluation_metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "confusion_matrix": {
                "tn": int(conf_matrix[0][0]),
                "fp": int(conf_matrix[0][1]),
                "fn": int(conf_matrix[1][0]),
                "tp": int(conf_matrix[1][1])
            }
        }
        
        metrics_json_path = os.path.join(self.reports_dir, "evaluation_metrics.json")
        with open(metrics_json_path, "w") as f:
            json.dump(evaluation_metrics, f, indent=4)
        print(f"\nSaved evaluation metrics JSON report to {metrics_json_path}")
        
        # Generate Confusion Matrix Visual Plot
        self.save_confusion_matrix_plot(conf_matrix)
        
        return evaluation_metrics

    def save_confusion_matrix_plot(self, conf_matrix: np.ndarray) -> None:
        """
        Saves a heatmapped confusion matrix plot to reports directory.
        """
        plot_path = os.path.join(self.reports_dir, "confusion_matrix.png")
        
        if PLOT_AVAILABLE:
            try:
                plt.figure(figsize=(6, 5))
                sns.heatmap(
                    conf_matrix, 
                    annot=True, 
                    fmt="d", 
                    cmap="Blues", 
                    xticklabels=["Fake News", "Real News"],
                    yticklabels=["Fake News", "Real News"]
                )
                plt.title("Confusion Matrix - Fake News Classifier")
                plt.ylabel("Actual Label")
                plt.xlabel("Predicted Label")
                plt.tight_layout()
                plt.savefig(plot_path, dpi=300)
                plt.close()
                print(f"Confusion matrix plot successfully saved to {plot_path}")
            except Exception as e:
                print(f"Warning: Failed to generate visualization plot due to: {e}")
        else:
            print("Note: matplotlib or seaborn libraries not installed. Skipping graphical plot.")
            print(f"To enable graphical output, add matplotlib and seaborn dependencies.")


if __name__ == "__main__":
    evaluator = ModelEvaluator()
    evaluator.evaluate()
