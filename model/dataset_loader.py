import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


class DatasetLoader:
    """
    Handles loading raw datasets from CSV or TSV, preprocessing text,
    and splitting data into training and test datasets.
    Includes a fallback synthetic generator to allow immediate model testing.
    """

    def __init__(self, raw_data_path: str = "data/raw", processed_data_path: str = "data/processed"):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path

    def load_dataset(self, filename: str = None) -> pd.DataFrame:
        """
        Loads the dataset from the raw directory. If no file is specified or found,
        it automatically generates a high-quality synthetic dataset of real and fake news.
        """
        if filename:
            full_path = os.path.join(self.raw_data_path, filename)
            if os.path.exists(full_path):
                print(f"Loading dataset from {full_path}")
                if filename.endswith(".csv"):
                    return pd.read_csv(full_path)
                elif filename.endswith(".tsv") or filename.endswith(".txt"):
                    return pd.read_csv(full_path, sep="\t")
            else:
                print(f"Warning: File {full_path} not found.")

        # Fallback to check if any csv file exists in raw folder
        if os.path.exists(self.raw_data_path):
            files = [f for f in os.listdir(self.raw_data_path) if f.endswith(".csv")]
            if files:
                fallback_path = os.path.join(self.raw_data_path, files[0])
                print(f"Loading first available CSV: {fallback_path}")
                return pd.read_csv(fallback_path)

        print("No input datasets found in raw data directory. Generating synthetic news dataset...")
        return self.generate_synthetic_data()

    def generate_synthetic_data(self, num_samples: int = 1000) -> pd.DataFrame:
        """
        Generates dummy/synthetic data for testing out of the box.
        """
        np.random.seed(42)
        
        real_news_templates = [
            "Congress passed the economic relief bill yesterday with bipartisan support. The new legislation aims to support small business owners and families.",
            "Scientists at the research institute have discovered a new enzyme that could degrade plastic in ocean waters in record time, offering a new solution to pollution.",
            "Local municipal authorities announced updates to the public transit system, introducing new electric buses to reduce carbon emissions across the city center.",
            "The Federal Reserve decided to maintain current interest rates following their monthly monetary policy board session, citing steady economic growth metrics.",
            "Medical researchers published a peer-reviewed clinical trial proving the safety and efficacy of the new malaria vaccine in young children."
        ]

        fake_news_templates = [
            "SHOCKING: Secret documents prove the government is using weather control satellites to manipulate election outcomes in major states! Spread this now!",
            "BREAKING NEWS: A secret potion made of common kitchen herbs has been proven to cure all cancers instantly, but major pharmaceutical lobbies are hiding it!",
            "Aliens have landed in a remote region of New Mexico, and the military has quarantined the entire town to hide the extraterrestrial spaceship.",
            "Unbelievable: Local politician caught on camera funneling millions of dollars of public school funds directly into their private offshore cryptocurrency accounts!",
            "An anonymous source reveals that the moon landing was filmed entirely inside a Hollywood studio directed by famous filmmakers."
        ]

        data = []
        for _ in range(num_samples):
            label = np.random.choice([0, 1])  # 0: Fake, 1: Real
            if label == 1:
                text = np.random.choice(real_news_templates)
            else:
                text = np.random.choice(fake_news_templates)
            
            # Add some minor noise/variation to texts
            words = text.split()
            if len(words) > 5:
                noise_index = np.random.randint(0, len(words))
                words[noise_index] = words[noise_index] + " "
            data.append({"text": " ".join(words), "label": label})

        df = pd.DataFrame(data)
        
        # Save synthetic data to raw folder for consistency
        os.makedirs(self.raw_data_path, exist_ok=True)
        synthetic_file = os.path.join(self.raw_data_path, "synthetic_news.csv")
        df.to_csv(synthetic_file, index=False)
        print(f"Synthetic dataset saved to {synthetic_file}")
        
        return df

    def prepare_splits(self, df: pd.DataFrame, text_col: str = "text", label_col: str = "label", 
                       test_size: float = 0.2, random_state: int = 42) -> tuple:
        """
        Splits DataFrame into Train and Test inputs/labels.
        """
        X = df[text_col]
        y = df[label_col]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    loader = DatasetLoader()
    df = loader.load_dataset()
    print("Dataset shape:", df.shape)
    print("Class counts:")
    print(df['label'].value_counts())
    
    X_train, X_test, y_train, y_test = loader.prepare_splits(df)
    print(f"Splits prepared: Train={len(X_train)}, Test={len(X_test)}")
