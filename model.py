"""
Machine Learning and Job Matching Engine.
Contains:
1. TF-IDF Cosine Similarity Job Matcher
2. Scikit-learn Classifier for predicting Resume Category
3. Dual-scoring calibration logic

Developed by DHARMIK MTH.
"""

import os
import re
import joblib
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILE = os.path.join(MODELS_DIR, "resume_classifier.pkl")
VECTORIZER_FILE = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
ENCODER_FILE = os.path.join(MODELS_DIR, "label_encoder.pkl")


def clean_text_for_ml(text: str) -> str:
    """Cleans text for TF-IDF vectorization and classifier inference."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+\s*", " ", text)
    text = re.sub(r"RT|cc", " ", text)
    text = re.sub(r"#\S+", " ", text)
    text = re.sub(r"@\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"[^\x00-\x7f]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


class ResumeClassifier:
    """Predicts Job Category for uploaded resumes using trained Scikit-learn model."""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self._load_or_train()

    def _load_or_train(self):
        """Loads model artifacts from disk or triggers auto-training."""
        if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE) and os.path.exists(ENCODER_FILE):
            try:
                self.model = joblib.load(MODEL_FILE)
                self.vectorizer = joblib.load(VECTORIZER_FILE)
                self.label_encoder = joblib.load(ENCODER_FILE)
                return
            except Exception as e:
                print(f"Warning: Failed loading saved model artifacts: {e}. Retraining...")

        # If not present or corrupt, train now
        from train_model import train_and_save_model
        train_and_save_model()
        self.model = joblib.load(MODEL_FILE)
        self.vectorizer = joblib.load(VECTORIZER_FILE)
        self.label_encoder = joblib.load(ENCODER_FILE)

    def predict_category(self, resume_text: str) -> Dict[str, Any]:
        """
        Predicts top category and top alternative categories with confidence percentages.
        """
        cleaned = clean_text_for_ml(resume_text)
        if not cleaned:
            return {
                "top_category": "General",
                "confidence": 0.0,
                "alternatives": []
            }

        text_vec = self.vectorizer.transform([cleaned])
        probs = self.model.predict_proba(text_vec)[0]

        # Top 5 indices
        top_indices = np.argsort(probs)[::-1][:5]
        top_category = self.label_encoder.inverse_transform([top_indices[0]])[0]
        top_confidence = round(float(probs[top_indices[0]]) * 100, 1)

        alternatives = []
        for idx in top_indices[1:]:
            cat_name = self.label_encoder.inverse_transform([idx])[0]
            cat_conf = round(float(probs[idx]) * 100, 1)
            if cat_conf > 1.0:  # Only report realistic alternatives
                alternatives.append({
                    "category": cat_name,
                    "confidence": cat_conf
                })

        return {
            "top_category": top_category,
            "confidence": top_confidence,
            "alternatives": alternatives
        }


class JobMatcher:
    """
    Computes TF-IDF Vectorizer Cosine Similarity and composite scoring
    between resume text and job description text.
    """

    @staticmethod
    def calculate_cosine_similarity(resume_text: str, jd_text: str) -> float:
        """
        Computes cosine similarity (0 to 100%) between resume and job description using TF-IDF.
        """
        cleaned_resume = clean_text_for_ml(resume_text)
        cleaned_jd = clean_text_for_ml(jd_text)

        if not cleaned_resume or not cleaned_jd:
            return 0.0

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )

        try:
            tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity * 100.0)
        except Exception:
            return 0.0

    @classmethod
    def evaluate_match(cls, resume_text: str, jd_text: str, skill_coverage_percent: float) -> Dict[str, Any]:
        """
        Calculates calibrated overall match score combining:
        1. TF-IDF Cosine Similarity (Semantic & keyword distribution): 50%
        2. Direct Skill Match Coverage: 50%
        """
        tfidf_score = cls.calculate_cosine_similarity(resume_text, jd_text)

        # Calibrated Composite Score
        composite_score = (0.50 * tfidf_score) + (0.50 * skill_coverage_percent)
        composite_score = round(min(100.0, max(0.0, composite_score)), 1)
        tfidf_score = round(tfidf_score, 1)

        # Determine Match Tier & Badge Color
        if composite_score >= 80:
            rating = "Excellent Fit"
            color = "emerald"
            badge_class = "badge-excellent"
            summary_message = "Outstanding alignment with the job description. The candidate exhibits strong skill overlap and contextual keyword relevance."
        elif composite_score >= 65:
            rating = "Strong Match"
            color = "blue"
            badge_class = "badge-strong"
            summary_message = "Good fit for the target role. Resume demonstrates core relevant proficiencies with minor gaps in secondary requirements."
        elif composite_score >= 45:
            rating = "Moderate Match"
            color = "amber"
            badge_class = "badge-moderate"
            summary_message = "Partial match. Found transferable skills, but key mandatory competencies from the job description are missing."
        else:
            rating = "Low Match"
            color = "rose"
            badge_class = "badge-low"
            summary_message = "Significant divergence. The candidate's background does not align well with the primary requirements of this position."

        return {
            "overall_score": composite_score,
            "tfidf_score": tfidf_score,
            "skill_score": skill_coverage_percent,
            "rating": rating,
            "color": color,
            "badge_class": badge_class,
            "summary_message": summary_message
        }


# Singleton instances for high performance in Flask
classifier_instance = None


def get_classifier() -> ResumeClassifier:
    """Returns singleton instance of ResumeClassifier."""
    global classifier_instance
    if classifier_instance is None:
        classifier_instance = ResumeClassifier()
    return classifier_instance
