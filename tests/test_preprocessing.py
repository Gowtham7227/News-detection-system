from model.preprocessing import TextPreprocessor

def test_clean_text():
    preprocessor = TextPreprocessor()
    raw_text = "<html><body>Verify: Http://Google.Com?q=Test! 123.</body></html>"
    cleaned = preprocessor.clean_text(raw_text)
    
    assert "verify" in cleaned
    assert "google" not in cleaned
    assert "123" not in cleaned
    assert "<html" not in cleaned

def test_tokenize_and_lemmatize():
    preprocessor = TextPreprocessor()
    raw_text = "The scientists are searching for new discoveries."
    processed = preprocessor.tokenize_and_lemmatize(raw_text)
    
    assert "scientist" in processed or "scientific" in processed or "scientists" in processed
    assert "are" not in processed
