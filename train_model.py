"""
Training script for Resume Category Classifier using Scikit-Learn and TF-IDF.
Trained on UpdatedResumeDataSet.csv.
Developed by DHARMIK MTH.
"""

import os
import re
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "UpdatedResumeDataSet.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILE = os.path.join(MODELS_DIR, "resume_classifier.pkl")
VECTORIZER_FILE = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
ENCODER_FILE = os.path.join(MODELS_DIR, "label_encoder.pkl")


def clean_resume_text(text: str) -> str:
    """Cleans raw resume text by stripping URLs, mentions, hashes, punctuations."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+\s*", " ", text)               # URLs
    text = re.sub(r"RT|cc", " ", text)                    # Twitter RTs
    text = re.sub(r"#\S+", " ", text)                     # Hashtags
    text = re.sub(r"@\S+", " ", text)                     # Mentions
    text = re.sub(r"[^\w\s]", " ", text)                  # Punctuations
    text = re.sub(r"[^\x00-\x7f]", " ", text)             # Non-ASCII
    text = re.sub(r"\s+", " ", text).strip()              # Extra whitespace
    return text.lower()


def train_and_save_model():
    """Trains TF-IDF + Logistic Regression on the Kaggle Resume dataset and saves artifacts."""
    print("=" * 60)
    print("AI Resume Screening & Job Matching System")
    print("Model Training Pipeline - Developed by DHARMIK MTH")
    print("=" * 60)

    # Check fallback path if not in dataset/
    dataset_file = DATASET_PATH
    if not os.path.exists(dataset_file):
        dataset_file = os.path.join(BASE_DIR, "UpdatedResumeDataSet.csv")

    if not os.path.exists(dataset_file):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH} or {dataset_file}")

    print(f"Loading dataset from: {dataset_file}")
    df = pd.read_csv(dataset_file)
    print(f"Total resumes: {len(df)} across {df['Category'].nunique()} categories")

    print("Cleaning resume texts...")
    df["cleaned_resume"] = df["Resume"].apply(clean_resume_text)

    # Encode target labels
    label_encoder = LabelEncoder()
    df["category_encoded"] = label_encoder.fit_transform(df["Category"])

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        df["cleaned_resume"],
        df["category_encoded"],
        test_size=0.2,
        random_state=42,
        stratify=df["category_encoded"]
    )

    print("Extracting TF-IDF features (unigrams & bigrams)...")
    tfidf = TfidfVectorizer(
        max_features=6000,
        ngram_range=(1, 2),
        stop_words="english",
        sublinear_tf=True
    )
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)

    print("Training Logistic Regression classifier...")
    classifier = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        random_state=42
    )
    classifier.fit(X_train_tfidf, y_train)

    y_pred = classifier.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Evaluation:")
    print(f"Test Accuracy: {accuracy * 100:.2f}%")

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(classifier, MODEL_FILE)
    joblib.dump(tfidf, VECTORIZER_FILE)
    joblib.dump(label_encoder, ENCODER_FILE)

    print(f"\nArtifacts successfully saved to: {MODELS_DIR}")
    print(f"  - Classifier: {MODEL_FILE}")
    print(f"  - TF-IDF Vectorizer: {VECTORIZER_FILE}")
    print(f"  - Label Encoder: {ENCODER_FILE}")
    print("\nTraining complete! Designed and Developed by DHARMIK MTH.")
    return accuracy


if __name__ == "__main__":
    train_and_save_model()
