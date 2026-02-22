"""
modules/intent_classifier.py
==============================
Loads the saved TF-IDF vectorizer and Logistic Regression model,
then exposes a single predict() function used by main.py.
"""

import os
import joblib

# ── paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "vectorizer.joblib")
MODEL_PATH      = os.path.join(BASE_DIR, "model", "intent_model.joblib")

# Module-level cache so we only load the model once
_vectorizer = None
_model      = None


def _load_models():
    """Load models from disk (only once per session)."""
    global _vectorizer, _model

    if _vectorizer is None or _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Please run  python train_model.py  first."
            )
        _vectorizer = joblib.load(VECTORIZER_PATH)
        _model      = joblib.load(MODEL_PATH)


def predict(text: str) -> str:
    """
    Predict the intent of the given text.

    Parameters
    ----------
    text : str
        The user's raw input sentence.

    Returns
    -------
    str
        One of the intent labels, e.g. 'greeting', 'tell_time', etc.
    """
    _load_models()
    vec    = _vectorizer.transform([text.lower()])
    intent = _model.predict(vec)[0]
    return intent


def predict_with_confidence(text: str) -> tuple[str, float]:
    """
    Same as predict() but also returns the confidence score (0–1).
    Useful for debugging / fallback logic.
    """
    _load_models()
    vec         = _vectorizer.transform([text.lower()])
    intent      = _model.predict(vec)[0]
    proba       = _model.predict_proba(vec).max()
    return intent, float(proba)
