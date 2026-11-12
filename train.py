"""Train a simple TF-IDF + Logistic Regression baseline.

Expected CSV: data/news.csv with columns `text` and `label`.
Labels must use 1 for REAL and 0 for FAKE. Use a documented, licensed,
representative dataset and evaluate on a held-out test set before deployment.
"""
from pathlib import Path
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "news.csv"
OUT = ROOT / "model" / "fake_news_pipeline.joblib"

if not DATA.exists():
    raise SystemExit("Missing data/news.csv. Add a labelled CSV with text,label columns first.")
df = pd.read_csv(DATA).dropna(subset=["text", "label"])
df["text"] = df["text"].astype(str)
df["label"] = df["label"].astype(int)
if set(df["label"].unique()) - {0, 1}:
    raise SystemExit("Labels must be 0 (FAKE) or 1 (REAL).")
if df["label"].nunique() != 2 or len(df) < 100:
    raise SystemExit("Provide at least 100 examples and both label classes for a basic baseline.")
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"])
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=100000, stop_words="english", min_df=2, max_df=0.98)),
    ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
])
pipeline.fit(X_train, y_train)
print(classification_report(y_test, pipeline.predict(X_test), target_names=["FAKE", "REAL"]))
OUT.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, OUT)
print(f"Saved baseline model to {OUT}")
