"""
train_model.py
==============
Trains a TF-IDF + Logistic Regression intent classifier and saves
the model and vectorizer using joblib.

Run this once before starting the assistant:
    python train_model.py
"""

import os
import sys

# Make sure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import joblib
import numpy as np

from data.training_data import TRAINING_DATA

# ── paths ──────────────────────────────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)

VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
MODEL_PATH      = os.path.join(MODEL_DIR, "intent_model.joblib")


def train():
    print("=" * 50)
    print("  Smart Assistant – Model Training")
    print("=" * 50)

    # Split data into sentences and labels
    sentences = [item[0] for item in TRAINING_DATA]
    labels    = [item[1] for item in TRAINING_DATA]

    print(f"\n✔  Loaded {len(sentences)} training examples across "
          f"{len(set(labels))} intents.")

    # Build a Pipeline: TF-IDF → Logistic Regression
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # unigrams + bigrams
        analyzer="word",
        lowercase=True,
    )
    clf = LogisticRegression(max_iter=1000, C=5.0, solver="lbfgs")

    pipeline = Pipeline([
        ("tfidf", vectorizer),
        ("clf",   clf),
    ])

    # Cross-validation to see how well the model generalises
    scores = cross_val_score(pipeline, sentences, labels, cv=5, scoring="accuracy")
    print(f"\n✔  5-fold CV accuracy: {np.mean(scores):.2%} "
          f"(±{np.std(scores):.2%})")

    # Train on ALL data before saving
    pipeline.fit(sentences, labels)
    print("✔  Final model trained on full dataset.")

    # Save vectorizer and model separately (so modules can load them independently)
    joblib.dump(pipeline.named_steps["tfidf"], VECTORIZER_PATH)
    joblib.dump(pipeline.named_steps["clf"],   MODEL_PATH)

    print(f"\n✔  Vectorizer saved → {VECTORIZER_PATH}")
    print(f"✔  Model saved      → {MODEL_PATH}")
    print("\nTraining complete! You can now run:  python main.py\n")


if __name__ == "__main__":
    train()
