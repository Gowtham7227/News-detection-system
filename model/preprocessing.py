import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Securely download necessary NLTK data if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)


class TextPreprocessor:
    """
    Text preprocessing pipeline for cleaning raw news articles.
    Applies lowercasing, HTML stripping, punctuation removal, stopword removal, and lemmatization.
    """

    def __init__(self, use_stemming: bool = False):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.use_stemming = use_stemming
        
        if self.use_stemming:
            from nltk.stem import PorterStemmer
            self.stemmer = PorterStemmer()

    def clean_text(self, text: str) -> str:
        """
        Cleans input string by removing HTML, punctuation, numbers, and converting to lowercase.
        """
        if not isinstance(text, str):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove digits/numbers
        text = re.sub(r'\d+', '', text)

        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize_and_lemmatize(self, text: str) -> str:
        """
        Cleans text, tokenizes, removes stopwords, and lemmatizes (or stems) each token.
        """
        cleaned_text = self.clean_text(text)
        tokens = cleaned_text.split()

        # Remove stopwords and apply lemmatization/stemming
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                if self.use_stemming:
                    processed_tokens.append(self.stemmer.stem(token))
                else:
                    processed_tokens.append(self.lemmatizer.lemmatize(token))

        return " ".join(processed_tokens)

    def preprocess_series(self, texts: list) -> list:
        """
        Preprocesses a list/pandas Series of strings.
        """
        return [self.tokenize_and_lemmatize(t) for t in texts]


if __name__ == "__main__":
    # Quick smoke test
    preprocessor = TextPreprocessor()
    sample_text = "<html><body>Warning! Fake news detected on http://example.com by Admin@test.com. The 5 key facts.</body></html>"
    print("Original:", sample_text)
    print("Cleaned: ", preprocessor.tokenize_and_lemmatize(sample_text))
