import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


class FeatureExtractor:
    """
    Wrapper for Scikit-Learn's TfidfVectorizer.
    Handles fitting on training text, transforming training/testing corpus,
    and saving/loading the vectorizer configuration.
    """

    def __init__(self, max_features: int = 5000, ngram_range: tuple = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            sublinear_tf=True
        )

    def fit(self, train_texts: list) -> 'FeatureExtractor':
        """
        Fits the TF-IDF Vectorizer on training documents.
        """
        self.vectorizer.fit(train_texts)
        return self

    def transform(self, texts: list):
        """
        Transforms text articles to TF-IDF sparse matrix format.
        """
        return self.vectorizer.transform(texts)

    def fit_transform(self, train_texts: list):
        """
        Fits and transforms text articles at the same time.
        """
        return self.vectorizer.fit_transform(train_texts)

    def save_vectorizer(self, filepath: str) -> None:
        """
        Saves the fitted vectorizer object to the given filepath.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.vectorizer, filepath)
        print(f"Vectorizer successfully saved to {filepath}")

    def load_vectorizer(self, filepath: str) -> 'FeatureExtractor':
        """
        Loads a pre-trained TF-IDF vectorizer.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No vectorizer artifact found at {filepath}")
        self.vectorizer = joblib.load(filepath)
        print(f"Vectorizer successfully loaded from {filepath}")
        return self


if __name__ == "__main__":
    texts = [
        "President signs bill into national law.",
        "Breaking: Aliens spotted inside capital buildings!"
    ]
    extractor = FeatureExtractor(max_features=10)
    features = extractor.fit_transform(texts)
    print("Features matrix shape:", features.shape)
    print("Feature names:", extractor.vectorizer.get_feature_names_out())
